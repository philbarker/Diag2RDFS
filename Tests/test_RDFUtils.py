import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import Namespace
from RDFUtils import NamespaceDict, uri2Namespace, str2uriref, curie2uriref


@pytest.fixture(scope="module")
def namespaces():
    return NamespaceDict()


def test_init(namespaces):
    n = namespaces
    assert type(n) is NamespaceDict
    assert len(n) == 0


def test_uri2Namespace():
    ns = uri2Namespace("http://schema.org/")
    assert ns == Namespace("http://schema.org/")
    with pytest.raises(ValueError) as e:
        uri2Namespace("schema.org")
    assert str(e.value) == "Namespace uri should start with http."
    with pytest.raises(ValueError) as e:
        uri2Namespace("https://schema.org")
    assert str(e.value) == "Namespace uri should end with / or #."


def test_addNamespace(namespaces):
    n = namespaces
    assert len(n) == 0
    ns = uri2Namespace("http://schema.org/")
    n.addNamespace("sdo:", ns)
    assert len(n) == 1
    assert n["sdo"] == Namespace(URIRef("http://schema.org/"))
    with pytest.raises(TypeError) as e:
        n.addNamespace(["sdo"], ns)
    assert str(e.value) == "Namespace prefix must be a string."
    with pytest.raises(TypeError) as e:
        n.addNamespace("sdo", "http://schema.org")
    assert str(e.value) == "Namespace must be rdflib namespace."
    assert len(n) == 1


def test_str2uriref(namespaces):
    n = namespaces
    uri_ref = str2uriref("http://schema.org/")
    assert uri_ref == URIRef("http://schema.org/")
    with pytest.raises(ValueError) as e:
        str2uriref("schema.org")
    assert str(e.value) == "String must be either CURIE or http[s] URI."


def test_curie2uriref(namespaces):
    n = namespaces
    assert "sdo" in namespaces.keys()  # we put it there testing addNamespace()
    curie = "sdo:name"
    uri_ref = curie2uriref(curie, n)
    assert uri_ref == URIRef("http://schema.org/name")
