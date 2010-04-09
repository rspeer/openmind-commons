import os, logging
import cPickle as pickle
from gzip import GzipFile
from django.conf import settings
from stat import ST_MTIME
joinpath = os.path.join

from csc.conceptnet4.analogyspace import conceptnet_2d_from_db
from csc.conceptnet4.analogyspace import concept_similarity, predict_features
from csc.conceptnet4.models import Feature
from csc.divisi.labeled_view import LabeledSVD2DResults

class SVDMissing(Exception):
    should_log = False
    user_visible = True
    http_code = 400 # HTTP Bad request
    
    def __init__(self, lang):
        Exception.__init__(self, 'SVD missing for language %s' % lang)

def tensor_filename(lang):
    return joinpath(settings.TENSOR_ROOT, lang+'_tensor')
def svd_filename(lang):
    return joinpath(settings.TENSOR_ROOT, lang+'_svd')

def get_modification_time(filename):
    return os.stat(filename)[ST_MTIME]

def _cache_load(cache, key, filename):
    if key not in cache: return None

    data, cached_mtime = cache[key]

    # If the file is newer than the cache, the cache is invalid.
    if cached_mtime < get_modification_time(filename): return None

    return data

def _get_cached(cache, key, filename, format):
    # Try to load from cache
    cached = _cache_load(cache, key, filename)
    if cached is not None:
        logging.info('Cache hit.')
        return cached

    # Get modification time first, to avoid the race condition while loading.
    actual_mtime = get_modification_time(filename)

    # Load
    logging.info('Loading...')
    if format == 'pytables':
        data = LabeledSVD2DResults.load_pytables(filename, copy=True)
    elif format == 'pickle':
        if filename.endswith('.gz'):
            file = GzipFile(filename, 'rb')
        else:
            file = open(filename, 'rb')
        data = pickle.load(file)

    # Cache the results
    logging.info('Saving to cache.')
    cache[key] = (data, actual_mtime)

    return data

_tensor_cache = {}
_svd_cache = {}

def get_tensor(lang):
    try:
        return _get_cached(_tensor_cache, lang, tensor_filename(lang), format='pickle')
    except OSError:
        raise SVDMissing(lang)

def get_svd_results(lang):
    try:
        return _get_cached(_svd_cache, lang, svd_filename(lang), format='pytables')
    except OSError:
        raise SVDMissing(lang)

#
# Computing the SVD
#
IDENTITIES = 3
CUTOFF=3

def run_analogy_space_lang(lang):
    # Open files (fail early on errors)
    tensor_name = tensor_filename(lang)
    tensor_name_new = tensor_name+'_new'
    tensor_file = GzipFile(tensor_name_new, 'wb')

    svd_name = svd_filename(lang)
    svd_name_new = svd_name + '_new'
    
    # Load matrix
    logging.info('Loading %s'% lang)
    cnet_2d = conceptnet_2d_from_db(lang, identities=IDENTITIES, cutoff=CUTOFF)
    logging.info('Normalize %r' % cnet_2d)
    cnet_2d = cnet_2d.normalized()

    # Save tensor
    logging.info('Save tensor as %s' % tensor_name)
    pickle.dump(cnet_2d, tensor_file, -1)
    tensor_file.close()
    os.rename(tensor_name_new, tensor_name)

    logging.info('Running SVD')
    svd = cnet_2d.svd(k=100)

    # Save SVD
    logging.info('Save as %s' % svd_name)
    svd.save_pytables(svd_name_new)
    os.rename(svd_name_new, svd_name)

def get_predictions_from_vector(lang, concepts, cat, count):
    count = 100
    tensor = get_tensor(lang)
    svd = get_svd_results(lang)
    items = svd.v_dotproducts_with(cat).top_items(count)
    print len(items)

    for feature, score in items:
        for concept in concepts:
            print concept, feature, score
            # Exclude items that are already in the database.
            # FIXME: check tensor format
            if (concept, feature) in tensor: continue
            print 'not in tensor'

            if not isinstance(feature, tuple): continue
            f = Feature.from_tuple(feature)
            if f.relation == u'InheritsFrom': continue
            print f
            
            prop = f.fill_in(concept)
            print prop

            # Exclude self-relations.
            if prop.concept1 == prop.concept2: continue

            yield prop, score

def predictions_for_concept(lang, concept, count):
    svd = get_svd_results(lang)
    if concept not in svd.u.label_list(0): return
    tensor = get_tensor(lang)
    predictions = predict_features(svd, concept).top_items(count*5)
    for feature, score in predictions:
        if (concept, feature) in tensor: continue
        if not isinstance(feature, tuple): continue
        f = Feature.from_tuple(feature)
        if f.relation.name == u'InheritsFrom': continue
        prop = f.fill_in(concept)
        if prop.concept1 == prop.concept2: continue
        yield prop, score

def similarities_for_concept(lang, concept, count):
    svd = get_svd_results(lang)
    if concept not in svd.u.label_list(0): return []
    return concept_similarity(svd, concept).top_items(count)

def all_svd_concepts(lang):
    svd = get_svd_results(lang)
    return svd.u.label_list(0)