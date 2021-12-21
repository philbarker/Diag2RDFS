import pytest
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, RDFS, DCTERMS
from rdflib.namespace import Namespace, NamespaceManager
from Diag2RDFS import Diag2RDFSConverter
from RDFUtils import curieUtils, NamespaceDict

test_file = "./Tests/TestData/DESM_Model2.csv"
DESM = Namespace(
    URIRef(
        "https://github.com/t3-innovation-network/desm/tree/main/schemas/desmSchema/"
    )
)

SDO = Namespace(URIRef("http://schema.org/"))


@pytest.fixture(scope="module")
def converter():
    return Diag2RDFSConverter()


def test_init(converter):
    c = converter
    assert c.metadata["title"] == ""
    assert c.metadata["date"] == ""
    assert type(c.schema) is Graph
    assert type(c.namespaces) is NamespaceDict
    assert c.diagMetaData == []
    assert c.diagClassData == []
    assert c.diagLinkData == []


def test_loadDiagData(converter):
    c = converter
    c.loadDiagData(test_file)
    assert len(c.diagMetaData) == 5
    assert len(c.diagClassData) == 2
    assert len(c.diagLinkData) == 2
    assert type(c.diagMetaData[0]) is dict
    assert c.diagMetaData[0]["Id"] == "1"
    assert c.diagMetaData[0]["Name"] == "Document"
    assert c.diagMetaData[0]["Shape Library"] == ""
    assert c.diagClassData[0]["Name"] == "Class"
    assert c.diagLinkData[0]["Name"] == "Line"
    with pytest.raises(TypeError) as e:
        c.loadDiagData(["sdo"])
    assert str(e.value) == "Filename must be a string."


def test_convertMetadata(converter):
    c = converter
    c.convertMetadata()
    assert c.metadata["title"] == "DESM Model"
    assert c.metadata["date"] == "2021-12-17"
    assert c.metadata["defines"] == "desm"


def test_convertNamespaces(converter):
    c = converter
    c.convertNamespaces()
    assert c.namespaces["desm"] == DESM


def test_convertClasses(converter):
    c = converter
    c.convertClasses()
    tr = (DESM.AbstractClassSet, RDF.type, RDFS.Class)
    assert tr in c.schema.triples((None, None, None))
    tr = (DESM.AbstractClassSet, RDFS.isDefinedBy, URIRef(DESM))
    assert tr in c.schema.triples((None, None, None))
    assert tr in c.schema.triples((None, None, None))


def test_convertLinkProperties(converter):
    c = converter
    c.convertLinkProperties()
    tr = (DCTERMS.isPartOf, RDF.type, RDF.Property)
    assert tr in c.schema.triples((None, None, None))
    tr = (DCTERMS.isPartOf, RDFS.isDefinedBy, URIRef(DCTERMS))
    assert tr in c.schema.triples((None, None, None))


def test_findClassByID(converter):
    c = converter
    assert "desm:AbstractClassMapping" == c.findClassByID("7")
    with pytest.raises(TypeError) as e:
        c.findClassByID(7)
    assert str(e.value) == "Class ID should be a string."
    with pytest.raises(ValueError) as e:
        c.findClassByID("42")
    assert str(e.value) == "Could not find class with id 42."


def test_getLinkSource(converter):
    c = converter
    link_data = c.diagLinkData[0]
    s = c.getLinkSource(link_data)
    assert s == DESM.AbstractClassMapping
    link_data = c.diagLinkData[1]
    s = c.getLinkSource(link_data)
    assert s == DESM.AbstractClassSet


def test_getLinkDestination(converter):
    c = converter
    link_data = c.diagLinkData[0]
    d = c.getLinkDestination(link_data)
    assert d == DESM.AbstractClassSet
    link_data = c.diagLinkData[1]
    d = c.getLinkDestination(link_data)
    assert d == DESM.AbstractClassMapping


def test_convertClassProperty(converter):
    c = converter
    prop_def = "dct:creator (xsd:string)"
    class_uriref = DESM.AbstractClassSet
    c.convertClassProperty(prop_def, class_uriref)
    tr = (DCTERMS.creator, SDO.rangeIncludes, RDFS.Literal)
    assert tr in c.schema.triples((None, None, None))
    assert tr in c.schema.triples((None, None, None))
