from django.views.static import serve
from django.http import HttpResponse
import tempfile
import os.path
here = os.path.dirname(os.path.abspath(__file__))

from subprocess import Popen, PIPE

from context import respond_with

def index(request):
    return serve(request,
                 document_root=here,
                 path='index.html')


from graphviz_imagemap import serve_cached_image, GVGraph

src = """
digraph G {
  node [style=filled];
  node0 [label="thing", URL="thing.html"];
  node1 [label="animate"]; node0 -> node1;
  node2 [label="inanimate"]; node0 -> node2;
  node3 [label="animal"]; node1 -> node3;
  node4 [label="mammal"]; node3 -> node4;
  node5 [label="cat"]; node4->node5;
  node6 [label="dog", fillcolor=green]; node4->node6;
}
"""
src = '''
digraph G {
overlap=true;
concept_616 -> concept_3473 [label="AtLocation"];
concept_537 -> concept_3473 [label="AtLocation"];
concept_6651 -> concept_4850 [label="IsA"];
concept_537 -> concept_18539 [label="CapableOf"];
concept_18539 -> concept_33 [label="PartOf"];
concept_5 -> concept_18539 [label="CapableOf"];
concept_220 -> concept_3473 [label="AtLocation"];
concept_7815 -> concept_4850 [label="IsA"];
concept_537 -> concept_4850 [label="IsA"];
concept_33 [label="tree", URL="/en/concept/tree/"];
concept_5 [label="something"];
concept_7815 [label="rabbit"];
concept_616 [label="cat"];
concept_18539 [label="bark"];
concept_3473 [label="kennel"];
concept_4850 [label="mammal"];
concept_537 [label="dog"];
concept_6651 [label="dolphin"];
concept_220 [label="wiener dog"];
}
'''

def clientside_map(request):
    g = GVGraph(src, engine='neato')
    return HttpResponse('''
<html><head><title>Test</title></head><body>
<img src="%(src)s" usemap="#%(map_name)s">%(map)s
</body></html>''' % dict(src='/lattice/graph_images/%s/' % g.key,
                         map_name=g.map_name,
                         map=g.map))
    


def write_graphviz(edges, out):
    out.write('digraph G {\n')

    known_concepts = set()
    for c1, c2 in edges:
        out.write('concept_%d -> concept_%d;\n' % (c1.id, c2.id))
        known_concepts.add(c1)
        known_concepts.add(c2)

    for concept in known_concepts:
        out.write('concept_%d [label="%s"];\n' % (concept.id, concept.text.encode('utf-8')))

    out.write('}') # close digraph


def as_graphviz(edges):
    from StringIO import StringIO
    out = StringIO()
    write_graphviz(edges, out)
    return out.getvalue()

        
def start_lattice(request, concept_name, lr, relation_name, fconcept_name):
    from csc.conceptnet4.models import Concept, Feature
    concept = Concept.get(concept_name, 'en')

    # Build the concept tree
    edges = concept.get_tree()

    session_data = dict(
        concept=concept,
        feature=Feature.from_tuple((lr, relation_name, fconcept_name)),
        edges=edges,
        )

    # Store the new session data, overwriting anything that was there before.
    request.session['lattice_learning'] = session_data

    # Render the graphviz.
    src = as_graphviz(edges)
    
    # Go to the initial view.
    g = GVGraph(src, engine='dot')
    return HttpResponse('''
<html><head><title>Test</title></head><body>
<img src="%(src)s" usemap="#%(map_name)s">%(map)s
</body></html>''' % dict(src='/lattice/graph_images/%s/' % g.key,
                         map_name=g.map_name,
                         map=g.map))
