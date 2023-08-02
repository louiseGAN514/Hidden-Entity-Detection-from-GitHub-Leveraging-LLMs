import json

from bs4 import BeautifulSoup
from pprint import pprint
from tqdm import tqdm


# -------------------------
# use beautifulsoup
# -------------------------

def bs4_find(text, target, patterns=None):
    soup = BeautifulSoup(text, features='lxml-xml')
    if patterns == None:
        return soup.find_all(target)
    matches = soup.find_all(target)
    res = []
    for _match in matches:
        # print(_match, type(_match))
        for pattern in patterns:
            if pattern in str(_match).lower():
                res.append(_match)
                break
    return res


# -------------------------
# read readme files
# -------------------------

README_JSON_XML_FILE = './data/readme2_v3.json'

with open(README_JSON_XML_FILE, 'r') as fr:
    readmes_xml = json.load(fr)
readmes_xml_noempty = {int(k):v for k,v in readmes_xml.items() if not v == ''}
##  pprint(list(readmes_xml_noempty.items())[:1])

# -------------------
# block extraction
# -------------------
## codeblock_dict = {}
def extract_block():
    block_dict = {}
    for k in tqdm(readmes_xml_noempty):
        content = readmes_xml_noempty[k]['content']
        ## textblock, codeblock
        block_dict[k] = [str(e) for e in bs4_find(content, 'codeblock' #)]
        , patterns=['@article', '@inproceedings', '@misc', '@Article', 
            '@InProceedings', ])]
    print(len({k for k in block_dict if not block_dict[k]==[]}))

    # with open('textblocks.json', 'w') as fw:
    #    json.dump(block_dict, fw, indent=4)
extract_block()

# --------------------
# link extraction
# --------------------
def extract_link():
    link_dict = dict()
    for k in tqdm(readmes_xml_noempty):
        content = readmes_xml_noempty[k]['content']
        _links = []
        for _match in bs4_find(content, 'link', patterns=['dataset', 'corpus', 'data' ]):
            if 'http' in str(_match).lower():
                if 'dataset' in str(_match).lower():
                    _links.append(str(_match))
                elif 'corpus' in str(_match).lower():
                    _links.append(str(_match))
                elif 'data' in str(_match.attrs['destination']):
                    _links.append(str(_match))
        link_dict[k] = _links
    print(len({k for k in link_dict if not link_dict[k]==[]}))
    with open('links.json', 'w') as fw:
        json.dump(link_dict, fw, indent=4)

# extract_link()
