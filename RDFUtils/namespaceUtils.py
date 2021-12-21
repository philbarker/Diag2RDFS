from rdflib import URIRef
from rdflib.namespace import Namespace


def uri2Namespace(uri):
    """Turn a string into a rdflib Namespace."""
    if type(uri) is not str:
        msg = "Namespace uri must be a string."
        print(uri)
        raise TypeError(msg)
    elif uri[:4] != "http":
        msg = "Namespace uri should start with http."
        print(uri)
        raise ValueError(msg)
    elif uri[-1] not in ["/", "#"]:
        msg = "Namespace uri should end with / or #."
        print(uri)
        raise ValueError(msg)
    else:
        return Namespace(URIRef(uri))


class NamespaceDict(dict):
    """A dict of string prefixes and the rdflib Namespaces they identify."""

    def __init__(self):
        super().__init__()

    def addNamespace(self, prefix, ns):
        """Add rdflib Namespace uri to dict with prefix as key."""
        if type(prefix) is not str:
            msg = "Namespace prefix must be a string."
            print(prefix)
            raise TypeError(msg)
        elif prefix[-1] == ":":  # strip trailing colon if there is one
            prefix = prefix[:-1]
        if type(ns) is not Namespace:
            msg = "Namespace must be rdflib namespace."
            print(ns)
            raise TypeError(msg)
        self[prefix] = ns
