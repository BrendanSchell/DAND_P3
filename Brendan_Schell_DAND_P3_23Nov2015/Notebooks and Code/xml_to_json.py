import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import codecs
import json

"""
Note: Code referenced from Udacity MongoDB course.
"""
filename = '/home/brendan/Documents/Courses/Data Analyst Nanodegree/P3/DAND-P3/toronto_canada.osm'
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square","Lane","Road","Trail", "Parkway", "Commons"]

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]



def test():
    
    process_map(filename)
    
def shape_element(element):
    node = {}
    node_refs = []
    address = {}
    created = {}
    pos = [float(0),float(0)]
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for a in element.items():
            
            if a[0] in CREATED:
                created[a[0]] = a[1]
            elif a[0] == 'lat':
                pos[0] = float(a[1])
            elif a[0] == 'lon':
                pos[1] = float(a[1])
            else:
                node[a[0]] = a[1]
        for i in element:
            if i.tag =='tag':
                v = i.get('k')
                if not problemchars.search(v):
                    if (v.find('addr') > -1) and (v.count(':') < 2):
			#make all postal codes upper case
                        if v == 'addr:postcode':
                                node[v.replace('addr:','')] = i.get('v').upper()
			#break address into sub-components
                        elif v == 'address':
                            if v[0:v.find(" ")].isdigit():
                                house_num = v[0:v.find(" ")]
                                temp = fix_address(v[v.find(" ")+1:])
                                if temp != -1:
                                    node['housenumber'] = house_num
                                    node['streetname'] = temp
                        #replace state with province        
                        elif v == 'addr:state':
                            node['province'] = i.get('v')
                        else:
                            address[v.replace('addr:','')] = i.get('v')
                    else:
                        if v.count(':') == 1:
                            # additional code to make all postal codes upper case
                                node[v] = i.get('v')
            elif i.tag == 'nd':
                
                if i.get('ref') is not None:
                    node_refs.append(i.get('ref'))
        
        if created != {}:
            node['created'] = created
        if address != {}:
            node['address'] = address
        if len(pos) > 0:
            node['pos'] = pos
        if len(node_refs) > 0:
            node['node_refs'] = node_refs
    	element.clear()
        return node
    else:
	
        return None

# use fast_iter since the file is large and uses up all RAM otherwise.
def process_map(file_in):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    
    with codecs.open(file_out, "w") as fo:
        context = ET.iterparse( file_in )
	fast_iter(context,fo)
             	
def fast_iter(context,fo):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    """
    for _, elem in context:
        process_element(elem,fo)
   


def process_element(elem,fo):
    el = shape_element(elem)
    if el:
	fo.write(json.dumps(el) + "\n")

       

def fix_address(street_name):
    m = street_type_re.search(street_name)
    if m:
        if m.group() in expected:
            
            return street_name
        else:
            return -1
    else:
        return -1



def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
def audit_post_code(post_codes,post_code):
    m = valid_post_code.search(post_code)
    if not m:
        post_codes['Invalid'].add(post_code)
    else:
        post_codes['Valid'].add(post_code)
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_state(elem):
    return (elem.attrib['k']) == "addr:state"

def is_full_address(elem):
    return (elem.attrib['k']) == "address"

def get_unique_tag_keys(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    post_codes = defaultdict(set)
    tags = []
    cnt = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            if cnt > 10000:
                break
            cnt = cnt + 1
            
            for tag in elem.iter("tag"):
                if tag.attrib['k'] not in tags:
                    tags.append(tag.attrib['k'])
    
    return tags

def audit_postal_codes(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    post_codes = defaultdict(set)
    tags = []
    cnt = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            if cnt > 1000:
                break
            
            
            for tag in elem.iter("tag"):
                
                if is_postal_code(tag):
                    cnt = cnt + 1
                    audit_post_code(post_codes, tag.attrib['v'])
                    
def audit_states(osmfile):
    osm_file = open(osmfile, "r")
    tags = []
    cnt = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            if cnt > 100:
                break
            
            
            for tag in elem.iter("tag"):
                
                if is_state(tag):
                    cnt = cnt + 1
                    print tag.attrib['v']
def audit_address(osmfile):
    osm_file = open(osmfile, "r")
    tags = []
    cnt = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            if cnt > 100:
                break
            
            
            for tag in elem.iter("tag"):
                
                if is_full_address(tag):
                    cnt = cnt + 1
                    print tag.attrib['v']
def update_name(name, mapping):    
    return post_codes
def update_name(name, mapping):

    name = name.replace('N.','North') #regular expression will not catch otherwise
    st_type = street_type_re.search(name).group()
    if st_type in mapping.keys():
        name = name.replace(st_type,mapping[st_type])
    return name

if __name__ == "__main__":
    test()
