from __future__ import unicode_literals
import uuid
import datetime
import re
"""This is based on python-bioformats.omexml @ version 1.5.2.
    tip1: check the attribute, if attribute==None. probably should set it.
    COMMENT: NEARLY DONE NOW. NOW SHIFT TO THE UNIVERSAL TEMPLATE. AND THEN
    COME BACK TO COMPLETE THE LEFTOVER.
    DEADLINE: 2019-01-29

    is self.ns['ome'] correct expression? in case some of them are not with
    'ome'
"""
import xml.etree.ElementTree
from xml.etree import cElementTree as ElementTree
import sys
if sys.version_info.major == 3:
    from io import StringIO
    uenc = 'utf-8'
    #uenc = 'unicode'
else:
    from cStringIO import StringIO
    uenc = 'utf-8'


def xsd_now():
    '''Return the current time in xsd:dateTime format'''
    return datetime.datetime.now().isoformat()


DEFAULT_NOW = xsd_now()

#
# The namespaces
#
# NS_ORIGINAL_METADATA = "openmicroscopy.org/OriginalMetadata"
NS_DEFAULT = "http://www.openmicroscopy.org/Schemas/{ns_key}/2016-06"
NS_RE = r"http://www.openmicroscopy.org/Schemas/(?P<ns_key>.*)/[0-9/-]"

default_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
    xmlns:ome="http://www.openmicroscopy.org/Schemas/OME/2016-06"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06/xsd">
</OME>""".format(ns_ome_default=NS_DEFAULT.format(ns_key='OME'))

#
# These are the OME-XML pixel types - not all supported by subimager
#
PT_INT8 = "int8"
PT_INT16 = "int16"
PT_INT32 = "int32"
PT_UINT8 = "uint8"
PT_UINT16 = "uint16"
PT_UINT32 = "uint32"
PT_FLOAT = "float"
PT_BIT = "bit"
PT_DOUBLE = "double"
PT_COMPLEX = "complex"
PT_DOUBLECOMPLEX = "double-complex"
#
# The allowed dimension types
#
DO_XYZCT = "XYZCT"
DO_XYZTC = "XYZTC"
DO_XYCTZ = "XYCTZ"
DO_XYCZT = "XYCZT"
DO_XYTCZ = "XYTCZ"
DO_XYTZC = "XYTZC"
#
# Original metadata corresponding to TIFF tags
# The text for these can be found in
# loci.formats.in.BaseTiffReader.initStandardMetadata
#
'''IFD # 254'''
OM_NEW_SUBFILE_TYPE = "NewSubfileType"
'''IFD # 256'''
OM_IMAGE_WIDTH = "ImageWidth"
'''IFD # 257'''
OM_IMAGE_LENGTH = "ImageLength"
'''IFD # 258'''
OM_BITS_PER_SAMPLE = "BitsPerSample"

'''IFD # 262'''
OM_PHOTOMETRIC_INTERPRETATION = "PhotometricInterpretation"
PI_WHITE_IS_ZERO = "WhiteIsZero"
PI_BLACK_IS_ZERO = "BlackIsZero"
PI_RGB = "RGB"
PI_RGB_PALETTE = "Palette"
PI_TRANSPARENCY_MASK = "Transparency Mask"
PI_CMYK = "CMYK"
PI_Y_CB_CR = "YCbCr"
PI_CIE_LAB = "CIELAB"
PI_CFA_ARRAY = "Color Filter Array"

'''BioFormats infers the image type from the photometric interpretation'''
OM_METADATA_PHOTOMETRIC_INTERPRETATION = "MetaDataPhotometricInterpretation"
MPI_RGB = "RGB"
MPI_MONOCHROME = "Monochrome"
MPI_CMYK = "CMYK"

'''IFD # 263'''
OM_THRESHHOLDING = "Threshholding"  # (sic)
'''IFD # 264 (but can be 265 if the orientation = 8)'''
OM_CELL_WIDTH = "CellWidth"
'''IFD # 265'''
OM_CELL_LENGTH = "CellLength"
'''IFD # 266'''
OM_FILL_ORDER = "FillOrder"
'''IFD # 279'''
OM_DOCUMENT_NAME = "Document Name"
'''IFD # 271'''
OM_MAKE = "Make"
'''IFD # 272'''
OM_MODEL = "Model"
'''IFD # 274'''
OM_ORIENTATION = "Orientation"
'''IFD # 277'''
OM_SAMPLES_PER_PIXEL = "SamplesPerPixel"
'''IFD # 280'''
OM_MIN_SAMPLE_VALUE = "MinSampleValue"
'''IFD # 281'''
OM_MAX_SAMPLE_VALUE = "MaxSampleValue"
'''IFD # 282'''
OM_X_RESOLUTION = "XResolution"
'''IFD # 283'''
OM_Y_RESOLUTION = "YResolution"
'''IFD # 284'''
OM_PLANAR_CONFIGURATION = "PlanarConfiguration"
PC_CHUNKY = "Chunky"
PC_PLANAR = "Planar"

'''IFD # 286'''
OM_X_POSITION = "XPosition"
'''IFD # 287'''
OM_Y_POSITION = "YPosition"
'''IFD # 288'''
OM_FREE_OFFSETS = "FreeOffsets"
'''IFD # 289'''
OM_FREE_BYTECOUNTS = "FreeByteCounts"
'''IFD # 290'''
OM_GRAY_RESPONSE_UNIT = "GrayResponseUnit"
'''IFD # 291'''
OM_GRAY_RESPONSE_CURVE = "GrayResponseCurve"
'''IFD # 292'''
OM_T4_OPTIONS = "T4Options"
'''IFD # 293'''
OM_T6_OPTIONS = "T6Options"
'''IFD # 296'''
OM_RESOLUTION_UNIT = "ResolutionUnit"
'''IFD # 297'''
OM_PAGE_NUMBER = "PageNumber"
'''IFD # 301'''
OM_TRANSFER_FUNCTION = "TransferFunction"

'''IFD # 305'''
OM_SOFTWARE = "Software"
'''IFD # 306'''
OM_DATE_TIME = "DateTime"
'''IFD # 315'''
OM_ARTIST = "Artist"
'''IFD # 316'''
OM_HOST_COMPUTER = "HostComputer"
'''IFD # 317'''
OM_PREDICTOR = "Predictor"
'''IFD # 318'''
OM_WHITE_POINT = "WhitePoint"
'''IFD # 322'''
OM_TILE_WIDTH = "TileWidth"
'''IFD # 323'''
OM_TILE_LENGTH = "TileLength"
'''IFD # 324'''
OM_TILE_OFFSETS = "TileOffsets"
'''IFD # 325'''
OM_TILE_BYTE_COUNT = "TileByteCount"
'''IFD # 332'''
OM_INK_SET = "InkSet"
'''IFD # 33432'''
OM_COPYRIGHT = "Copyright"
#
# Well row/column naming conventions
#
NC_LETTER = "letter"
NC_NUMBER = "number"


def page_name_original_metadata(index):
    '''Get the key name for the page name metadata data for the indexed tiff page
    These are TIFF IFD #'s 285+
    index - zero-based index of the page
    '''
    return "PageName #%d" % index


def get_text(node):
    '''Get the contents of text nodes in a parent node'''
    return node.text


def set_text(node, text):
    '''Set the text of a parent'''
    node.text = text


def qn(namespace, tag_name):
    '''Return the qualified name for a given namespace and tag name
    This is the ElementTree representation of a qualified name
    '''
    return "{%s}%s" % (namespace, tag_name)


def split_qn(qn):
    '''Split a qualified tag name or return None if namespace not present'''
    m = re.match('\{(.*)\}(.*)', qn)
    return m.group(1), m.group(2) if m else None


def get_namespaces(node):
    '''Get top-level XML namespaces from a node.'''
    ns_lib = {'ome': None, 'sa': None, 'spw': None}
    for child in node.iter():
        ns = split_qn(child.tag)[0]
        match = re.match(NS_RE, ns)
        if match:
            ns_key = match.group('ns_key').lower()
            ns_lib[ns_key] = ns
    return ns_lib


def get_float_attr(node, attribute):
    '''Cast an element attribute to a float or return None if not present'''
    attr = node.get(attribute)
    return None if attr is None else float(attr)


def get_int_attr(node, attribute):
    '''Cast an element attribute to an int or return None if not present'''
    attr = node.get(attribute)
    return None if attr is None else int(attr)


def make_text_node(parent, namespace, tag_name, text):
    '''Either make a new node and add the given text or replace the text
    parent - the parent node to the node to be created or found
    namespace - the namespace of the node's qualified name
    tag_name - the tag name of  the node's qualified name
    text - the text to be inserted
    '''
    qname = qn(namespace, tag_name)
    node = parent.find(qname)
    if node is None:
        node = ElementTree.SubElement(parent, qname)
    set_text(node, text)


# only return omexml.OMEXML() each time
class OMEXML():
    """inherit the OMEXML from bioformats, and then extend.
    @Author: Hao Xu
    Reads and writes OME-XML with methods to get and set it.
    The OMEXML class has four main purposes: to parse OME-XML, to output
    OME-XML, to provide a structured mechanism for inspecting OME-XML and to
    let the caller create and modify OME-XML.
    There are two ways to invoke the constructor. If you supply XML as a string
    or unicode string, the constructor will parse it and will use it as the
    base for any inspection and modification. If you don't supply XML, you'll
    get a bland OME-XML object which has a one-channel image. You can modify
    it programatically and get the modified OME-XML back out by calling to_xml.
    There are two ways to get at the XML. The arduous way is to get the
    root_node of the DOM and explore it yourself using the DOM API
    (http://docs.python.org/library/xml.dom.html#module-xml.dom). The easy way,
    where it's supported is to use properties on OMEXML and on some of its
    derived objects. For instance:
    >>> o = OMEXML()
    >>> print o.image().AcquisitionDate
    will get you the date that image # 0 was acquired.
    >>> o = OMEXML()
    >>> o.image().Name = "MyImage"
    will set the image name to "MyImage".
    You can add and remove objects using the "count" properties. Each of these
    handles hooking up and removing orphaned elements for you and should be
    less error prone than creating orphaned elements and attaching them. For
    instance, to create a three-color image:
    >>> o = OMEXML()
    >>> o.image().Pixels.channel_count = 3
    >>> o.image().Pixels.Channel(0).Name = "Red"
    >>> o.image().Pixels.Channel(1).Name = "Green"
    >>> o.image().Pixels.Channel(2).Name = "Blue"
    See the `OME-XML schema documentation <http://git.openmicroscopy.org/src/develop/components/specification/Documentation/Generated/OME-2011-06/
    ome.html>`_.
    """

    def __init__(self, xml=None):
        if xml is None:
            xml = default_xml
        if isinstance(xml, str):
            xml = xml.encode("utf-8")
        try:
            self.dom = ElementTree.ElementTree(ElementTree.fromstring(xml))
        except UnicodeEncodeError:
            xml = xml.encode("utf-8")
            self.dom = ElementTree.ElementTree(ElementTree.fromstring(xml))
        # determine OME namespaces
        self.ns = get_namespaces(self.dom.getroot())
        if self.ns['ome'] is None:
            raise Exception("Error: String not in OME-XML format")

    def __str__(self):
        #
        # need to register the ome namespace because BioFormats expects
        # that namespace to be the default or to be explicitly named "ome"
        #
        for ns_key in ["ome", "sa", "spw"]:
            ns = self.ns.get(ns_key) or NS_DEFAULT.format(ns_key=ns_key)
            ElementTree.register_namespace(ns_key, ns)
        # ElementTree.register_namespace("ome", NS_ORIGINAL_METADATA)
        result = StringIO()
        ElementTree.ElementTree(
            self.root_node).write(result, encoding=uenc, method="xml")
        return result.getvalue()

    def to_xml(self, indent="\t", newline="\n", encoding=uenc):
        '''string the xml'''
        return ''.join(
        ('''<?xml version="1.0" encoding="UTF-8"?>\n''', str(self)))

    def get_ns(self, key):
        return self.ns[key]

    @property
    def root_node(self):
        return self.dom.getroot()

    @property
    def UUID(self):
        return self.root_node.get("UUID")

    @UUID.setter
    def UUID(self, value):
        self.root_node.set("UUID", value)

    @property
    def Creator(self):
        return self.root_node.get("Creator")

    @Creator.setter
    def Creator(self, value):
        self.root_node.set("Creator", value)

    @property
    def image_count(self):
        '''The number of images (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Image")))

    # here is some revision in OMEXML() part from inherited class.
    @image_count.setter
    def image_count(self, value):
        '''Add or remove image nodes as needed'''
        assert value > 0
        if self.image_count > value:
            image_nodes = self.root_node.find(qn(self.ns['ome'], "Image"))
            for image_node in image_nodes[value:]:
                self.root_node.remove(image_node)

        elif self.image_count < value:
            for _ in range(self.image_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Image"))


    def image(self, index=0):
        '''Get the indexed instrument elelment'''
        if self.image_count == 0:
            self.image_count = 1
        return self.Image(
            self.root_node.findall(qn(self.ns['ome'], "Image"))[index])

    # from here, add more functions inside the class
    @property
    def instrument_count(self):
        '''The number of instruments (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Instrument")))

    @instrument_count.setter
    def instrument_count(self, value):
        '''Add or remove instrument nodes as needed'''
        assert value > 0

        if self.instrument_count > value:
            instrument_nodes = self.root_node.findall(
                qn(self.ns['ome'], "Instrument"))
            for instrument_node in instrument_nodes[value:]:
                self.root_node.remove(instrument_node)
        elif self.instrument_count < value:
            for _ in range(self.instrument_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Instrument"))


    def instrument(self, index=0):
        '''Get the indexed instrument elelment'''
        if self.instrument_count == 0:
            self.instrument_count = 1
        return self.Instrument(
            self.root_node.findall(qn(self.ns['ome'], "Instrument"))[index])

    # project
    @property
    def project_count(self):
        '''The number of projects (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Project")))

    @project_count.setter
    def project_count(self, value):
        '''Add or remove project nodes as needed'''
        assert value > 0

        if self.project_count > value:
            project_nodes = self.root_node.findall(
                qn(self.ns['ome'], "Project"))
            for project_node in project_nodes[value:]:
                self.root_node.remove(project_node)
        elif self.project_count < value:
            for _ in range(self.project_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Project"))


    def project(self, index=0):
        '''Get the indexed project elelment'''
        if self.project_count == 0:
            self.project_count = 1
        return self.Project(self.root_node.findall(
            qn(self.ns['ome'], "Project"))[index])

    # Dataset
    @property
    def dataset_count(self):
        '''The number of datasets (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Dataset")))

    @dataset_count.setter
    def dataset_count(self, value):
        '''Add or remove dataset nodes as needed'''
        assert value > 0

        if self.dataset_count > value:
            dataset_nodes = self.root_node.findall(qn(self.ns['ome'], "Dataset"))
            for dataset_node in dataset_nodes[value:]:
                self.root_node.remove(dataset_node)
        elif self.dataset_count < value:
            for _ in range(self.dataset_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Dataset"))


    def dataset(self, index=0):
        '''Get the indexed dataset elelment'''
        if self.dataset_count == 0:
            self.dataset_count = 1
        return self.Dataset(
            self.root_node.findall(qn(self.ns['ome'], "Dataset"))[index])

    # folder
    @property
    def folder_count(self):
        '''The number of folders (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Folder")))

    @folder_count.setter
    def folder_count(self, value):
        '''Add or remove folder nodes as needed'''
        assert value > 0

        if self.folder_count > value:
            folder_nodes = self.root_node.findall(
                qn(self.ns['ome'], "Folder"))
            for folder_node in folder_nodes[value:]:
                self.root_node.remove(folder_node)
        elif self.folder_count < value:
            for _ in range(self.folder_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Folder"))


    def folder(self, index=0):
        '''Get the indexed folder elelment'''
        if self.folder_count == 0:
            self.folder_count = 1
        return self.Folder(
            self.root_node.findall(qn(self.ns['ome'], "Folder"))[index])

    # Experiment
    @property
    def experiment_count(self):
        '''The number of experiments (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Experiment")))

    @experiment_count.setter
    def experiment_count(self, value):
        '''Add or remove experiment nodes as needed'''
        assert value > 0

        if self.experiment_count > value:
            experiment_nodes = self.root_node.findall(
                qn(self.ns['ome'], "Experiment"))
            for experiment_node in experiment_nodes[value:]:
                self.root_node.remove(experiment_node)
        elif self.experiment_count < value:
            for _ in range(self.experiment_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Experiment"))


    def experiment(self, index=0):
        '''Get the indexed experiment elelment'''
        if self.experiment_count == 0:
            self.experiment_count = 1
        return self.Experiment(
            self.root_node.findall(qn(self.ns['ome'], "Experiment"))[index])

    # plate
    @property
    def plate_count(self):
        '''The number of plates (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Plate")))

    @plate_count.setter
    def plate_count(self, value):
        '''Add or remove plate nodes as needed'''
        assert value > 0

        if self.plate_count > value:
            plate_nodes = self.root_node.findall(qn(self.ns['ome'], "Plate"))
            for plate_node in plate_nodes[value:]:
                self.root_node.remove(plate_node)
        elif self.plate_count < value:
            for _ in range(self.plate_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Plate"))


    def plate(self, index=0):
        '''Get the indexed plate elelment'''
        if self.plate_count == 0:
            self.plate_count = 1
        return self.Plate(
            self.root_node.findall(qn(self.ns['ome'], "Plate"))[index])

    # screen
    @property
    def screen_count(self):
        '''The number of screens (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Screen")))

    @screen_count.setter
    def screen_count(self, value):
        '''Add or remove screen nodes as needed'''
        assert value > 0

        if self.screen_count > value:
            screen_nodes = self.root_node.findall(qn(self.ns['ome'], "Screen"))
            for screen_node in screen_nodes[value:]:
                self.root_node.remove(screen_node)
        elif self.screen_count < value:
            for _ in range(self.screen_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Screen"))


    def screen(self, index=0):
        '''Get the indexed screen elelment'''
        if self.screen_count == 0:
            self.screen_count = 1
        return self.Screen(
            self.root_node.findall(qn(self.ns['ome'], "Screen"))[index])

    # experimenter
    @property
    def experimenter_count(self):
        '''The number of experimenters (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "Experimenter")))

    @experimenter_count.setter
    def experimenter_count(self, value):
        '''Add or remove experimenter nodes as needed'''
        assert value > 0

        if self.experimenter_count > value:
            experimenter_nodes = self.root_node.findall(
                qn(self.ns['ome'], "Experimenter"))
            for experimenter_node in experimenter_nodes[value:]:
                self.root_node.remove(experimenter_node)
        elif self.experimenter_count < value:
            for _ in range(self.experimenter_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "Experimenter"))


    def experimenter(self, index=0):
        '''Get the indexed experimenter elelment'''
        if self.experimenter_count == 0:
            self.experimenter_count = 1
        return self.Experimenter(
            self.root_node.findall(qn(self.ns['ome'], "Experimenter"))[index])

    # experimentergroup
    @property
    def experimentergroup_count(self):
        '''The number of experimentergroups (= series) specified by the XML'''
        return len(self.root_node.findall(
            qn(self.ns['ome'], "ExperimenterGroup")))

    @experimentergroup_count.setter
    def experimentergroup_count(self, value):
        '''Add or remove experimentergroup nodes as needed'''
        assert value > 0

        if self.experimentergroup_count > value:
            experimentergroup_nodes = self.root_node.findall(
                qn(self.ns['ome'], "ExperimenterGroup"))
            for experimentergroup_node in experimentergroup_nodes[value:]:
                self.root_node.remove(experimentergroup_node)
        elif self.experimentergroup_count < value:
            for _ in range(self.experimentergroup_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "ExperimenterGroup"))


    def experimentergroup(self, index=0):
        '''Get the indexed experimentergroup elelment'''
        if self.experimentergroup_count == 0:
            self.experimentergroup_count = 1
        return self.ExperimenterGroup(self.root_node.findall(
            qn(self.ns['ome'], "ExperimenterGroup"))[index])

    # structuredannotations
    @property
    def structuredannotations_count(self):
        '''The number of structuredannotationss (= series) specified by the
        XML'''
        return len(self.root_node.findall(
            qn(self.ns['ome'], "StructuredAnnotations")))

    @structuredannotations_count.setter
    def structuredannotations_count(self, value):
        '''Add or remove structuredannotations nodes as needed'''
        assert value > 0

        if self.structuredannotations_count > value:
            structuredannotations_nodes = self.root_node.findall(
                qn(self.ns['ome'], "StructuredAnnotations"))
            for structuredannotations_node in structuredannotations_nodes[value:]:
                self.root_node.remove(structuredannotations_node)
        elif self.structuredannotations_count < value:
            for _ in range(self.structuredannotations_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(
                        self.ns['ome'], "StructuredAnnotations"))


    def structuredannotations(self, index=0):
        '''Get the indexed structuredannotations elelment'''
        if self.structuredannotations_count == 0:
            self.structuredannotations_count = 1
        return self.StructuredAnnotations(self.root_node.findall(
            qn(self.ns['ome'], "StructuredAnnotations"))[index])

    # roi
    @property
    def roi_count(self):
        '''The number of rois (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "ROI")))

    @roi_count.setter
    def roi_count(self, value):
        '''Add or remove roi nodes as needed'''
        assert value > 0

        if self.roi_count > value:
            roi_nodes = self.root_node.findall(qn(self.ns['ome'], "ROI"))
            for roi_node in roi_nodes[value:]:
                self.root_node.remove(roi_node)
        elif self.roi_count < value:
            for _ in range(self.roi_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "ROI"))


    def roi(self, index=0):
        '''Get the indexed roi elelment'''
        if self.roi_count == 0:
            self.roi_count =1
        return self.ROI(
            self.root_node.findall(qn(self.ns['ome'], "ROI"))[index])

    # binaryonly
    @property
    def binaryonly_count(self):
        '''The number of binaryonlys (= series) specified by the XML'''
        return len(self.root_node.findall(qn(self.ns['ome'], "BinaryOnly")))

    @binaryonly_count.setter
    def binaryonly_count(self, value):
        '''Add or remove binaryonly nodes as needed'''
        assert value > 0

        if self.binaryonly_count > value:
            binaryonly_nodes = self.root_node.findall(
                qn(self.ns['ome'], "BinaryOnly"))
            for binaryonly_node in binaryonly_nodes[value:]:
                self.root_node.remove(binaryonly_node)
        elif self.binaryonly_count < value:
            for _ in range(self.binaryonly_count, value):
                ElementTree.SubElement(
                    self.root_node, qn(self.ns['ome'], "BinaryOnly"))


    def binaryonly(self, index=0):
        '''Get the indexed binaryonly elelment'''
        if self.binaryonly_count == 0:
            self.binaryonly_count =1
        return self.BinaryOnly(self.root_node.findall(
            qn(self.ns['ome'], "BinaryOnly"))[index])

    # this the whole schema diagram
    #
    # class instrument
    class Instrument():
        '''Representation of the OME/Instrument element'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)



        @property
        def detector_count(self):
            '''The number of detectors in the instrument
            List all the detectors in this instrument.
            '''
            return len(self.node.findall(qn(self.ns['ome'], "Detector")))

        @detector_count.setter
        def detector_count(self, value):
            assert value >= 0
            detector_count = self.detector_count
            if detector_count > value:
                detectors = self.node.findall(
                    qn(self.ns['ome'], "Detector"))
                for detector in detectors[value:]:
                    self.node.remove(detector)
            else:
                for _ in range(detector_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Detector"))


        def Detector(self, index=0):
            '''Get the indexed detector from Instrument element'''
            if self.detector_count == 0:
                self.detector_count =1
            return OMEXML.Detector(
                self.node.findall(qn(self.ns['ome'], "Detector"))[index])

        @property
        def microscope_count(self):
            '''The number of microscopes in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Microscope")))

        @microscope_count.setter
        def microscope_count(self, value):
            '''Set the number of microscope element'''
            assert value >= 0
            microscope_count = self.microscope_count
            if microscope_count > value:
                microscopes = self.node.findall(
                    qn(self.ns['ome'], "Microscope"))
                for microscope in microscopes[value:]:
                    self.node.remove(microscope)
            else:
                for _ in range(microscope_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Microscope"))


        def Microscope(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.microscope_count == 0:
                self.microscope_count =1
            return OMEXML.Microscope(
                self.node.findall(qn(self.ns['ome'], "Microscope"))[index])

        @property
        def objective_count(self):
            '''The number of objectives in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Objective")))

        @objective_count.setter
        def objective_count(self, value):
            assert value >= 0
            objective_count = self.objective_count
            if objective_count > value:
                objectives = self.node.findall(
                    qn(self.ns['ome'], "Objective"))
                for objective in objectives[value:]:
                    self.node.remove(objective)
            else:
                for _ in range(objective_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Objective"))


        def Objective(self, index=0):
            '''Get the indexed Objective from Instrument element'''
            if self.objective_count == 0:
                self.objective_count =1
            return OMEXML.Objective(
                self.node.findall(qn(self.ns['ome'], "Objective"))[index])

        @property
        def lightsourcegroup_count(self):
            '''The number of lightsourcegroups in the instrument'''
            return len(
                self.node.findall(qn(self.ns['ome'], "LightSourceGroup")))

        @lightsourcegroup_count.setter
        def lightsourcegroup_count(self, value):
            '''Set the lightsourcegroup count'''
            assert value >= 0
            lightsourcegroup_count = self.lightsourcegroup_count
            if lightsourcegroup_count > value:
                lightsourcegroups = self.node.findall(
                    qn(self.ns['ome'], "LightSourceGroup"))
                for lightsourcegroup in lightsourcegroups[value:]:
                    self.node.remove(lightsourcegroup)
            else:
                for _ in range(lightsourcegroup_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LightSourceGroup"))


        def LightSourceGroup(self, index=0):
            '''Get the indexed lightsourcegroup from Instrument element'''
            if self.lightsourcegroup_count == 0:
                self.lightsourcegroup_count =1
            return OMEXML.LightSourceGroup(self.node.findall(
                qn(self.ns['ome'], "LightSourceGroup"))[index])

        # Arc lightsource
        @property
        def arc_count(self):
            '''The number of arcs in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Arc")))

        @arc_count.setter
        def arc_count(self, value):
            '''Set the arc count'''
            assert value >= 0
            arc_count = self.arc_count
            if arc_count > value:
                arcs = self.node.findall(
                    qn(self.ns['ome'], "Arc"))
                for arc in arcs[value:]:
                    self.node.remove(arc)
            else:
                for _ in range(arc_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Arc"))


        def Arc(self, index=0):
            '''Get the indexed arc from Instrument element'''
            if self.arc_count == 0:
                self.arc_count = 1
            return OMEXML.Arc(
                self.node.findall(qn(self.ns['ome'], "Arc"))[index])

        # Filament lightsource
        @property
        def filament_count(self):
            '''The number of filaments in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Filament")))

        @filament_count.setter
        def filament_count(self, value):
            '''Set the filament count'''
            assert value >= 0
            filament_count = self.filament_count
            if filament_count > value:
                filaments = self.node.findall(
                    qn(self.ns['ome'], "Filament"))
                for filament in filaments[value:]:
                    self.node.remove(filament)
            else:
                for _ in range(filament_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Filament"))


        def Filament(self, index=0):
            '''Get the indexed filament from Instrument element'''
            if self.filament_count == 0:
                self.filament_count = 1
            return OMEXML.Filament(
                self.node.findall(qn(self.ns['ome'], "Filament"))[index])

        # Laser lightsource
        @property
        def laser_count(self):
            '''The number of lasers in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Laser")))

        @laser_count.setter
        def laser_count(self, value):
            '''Set the laser count'''
            assert value >= 0
            laser_count = self.laser_count
            if laser_count > value:
                lasers = self.node.findall(
                    qn(self.ns['ome'], "Laser"))
                for laser in lasers[value:]:
                    self.node.remove(laser)
            else:
                for _ in range(laser_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Laser"))

        def Laser(self, index=0):
            '''Get the indexed laser from Instrument element'''
            if self.laser_count == 0:
                self.laser_count = 1
            return OMEXML.Laser(
                self.node.findall(qn(self.ns['ome'], "Laser"))[index])

        # LightEmittingDiode lightsource
        @property
        def lightemittingdiode_count(self):
            '''The number of lightemittingdiodes in the instrument'''
            return len(self.node.findall(
                qn(self.ns['ome'], "LightEmittingDiode")))

        @lightemittingdiode_count.setter
        def lightemittingdiode_count(self, value):
            '''Set the lightemittingdiode count'''
            assert value >= 0
            lightemittingdiode_count = self.lightemittingdiode_count
            if lightemittingdiode_count > value:
                lightemittingdiodes = self.node.findall(
                    qn(self.ns['ome'], "LightEmittingDiode"))
                for lightemittingdiode in lightemittingdiodes[value:]:
                    self.node.remove(lightemittingdiode)
            else:
                for _ in range(lightemittingdiode_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LightEmittingDiode"))


        def LightEmittingDiode(self, index=0):
            '''Get the indexed lightemittingdiode from Instrument element'''
            if self.lightemittingdiode_count == 0:
                self.lightemittingdiode_count = 1
            return OMEXML.LightEmittingDiode(self.node.findall(qn(
                self.ns['ome'], "LightEmittingDiode"))[index])

        # GenericExcitationSource lightsource
        @property
        def genericexcitationsource_count(self):
            '''The number of genericexcitationsources in the instrument'''
            return len(self.node.findall(
                qn(self.ns['ome'], "GenericExcitationSource")))

        @genericexcitationsource_count.setter
        def genericexcitationsource_count(self, value):
            '''Set the genericexcitationsource count'''
            assert value >= 0
            genericexcitationsource_count = self.genericexcitationsource_count
            if genericexcitationsource_count > value:
                genericexcitationsources = self.node.findall(
                    qn(self.ns['ome'], "GenericExcitationSource"))
                for genericexcitationsource in genericexcitationsources[value:]:
                    self.node.remove(genericexcitationsource)
            else:
                for _ in range(genericexcitationsource_count, value):
                    ElementTree.SubElement(self.node, qn(
                        self.ns['ome'], "GenericExcitationSource"))


        def GenericExcitationSource(self, index=0):
            '''Get the indexed genericexcitationsource from Instrument
            element'''
            if self.genericexcitationsource_count == 0:
                self.genericexcitationsource_count = 1
            return OMEXML.GenericExcitationSource(self.node.findall(
                qn(self.ns['ome'], "GenericExcitationSource"))[index])

        # Dichroic lightsource
        @property
        def dichroic_count(self):
            '''The number of dichroics in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Dichroic")))

        @dichroic_count.setter
        def dichroic_count(self, value):
            '''Set the dichroic count'''
            assert value >= 0
            dichroic_count = self.dichroic_count
            if dichroic_count > value:
                dichroics = self.node.findall(
                    qn(self.ns['ome'], "Dichroic"))
                for dichroic in dichroics[value:]:
                    self.node.remove(dichroic)
            else:
                for _ in range(dichroic_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Dichroic"))


        def Dichroic(self, index=0):
            '''Get the indexed dichroic from Instrument element'''
            if self.dichroic_count == 0:
                self.dichroic_count = 1
            return OMEXML.Dichroic(
                self.node.findall(qn(self.ns['ome'], "Dichroic"))[index])

        # FilterSet
        @property
        def filterset_count(self):
            '''The number of filtersets in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "FilterSet")))

        @filterset_count.setter
        def filterset_count(self, value):
            '''Set the filterset count'''
            assert value >= 0
            filterset_count = self.filterset_count
            if filterset_count > value:
                filtersets = self.node.findall(
                    qn(self.ns['ome'], "FilterSet"))
                for filterset in filtersets[value:]:
                    self.node.remove(filterset)
            else:
                for _ in range(filterset_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "FilterSet"))


        def FilterSet(self, index=0):
            '''Get the indexed filterset from Instrument element'''
            if self.filterset_count == 0:
                self.filterset_count =1
            return OMEXML.FilterSet(
                self.node.findall(qn(self.ns['ome'], "FilterSet"))[index])

        @property
        def filter_count(self):
            '''Get the filter number'''
            return len(self.node.findall(qn(self.ns['ome'], "Filter")))

        @filter_count.setter
        def filter_count(self, value):
            '''Set the filter number'''
            assert value >= 0
            filter_count = self.filter_count
            if filter_count > value:
                filters = self.node.findall(
                    qn(self.ns['ome'], "Filter"))
                for the_filter in filters[value:]:
                    self.node.remove(the_filter)
            else:
                for _ in range(filter_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Filter"))

        def Filter(self, index=0):
            '''Get the indexed filter from Instrument element'''
            if self.filter_count == 0:
                self.filter_count = 1
            return OMEXML.Filter(
                self.node.findall(qn(self.ns['ome'], "Filter"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

    class Dataset():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])


        @property
        def experimentergroupref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef")))
        @experimentergroupref_count.setter
        def experimentergroupref_count(self, experimentergroupref):
        	assert experimentergroupref >= 0
        	experimentergroupref_count = self.experimentergroupref_count
        	if experimentergroupref_count > experimentergroupref:
        		experimentergrouprefs = self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))
        		for experimentergroupref in experimentergrouprefs[experimentergroupref:]:
        			self.node.remove(experimentergroupref)
        	else:
        		for _ in range(experimentergroupref_count, experimentergroupref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterGroupRef"))

        def ExperimenterGroupRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimentergroupref_count == 0:
        		self.experimentergroupref_count = 1
        	return OMEXML.ExperimenterGroupRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))[index])


        @property
        def imageref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ImageRef")))
        @imageref_count.setter
        def imageref_count(self, value):
            assert value >= 0
            imageref_count = self.imageref_count
            if imageref_count > value:
                imagerefs = self.node.findall(
                    qn(self.ns['ome'], "ImageRef"))
                for imageref in imagerefs[value:]:
                    self.node.remove(imageref)
            else:
                for _ in range(imageref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ImageRef"))

        def ImageRef(self, index=0):
            '''Set ImageRef'''
            imageref = self.node.find(
                qn(self.ns['ome'], "ImageRef"))
            if self.imageref_count == 0:
                self.imageref_count = 1
            return OMEXML.ImageRef(self.node.findall(qn(self.ns['ome'], "ImageRef"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

    class ImageRef():
        '''ImageRef'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Project():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])


        @property
        def experimentergroupref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef")))
        @experimentergroupref_count.setter
        def experimentergroupref_count(self, experimentergroupref):
        	assert experimentergroupref >= 0
        	experimentergroupref_count = self.experimentergroupref_count
        	if experimentergroupref_count > experimentergroupref:
        		experimentergrouprefs = self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))
        		for experimentergroupref in experimentergrouprefs[experimentergroupref:]:
        			self.node.remove(experimentergroupref)
        	else:
        		for _ in range(experimentergroupref_count, experimentergroupref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterGroupRef"))

        def ExperimenterGroupRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimentergroupref_count == 0:
        		self.experimentergroupref_count = 1
        	return OMEXML.ExperimenterGroupRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))[index])


        @property
        def datasetref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "DatasetRef")))
        @datasetref_count.setter
        def datasetref_count(self, value):
            assert value >= 0
            datasetref_count = self.datasetref_count
            if datasetref_count > value:
                datasetrefs = self.node.findall(qn(self.ns['ome'], "DatasetRef"))
                for datasetref in datasetrefs[value:]:
                    self.node.remove(datasetref)
            else:
                for _ in range(datasetref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "DatasetRef"))

        def DatasetRef(self, index=0):
            '''Set DatasetRef'''
            datasetref = self.node.find(
                qn(self.ns['ome'], "DatasetRef"))
            if self.datasetref_count == 0:
                self.datasetref_count = 1
            return OMEXML.DatasetRef(self.node.findall(qn(self.ns['ome'], "DatasetRef"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])
    class DatasetRef():
        '''DatasetRef'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Folder():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def imageref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ImageRef")))
        @imageref_count.setter
        def imageref_count(self, value):
            assert value >= 0
            imageref_count = self.imageref_count
            if imageref_count > value:
                imagerefs = self.node.findall(
                    qn(self.ns['ome'], "ImageRef"))
                for imageref in imagerefs[value:]:
                    self.node.remove(imageref)
            else:
                for _ in range(imageref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ImageRef"))

        def ImageRef(self, index=0):
            '''Set ImageRef'''
            imageref = self.node.find(
                qn(self.ns['ome'], "ImageRef"))
            if self.imageref_count == 0:
                self.imageref_count = 1
            return OMEXML.ImageRef(self.node.findall(qn(self.ns['ome'], "ImageRef"))[index])


        @property
        def folderref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "FolderRef")))
        @folderref_count.setter
        def folderref_count(self, value):
            assert value >= 0
            folderref_count = self.folderref_count
            if folderref_count > value:
                folderrefs = self.node.findall(
                    qn(self.ns['ome'], "FolderRef"))
                for folderref in folderrefs[value:]:
                    self.node.remove(folderref)
            else:
                for _ in range(folderref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "FolderRef"))

        def FolderRef(self, index=0):
            '''Set FolderRef'''
            folderref = self.node.find(
                qn(self.ns['ome'], "FolderRef"))
            if self.folderref_count == 0:
                self.folderref_count = 1
            return OMEXML.FolderRef(self.node.findall(qn(self.ns['ome'], "FolderRef"))[index])


        @property
        def roiref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ROIRef")))
        @roiref_count.setter
        def roiref_count(self, value):
            assert value >= 0
            roiref_count = self.roiref_count
            if roiref_count > value:
                roirefs = self.node.findall(qn(self.ns['ome'], "ROIRef"))
                for roiref in roirefs[value:]:
                    self.node.remove(roiref)
            else:
                for _ in range(roiref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ROIRef"))

        def ROIRef(self, index=0):
            '''Set ROIRef'''
            imageref = self.node.find(
                qn(self.ns['ome'], "ROIRef"))
            if self.roiref_count == 0:
                self.roiref_count = 1
            return OMEXML.ROIRef(self.node.findall(qn(self.ns['ome'], "ROIRef"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

    class FolderRef():
        '''FolderRef'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Experiment():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Type(self):
            return self.node.get("Type")

        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])


        @property
        def microbeammanipulation_count(self):
            return len(self.node.findall(
                qn(self.ns['ome'], "MicrobeamManipulation")))

        @microbeammanipulation_count.setter
        def microbeammanipulation_count(self, value):
            assert value > 0
            microbeammanipulation_count = self.microbeammanipulation_count
            if microbeammanipulation_count > value:
                microbeammanipulation = self.node.findall(
                    qn(self.ns['ome'], "MicrobeamManipulation"))
                for microbeammanipulation in microbeammanipulation[value:]:
                    self.node.remove(microbeammanipulation)
            else:
                for _ in range(microbeammanipulation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "MicrobeamManipulation"))


        def MicrobeamManipulation(self, index=0):
            '''Get the indexed microbeammanipulation from the Pixels element'''
            if self.microbeammanipulation_count == 0:
                self.microbeammanipulation_count = 1
            return OMEXML.MicrobeamManipulation(self.node.findall(
                qn(self.ns['ome'], "MicrobeamManipulation"))[index])

    class MicrobeamManipulation():
        'OME/Experiment/MicrobeamManipulation'

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Type(self):
            return self.node.get("Type")

        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])


        @property
        def lightsourcesettings_count(self):
            return len(self.node.findall(
                qn(self.ns['ome'], "LightSourceSettings")))

        @lightsourcesettings_count.setter
        def lightsourcesettings_count(self, value):
            assert value > 0
            lightsourcesettings_count = self.lightsourcesettings_count
            if lightsourcesettings_count > value:
                lightsourcesettings = self.node.findall(
                    qn(self.ns['ome'], "LightSourceSettings"))
                for lightsourcesettings in lightsourcesettings[value:]:
                    self.node.remove(lightsourcesettings)
            else:
                for _ in range(lightsourcesettings_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LightSourceSettings"))


        def LightSourceSettings(self, index=0):
            '''Get the indexed lightsourcesettings from the Pixels element'''
            if self.lightsourcesettings_count == 0:
                self.lightsourcesettings_count = 1
            return OMEXML.LightSourceSettings(self.node.findall(
                qn(self.ns['ome'], "LightSourceSettings"))[index])


        @property
        def roiref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ROIRef")))
        @roiref_count.setter
        def roiref_count(self, value):
            assert value >= 0
            roiref_count = self.roiref_count
            if roiref_count > value:
                roirefs = self.node.findall(qn(self.ns['ome'], "ROIRef"))
                for roiref in roirefs[value:]:
                    self.node.remove(roiref)
            else:
                for _ in range(roiref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ROIRef"))

        def ROIRef(self, index=0):
            '''Set ROIRef'''
            roiref = self.node.find(
                qn(self.ns['ome'], "ROIRef"))
            if self.roiref_count == 0:
                self.roiref_count = 1
            return OMEXML.ROIRef(self.node.findall(qn(self.ns['ome'], "ROIRef"))[index])


    class Plate():
        '''OME/Plate'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def Status(self):
            return self.node.get("Status")

        @Status.setter
        def Status(self, value):
            self.node.set("Status", value)


        @property
        def ExternalIdentifier(self):
            return self.node.get("ExternalIdentifier")

        @ExternalIdentifier.setter
        def ExternalIdentifier(self, value):
            self.node.set("ExternalIdentifier", value)


        @property
        def ColumnNamingConvention(self):
            return self.node.get("ColumnNamingConvention")

        @ColumnNamingConvention.setter
        def ColumnNamingConvention(self, value):
            self.node.set("ColumnNamingConvention", value)


        @property
        def RowNamingConvention(self):
            return self.node.get("RowNamingConvention")

        @RowNamingConvention.setter
        def RowNamingConvention(self, value):
            self.node.set("RowNamingConvention", value)


        @property
        def WellOriginX(self):
            return self.node.get("WellOriginX")

        @WellOriginX.setter
        def WellOriginX(self, value):
            self.node.set("WellOriginX", value)


        @property
        def WellOriginXUnit(self):
            return self.node.get("WellOriginXUnit")

        @WellOriginXUnit.setter
        def WellOriginXUnit(self, value):
            self.node.set("WellOriginXUnit", value)


        @property
        def WellOriginY(self):
            return self.node.get("WellOriginY")

        @WellOriginY.setter
        def WellOriginY(self, value):
            self.node.set("WellOriginY", value)


        @property
        def WellOriginYUnit(self):
            return self.node.get("WellOriginYUnit")

        @WellOriginYUnit.setter
        def WellOriginYUnit(self, value):
            self.node.set("WellOriginYUnit", value)


        @property
        def Rows(self):
            return self.node.get("Rows")

        @Rows.setter
        def Rows(self, value):
            self.node.set("Rows", value)


        @property
        def Columns(self):
            return self.node.get("Columns")

        @Columns.setter
        def Columns(self, value):
            self.node.set("Columns", value)


        @property
        def FieldIndex(self):
            return self.node.get("FieldIndex")

        @FieldIndex.setter
        def FieldIndex(self, value):
            self.node.set("FieldIndex", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def well_count(self):
            '''The number of wells in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Well")))

        @well_count.setter
        def well_count(self, value):
            '''Set the number of well element'''
            assert value >= 0
            well_count = self.well_count
            if well_count > value:
                wells = self.node.findall(qn(self.ns['ome'], "Well"))
                for well in wells[value:]:
                    self.node.remove(well)
            else:
                for _ in range(well_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Well"))


        def Well(self, index=0):
            '''Get the indexed well from Instrument element'''
            if self.well_count == 0:
                self.well_count = 1
            return OMEXML.Well(
                self.node.findall(qn(self.ns['ome'], "Well"))[index])

        @property
        def plateacquisition_count(self):
            '''The number of plateacquisitions in the instrument'''
            return len(self.node.findall(
                qn(self.ns['ome'], "PlateAcquisition")))

        @plateacquisition_count.setter
        def plateacquisition_count(self, value):
            '''Set the number of plateacquisition element'''
            assert value >= 0
            plateacquisition_count = self.plateacquisition_count
            if plateacquisition_count > value:
                plateacquisitions = self.node.findall(
                    qn(self.ns['ome'], "PlateAcquisition"))
                for plateacquisition in plateacquisitions[value:]:
                    self.node.remove(plateacquisition)
            else:
                for _ in range(plateacquisition_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "PlateAcquisition"))


        def PlateAcquisition(self, index=0):
            '''Get the indexed plateacquisition from Instrument element'''
            if self.plateacquisition_count == 0:
                self.plateacquisition_count = 1
            return OMEXML.PlateAcquisition(
                self.node.findall(
                    qn(self.ns['ome'], "PlateAcquisition"))[index])

    class PlateAcquisition():

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def EndTime(self):
            return self.node.get("EndTime")

        @EndTime.setter
        def EndTime(self, value):
            self.node.set("EndTime", value)


        @property
        def StartTime(self):
            return self.node.get("StartTime")

        @StartTime.setter
        def StartTime(self, value):
            self.node.set("StartTime", value)


        @property
        def MaximumFieldCount(self):
            return self.node.get("MaximumFieldCount")

        @MaximumFieldCount.setter
        def MaximumFieldCount(self, value):
            self.node.set("MaximumFieldCount", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def wellsampleref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "WellSampleRef")))
        @wellsampleref_count.setter
        def wellsampleref_count(self, value):
            assert value >= 0
            wellsampleref_count = self.wellsampleref_count
            if wellsampleref_count > value:
                wellsamplerefs = self.node.findall(qn(self.ns['ome'], "WellSampleRef"))
                for wellsampleref in wellsamplerefs[value:]:
                    self.node.remove(wellsampleref)
            else:
                for _ in range(wellsampleref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "WellSampleRef"))

        def WellSampleRef(self, index=0):
            '''Set WellSampleRef'''
            wellsampleref = self.node.find(
                qn(self.ns['ome'], "WellSampleRef"))
            if self.wellsampleref_count == 0:
                self.wellsampleref_count = 1
            return OMEXML.WellSampleRef(self.node.findall(qn(self.ns['ome'], "WellSampleRef"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class WellSampleRef():
        '''WellSampleRef'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Well():
        '''OME/Plate/Well'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Row(self):
            return self.node.get("Row")

        @Row.setter
        def Row(self, value):
            self.node.set("Row", value)


        @property
        def Column(self):
            return self.node.get("Column")

        @Column.setter
        def Column(self, value):
            self.node.set("Column", value)


        @property
        def ExternalDescription(self):
            return self.node.get("ExternalDescription")

        @ExternalDescription.setter
        def ExternalDescription(self, value):
            self.node.set("ExternalDescription", value)


        @property
        def ExternalIdentifier(self):
            return self.node.get("ExternalIdentifier")

        @ExternalIdentifier.setter
        def ExternalIdentifier(self, value):
            self.node.set("ExternalIdentifier", value)


        @property
        def Type(self):
            return self.node.get("Type")

        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def Color(self):
            return self.node.get("Color")

        @Color.setter
        def Color(self, value):
            self.node.set("Color", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def reagentref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ReagentRef")))
        @reagentref_count.setter
        def reagentref_count(self, value):
            assert value >= 0
            reagentref_count = self.reagentref_count
            if reagentref_count > value:
                reagentrefs = self.node.findall(qn(self.ns['ome'], "ReagentRef"))
                for reagentref in reagentrefs[value:]:
                    self.node.remove(reagentref)
            else:
                for _ in range(reagentref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ReagentRef"))

        def ReagentRef(self, index=0):
            '''Set ReagentRef'''
            reagentref = self.node.find(
                qn(self.ns['ome'], "ReagentRef"))
            if self.reagentref_count == 0:
                self.reagentref_count = 1
            return OMEXML.ReagentRef(self.node.findall(qn(self.ns['ome'], "ReagentRef"))[index])


        @property
        def wellsample_count(self):
            '''The number of wellsamples in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "WellSample")))

        @wellsample_count.setter
        def wellsample_count(self, value):
            '''Set the number of wellsample element'''
            assert value >= 0
            wellsample_count = self.wellsample_count
            if wellsample_count > value:
                wellsamples = self.node.findall(
                    qn(self.ns['ome'], "WellSample"))
                for wellsample in wellsamples[value:]:
                    self.node.remove(wellsample)
            else:
                for _ in range(wellsample_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "WellSample"))


        def WellSample(self, index=0):
            '''Get the indexed wellsample from Instrument element'''
            if self.wellsample_count == 0:
                self.wellsample_count = 1
            return OMEXML.WellSample(
                self.node.findall(qn(self.ns['ome'], "WellSample"))[index])

    class ReagentRef():
        '''ReagentRef'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class WellSample():
        'OME/Plate'

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def PositionX(self):
            return self.node.get("PositionX")

        @PositionX.setter
        def PositionX(self, value):
            self.node.set("PositionX", value)


        @property
        def PositionXUnit(self):
            return self.node.get("PositionXUnit")

        @PositionXUnit.setter
        def PositionXUnit(self, value):
            self.node.set("PositionXUnit", value)


        @property
        def PositionY(self):
            return self.node.get("PositionY")

        @PositionY.setter
        def PositionY(self, value):
            self.node.set("PositionY", value)


        @property
        def PositionYUnit(self):
            return self.node.get("PositionYUnit")

        @PositionYUnit.setter
        def PositionYUnit(self, value):
            self.node.set("PositionYUnit", value)


        @property
        def TimePoint(self):
            return self.node.get("TimePoint")

        @TimePoint.setter
        def TimePoint(self, value):
            self.node.set("TimePoint", value)


        @property
        def Index(self):
            return self.node.get("Index")

        @Index.setter
        def Index(self, value):
            self.node.set("Index", value)

        @property
        def imageref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ImageRef")))
        @imageref_count.setter
        def imageref_count(self, value):
            assert value >= 0
            imageref_count = self.imageref_count
            if imageref_count > value:
                imagerefs = self.node.findall(
                    qn(self.ns['ome'], "ImageRef"))
                for imageref in imagerefs[value:]:
                    self.node.remove(imageref)
            else:
                for _ in range(imageref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ImageRef"))

        def ImageRef(self, index=0):
            '''Set ImageRef'''
            imageref = self.node.find(
                qn(self.ns['ome'], "ImageRef"))
            if self.imageref_count == 0:
                self.imageref_count = 1
            return OMEXML.ImageRef(self.node.findall(qn(self.ns['ome'], "ImageRef"))[index])


    class Screen():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def ProtocolIdentifier(self):
            return self.node.get("ProtocolIdentifier")

        @ProtocolIdentifier.setter
        def ProtocolIdentifier(self, value):
            self.node.set("ProtocolIdentifier", value)


        @property
        def ProtocolDescription(self):
            return self.node.get("ProtocolDescription")

        @ProtocolDescription.setter
        def ProtocolDescription(self, value):
            self.node.set("ProtocolDescription", value)


        @property
        def ReagentSetDescription(self):
            return self.node.get("ReagentSetDescription")

        @ReagentSetDescription.setter
        def ReagentSetDescription(self, value):
            self.node.set("ReagentSetDescription", value)


        @property
        def ReagentSetIdentifier(self):
            return self.node.get("ReagentSetIdentifier")

        @ReagentSetIdentifier.setter
        def ReagentSetIdentifier(self, value):
            self.node.set("ReagentSetIdentifier", value)


        @property
        def Type(self):
            return self.node.get("Type")

        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def plateref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "PlateRef")))
        @plateref_count.setter
        def plateref_count(self, value):
            assert value >= 0
            plateref_count = self.plateref_count
            if plateref_count > value:
                platerefs = self.node.findall(qn(self.ns['ome'], "PlateRef"))
                for plateref in platerefs[value:]:
                    self.node.remove(plateref)
            else:
                for _ in range(plateref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "PlateRef"))

        def PlateRef(self, index=0):
            '''Set PlateRef'''
            plateref = self.node.find(
                qn(self.ns['ome'], "PlateRef"))
            if self.plateref_count == 0:
                self.plateref_count = 1
            return OMEXML.PlateRef(self.node.findall(qn(self.ns['ome'], "PlateRef"))[index])


        @property
        def reagent_count(self):
            '''The number of reagents in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Reagent")))

        @reagent_count.setter
        def reagent_count(self, value):
            '''Set the number of reagent element'''
            assert value >= 0
            reagent_count = self.reagent_count
            if reagent_count > value:
                reagents = self.node.findall(
                    qn(self.ns['ome'], "Reagent"))
                for reagent in reagents[value:]:
                    self.node.remove(reagent)
            else:
                for _ in range(reagent_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Reagent"))


        def Reagent(self, index=0):
            '''Get the indexed reagent from Instrument element'''
            if self.reagent_count == 0:
                self.reagent_count = 1
            return OMEXML.Reagent(
                self.node.findall(qn(self.ns['ome'], "Reagent"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class Reagent():
        '''Screen/Reagent'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def ReagentIdentifier(self):
            return self.node.get("ReagentIdentifier")

        @ReagentIdentifier.setter
        def ReagentIdentifier(self, value):
            self.node.set("ProtocolIdentifier", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class PlateRef():
        '''PlateRef'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Experimenter():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def FirstName(self):
            return self.node.get("FirstName")

        @FirstName.setter
        def FirstName(self, value):
            self.node.set("FirstName", value)

        @property
        def MiddleName(self):
            return self.node.get("MiddleName")

        @MiddleName.setter
        def MiddleName(self, value):
            self.node.set("MiddleName", value)


        @property
        def LastName(self):
            return self.node.get("LastName")

        @LastName.setter
        def LastName(self, value):
            self.node.set("LastName", value)


        @property
        def Email(self):
            return self.node.get("Email")

        @Email.setter
        def Email(self, value):
            self.node.set("Email", value)


        @property
        def Institution(self):
            return self.node.get("Institution")

        @Institution.setter
        def Institution(self, value):
            self.node.set("Institution", value)


        @property
        def UserName(self):
            return self.node.get("UserName")

        @UserName.setter
        def UserName(self, value):
            self.node.set("UserName", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class ExperimenterGroup():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")

        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])


        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])


        def Leader(self):
            '''Set Leader'''
            leader = self.node.find(
                qn(self.ns['ome'], "Leader"))
            if leader is None:
                leader = ElementTree.SubElement(
                    self.node, qn(self.ns['ome'], "Leader"))
            return OMEXML.Leader(leader)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class Leader():
        '''Leader'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")

        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class StructuredAnnotations():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def xmlannotation_count(self):
            '''The number of xmlannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "XMLAnnotation")))

        @xmlannotation_count.setter
        def xmlannotation_count(self, value):
            '''Set the number of xmlannotation element'''
            assert value >= 0
            xmlannotation_count = self.xmlannotation_count
            if xmlannotation_count > value:
                xmlannotations = self.node.findall(
                    qn(self.ns['ome'], "XMLAnnotation"))
                for xmlannotation in xmlannotations[value:]:
                    self.node.remove(xmlannotation)
            else:
                for _ in range(xmlannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "XMLAnnotation"))


        def XMLAnnotation(self, index=0):
            '''Get the indexed xmlannotation from Instrument element'''
            if self.xmlannotation_count == 0:
                self.xmlannotation_count = 1
            return OMEXML.XMLAnnotation(
                self.node.findall(qn(self.ns['ome'], "XMLAnnotation"))[index])

        @property
        def fileannotation_count(self):
            '''The number of fileannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "FileAnnotation")))

        @fileannotation_count.setter
        def fileannotation_count(self, value):
            '''Set the number of fileannotation element'''
            assert value >= 0
            fileannotation_count = self.fileannotation_count
            if fileannotation_count > value:
                fileannotations = self.node.findall(
                    qn(self.ns['ome'], "FileAnnotation"))
                for fileannotation in fileannotations[value:]:
                    self.node.remove(fileannotation)
            else:
                for _ in range(fileannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "FileAnnotation"))


        def FileAnnotation(self, index=0):
            '''Get the indexed fileannotation from Instrument element'''
            if self.fileannotation_count == 0:
                self.fileannotation_count = 1
            return OMEXML.FileAnnotation(
                self.node.findall(qn(self.ns['ome'], "FileAnnotation"))[index])

        @property
        def listannotation_count(self):
            '''The number of listannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "ListAnnotation")))

        @listannotation_count.setter
        def listannotation_count(self, value):
            '''Set the number of listannotation element'''
            assert value >= 0
            listannotation_count = self.listannotation_count
            if listannotation_count > value:
                listannotations = self.node.findall(
                    qn(self.ns['ome'], "ListAnnotation"))
                for listannotation in listannotations[value:]:
                    self.node.remove(listannotation)
            else:
                for _ in range(listannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ListAnnotation"))


        def ListAnnotation(self, index=0):
            '''Get the indexed listannotation from Instrument element'''
            if self.listannotation_count == 0:
                self.listannotation_count = 1
            return OMEXML.ListAnnotation(
                self.node.findall(qn(self.ns['ome'], "ListAnnotation"))[index])

        @property
        def longannotation_count(self):
            '''The number of longannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "LongAnnotation")))

        @longannotation_count.setter
        def longannotation_count(self, value):
            '''Set the number of longannotation element'''
            assert value >= 0
            longannotation_count = self.longannotation_count
            if longannotation_count > value:
                longannotations = self.node.findall(
                    qn(self.ns['ome'], "LongAnnotation"))
                for longannotation in longannotations[value:]:
                    self.node.remove(longannotation)
            else:
                for _ in range(longannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LongAnnotation"))


        def LongAnnotation(self, index=0):
            '''Get the indexed longannotation from Instrument element'''
            if self.longannotation_count == 0:
                self.longannotation_count = 1
            return OMEXML.LongAnnotation(
                self.node.findall(qn(self.ns['ome'], "LongAnnotation"))[index])

        @property
        def doubleannotation_count(self):
            '''The number of doubleannotations in the instrument'''
            return len(
                self.node.findall(qn(self.ns['ome'], "DoubleAnnotation")))

        @doubleannotation_count.setter
        def doubleannotation_count(self, value):
            '''Set the number of doubleannotation element'''
            assert value >= 0
            doubleannotation_count = self.doubleannotation_count
            if doubleannotation_count > value:
                doubleannotations = self.node.findall(
                    qn(self.ns['ome'], "DoubleAnnotation"))
                for doubleannotation in doubleannotations[value:]:
                    self.node.remove(doubleannotation)
            else:
                for _ in range(doubleannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "DoubleAnnotation"))


        def DoubleAnnotation(self, index=0):
            '''Get the indexed doubleannotation from Instrument element'''
            if self.doubleannotation_count == 0:
                self.doubleannotation_count = 1
            return OMEXML.DoubleAnnotation(self.node.findall(
                qn(self.ns['ome'], "DoubleAnnotation"))[index])

        @property
        def commentannotation_count(self):
            '''The number of commentannotations in the instrument'''
            return len(
                self.node.findall(qn(self.ns['ome'], "CommentAnnotation")))

        @commentannotation_count.setter
        def commentannotation_count(self, value):
            '''Set the number of commentannotation element'''
            assert value >= 0
            commentannotation_count = self.commentannotation_count
            if commentannotation_count > value:
                commentannotations = self.node.findall(
                    qn(self.ns['ome'], "CommentAnnotation"))
                for commentannotation in commentannotations[value:]:
                    self.node.remove(commentannotation)
            else:
                for _ in range(commentannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "CommentAnnotation"))


        def CommentAnnotation(self, index=0):
            '''Get the indexed commentannotation from Instrument element'''
            if self.commentannotation_count == 0:
                self.commentannotation_count = 1
            return OMEXML.CommentAnnotation(self.node.findall(
                    qn(self.ns['ome'], "CommentAnnotation"))[index])

        @property
        def booleanannotation_count(self):
            '''The number of booleanannotations in the instrument'''
            return len(self.node.findall(
                qn(self.ns['ome'], "BooleanAnnotation")))

        @booleanannotation_count.setter
        def booleanannotation_count(self, value):
            '''Set the number of booleanannotation element'''
            assert value >= 0
            booleanannotation_count = self.booleanannotation_count
            if booleanannotation_count > value:
                booleanannotations = self.node.findall(
                    qn(self.ns['ome'], "BooleanAnnotation"))
                for booleanannotation in booleanannotations[value:]:
                    self.node.remove(booleanannotation)
            else:
                for _ in range(booleanannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "BooleanAnnotation"))


        def BooleanAnnotation(self, index=0):
            '''Get the indexed booleanannotation from Instrument element'''
            if self.booleanannotation_count == 0:
                self.booleanannotation_count = 1
            return OMEXML.BooleanAnnotation(self.node.findall(
                qn(self.ns['ome'], "BooleanAnnotation"))[index])

        @property
        def timestampannotation_count(self):
            '''The number of timestampannotations in the instrument'''
            return len(self.node.findall(
                qn(self.ns['ome'], "TimestampAnnotation")))

        @timestampannotation_count.setter
        def timestampannotation_count(self, value):
            '''Set the number of timestampannotation element'''
            assert value >= 0
            timestampannotation_count = self.timestampannotation_count
            if timestampannotation_count > value:
                timestampannotations = self.node.findall(
                    qn(self.ns['ome'], "TimestampAnnotation"))
                for timestampannotation in timestampannotations[value:]:
                    self.node.remove(timestampannotation)
            else:
                for _ in range(timestampannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "TimestampAnnotation"))


        def TimestampAnnotation(self, index=0):
            '''Get the indexed timestampannotation from Instrument element'''
            if self.timestampannotation_count == 0:
                self.timestampannotation_count = 1
            return OMEXML.TimestampAnnotation(
                self.node.findall(qn(self.ns['ome'], "TimestampAnnotation"))[index])

        @property
        def tagannotation_count(self):
            '''The number of tagannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "TagAnnotation")))

        @tagannotation_count.setter
        def tagannotation_count(self, value):
            '''Set the number of tagannotation element'''
            assert value >= 0
            tagannotation_count = self.tagannotation_count
            if tagannotation_count > value:
                tagannotations = self.node.findall(
                    qn(self.ns['ome'], "TagAnnotation"))
                for tagannotation in tagannotations[value:]:
                    self.node.remove(tagannotation)
            else:
                for _ in range(tagannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "TagAnnotation"))


        def TagAnnotation(self, index=0):
            '''Get the indexed tagannotation from Instrument element'''
            if self.tagannotation_count == 0:
                self.tagannotation_count = 1
            return OMEXML.TagAnnotation(
                self.node.findall(qn(self.ns['ome'], "TagAnnotation"))[index])

        @property
        def termannotation_count(self):
            '''The number of termannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "TermAnnotation")))

        @termannotation_count.setter
        def termannotation_count(self, value):
            '''Set the number of termannotation element'''
            assert value >= 0
            termannotation_count = self.termannotation_count
            if termannotation_count > value:
                termannotations = self.node.findall(
                    qn(self.ns['ome'], "TermAnnotation"))
                for termannotation in termannotations[value:]:
                    self.node.remove(termannotation)
            else:
                for _ in range(termannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "TermAnnotation"))


        def TermAnnotation(self, index=0):
            '''Get the indexed termannotation from Instrument element'''
            if self.termannotation_count == 0:
                self.termannotation_count = 1
            return OMEXML.TermAnnotation(
                self.node.findall(qn(self.ns['ome'], "TermAnnotation"))[index])

        @property
        def mapannotation_count(self):
            '''The number of mapannotations in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "MapAnnotation")))

        @mapannotation_count.setter
        def mapannotation_count(self, value):
            '''Set the number of mapannotation element'''
            assert value >= 0
            mapannotation_count = self.mapannotation_count
            if mapannotation_count > value:
                mapannotations = self.node.findall(
                    qn(self.ns['ome'], "MapAnnotation"))
                for mapannotation in mapannotations[value:]:
                    self.node.remove(mapannotation)
            else:
                for _ in range(mapannotation_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "MapAnnotation"))


        def MapAnnotation(self, index=0):
            '''Get the indexed mapannotation from Instrument element'''
            if self.mapannotation_count == 0:
                self.mapannotation_count = 1
            return OMEXML.MapAnnotation(
                self.node.findall(qn(self.ns['ome'], "MapAnnotation"))[index])


    class XMLAnnotation():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")

        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")

        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

    class FileAnnotation():
        '''FileAnnoation'''

        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class ListAnnotation():
        '''ListAnnotation'''
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class LongAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])



        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])



    class DoubleAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class CommentAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class BooleanAnnotation():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class TimestampAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class TagAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class TermAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class MapAnnotation():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def NameSpace(self):
            return self.node.get("NameSpace")
        @NameSpace.setter
        def NameSpace(self, value):
            self.node.set("NameSpace", value)


        @property
        def Annotator(self):
            return self.node.get("Annotator")
        @Annotator.setter
        def Annotator(self, value):
            self.node.set("Annotator", value)


        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def value_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Value")))
        @value_count.setter
        def value_count(self, value):
        	assert value >= 0
        	value_count = self.value_count
        	if value_count > value:
        		values = self.node.findall(qn(self.ns['ome'], "Value"))
        		for value in values[value:]:
        			self.node.remove(value)
        	else:
        		for _ in range(value_count, value):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Value"))

        def Value(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.value_count == 0:
        		self.value_count = 1
        	return OMEXML.Value(
                self.node.findall(qn(self.ns['ome'], "Value"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])




    class ROI():
        "OME/ROI"
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Name(self):
            return self.node.get("Name")
        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def union_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Union")))
        @union_count.setter
        def union_count(self, union):
        	assert union >= 0
        	union_count = self.union_count
        	if union_count > union:
        		unions = self.node.findall(qn(self.ns['ome'], "Union"))
        		for union in unions[union:]:
        			self.node.remove(union)
        	else:
        		for _ in range(union_count, union):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Union"))

        def Union(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.union_count == 0:
        		self.union_count = 1
        	return OMEXML.Union(
                self.node.findall(qn(self.ns['ome'], "Union"))[index])

        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class BinaryOnly():
        "OME/BinaryOnly"
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def MetadataFile(self):
            return self.node.get("MetadataFile")
        @MetadataFile.setter
        def MetadataFile(self, value):
            self.node.set("MetadataFile", value)


        @property
        def UUID(self):
            return self.node.get("UUID")
        @UUID.setter
        def UUID(self, value):
            self.node.set("UUID", value)
    # above is the whole schema diagram


    # this part are mainly for classes for instrument
    #
    class Microscope():
        '''The OME/Instrument/Microscope element. The Microscope element
        represents the Microscope in an OME image and, for an OME-XML encoded
        image, will actually contain the base-64 encoded pixel data. It has
        the Manufacturer, Model, SerialNumber, Type, etc.'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class LightSourceGroup():
        '''The lightsourcegroup element in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class Arc():
        '''The arc element in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)

        # Type


    class Filament():
        '''lightsource in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)



    class Laser():
        '''lightsource in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def LaserMedium(self):
            return self.node.get("LaserMedium")
        @LaserMedium.setter
        def LaserMedium(self, value):
            self.node.set("LaserMedium", value)

        @property
        def Wavelength(self):
            return self.node.get("Wavelength")
        @Wavelength.setter
        def Wavelength(self, value):
            self.node.set("Wavelength", value)


        @property
        def WavelengthUnit(self):
            return self.node.get("WavelengthUnit")
        @WavelengthUnit.setter
        def WavelengthUnit(self, value):
            self.node.set("WavelengthUnit", value)


        @property
        def FrequencyMultiplication(self):
            return self.node.get("FrequencyMultiplication")
        @FrequencyMultiplication.setter
        def FrequencyMultiplication(self, value):
            self.node.set("FrequencyMultiplication", value)


        @property
        def Tuneable(self):
            return self.node.get("Tuneable")
        @Tuneable.setter
        def Tuneable(self, value):
            self.node.set("Tuneable", value)


        @property
        def Pulse(self):
            return self.node.get("Pulse")
        @Pulse.setter
        def Pulse(self, value):
            self.node.set("Pulse", value)


        @property
        def PockelCell(self):
            return self.node.get("PockelCell")
        @PockelCell.setter
        def PockelCell(self, value):
            self.node.set("PockelCell", value)


        @property
        def RepetitionRate(self):
            return self.node.get("RepetitionRate")
        @RepetitionRate.setter
        def RepetitionRate(self, value):
            self.node.set("RepetitionRate", value)


        @property
        def RepetitionRateUnit(self):
            return self.node.get("RepetitionRateUnit")
        @RepetitionRateUnit.setter
        def RepetitionRateUnit(self, value):
            self.node.set("RepetitionRateUnit", value)


        @property
        def pump_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Pump")))
        @pump_count.setter
        def pump_count(self, pump):
        	assert pump >= 0
        	pump_count = self.pump_count
        	if pump_count > pump:
        		pumps = self.node.findall(qn(self.ns['ome'], "Pump"))
        		for pump in pumps[pump:]:
        			self.node.remove(pump)
        	else:
        		for _ in range(pump_count, pump):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Pump"))

        def Pump(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.pump_count == 0:
        		self.pump_count = 1
        	return OMEXML.Pump(
                self.node.findall(qn(self.ns['ome'], "Pump"))[index])


    class Pump():
        '''Pump'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class LightEmittingDiode():
        '''lightsource in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class GenericExcitationSource():
        '''lightsource in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def Power(self):
            return self.node.get("Power")
        @Power.setter
        def Power(self, value):
            self.node.set("Power", value)


        @property
        def PowerUnit(self):
            return self.node.get("PowerUnit")
        @PowerUnit.setter
        def PowerUnit(self, value):
            self.node.set("PowerUnit", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def map_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Map")))
        @map_count.setter
        def map_count(self, map):
        	assert map >= 0
        	map_count = self.map_count
        	if map_count > map:
        		maps = self.node.findall(qn(self.ns['ome'], "Map"))
        		for map in maps[map:]:
        			self.node.remove(map)
        	else:
        		for _ in range(map_count, map):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Map"))

        def Map(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.map_count == 0:
        		self.map_count = 1
        	return OMEXML.Map(
                self.node.findall(qn(self.ns['ome'], "Map"))[index])


    class Map():
        '''Map'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def K(self):
            return self.node.get("K")
        @K.setter
        def K(self, value):
            self.node.set("K", value)


    class Detector():
        '''Element Detector in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)



        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Type(self):
            return get_int_attr(self.node, "Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", str(value))


        @property
        def Gain(self):
            return self.node.get("Gain")
        @Gain.setter
        def Gain(self, value):
            self.node.set("Gain", value)


        @property
        def AmplificationGain(self):
            return self.node.get("AmplificationGain")
        @AmplificationGain.setter
        def AmplificationGain(self, value):
            self.node.set("AmplificationGain", value)


        @property
        def Voltage(self):
            self.node.get("Voltage")
        @Voltage.setter
        def Voltage(self, value):
            return self.node.set("Voltage", value)


        @property
        def VoltageUnit(self):
            self.node.get("VoltageUnit")
        @VoltageUnit.setter
        def VoltageUnit(self, value):
            self.node.set("VoltageUnit", value)

        @property
        def Offset(self):
            return self.node.get("Offset")
        @Offset.setter
        def Offset(self, value):
            self.node.set("Offset", value)


        @property
        def Zoom(self):
            return self.node.get("Zoom")
        @Zoom.setter
        def Zoom(self, value):
            self.node.set("Zoom", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class Objective():
        '''Element Objective in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def LensNA(self):
            return self.node.get("LensNA")
        @LensNA.setter
        def LensNA(self, value):
            self.node.set("LensNA", value)

        @property
        def Correction(self):
            return self.node.get("Correction")
        @Correction.setter
        def Correction(self, value):
            self.node.set("Correction", value)


        @property
        def NominalMagnification(self):
            return self.node.get("NominalMagnification")
        @NominalMagnification.setter
        def NominalMagnification(self, value):
            self.node.set("NominalMagnification", value)


        @property
        def WorkingDistance(self):
            return get_int_attr(self.node, "WorkingDistance")
        @WorkingDistance.setter
        def WorkingDistance(self, value):
            self.node.set("WorkingDistance", str(value))


        @property
        def WorkingDistanceUnit(self):
            return get_int_attr(self.node, "WorkingDistanceUnit")
        @WorkingDistanceUnit.setter
        def WorkingDistanceUnit(self, value):
            self.node.set("WorkingDistanceUnit", str(value))


        @property
        def Iris(self):
            return self.node.get("Iris")
        @Iris.setter
        def Iris(self, value):
            self.node.set("Iris", value)


        @property
        def Immersion(self):
            return self.node.get("Immersion")
        @Immersion.setter
        def Immersion(self, value):
            self.node.set("Immersion", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class Filter():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def FilterWheel(self):
            return self.node.get("FilterWheel")
        @FilterWheel.setter
        def FilterWheel(self, value):
            self.node.set("FilterWheel", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def transmittancerange_count(self):
            return len(
                self.node.findall(qn(self.ns['ome'], "TransmittanceRange")))
        @transmittancerange_count.setter
        def transmittancerange_count(self, value):
            assert value >= 0
            transmittancerange_count = self.transmittancerange_count
            if transmittancerange_count > value:
                transmittanceranges = self.node.findall(
                    qn(self.ns['ome'], "TransmittanceRange"))
                for transmittancerange in transmittanceranges[value:]:
                    self.node.remove(transmittancerange)
            else:
                for _ in range(transmittancerange_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "TransmittanceRange"))

        def TransmittanceRange(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.transmittancerange_count == 0:
                self.transmittancerange_count = 1
            return OMEXML.TransmittanceRange(self.node.findall(
                qn(self.ns['ome'], "TransmittanceRange"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class TransmittanceRange():
        '''TransmittanceRange in OMEXML/Filter'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def CutIn(self):
            return self.node.get("CutIn")
        @CutIn.setter
        def CutIn(self, value):
            self.node.set("CutIn", value)


        @property
        def CutInUnit(self):
            return self.node.get("CutInUnit")
        @CutInUnit.setter
        def CutInUnit(self, value):
            self.node.set("CutInUnit", value)


        @property
        def CutInTolerance(self):
            return self.node.get("CutInTolerance")
        @CutInTolerance.setter
        def CutInTolerance(self, value):
            self.node.set("CutInTolerance", value)


        @property
        def CutInToleranceUnit(self):
            return self.node.get("CutInToleranceUnit")
        @CutInToleranceUnit.setter
        def CutInToleranceUnit(self, value):
            self.node.set("CutInToleranceUnit", value)


        @property
        def CutOut(self):
            return self.node.get("CutOut")
        @CutOut.setter
        def CutOut(self, value):
            self.node.set("CutOut", value)


        @property
        def CutOutUnit(self):
            return self.node.get("CutOutUnit")
        @CutOutUnit.setter
        def CutOutUnit(self, value):
            self.node.set("CutOutUnit", value)


        @property
        def CutOutTolerance(self):
            return self.node.get("CutOutTolerance")
        @CutOutTolerance.setter
        def CutOutTolerance(self, value):
            self.node.set("CutOutTolerance", value)


        @property
        def CutOutToleranceUnit(self):
            return self.node.get("CutOutToleranceUnit")
        @CutOutToleranceUnit.setter
        def CutOutToleranceUnit(self, value):
            self.node.set("CutOutToleranceUnit", value)


        @property
        def Transmittance(self):
            return self.node.get("Transmittance")
        @Transmittance.setter
        def Transmittance(self, value):
            self.node.set("Transmittance", value)


    class FilterSet():
        '''FilterSet in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)



        @property
        def excitationfilterref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "ExcitationFilterRef")))
        @excitationfilterref_count.setter
        def excitationfilterref_count(self, value):
            assert value >= 0
            excitationfilterref_count = self.excitationfilterref_count
            if excitationfilterref_count > value:
                excitationfilterrefs = self.node.findall(
                    qn(self.ns['ome'], "ExcitationFilterRef"))
                for excitationfilterref in excitationfilterrefs[value:]:
                    self.node.remove(excitationfilterref)
            else:
                for _ in range(excitationfilterref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ExcitationFilterRef"))

        def ExcitationFilterRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.excitationfilterref_count == 0:
                self.excitationfilterref_count = 1
            return OMEXML.ExcitationFilterRef(self.node.findall(
                qn(self.ns['ome'], "ExcitationFilterRef"))[index])


        @property
        def dichroicref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "DichroicRef")))
        @dichroicref_count.setter
        def dichroicref_count(self, value):
            assert value >= 0
            dichroicref_count = self.dichroicref_count
            if dichroicref_count > value:
                dichroicrefs = self.node.findall(
                    qn(self.ns['ome'], "DichroicRef"))
                for dichroicref in dichroicrefs[value:]:
                    self.node.remove(dichroicref)
            else:
                for _ in range(dichroicref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "DichroicRef"))

        def DichroicRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.dichroicref_count == 0:
                self.dichroicref_count = 1
            return OMEXML.DichroicRef(self.node.findall(
                qn(self.ns['ome'], "DichroicRef"))[index])

        @property
        def emissionfilterref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "EmissionFilterRef")))
        @emissionfilterref_count.setter
        def emissionfilterref_count(self, value):
            assert value >= 0
            emissionfilterref_count = self.emissionfilterref_count
            if emissionfilterref_count > value:
                emissionfilterrefs = self.node.findall(
                    qn(self.ns['ome'], "EmissionFilterRef"))
                for emissionfilterref in emissionfilterrefs[value:]:
                    self.node.remove(emissionfilterref)
            else:
                for _ in range(emissionfilterref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "EmissionFilterRef"))

        def EmissionFilterRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.emissionfilterref_count == 0:
                self.emissionfilterref_count = 1
            return OMEXML.EmissionFilterRef(self.node.findall(
                qn(self.ns['ome'], "EmissionFilterRef"))[index])


    class EmissionFilterRef():
        '''EmissionFilterRef'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class DichroicRef():
        '''DichroicRef'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class ExcitationFilterRef():
        '''ExcitationFilterRef'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)



    class Dichroic():
        '''Dichroic in OME/Instrument'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Manufacturer(self):
            return self.node.get("Manufacturer")
        @Manufacturer.setter
        def Manufacturer(self, value):
            self.node.set("Manufacturer", value)


        @property
        def Model(self):
            return self.node.get("Model")
        @Model.setter
        def Model(self, value):
            self.node.set("Model", value)


        @property
        def SerialNumber(self):
            return self.node.get("SerialNumber")
        @SerialNumber.setter
        def SerialNumber(self, value):
            self.node.set("SerialNumber", value)


        @property
        def LotNumber(self):
            return self.node.get("LotNumber")
        @LotNumber.setter
        def LotNumber(self, value):
            self.node.set("LotNumber", value)


        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

    # above are elemeents for classes mainly for instrument



    # here starts the ome/image part
    class Image():
        '''Representation of the OME/Image element'''
        def __init__(self, node):
            '''Initialize with the DOM Image node'''
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")
        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def acquisitiondate_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AcquisitionDate")))
        @acquisitiondate_count.setter
        def acquisitiondate_count(self, value):
            assert value >= 0
            acquisitiondate_count = self.acquisitiondate_count
            if acquisitiondate_count > value:
                acquisitiondates = self.node.findall(
                    qn(self.ns['ome'], "AcquisitionDate"))
                for acquisitiondate in acquisitiondates[value:]:
                    self.node.remove(acquisitiondate)
            else:
                for _ in range(acquisitiondate_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AcquisitionDate"))

        def AcquisitionDate(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.acquisitiondate_count == 0:
                self.acquisitiondate_count = 1
            return OMEXML.AcquisitionDate(self.node.findall(
                qn(self.ns['ome'], "AcquisitionDate"))[index])

        @property
        def description_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Description")))
        @description_count.setter
        def description_count(self, value):
            assert value >= 0
            description_count = self.description_count
            if description_count > value:
                descriptions = self.node.findall(
                    qn(self.ns['ome'], "Description"))
                for description in descriptions[value:]:
                    self.node.remove(description)
            else:
                for _ in range(description_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Description"))

        def Description(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.description_count == 0:
                self.description_count = 1
            return OMEXML.Description(self.node.findall(
                qn(self.ns['ome'], "Description"))[index])

        @property
        def experimenterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterRef")))
        @experimenterref_count.setter
        def experimenterref_count(self, experimenterref):
        	assert experimenterref >= 0
        	experimenterref_count = self.experimenterref_count
        	if experimenterref_count > experimenterref:
        		experimenterrefs = self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))
        		for experimenterref in experimenterrefs[experimenterref:]:
        			self.node.remove(experimenterref)
        	else:
        		for _ in range(experimenterref_count, experimenterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterRef"))

        def ExperimenterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimenterref_count == 0:
        		self.experimenterref_count = 1
        	return OMEXML.ExperimenterRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterRef"))[index])

        @property
        def experimentref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimentRef")))
        @experimentref_count.setter
        def experimentref_count(self, experimentref):
        	assert experimentref >= 0
        	experimentref_count = self.experimentref_count
        	if experimentref_count > experimentref:
        		experimentrefs = self.node.findall(qn(self.ns['ome'], "ExperimentRef"))
        		for experimentref in experimentrefs[experimentref:]:
        			self.node.remove(experimentref)
        	else:
        		for _ in range(experimentref_count, experimentref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimentRef"))

        def ExperimentRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimentref_count == 0:
        		self.experimentref_count = 1
        	return OMEXML.ExperimentRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimentRef"))[index])

        @property
        def experimentergroupref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef")))
        @experimentergroupref_count.setter
        def experimentergroupref_count(self, experimentergroupref):
        	assert experimentergroupref >= 0
        	experimentergroupref_count = self.experimentergroupref_count
        	if experimentergroupref_count > experimentergroupref:
        		experimentergrouprefs = self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))
        		for experimentergroupref in experimentergrouprefs[experimentergroupref:]:
        			self.node.remove(experimentergroupref)
        	else:
        		for _ in range(experimentergroupref_count, experimentergroupref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExperimenterGroupRef"))

        def ExperimenterGroupRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.experimentergroupref_count == 0:
        		self.experimentergroupref_count = 1
        	return OMEXML.ExperimenterGroupRef(
        		self.node.findall(qn(self.ns['ome'], "ExperimenterGroupRef"))[index])

        @property
        def instrumentref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "InstrumentRef")))
        @instrumentref_count.setter
        def instrumentref_count(self, instrumentref):
        	assert instrumentref >= 0
        	instrumentref_count = self.instrumentref_count
        	if instrumentref_count > instrumentref:
        		instrumentrefs = self.node.findall(qn(self.ns['ome'], "InstrumentRef"))
        		for instrumentref in instrumentrefs[instrumentref:]:
        			self.node.remove(instrumentref)
        	else:
        		for _ in range(instrumentref_count, instrumentref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "InstrumentRef"))

        def InstrumentRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.instrumentref_count == 0:
        		self.instrumentref_count = 1
        	return OMEXML.InstrumentRef(
        		self.node.findall(qn(self.ns['ome'], "InstrumentRef"))[index])

        @property
        def roiref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ROIRef")))
        @roiref_count.setter
        def roiref_count(self, roiref):
        	assert roiref >= 0
        	roiref_count = self.roiref_count
        	if roiref_count > roiref:
        		roirefs = self.node.findall(qn(self.ns['ome'], "ROIRef"))
        		for roiref in roirefs[roiref:]:
        			self.node.remove(roiref)
        	else:
        		for _ in range(roiref_count, roiref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ROIRef"))

        def ROIRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.roiref_count == 0:
        		self.roiref_count = 1
        	return OMEXML.ROIRef(
        		self.node.findall(qn(self.ns['ome'], "ROIRef"))[index])

        @property
        def microbeammanipulationref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "MicrobeamManipulationRef")))
        @microbeammanipulationref_count.setter
        def microbeammanipulationref_count(self, microbeammanipulationref):
        	assert microbeammanipulationref >= 0
        	microbeammanipulationref_count = self.microbeammanipulationref_count
        	if microbeammanipulationref_count > microbeammanipulationref:
        		microbeammanipulationrefs = self.node.findall(qn(self.ns['ome'], "MicrobeamManipulationRef"))
        		for microbeammanipulationref in microbeammanipulationrefs[microbeammanipulationref:]:
        			self.node.remove(microbeammanipulationref)
        	else:
        		for _ in range(microbeammanipulationref_count, microbeammanipulationref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "MicrobeamManipulationRef"))

        def MicrobeamManipulationRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.microbeammanipulationref_count == 0:
        		self.microbeammanipulationref_count = 1
        	return OMEXML.MicrobeamManipulationRef(
        		self.node.findall(qn(self.ns['ome'], "MicrobeamManipulationRef"))[index])


        @property
        def objectivesettings_count(self):
            '''The number of objectivesettingss in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "ObjectiveSettings")))

        @objectivesettings_count.setter
        def objectivesettings_count(self, value):
            assert value >= 0
            objectivesettings_count=self.objectivesettings_count
            if objectivesettings_count > value:
                objectivesettingss=self.node.findall(
                    qn(self.ns['ome'], "ObjectiveSettings"))
                for objectivesettings in objectivesettingss[value:]:
                    self.node.remove(objectivesettings)
            else:
                for _ in range(objectivesettings_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "ObjectiveSettings"))


        def ObjectiveSettings(self, index=0):
            '''Get the indexed ObjectiveSettings from Instrument element'''
            objectivesettings=self.node.find(
                qn(self.ns['ome'], "ObjectiveSettings"))
            if objectivesettings is None:
                self.objectivesettings_count = 1
            return OMEXML.ObjectiveSettings(self.node.findall(
                qn(self.ns['ome'], "ObjectiveSettings"))[index])

        @property
        def imagingenvironment_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ImagingEnvironment")))
        @imagingenvironment_count.setter
        def imagingenvironment_count(self, imagingenvironment):
        	assert imagingenvironment >= 0
        	imagingenvironment_count = self.imagingenvironment_count
        	if imagingenvironment_count > imagingenvironment:
        		imagingenvironments = self.node.findall(qn(self.ns['ome'], "ImagingEnvironment"))
        		for imagingenvironment in imagingenvironments[imagingenvironment:]:
        			self.node.remove(imagingenvironment)
        	else:
        		for _ in range(imagingenvironment_count, imagingenvironment):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ImagingEnvironment"))

        def ImagingEnvironment(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.imagingenvironment_count == 0:
        		self.imagingenvironment_count = 1
        	return OMEXML.ImagingEnvironment(
        		self.node.findall(qn(self.ns['ome'], "ImagingEnvironment"))[index])

        @property
        def stagelabel_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "StageLabel")))
        @stagelabel_count.setter
        def stagelabel_count(self, stagelabel):
        	assert stagelabel >= 0
        	stagelabel_count = self.stagelabel_count
        	if stagelabel_count > stagelabel:
        		stagelabels = self.node.findall(qn(self.ns['ome'], "StageLabel"))
        		for stagelabel in stagelabels[stagelabel:]:
        			self.node.remove(stagelabel)
        	else:
        		for _ in range(stagelabel_count, stagelabel):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "StageLabel"))

        def StageLabel(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.stagelabel_count == 0:
        		self.stagelabel_count = 1
        	return OMEXML.StageLabel(
        		self.node.findall(qn(self.ns['ome'], "StageLabel"))[index])

        @property
        def pixels_count(self):
            '''The number of pixels in the instrument'''
            return len(self.node.findall(qn(self.ns['ome'], "Pixels")))

        @pixels_count.setter
        def pixels_count(self, value):
            assert value >= 0
            pixels_count=self.pixels_count
            if pixels_count > value:
                pixelss=self.node.findall(
                    qn(self.ns['ome'], "Pixels"))
                for pixels in pixelss[value:]:
                    self.node.remove(pixels)
            else:
                for _ in range(pixels_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Pixels"))


        def Pixels(self, index=0):
            '''Get the indexed Pixels from Instrument element'''
            pixels=self.node.find(qn(self.ns['ome'], "Pixels"))
            if pixels is None:
                self.pixels_count = 1
            return OMEXML.Pixels(
                self.node.findall(qn(self.ns['ome'], "Pixels"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class ExperimentRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)



    class ExperimenterRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))


    class ExperimenterGroupRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))


    class InstrumentRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class ROIRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class MicrobeamManipulationRef():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))


    class ObjectiveSettings():
        '''ObjectiveSettings in OME/Image'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def CorrectionCollar(self):
            return self.node.get("CorrectionCollar")
        @CorrectionCollar.setter
        def CorrectionCollar(self, value):
            self.node.set("CorrectionCollar", value)


        @property
        def Medium(self):
            return self.node.get("Medium")
        @Medium.setter
        def Medium(self, value):
            self.node.set("Medium", value)


        @property
        def RefractiveIndex(self):
            return self.node.get("RefractiveIndex")
        @RefractiveIndex.setter
        def RefractiveIndex(self, value):
            self.node.set("RefractiveIndex", value)


    class ImagingEnvironment():
        '''Initialize with the OME/Image/ImagingEnvironment'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Temperature(self):
            return self.node.get("Temperature")
        @Temperature.setter
        def Temperature(self, value):
            self.node.set("Temperature", value)


        @property
        def TemperatureUnit(self):
            return self.node.get("TemperatureUnit")
        @TemperatureUnit.setter
        def TemperatureUnit(self, value):
            self.node.set("TemperatureUnit", value)


        @property
        def AirPressure(self):
            return self.node.get("AirPressure")
        @AirPressure.setter
        def AirPressure(self, value):
            self.node.set("AirPressure", value)


        @property
        def AirPressureUnit(self):
            return self.node.get("AirPressureUnit")
        @AirPressureUnit.setter
        def AirPressureUnit(self, value):
            self.node.set("AirPressureUnit", value)


        @property
        def Humidity(self):
            return self.node.get("Humidity")
        @Humidity.setter
        def Humidity(self, value):
            self.node.set("Humidity", value)


        @property
        def CO2Percent(self):
            return self.node.get("CO2Percent")
        @CO2Percent.setter
        def CO2Percent(self, value):
            self.node.set("CO2Percent", value)


        @property
        def map_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "Map")))
        @map_count.setter
        def map_count(self, map):
        	assert map >= 0
        	map_count = self.map_count
        	if map_count > map:
        		maps = self.node.findall(qn(self.ns['ome'], "Map"))
        		for map in maps[map:]:
        			self.node.remove(map)
        	else:
        		for _ in range(map_count, map):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Map"))

        def Map(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.map_count == 0:
        		self.map_count = 1
        	return OMEXML.Map(
                self.node.findall(qn(self.ns['ome'], "Map"))[index])


    class StageLabel():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Name(self):
            return self.node.get("Name")
        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def X(self):
            return self.node.get("X")
        @X.setter
        def X(self, value):
            self.node.set("X", value)


        @property
        def XUnit(self):
            return self.node.get("XUnit")
        @XUnit.setter
        def XUnit(self, value):
            self.node.set("XUnit", value)


        @property
        def YUnit(self):
            return self.node.get("YUnit")
        @YUnit.setter
        def YUnit(self, value):
            self.node.set("YUnit", value)


        @property
        def Y(self):
            return self.node.get("Y")
        @Y.setter
        def Y(self, value):
            self.node.set("Y", value)


        @property
        def Z(self):
            return self.node.get("Z")
        @Z.setter
        def Z(self, value):
            self.node.set("Z", value)


        @property
        def ZUnit(self):
            return self.node.get("ZUnit")
        @ZUnit.setter
        def ZUnit(self, value):
            self.node.set("ZUnit", value)


    class Pixels():
        '''The OME/Image/Pixels element
        The Pixels element represents the pixels in an OME image and, for
        an OME-XML encoded image, will actually contain the base-64 encoded
        pixel data. It has the X, Y, Z, C, and T extents of the image
        and it specifies the channel interleaving and channel depth.
        '''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def DimensionOrder(self):
            '''The ordering of image planes in the file
            A 5-letter code indicating the ordering of pixels, from the most
            rapidly varying to least. Use the DO_* constants (for instance
            DO_XYZCT) to compare and set this.
            '''
            return self.node.get("DimensionOrder")
        @DimensionOrder.setter
        def DimensionOrder(self, value):
            self.node.set("DimensionOrder", value)


        @property
        def Type(self):
            return self.node.get("Type")
        @Type.setter
        def Type(self, value):
            self.node.set("Type", value)

        @property
        def SignificantBits(self):
            return self.node.get("SignificantBits")
        @SignificantBits.setter
        def SignificantBits(self, value):
            self.node.set("SignificantBits", value)


        @property
        def Interleaved(self):
            return self.node.get("Interleaved")
        @Interleaved.setter
        def Interleaved(self, value):
            self.node.set("Interleaved", value)


        @property
        def BigEndian(self):
            return self.node.get("BigEndian")
        @BigEndian.setter
        def BigEndian(self, value):
            self.node.set("BigEndian", value)


        @property
        def SizeX(self):
            '''The dimensions of the image in the X direction in pixels'''
            return get_int_attr(self.node, "SizeX")
        @SizeX.setter
        def SizeX(self, value):
            self.node.set("SizeX", str(value))


        @property
        def SizeY(self):
            '''The dimensions of the image in the Y direction in pixels'''
            return get_int_attr(self.node, "SizeY")
        @SizeY.setter
        def SizeY(self, value):
            self.node.set("SizeY", str(value))


        @property
        def SizeZ(self):
            '''The dimensions of the image in the Z direction in pixels'''
            return get_int_attr(self.node, "SizeZ")

        @SizeZ.setter
        def SizeZ(self, value):
            self.node.set("SizeZ", str(value))


        @property
        def SizeT(self):
            '''The dimensions of the image in the T direction in pixels'''
            return get_int_attr(self.node, "SizeT")

        @SizeT.setter
        def SizeT(self, value):
            self.node.set("SizeT", str(value))


        @property
        def SizeC(self):
            '''The dimensions of the image in the C direction in pixels'''
            return get_int_attr(self.node, "SizeC")
        @SizeC.setter
        def SizeC(self, value):
            self.node.set("SizeC", str(value))


        @property
        def PhysicalSizeXUnit(self):
            '''The unit of length of a pixel in X direction.'''
            return self.node.get("PhysicalSizeXUnit")
        @PhysicalSizeXUnit.setter
        def PhysicalSizeXUnit(self, value):
            self.node.set("PhysicalSizeXUnit", str(value))

        @property
        def PhysicalSizeYUnit(self):
            '''The unit of length of a pixel in Y direction.'''
            return self.node.get("PhysicalSizeYUnit")
        @PhysicalSizeYUnit.setter
        def PhysicalSizeYUnit(self, value):
            self.node.set("PhysicalSizeYUnit", str(value))


        @property
        def PhysicalSizeZUnit(self):
            '''The unit of length of a voxel in Z direction.'''
            return self.node.get("PhysicalSizeZUnit")
        @PhysicalSizeZUnit.setter
        def PhysicalSizeZUnit(self, value):
            self.node.set("PhysicalSizeZUnit", str(value))


        @property
        def PhysicalSizeX(self):
            '''The length of a single pixel in X direction.'''
            return get_float_attr(self.node, "PhysicalSizeX")
        @PhysicalSizeX.setter
        def PhysicalSizeX(self, value):
            self.node.set("PhysicalSizeX", str(value))


        @property
        def PhysicalSizeY(self):
            '''The length of a single pixel in Y direction.'''
            return get_float_attr(self.node, "PhysicalSizeY")
        @PhysicalSizeY.setter
        def PhysicalSizeY(self, value):
            self.node.set("PhysicalSizeY", str(value))


        @property
        def PhysicalSizeZ(self):
            return get_float_attr(self.node, "PhysicalSizeZ")
        @PhysicalSizeZ.setter
        def PhysicalSizeZ(self, value):
            self.node.set("PhysicalSizeZ", str(value))


        @property
        def TimeIncrement(self):
            '''The size of a voxel in Z direction or None for 2D images.'''
            return get_float_attr(self.node, "TimeIncrement")
        @TimeIncrement.setter
        def TimeIncrement(self, value):
            self.node.set("TimeIncrement", str(value))


        @property
        def TimeIncrementUnit(self):
            '''The unit of length of a voxel in Z direction.'''
            return self.node.get("TimeIncrementUnit")
        @TimeIncrementUnit.setter
        def TimeIncrementUnit(self, value):
            self.node.set("TimeIncrementUnit", str(value))


        @property
        def channel_count(self):
            '''The number of channels in the image
            You can change the number of channels in the image by
            setting the channel_count:
            pixels.channel_count = 3
            pixels.Channel(0).Name = "Red"
            ...
            '''
            return len(self.node.findall(qn(self.ns['ome'], "Channel")))

        @channel_count.setter
        def channel_count(self, value):
            assert value > 0
            channel_count=self.channel_count
            if channel_count > value:
                channels=self.node.findall(qn(self.ns['ome'], "Channel"))
                for channel in channels[value:]:
                    self.node.remove(channel)
            else:
                for _ in range(channel_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Channel"))


        def Channel(self, index=0):
            '''Get the indexed channel from the Pixels element'''
            channel=self.node.findall(qn(self.ns['ome'], "Channel"))
            if self.channel_count == 0:
                self.channel_count = 1
            return OMEXML.Channel(
                self.node.findall(qn(self.ns['ome'], "Channel"))[index])

        @property
        def plane_count(self):
            '''The number of planes in the image
            An image with only one plane or an interleaved color plane will
            often not have any planes.
            You can change the number of planes in the image by
            setting the plane_count:
            pixels.plane_count = 3
            pixels.Plane(0).TheZ=pixels.Plane(0).TheC=pixels.Plane(0).TheT=0
            ...
            '''
            return len(self.node.findall(qn(self.ns['ome'], "Plane")))

        @plane_count.setter
        def plane_count(self, value):
            assert value >= 0
            plane_count=self.plane_count
            if plane_count > value:
                planes=self.node.findall(qn(self.ns['ome'], "Plane"))
                for plane in planes[value:]:
                    self.node.remove(plane)
            else:
                for _ in range(plane_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "Plane"))


        def Plane(self, index=0):
            '''Get the indexed plane from the Pixels element'''
            if self.plane_count == 0:
                self.plane_count = 1
            plane=self.node.findall(qn(self.ns['ome'], "Plane"))[index]
            return OMEXML.Plane(plane)

        @property
        def bindata_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "BinData")))
        @bindata_count.setter
        def bindata_count(self, value):
            assert value >= 0
            bindata_count=self.bindata_count
            if bindata_count > value:
                bindatas=self.node.findall(qn(self.ns['ome'], "BinData"))
                for bindata in bindatas[value:]:
                    self.node.remove(bindata)
            else:
                for _ in range(bindata_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "BinData"))

        def BinData(self, index=0):
            '''Get the indexed bindata from the Pixels element'''
            if self.bindata_count == 0:
                self.bindata_count = 1
            bindata=self.node.findall(qn(self.ns['ome'], "BinData"))[index]
            return OMEXML.BinData(bindata)

        @property
        def tiffdata_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "TiffData")))
        @tiffdata_count.setter
        def tiffdata_count(self, value):
            assert value >= 0
            tiffdata_count=self.tiffdata_count
            if tiffdata_count > value:
                tiffdatas=self.node.findall(qn(self.ns['ome'], "TiffData"))
                for tiffdata in tiffdatas[value:]:
                    self.node.remove(tiffdata)
            else:
                for _ in range(tiffdata_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "TiffData"))


        def TiffData(self, index=0):
            '''Get the indexed tiffdata from the Pixels element'''
            if self.tiffdata_count == 0:
                self.tiffdata_count = 1
            tiffdata=self.node.findall(qn(self.ns['ome'], "TiffData"))[index]
            return OMEXML.TiffData(tiffdata)


        @property
        def metadataonly_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "MetadataOnly")))
        @metadataonly_count.setter
        def metadataonly_count(self, metadataonly):
        	assert metadataonly >= 0
        	metadataonly_count = self.metadataonly_count
        	if metadataonly_count > metadataonly:
        		metadataonlys = self.node.findall(qn(self.ns['ome'], "MetadataOnly"))
        		for metadataonly in metadataonlys[metadataonly:]:
        			self.node.remove(metadataonly)
        	else:
        		for _ in range(metadataonly_count, metadataonly):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "MetadataOnly"))

        def MetadataOnly(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.metadataonly_count == 0:
        		self.metadataonly_count = 1
        	return OMEXML.MetadataOnly(
        		self.node.findall(qn(self.ns['ome'], "MetadataOnly"))[index])


    class TiffData():
        '''TiffData in OME/Image/Pixels'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def IFD(self):
            return self.node.get("IFD")
        @IFD.setter
        def IFD(self, value):
            self.node.set("IFD", value)


        @property
        def FirstZ(self):
            return self.node.get("FirstZ")
        @FirstZ.setter
        def FirstZ(self, value):
            self.node.set("FirstZ", value)


        @property
        def FirstT(self):
            return self.node.get("FirstT")
        @FirstT.setter
        def FirstT(self, value):
            self.node.set("FirstT", value)


        @property
        def FirstC(self):
            return self.node.get("FirstC")
        @FirstC.setter
        def FirstC(self, value):
            self.node.set("FirstC", value)


        @property
        def PlaneCount(self):
            return self.node.get("PlaneCount")
        @PlaneCount.setter
        def PlaneCount(self, value):
            self.node.set("PlaneCount", value)


        @property
        def uuid_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "UUID")))
        @uuid_count.setter
        def uuid_count(self, uuid):
        	assert uuid >= 0
        	uuid_count = self.uuid_count
        	if uuid_count > uuid:
        		uuids = self.node.findall(qn(self.ns['ome'], "UUID"))
        		for uuid in uuids[uuid:]:
        			self.node.remove(uuid)
        	else:
        		for _ in range(uuid_count, uuid):
        			ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "UUID"))

        def UUID(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.uuid_count == 0:
        		self.uuid_count = 1
        	return OMEXML.UUID_spec(
                self.node.findall(qn(self.ns['ome'], "UUID"))[index])


    class UUID_spec():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)
        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def FileName(self):
            return self.node.get("FileName")
        @FileName.setter
        def FileName(self, value):
            self.node.set("FileName", value)


    class BinData():
        '''BinData in OME/Image/Pixels'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def Compression(self):
            return self.node.get("Compression")
        @Compression.setter
        def Compression(self, value):
            self.node.set("Compression", value)


        @property
        def BigEndian(self):
            return self.node.get("BigEndian")
        @BigEndian.setter
        def BigEndian(self, value):
            self.node.set("BigEndian", value)


        @property
        def Length(self):
            return self.node.get("Length")
        @Length.setter
        def Length(self, value):
            self.node.set("Length", value)


    class Channel():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Name(self):
            return self.node.get("Name")
        @Name.setter
        def Name(self, value):
            self.node.set("Name", value)


        @property
        def SamplesPerPixel(self):
            return self.node.get("SamplesPerPixel")
        @SamplesPerPixel.setter
        def SamplesPerPixel(self, value):
            self.node.set("SamplesPerPixel", value)


        @property
        def IlluminationType(self):
            return self.node.get("IlluminationType")
        @IlluminationType.setter
        def IlluminationType(self, value):
            self.node.set("IlluminationType", value)


        @property
        def PinholeSize(self):
            return self.node.get("PinholeSize")
        @PinholeSize.setter
        def PinholeSize(self, value):
            self.node.set("PinholeSize", value)


        @property
        def PinholeSizeUnit(self):
            return self.node.get("PinholeSizeUnit")
        @PinholeSizeUnit.setter
        def PinholeSizeUnit(self, value):
            self.node.set("PinholeSizeUnit", value)


        @property
        def AcquisitionMode(self):
            return self.node.get("AcquisitionMode")
        @AcquisitionMode.setter
        def AcquisitionMode(self, value):
            self.node.set("AcquisitionMode", value)


        @property
        def ContrastMode(self):
            return self.node.get("ContrastMode")
        @ContrastMode.setter
        def ContrastMode(self, value):
            self.node.set("ContrastMode", value)


        @property
        def ExcitationWavelength(self):
            return self.node.get("ExcitationWavelength")
        @ExcitationWavelength.setter
        def ExcitationWavelength(self, value):
            self.node.set("ExcitationWavelength", value)


        @property
        def ExcitationWavelengthUnit(self):
            return self.node.get("ExcitationWavelengthUnit")
        @ExcitationWavelengthUnit.setter
        def ExcitationWavelengthUnit(self, value):
            self.node.set("ExcitationWavelengthUnit", value)


        @property
        def EmissionWavelengthUnit(self):
            return self.node.get("EmissionWavelengthUnit")
        @EmissionWavelengthUnit.setter
        def EmissionWavelengthUnit(self, value):
            self.node.set("EmissionWavelengthUnit", value)


        @property
        def EmissionWavelength(self):
            return self.node.get("EmissionWavelength")
        @EmissionWavelength.setter
        def EmissionWavelength(self, value):
            self.node.set("EmissionWavelength", value)


        @property
        def Fluor(self):
            return self.node.get("Fluor")
        @Fluor.setter
        def Fluor(self, value):
            self.node.set("Fluor", value)


        @property
        def NDFilter(self):
            return self.node.get("NDFilter")
        @NDFilter.setter
        def NDFilter(self, value):
            self.node.set("NDFilter", value)


        @property
        def PockelCellSettings(self):
            return self.node.get("PockelCellSettings")
        @PockelCellSettings.setter
        def PockelCellSettings(self, value):
            self.node.set("PockelCellSettings", value)


        @property
        def Color(self):
            return self.node.get("Color")
        @Color.setter
        def Color(self, value):
            self.node.set("Color", value)


        @property
        def lightsourcesettings_count(self):
            return len(self.node.findall(
                qn(self.ns['ome'], "LightSourceSettings")))

        @lightsourcesettings_count.setter
        def lightsourcesettings_count(self, value):
            assert value > 0
            lightsourcesettings_count=self.lightsourcesettings_count
            if lightsourcesettings_count > value:
                lightsourcesettings=self.node.findall(
                    qn(self.ns['ome'], "LightSourceSettings"))
                for lightsourcesettings in lightsourcesettings[value:]:
                    self.node.remove(lightsourcesettings)
            else:
                for _ in range(lightsourcesettings_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LightSourceSettings"))


        def LightSourceSettings(self, index=0):
            '''Get the indexed lightsourcesettings from the Pixels element'''
            if self.lightsourcesettings_count == 0:
                self.lightsourcesettings_count = 1
            return OMEXML.LightSourceSettings(self.node.findall(
                qn(self.ns['ome'], "LightSourceSettings"))[index])


        @property
        def detectorsettings_count(self):
            return len(self.node.findall(
                qn(self.ns['ome'], "DetectorSettings")))
        @detectorsettings_count.setter
        def detectorsettings_count(self, value):
            assert value > 0
            detectorsettings_count=self.detectorsettings_count
            if detectorsettings_count > value:
                detectorsettings=self.node.findall(
                    qn(self.ns['ome'], "DetectorSettings"))
                for detectorsetting in detectorsettings[value:]:
                    self.node.remove(detectorsetting)
            else:
                for _ in range(detectorsettings_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "DetectorSettings"))


        def DetectorSettings(self, index=0):
            '''Get the indexed detectorsettings from the Pixels element'''
            detectorsettings=self.node.find(
                qn(self.ns['ome'], "DetectorSettings"))
            if self.detectorsettings_count == 0:
                self.detectorsettings_count = 1

            return OMEXML.DetectorSettings(self.node.findall(
                qn(self.ns['ome'], "DetectorSettings"))[index])


        @property
        def lightpath_count(self):
            return len(self.node.findall(
                qn(self.ns['ome'], "LightPath")))
        @lightpath_count.setter
        def lightpath_count(self, value):
            assert value > 0
            lightpath_count=self.lightpath_count
            if lightpath_count > value:
                lightpaths=self.node.findall(
                    qn(self.ns['ome'], "LightPath"))
                for lightpath in lightpaths[value:]:
                    self.node.remove(lightpath)
            else:
                for _ in range(lightpath_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "LightPath"))


        def LightPath(self, index=0):
            if self.lightpath_count == 0:
                self.lightpath_count = 1
            return OMEXML.LightPath(
                self.node.findall(qn(self.ns['ome'], "LightPath"))[index])

        @property
        def filtersetref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "FilterSetRef")))
        @filtersetref_count.setter
        def filtersetref_count(self, filtersetref):
        	assert filtersetref >= 0
        	filtersetref_count = self.filtersetref_count
        	if filtersetref_count > filtersetref:
        		filtersetrefs = self.node.findall(qn(self.ns['ome'], "FilterSetRef"))
        		for filtersetref in filtersetrefs[filtersetref:]:
        			self.node.remove(filtersetref)
        	else:
        		for _ in range(filtersetref_count, filtersetref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "FilterSetRef"))

        def FilterSetRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.filtersetref_count == 0:
        		self.filtersetref_count = 1
        	return OMEXML.FilterSetRef(
        		self.node.findall(qn(self.ns['ome'], "FilterSetRef"))[index])


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class LightSourceSettings():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Attenuation(self):
            return self.node.get("Attenuation")
        @Attenuation.setter
        def Attenuation(self, value):
            self.node.set("Attenuation", value)


        @property
        def Wavelength(self):
            return self.node.get("Wavelength")
        @Wavelength.setter
        def Wavelength(self, value):
            self.node.set("Wavelength", value)


        @property
        def WavelengthUnit(self):
            return self.node.get("WavelengthUnit")
        @WavelengthUnit.setter
        def WavelengthUnit(self, value):
            self.node.set("WavelengthUnit", value)



    class FilterSetRef():
        '''FilterSetRef in OME/Image/Channel'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)



    class LightPath():
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def excitationfilterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "ExcitationFilterRef")))
        @excitationfilterref_count.setter
        def excitationfilterref_count(self, excitationfilterref):
        	assert excitationfilterref >= 0
        	excitationfilterref_count = self.excitationfilterref_count
        	if excitationfilterref_count > excitationfilterref:
        		excitationfilterrefs = self.node.findall(qn(self.ns['ome'], "ExcitationFilterRef"))
        		for excitationfilterref in excitationfilterrefs[excitationfilterref:]:
        			self.node.remove(excitationfilterref)
        	else:
        		for _ in range(excitationfilterref_count, excitationfilterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "ExcitationFilterRef"))

        def ExcitationFilterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.excitationfilterref_count == 0:
        		self.excitationfilterref_count = 1
        	return OMEXML.ExcitationFilterRef(
        		self.node.findall(qn(self.ns['ome'], "ExcitationFilterRef"))[index])

        @property
        def emissionfilterref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "EmissionFilterRef")))
        @emissionfilterref_count.setter
        def emissionfilterref_count(self, emissionfilterref):
        	assert emissionfilterref >= 0
        	emissionfilterref_count = self.emissionfilterref_count
        	if emissionfilterref_count > emissionfilterref:
        		emissionfilterrefs = self.node.findall(qn(self.ns['ome'], "EmissionFilterRef"))
        		for emissionfilterref in emissionfilterrefs[emissionfilterref:]:
        			self.node.remove(emissionfilterref)
        	else:
        		for _ in range(emissionfilterref_count, emissionfilterref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "EmissionFilterRef"))

        def EmissionFilterRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.emissionfilterref_count == 0:
        		self.emissionfilterref_count = 1
        	return OMEXML.EmissionFilterRef(
        		self.node.findall(qn(self.ns['ome'], "EmissionFilterRef"))[index])

        @property
        def dichroicref_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "DichroicRef")))
        @dichroicref_count.setter
        def dichroicref_count(self, dichroicref):
        	assert dichroicref >= 0
        	dichroicref_count = self.dichroicref_count
        	if dichroicref_count > dichroicref:
        		dichroicrefs = self.node.findall(qn(self.ns['ome'], "DichroicRef"))
        		for dichroicref in dichroicrefs[dichroicref:]:
        			self.node.remove(dichroicref)
        	else:
        		for _ in range(dichroicref_count, dichroicref):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "DichroicRef"))

        def DichroicRef(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.dichroicref_count == 0:
        		self.dichroicref_count = 1
        	return OMEXML.DichroicRef(
        		self.node.findall(qn(self.ns['ome'], "DichroicRef"))[index])

        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])


    class DetectorSettings():
        '''For DetectorRef in Image/LogicalChannel'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


        @property
        def Gain(self):
            return self.node.get("Gain")
        @Gain.setter
        def Gain(self, value):
            self.node.set("Gain", value)


        @property
        def Offset(self):
            return self.node.get("Offset")
        @Offset.setter
        def Offset(self, value):
            self.node.set("Offset", value)


        @property
        def Zoom(self):
            return self.node.get("Zoom")
        @Zoom.setter
        def Zoom(self, value):
            self.node.set("Zoom", value)


        @property
        def Binning(self):
            return self.node.get("Binning")
        @Binning.setter
        def Binning(self, value):
            self.node.set("Binning", value)

        @property
        def Integration(self):
            return self.node.get("Integration")
        @Integration.setter
        def Integration(self, value):
            self.node.set("Integration", value)


        @property
        def ReadOutRate(self):
            return self.node.get("ReadOutRate")
        @ReadOutRate.setter
        def ReadOutRate(self, value):
            self.node.set("ReadOutRate", value)


        @property
        def ReadOutRateUnit(self):
            return self.node.get("ReadOutRateUnit")
        @ReadOutRateUnit.setter
        def ReadOutRateUnit(self, value):
            self.node.set("ReadOutRateUnit", value)


        @property
        def Voltage(self):
            return self.node.get("Voltage")
        @Voltage.setter
        def Voltage(self, value):
            self.node.set("Voltage", value)


        @property
        def VoltageUnit(self):
            return self.node.get("VoltageUnit")
        @VoltageUnit.setter
        def VoltageUnit(self, value):
            self.node.set("VoltageUnit", value)


    class Plane(object):
        '''The OME/Image/Pixels/Plane element
        The Plane element represents one 2-dimensional image plane. It
        has the Z, C and T indices of the plane and optionally has the
        X, Y, Z, exposure time and a relative time delta.
        '''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def TheZ(self):
            '''The Z index of the plane'''
            return get_int_attr(self.node, "TheZ")

        @TheZ.setter
        def TheZ(self, value):
            self.node.set("TheZ", str(value))


        @property
        def TheC(self):
            '''The channel index of the plane'''
            return get_int_attr(self.node, "TheC")

        @TheC.setter
        def TheC(self, value):
            self.node.set("TheC", str(value))


        @property
        def TheT(self):
            '''The T index of the plane'''
            return get_int_attr(self.node, "TheT")

        @TheT.setter
        def TheT(self, value):
            self.node.set("TheT", str(value))


        @property
        def DeltaT(self):
            '''# of seconds since the beginning of the experiment'''
            return get_float_attr(self.node, "DeltaT")

        @DeltaT.setter
        def DeltaT(self, value):
            self.node.set("DeltaT", str(value))


        @property
        def ExposureTime(self):
            '''Units are seconds. Duration of acquisition????'''
            exposure_time=self.node.get("ExposureTime")
            if exposure_time is not None:
                return float(exposure_time)
            return None
        @ExposureTime.setter
        def ExposureTime(self, value):
            '''Units are seconds. Duration of acquisition????'''
            self.node.set("ExposureTime", value)

        @property
        def ExposureTimeUnit(self):
            '''The T index of the plane'''
            return get_int_attr(self.node, "ExposureTimeUnit")
        @ExposureTimeUnit.setter
        def ExposureTimeUnit(self, value):
            self.node.set("ExposureTimeUnit", str(value))

        @property
        def PositionXUnit(self):
            '''X position of stage'''
            position_x=self.node.get("PositionXUnit")
            if position_x is not None:
                return float(position_x)
            return None
        @PositionXUnit.setter
        def PositionXUnit(self, value):
            self.node.set("PositionXUnit", str(value))

        @property
        def PositionX(self):
            '''X position of stage'''
            position_x=self.node.get("PositionX")
            if position_x is not None:
                return float(position_x)
            return None
        @PositionX.setter
        def PositionX(self, value):
            self.node.set("PositionX", str(value))

        @property
        def PositionY(self):
            '''Y position of stage'''
            return get_float_attr(self.node, "PositionY")

        @PositionY.setter
        def PositionY(self, value):
            self.node.set("PositionY", str(value))

        @property
        def PositionYUnit(self):
            '''Y position of stage'''
            return get_float_attr(self.node, "PositionYUnit")

        @PositionYUnit.setter
        def PositionYUnit(self, value):
            self.node.set("PositionYUnit", str(value))


        @property
        def PositionZ(self):
            '''Z position of stage'''
            return get_float_attr(self.node, "PositionZ")

        @PositionZ.setter
        def PositionZ(self, value):
            self.node.set("PositionZ", str(value))


        @property
        def PositionZUnit(self):
            '''Z position of stage'''
            return get_float_attr(self.node, "PositionZUnit")

        @PositionZUnit.setter
        def PositionZUnit(self, value):
            self.node.set("PositionZUnit", str(value))


        @property
        def annotationref_count(self):
            return len(self.node.findall(qn(self.ns['ome'], "AnnotationRef")))
        @annotationref_count.setter
        def annotationref_count(self, value):
            assert value >= 0
            annotationref_count = self.annotationref_count
            if annotationref_count > value:
                annotationrefs = self.node.findall(
                    qn(self.ns['ome'], "AnnotationRef"))
                for annotationref in annotationrefs[value:]:
                    self.node.remove(annotationref)
            else:
                for _ in range(annotationref_count, value):
                    ElementTree.SubElement(
                        self.node, qn(self.ns['ome'], "AnnotationRef"))

        def AnnotationRef(self, index=0):
            '''Get the indexed microscope from Instrument element'''
            if self.annotationref_count == 0:
                self.annotationref_count = 1
            return OMEXML.AnnotationRef(self.node.findall(
                qn(self.ns['ome'], "AnnotationRef"))[index])

        @property
        def hashsha1_count(self):
        	return len(self.node.findall(qn(self.ns['ome'], "HashSHA1")))
        @hashsha1_count.setter
        def hashsha1_count(self, hashsha1):
        	assert hashsha1 >= 0
        	hashsha1_count = self.hashsha1_count
        	if hashsha1_count > hashsha1:
        		hashsha1s = self.node.findall(qn(self.ns['ome'], "HashSHA1"))
        		for hashsha1 in hashsha1s[hashsha1:]:
        			self.node.remove(hashsha1)
        	else:
        		for _ in range(hashsha1_count, hashsha1):
        			ElementTree.SubElement(
        				self.node, qn(self.ns['ome'], "HashSHA1"))

        def HashSHA1(self, index=0):
        	'''Get the indexed microscope from Instrument element'''
        	if self.hashsha1_count == 0:
        		self.hashsha1_count = 1
        	return OMEXML.HashSHA1(
        		self.node.findall(qn(self.ns['ome'], "HashSHA1"))[index])

# here is the end of OME/Image

    class AnnotationRef():
        '''AnnotationRef'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

        @property
        def ID(self):
            return self.node.get("ID")
        @ID.setter
        def ID(self, value):
            self.node.set("ID", value)


    class Description():
        '''Description'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class Value():
        '''Value'''
        def __init__(self, node):
            self.node=node
            self.ns=get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class Union():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class Correction():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class AcquisitionDate():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class MetadataOnly():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))

    class HashSHA1():
        def __init__(self, node):
            self.node = node
            self.ns = get_namespaces(self.node)

        @property
        def text(self):
            return get_text(self.node)
        @text.setter
        def text(self, value):
            set_text(self.node, str(value))
