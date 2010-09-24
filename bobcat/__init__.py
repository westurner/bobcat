"""
============
Bobcat
============
A semantic documentation utility.

Objective
=============
Render System Metadata into ReStructuredText, for Sphinx.


References
============
- http://code.google.com/p/fuxi/wiki/FuXiUserManual
- http://packages.python.org/ordf/vocabulary.html#vocabulary-modules

Dependencies
=============
FuXi (RDFLib < 3a)


"""
import rdflib
import copy
from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace, URIRef
import datetime
import os, pkg_resources




def load_graph(schema, components, additional=None, debug=False):
    """

    :param schema: Schema Graph
    :type schema: `rdflib.Graph`
    :param components: Component Graph
    :type components: `rdflib.Graph`
    :param debug: Whether to print debugging information
    :type debug: bool

    :returns: Schema U Schema.inferred U Components
    :rtype: `rdflib.Graph`

    """
    from FuXi.Rete.Util import generateTokenSet
    from FuXi.DLP.DLNormalization import NormalFormReduction
    from FuXi.Rete.RuleStore import SetupRuleStore
    rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)

    NormalFormReduction(schema)
    network.setupDescriptionLogicProgramming(schema)
    network.feedFactsToAdd(generateTokenSet(schema))
    network.feedFactsToAdd(generateTokenSet(components))
    
    len_additional = 0
    if additional:
        for g in additional:
            network.feedFactsToAdd(generateTokenSet(g))
            len_additional += len(g)

    if debug:
        print network

        print dir(network)

        for r in network.rules:
            print r

        for f in network.inferredFacts:
            print f

    len_schema = len(schema)
    len_components = len(components)
    len_inferred = len(network.inferredFacts)

    print "==================="
    print "Component Reference"
    print "==================="
    print "Report Information"
    print "=================="
    print "Generated by Bobcat @ %s" % datetime.datetime.now()
    print ""
    print ".. list-table::"
    print "   :header-rows: 1"
    print ""
    print rest_list_table_row(["Graph","Count"])
    print rest_list_table_row(["Schema", len_schema])
    print rest_list_table_row(["Components", len_components])
    print rest_list_table_row(["Additional", len_additional])
    print rest_list_table_row(["------","------"])
    print rest_list_table_row(["Inferred", len_inferred])
    print rest_list_table_row(["------","------"])
    print rest_list_table_row(["Subtotal",
        len_schema + len_components + len_inferred + len_additional])
    print rest_list_table_row(["------","------"])



    gall = schema
    gall += components
    if additional:
        for g in additional:
            gall += g

    gall_inferred = copy.deepcopy(gall)

    for f in network.inferredFacts:
        gall_inferred.add(f)

    print rest_list_table_row(["Union Total",len(gall_inferred)])

    return gall_inferred, gall


SCHEMA=('/home/wturner/workspace/webcpoe/src/WebCPOE/docs/system/kb/schema-protege_mangled.turtle.owl', 'n3')
DATA=('/home/wturner/workspace/webcpoe/src/WebCPOE/docs/system/kb/components.n3', 'n3')
DOAP_LOCAL=('/home/wturner/workspace/webcpoe/src/WebCPOE/docs/system/kb/doap.rdf.xml', 'xml')
RDF_LOCAL=('/home/wturner/workspace/webcpoe/src/WebCPOE/docs/system/kb/22-rdf-syntax-ns.rdf.xml', 'xml')
RDFS_LOCAL=('/home/wturner/workspace/webcpoe/src/WebCPOE/docs/system/kb/rdf-schema.rdf.xml', 'xml')


RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
SYS = rdflib.Namespace('http://cpoe.keg.unmc.edu/ns/systems#')
DOAP = rdflib.Namespace('http://usefulinc.com/ns/doap#')
NAMESPACES = {
        'rdf': RDF,
        'rdfs': RDFS,
        'sys': SYS,
        'doap': DOAP,
}

def main():
    import optparse

    prs = optparse.OptionParser()

    prs.add_option('-l','--load',dest='ontology_paths', action="append",nargs=2,
        help="Load the specified <path> and <format>")

    (opts,args) = prs.parse_args()

    if opts.ontology_paths:
        raise NotImplementedError
    else:
        gschema = ConjunctiveGraph().parse(SCHEMA[0],format=SCHEMA[1])
        gdata = ConjunctiveGraph().parse(DATA[0],format=DATA[1])
        gdoap = ConjunctiveGraph().parse(DOAP_LOCAL[0],format=DOAP_LOCAL[1])
        grdf = ConjunctiveGraph().parse(RDF_LOCAL[0], format=RDF_LOCAL[1])
        grdfs = ConjunctiveGraph().parse(RDFS_LOCAL[0], format=RDFS_LOCAL[1])

        # Add inferred facts
        gall_inferred, gall = load_graph(gschema, gdata,
                                        additional=[gdoap,
                                                    grdf,
                                                    grdfs])

        print_rest(gall_inferred, gall)
        return gall_inferred

# FIXME: REST injection
def rest_format_predicate(uri=None, label=None):
    """
    :param uri: URIRef
    :type uri: `rdflib.URIRef`
    :param label: RDFS Label (or equivalent)
    :type label: str

    :returns: ReStructuredText-formatted predicate
    :rtype: str
    """
    if uri and label:
        label = label.encode('ascii','xmlcharrefreplace')
        label = label.replace('`','')
        label = label.replace('<','&laquote;')
        label = label.replace('>', '&raquote;')
        return u'`{0} <{1}>`_'.format(label, uri)
    return uri

def rest_list_table_row(values, indent=3):
    """
    :param args: column values
    :type args: list

    :returns: ReStructuredText-formatted List-table row
    :rtype: str
    """
    indent = indent * ' '
    rows = ['%s* - %s' % (indent,values.pop(0))]
    for value in values:
        rows.append('%s  - %s' % (indent,value))
    return '\n'.join(rows)

FILTER_PREDICATES = [
DOAP["name"], # Already displayed in header
None
]
def format_component_row(row):
    """

    """
    (p, p_label, o, o_label) = row
    if p_label and p_label.language is not None and p_label.language != "en":
        return False
    if o_label and o_label.language is not None and o_label.language != "en":
        return False
    if p in FILTER_PREDICATES:
        return False
    return [
        rest_format_predicate(p, p_label),
        rest_format_predicate(o, o_label)
    ]

def rest_list_table(query,formatter,name=None):
    """
    Generate a formatted ReStructuredText List-Table y formatting 'rows' in query
    with formatter

    :param query: [(predicate, predicate_label,
                    object, object_label),...]
    :type query: list

    """

    print ".. list-table:: %s" % name or ''
    print "   :header-rows: 1"
    print ""

    print rest_list_table_row(["Predicate", "Object"], indent=3)

    for row in query:
        formatted = formatter(row)
        if formatted:
            print rest_list_table_row(formatted, indent=3)



def print_rest(ginferred, gall):

    #project_names = dict(get_project_names(ginferred))

    print ""
    print "Components"
    print "=========="

    #print project_names.keys()
    components = ginferred.query("""
    SELECT ?component ?name
    WHERE {
        ?component rdf:type sys:Component
        OPTIONAL { ?component doap:name ?name }
    }
    ORDER BY ?component ?name
    """,initNs=NAMESPACES)

    for component in components:
        component,name = component
        name = name or component

        print ''
        print name
        print '-'*len(name)
        query = ginferred.query("""
        SELECT DISTINCT ?p ?pred_label ?o ?obj_label
        WHERE {
            <%s> ?p ?o .
            OPTIONAL { ?o rdfs:label ?obj_label . }
            OPTIONAL { ?p rdfs:label ?pred_label . }
                FILTER (?o != <http://www.w3.org/2002/07/owl#NamedIndividual>)

        }
        ORDER BY ?p ?o
        """ % component, initNs=NAMESPACES )# FIXME: injection

        rest_list_table(query, format_component_row)

    return None

def get_project_names(gall):
    for n in gall.triples((None, DOAP['name'], None)):
        yield n[0], n[2]



if __name__=="__main__":
    main()