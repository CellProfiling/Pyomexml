"""Demonstarte the xml data from the template of ome_xml.py."""
import os
import sys
from xml.dom import minidom
import uuid
import pyomexml.omexml as ome
PATH_A = os.path.abspath(
    os.path.join('../', os.path.dirname(__file__)))
del sys.path[0]
sys.path.insert(0, PATH_A)
from tests.editor.xml_instrument import edit_instrument
from tests.editor.xml_image import edit_image
from tests.editor.xml_experiments import edit_experiments


def ome_xml():
    """ome.xml editing pipeline and return the xml data."""
    omexml = ome.OMEXML()
    omexml.Creator = "@Hao Xu:CellAtlas of HPA V0.0.0"
    omexml.UUID = str(uuid.uuid4())
    # This part add the element to edit
    edit_experiments(omexml)
    edit_instrument(omexml)
    edit_image(omexml)
    # This is the end of xml editing

    return omexml


def output_xml():
    """use demo.xml to demonstrate the modified xml_file"""
    # get the xml data for viewing
    xml_data = ome_xml()
    xml_data = xml_data.to_xml()
    parse_xml = minidom.parseString(xml_data)
    pretty_xml = parse_xml.toprettyxml()
    xml_path = os.path.abspath(os.path.join(__file__, '../look.xml'))
    xml_file = open(xml_path, 'w')
    xml_file.write(pretty_xml)
    xml_file.close()


if __name__ == '__main__':
    output_xml()
