                 
def render_xdot(src, engine='dot'):
    srcfile = tempfile.NamedTemporaryFile()
    srcfile.write(src)
    srcfile.flush()
    return Popen([engine, '-Txdot', srcfile.name], stdout=PIPE).communicate()[0]



def graph(request):
    from conceptnet_graph import as_graphviz, graph_around
    from csc.conceptnet4.models import Concept
    src = as_graphviz(graph_around(Concept.get('dog','en')))
    xdot = render_xdot(src, engine='twopi')
    return HttpResponse(xdot, mimetype='text/plain')
