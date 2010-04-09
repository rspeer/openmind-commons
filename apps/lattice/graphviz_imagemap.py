'''
Little library to do client-side imagemaps with Graphviz.

Uses Django's caching API to allow the image to be fetched separatedly
from its map.
'''

from django.core.cache import cache
import os.path
from subprocess import Popen
import tempfile

def _hash(s):
    import hashlib
    return hashlib.sha1(s).hexdigest()

CACHE_PREFIX = 'gviz_cmap_'

def serve_cached_image(request, key):
    from django.http import HttpResponse, Http404
    cache_key = CACHE_PREFIX + key
    res = cache.get(cache_key, None)
    if res is None:
        raise Http404
    cmap, img = res
    return HttpResponse(img, mimetype='image/png')


def name_for_map(m):
    import re
    return re.match('^<map id="([^"]+)"', m).group(1)


class GVGraph(object):
    def __init__(self, dot_src, engine='dot', cache_timeout=120):
        self.dot_src = dot_src
        self.engine = engine
        self.key = '%s_%s' % (engine, _hash(dot_src))
        self.cache_key = CACHE_PREFIX + self.key

    def clientside_map(self):
        res = cache.get(self.cache_key, None)
        if res is None:
            res = self._compute_cmap()
            cache.set(self.cache_key, res, 30)
        return res

    @property
    def map(self):
        cmap, img = self.clientside_map()
        return cmap

    @property
    def img(self):
        cmap, img = self.clientside_map()
        return img

    @property
    def map_name(self):
        return name_for_map(self.map)
    
    def _compute_cmap(self):
        dir = tempfile.mkdtemp()
        try:
            map_file = os.path.join(dir, 'map')
            img_file = os.path.join(dir, 'img')
            src_file = os.path.join(dir, 'src')
            with open(src_file, 'w') as out:
                out.write(self.dot_src)
            Popen([self.engine, '-Tcmapx', '-o', map_file, '-Tpng', '-o', img_file, src_file]).communicate()

            return open(map_file).read(), open(img_file).read()
        finally:
            import shutil
            shutil.rmtree(dir)

