from csv import DictReader
from copy import copy, deepcopy
from pprint import PrettyPrinter
from rdflib import Graph, Literal, URIRef, RDF, RDFS, SKOS, SDO
from rdflib.namespace import Namespace, NamespaceManager
from RDFUtils import str2uriref, curie2uriref, splitCurie, NamespaceDict, uri2Namespace

# default column headings in csv
# these could usefully be in a config file
id = "Id"
name = "Name"
shape_library = "Shape Library"
page_id = "Page_ID"
contained_by = "Contained By"
group = "Group"
line_source = "Line Source"
line_destination = "Line Destination"
source_arrow = "Source Arrow"
destination_arrow = "Destination Arrow"
satus = "Status"
text_1 = "Text Area 1"
text_2 = "Text Area 2"
text_3 = "Text Area 3"
date = "dct:date"
description = "dct:description"
issued = "dct:issued"
title = "dct:title"
defines = "defines"
equivalent_class = "owl:equivalentclass"
prefixes = "prefixes"
comment = "rdfs:comment"
label = "rdfs:label"
subclass_of = "rdfs:subclassof"
scope_note = "skos:scopenote"

SDO.rangeIncludes = URIRef("http://schema.org/rangeIncludes")
SDO.domainIncludes = URIRef("http://schema.org/domainIncludes")


class Diag2RDFSConverter:
    """Methods to convert csv data from a Lucid class diagram to RDF Schema."""

    def __init__(self):
        self.metadata = dict()
        self.metadata["title"] = str()
        self.metadata["date"] = str()
        self.metadata["defines"] = str()
        self.schema = Graph()
        self.namespaces = NamespaceDict()
        self.diagMetaData = list()
        self.diagClassData = list()
        self.diagLinkData = list()
        self.schema.bind("sdo", SDO)
        self.schema.bind("skos", SKOS)

    def convertDiag2RDFS(self, fname):
        """Load and convert diagram data into a RDF Graph."""
        self.loadDiagData(fname)
        self.convertMetadata()
        self.convertNamespaces()
        self.convertClasses()
        self.convertLinkProperties()

    def loadDiagData(self, fname):
        """Read diagram data in CSV format and store as lists of dicts."""
        if type(fname) is not str:
            msg = "Filename must be a string."
            print(fname)
            raise TypeError(msg)
        with open(fname, "r") as diag_file:
            csvReader = DictReader(diag_file)
            for row in csvReader:
                if row["Name"] in ["Document", "Page", "Text"]:
                    self.diagMetaData.append(row)
                if row["Name"] == "Class":
                    self.diagClassData.append(row)
                if row["Name"] == "Line":
                    self.diagLinkData.append(row)

    def convertMetadata(self):
        """Convert the metadata list into metadata properties."""
        for line in self.diagMetaData:
            if line[name] == "Document":
                self.metadata["title"] = line[text_1]
            if line[name] == "Page":
                self.metadata["date"] = line[date]
                self.metadata["defines"] = line[defines]

    def convertNamespaces(self):
        """Convert any prefix defintions in the metadata list into rdflib namespaces, and add them to the namespace dict and schema graph."""
        for line in self.diagMetaData:
            if line[name] == "Page":
                for ns_def in line[prefixes].split("\n"):
                    [pre, uri] = ns_def.split(": ")
                    ns = uri2Namespace(uri)
                    self.namespaces.addNamespace(pre, ns)
                    self.schema.bind(pre, ns)

    def convertClasses(self):
        """Convert class cURIes from the classes list to rdflib URIRefs and add them with defintion data to the schema graph.

        Locally defined classes are fully defined, those from other namespaces defer to the external definition."""
        for line in self.diagClassData:
            c_uris = line[text_1].split("\n")
            for c_uri in c_uris:
                c_uriref, ns_id, ns_uriref = splitCurie(c_uri, self.namespaces)
                self.schema.add((c_uriref, RDF.type, RDFS.Class))
                self.schema.add(((c_uriref, RDFS.isDefinedBy, ns_uriref)))
                if ns_id == self.metadata["defines"]:
                    if line[label] != "":
                        value = Literal(line[label])
                        self.schema.add((c_uriref, RDFS.label, value))
                    if line[comment] != "":
                        value = Literal(line[comment])
                        self.schema.add((c_uriref, RDFS.comment, value))
                    if line[subclass_of] != "":
                        value = Literal(line[subclass_of])
                        self.schema.add((c_uriref, RDFS.label, value))
                    if line[scope_note] != "":
                        value = Literal(line[scope_note])
                        self.schema.add((c_uriref, RDFS.label, value))
                if line[text_2] != "":
                    prop_defs = line[text_2].split("\n")
                    for prop_def in prop_defs:
                        self.convertClassProperty(prop_def, c_uriref)

    def convertClassProperty(self, prop_def, c_uriref):
        """Convert property cURIe from the list of properties associated with a class to rdflib URIRefs and add them with defintion data to the schema graph.

        The properties are assumed to have Literal values. Optionally a datatype may be include in parentheses after the property CURIe/URI in the definition.

        Locally defined properties are fully defined, those from other namespaces defer to the external definition."""
        if type(prop_def) is not str:
            print(prop_def)
            msg = "Class property definition must be a string"
            raise TypeError(msg)
        if "(" in prop_def:
            [p_uri, dataType] = prop_def.split(" (")
            dataType = dataType[:-1]  # strip trailling ')'
        else:
            p_uri = prop_def
            dataType = str()
        p_uriref, ns_id, ns_uriref = splitCurie(p_uri, self.namespaces)
        self.schema.add((p_uriref, RDF.type, RDF.Property))
        self.schema.add(((p_uriref, RDFS.isDefinedBy, ns_uriref)))
        if ns_id == self.metadata["defines"]:
            self.schema.add(((p_uriref, RDFS.range, RDFS.Literal)))
            self.schema.add(((p_uriref, RDFS.domain, c_uriref)))
        else:  # tread softly...
            self.schema.add(((p_uriref, SDO.rangeIncludes, RDFS.Literal)))
            self.schema.add(((p_uriref, SDO.domainIncludes, c_uriref)))
        return p_uriref

    def convertLinkProperties(self):
        """Convert property cURIes from the properties list to rdflib URIRefs and add them with defintion data to the schema graph.

        Locally defined properties are fully defined, those from other namespaces defer to the external definition."""
        for line in self.diagLinkData:
            p_uris = line[text_1].split("\n")
            source = self.getLinkSource(line)
            destination = self.getLinkDestination(line)
            for p_uri in p_uris:
                p_uriref, ns_id, ns_uriref = splitCurie(p_uri, self.namespaces)
                self.schema.add((p_uriref, RDF.type, RDF.Property))
                self.schema.add(((p_uriref, RDFS.isDefinedBy, ns_uriref)))
                if ns_id == self.metadata["defines"]:
                    self.schema.add((p_uriref, RDFS.domain, source))
                    self.schema.add((p_uriref, RDFS.range, destination))
                    if line[label] != "":
                        value = Literal(line[label])
                        self.schema.add((p_uriref, RDFS.label, value))
                    if line[comment] != "":
                        value = Literal(line[comment])
                        self.schema.add((p_uriref, RDFS.comment, value))
                    if line[scope_note] != "":
                        value = Literal(line[scope_note])
                        self.schema.add((p_uriref, RDFS.label, value))
                else:  # tread softly...
                    self.schema.add((p_uriref, SDO.domainIncludes, source))
                    self.schema.add((p_uriref, SDO.rangeIncludes, destination))

    def getLinkSource(self, link_data):
        """Return the URIRef of the class at the start of a link."""
        if type(link_data) is not dict:
            print(link_data)
            msg = "Link data must be a dict."
            raise TypeError(msg)
        if link_data[source_arrow] == "None":
            source_id = link_data[line_source]
        elif link_data[source_arrow] == "Arrow":
            source_id = link_data[line_destination]
        else:
            msg = "Unknown value for source_arrow: " + link_data[source_arrow]
            raise ValueError(msg)
        source = self.findClassByID(source_id)
        return str2uriref(source, self.namespaces)

    def getLinkDestination(self, link_data):
        """Return the URIRef of the class at the end of a link."""
        if type(link_data) is not dict:
            print(link_data)
            msg = "Link data must be a dict."
            raise TypeError(msg)
        if link_data[destination_arrow] == "Arrow":
            destination_id = link_data[line_destination]
        elif link_data[destination_arrow] == "None":
            destination_id = link_data[line_source]
        else:
            msg = "Unknown value for destination_arrow: " + link_data[destination_arrow]
            raise ValueError(msg)
        destination = self.findClassByID(destination_id)
        return str2uriref(destination, self.namespaces)

    def findClassByID(self, class_id):
        if type(class_id) is not str:
            print(class_id)
            msg = "Class ID should be a string."
            raise TypeError(msg)
        for line in self.diagClassData:
            if line[id] == class_id:
                return line[text_1]
        # if you get here you didn't find a class matching the id
        print(class_id)
        msg = "Could not find class with id " + class_id + "."
        raise ValueError(msg)

    def writeSchema(self):
        print("# Title: ", self.metadata["title"])
        print("# Date: ", self.metadata["date"])
        print(self.schema.serialize())
