from .namespaceUtils import NamespaceDict, uri2Namespace
from rdflib import URIRef


def str2uriref(uri_str, namespaces=None):
    """Convert a string URI or cURI to an rdflib URIRef"""
    if type(uri_str) is not str:
        msg = "URI must be a string."
        raise TypeError(msg)
    if uri_str[:4] == "http":
        if uri_str.split(":")[1][:2] == "//":
            return URIRef(uri_str)
        else:
            print(uri_str)
            msg = "URI string looks like invalid http URI."
            raise ValueError(msg)
    elif namespaces != None:
        return curie2uriref(uri_str, namespaces)
    else:
        msg = "String must be either CURIE or http[s] URI."
        raise ValueError(msg)


def curie2uriref(curie_str, namespaces):
    """Turn a compact URI into a rdflib URIRef"""
    if type(curie_str) is not str:
        print(curie_str)
        msg = "Compact URI must be a string."
        raise TypeError(msg)
    if type(namespaces) is not NamespaceDict:
        print(namespaces)
        msg = "Namespaces must be a RDFUtils NamespaceDict."
        raise TypeError(msg)
    if ":" in curie_str:  # To do : check for >1 :
        [pre, name] = curie_str.split(":")
        uri_str = namespaces[pre] + name
        return str2uriref(uri_str)
    elif "base" in namespaces.keys():
        uri_str = namespaces[base] + curie_str
        return str2uriref(uri_str)
    else:
        msg = "Need to provide prefixed curie or base namespace."
        raise ValueError(msg)
    pass


def splitCurie(curie, namespaces):
    """Split a compact URI into URIRef of CURIe, id and URIRef of namespace"""
    if type(curie) is not str:
        print(curie)
        msg = "CURIe should be a string."
        raise TypeError(msg)
    if type(namespaces) is not NamespaceDict:
        msg = "Namespaces must be a RDFUtils NamespaceDict."
        raise TypeError(msg)
    parts = curie.split(":")
    if len(parts) == 2:
        ns_id = parts[0]
    else:
        print(curie)
        msg = "CURIe should have two colons ':' in it."
        raise ValueError(msg)
    if ns_id in namespaces.keys():
        uriref = str2uriref(curie, namespaces)
        ns_uri = URIRef(namespaces[ns_id])
        return uriref, ns_id, ns_uri
    else:
        print(curie)
        msg = "No namespace for CURIe prefix."
        raise TypeError(msg)


def splitCuri(curi):
    """Split a compact uri into prefix and name."""
    parts = curi.split(":")
    if len(parts) == 2:
        return parts
    else:
        msg = "CURI should have one colon."
        raise Exception(msg)


def expandCuri(curi, namespaces):
    [pre, name] = splitCuri(curi)
    if pre in namespaces.keys():
        return namespaces[pre] + name
    else:
        msg = "Cannot expand curi with unknown prefix " + curi
        raise Exception(msg)


def curi2URIRef(curi, namespaces):
    uri = expandCuri(curi, namespaces)
    return URIRef(uri)


def unpackProperties(self, string):
    """Turn a string with properties separted by linebreaks into a list of properties."""
    plist = string.split("\n")
    return plist
