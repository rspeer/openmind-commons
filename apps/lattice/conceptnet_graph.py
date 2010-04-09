from csc.conceptnet4.models import Relation
from django.db.models import Q

def graph_around(central_concept, levels=2, relations=None, max_outdegree=5):
    finished_concepts = set()
    concepts_at_current_level = set([central_concept])
    edges = set()

    relations_filter = Q()
    for rel in relations or []:
        relations_filter |= Q(relation=Relation.get(rel))

    for level in xrange(levels):
        print 'Level', level, 'with', len(concepts_at_current_level), 'concepts'
        next_concepts = set()

        def consider(concept):
            if concept not in finished_concepts and concept not in concepts_at_current_level:
                next_concepts.add(concept)
                
        for concept in concepts_at_current_level:
            if concept in finished_concepts: continue
            assertions = concept.get_assertions().filter(relations_filter)[:max_outdegree]
            for assertion in assertions:
                if assertion.concept1 == concept:
                    consider(assertion.concept2)
                elif assertion.concept2 == concept:
                    consider(assertion.concept1)
                else:
                    raise RuntimeError('Impossible assertion')

                edges.add((assertion.concept1, assertion.relation, assertion.concept2, assertion.score))

            finished_concepts.add(concept)

        concepts_at_current_level = next_concepts

    return edges


def write_graphviz(edges, out):
    out.write('digraph G {\n')

    known_concepts = set()
    for c1, rel, c2, score in edges:
        out.write('concept_%d -> concept_%d [label="%s"];\n' % (c1.id, c2.id, rel.name.encode('utf-8')))
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
