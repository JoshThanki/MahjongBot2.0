import codecs
import struct
import xml.etree.ElementTree as ET

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
import cProfile

import sqlite3

dbfile = '2020.db'

con = sqlite3.connect(dbfile)

cur = con.cursor()


res = cur.execute("SELECT log_content FROM logs")

firstBlob = res.fetchone()[0]

print("\n")


print("\n")

con.close()


XML = etree.XML

decompress = bz2.decompress

content = decompress(firstBlob)

xml = XML(content, etree.XMLParser(recover=True))

xml_string = ET.tostring(xml, encoding='unicode')

print(xml_string)


# def decode(str):
#     decodedBlob = codecs.decode(str, "hex_codec")
#     return decodedBlob



# def decode_blob_to_xml(blob_data):
#     # Initialize XML root element
#     root = ET.Element("root")
    
#     # Define the structure of the blob data
#     record_size = 8 + 20  # Example: 8 bytes for integer, 20 bytes for string
    
#     # Process the blob data
#     offset = 0
#     while offset < len(blob_data):
#         # Extract an integer (8 bytes) and a string (20 bytes)
#         int_val = struct.unpack_from('Q', blob_data, offset)[0]
#         str_val = struct.unpack_from('20s', blob_data, offset + 8)[0].decode('utf-8').strip('\x00')
        
#         # Create XML element for each record
#         record_elem = ET.SubElement(root, "record")
#         int_elem = ET.SubElement(record_elem, "integer")
#         int_elem.text = str(int_val)
#         str_elem = ET.SubElement(record_elem, "string")
#         str_elem.text = str_val
        
#         # Move to the next record
#         offset += record_size
    
#     # Convert the XML tree to a string
#     xml_str = ET.tostring(root, encoding='unicode')
#     return xml_str


# # Decode blob to XML
# xml_output = decode_blob_to_xml(firstBlob)
