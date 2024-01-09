import json

from bs4 import BeautifulSoup
from pprint import pprint
import numpy as np
import pandas as pd
from tqdm import tqdm
from utils import hyperlink_extraction, para_extraction_with_links, para_extraction_with_links_XML_parser

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

# print(len(readmes_xml_noempty))
# for k,v in readmes_xml_noempty.items():
#     _name, _fullname, _content = v['name'], v['fullname'], v['content']
#     _owner, _repo = _fullname.split('/')
#     with open('./data/readme_xml/{}_{}_{}_{}.xml'.format(k, _name, _owner, _repo), 'w') as fw:
#         fw.write(_content)
    # pprint(list(readmes_xml_noempty.items())[:1])

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
    print('The number of XML containing extracted blocks is ', len({k for k in block_dict if not block_dict[k]==[]}))

    # with open('textblocks.json', 'w') as fw:
    #    json.dump(block_dict, fw, indent=4)
# extract_block()

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
    print('The number of XML containing extracted links is ', len({k for k in link_dict if not link_dict[k]==[]}))
    with open('links.json', 'w') as fw:
        json.dump(link_dict, fw, indent=4)

# extract_link()

def extract_link_with_context_old():
    repo_ids, links, texts, prev_texts, next_texts = [], [], [], [], []
    for k in tqdm(readmes_xml_noempty):
        readme = readmes_xml_noempty[k]['content']
        """add readme preprocessing steps """
        readme = readme.replace('\n', '')
        try:
            _links, _texts, _prev_texts,_next_texts = hyperlink_extraction(readme)
            if type(_links) == str:
                _links, _texts, _prev_texts, _next_texts = [_links], [_texts],[_prev_texts],[_next_texts]
            for _link,_text,_prev_text, _next_text in zip(_links,_texts,_prev_texts,_next_texts):
                # _link, _text, _prev_text, _next_text = ee
                if not('dataset' in _link or 'corpus' in _link or 'data' in _link):
                    continue
                if _link[-3:] == 'pdf' or _link[-3:]=='pth' or _link[-3:]=='log':
                    continue
                repo_ids.append(k)
                links.append(_link)
                texts.append(_text)
                prev_texts.append(_prev_text)
                next_texts.append(_next_text)
        except TypeError as e:
            pass

    links_extract_df = pd.DataFrame(data={'repoId':repo_ids, 'link':links, 
        'prev_text': prev_texts, 'text': texts, 'next_text': next_texts})
    print(links_extract_df.head(5))
    print(len(links_extract_df))
    links_extract_df.to_csv('./res/links_extraction_no_pdf_link_withID_context_211123.csv', index=False, sep='|||')
    print('Unique link number is ', len(links_extract_df['link'].unique()))

    links_with_candidname_df = links_extract_df[links_extract_df['text'].str.contains('(?i)data(?:\s|)set(?:s|)')]
    links_with_candidname_df.to_csv('./res/links_with_candidate_name_withID_context_211123.csv',index=False, sep='|||')
    print('Unique link number with a candidate name is ', len(links_with_candidname_df['link'].unique()))


def extract_link_with_context():
    repo_ids, links, texts, contexts, raw_contexts = [],[], [], [], []
    for k in tqdm(readmes_xml_noempty):
        readme = readmes_xml_noempty[k]['content']
        """add readme preprocessing steps """
        readme = readme.replace('\n', '')
        try:
            _links, _texts, _contexts,_raw_contexts = para_extraction_with_links(readme)
            for _link,_text,_context, _raw_context in zip(_links,_texts,_contexts,_raw_contexts):
                # _link, _text, _prev_text, _next_text = ee
                if not('dataset' in _link or 'corpus' in _link or 'data' in _link):
                    continue
                if _link[-3:] == 'pdf' or _link[-3:]=='pth' or _link[-3:]=='log':
                    continue
                repo_ids.append(k)
                links.append(_link)
                texts.append(_text)
                contexts.append(_context)
                raw_contexts.append(_raw_context)
        except TypeError as e:
            pass

    links_extract_df = pd.DataFrame(data={'repoId':repo_ids, 'link':links, 
        'text': texts, 'context': contexts, 'raw_context': raw_contexts})
    print(links_extract_df.head(5))
    print(len(links_extract_df))
    links_extract_df.to_csv('./res/para_extraction_with_links_no_pdf_link_withID_221123.csv', index=False, sep='|')
    print('Unique link number is ', len(links_extract_df['link'].unique()))



def extract_link_with_context_XML_parser():
    repo_ids, links, texts, contexts = [],[], [], []
    link_starts, link_ends, text_starts, text_ends = [],[],[],[]
    for k in tqdm(readmes_xml_noempty):
        readme = readmes_xml_noempty[k]['content']
        """add readme preprocessing steps """
        readme = readme.replace('\n', '')
        readme = ' '.join(readme.split())
        try:
            _contexts,_links = para_extraction_with_links_XML_parser(readme)
            for _context, _link_list in zip(_contexts,_links):
                # _link, _text, _prev_text, _next_text = ee
                for _link_entry in _link_list:
                    _link = _context[_link_entry['url_start']:_link_entry['url_end']]
                    _text = _context[_link_entry['text_start']: _link_entry['text_end']]
                    # print('link: ', _link, '\n', 'text:', _text)
                    if not ('dataset' in _link or 'corpus' in _link or 'data' in _link):
                        continue
                    if _link[-3:] == 'pdf' or _link[-3:]=='pth' or _link[-3:]=='log':
                        continue
                    repo_ids.append(k)
                    links.append(_link)
                    texts.append(_text)
                    contexts.append(_context)
                    link_starts.append(_link_entry['url_start'])
                    link_ends.append(_link_entry['url_end'])
                    text_starts.append(_link_entry['text_start'])
                    text_ends.append(_link_entry['text_end'])
        except TypeError as e:
            pass

    links_extract_df = pd.DataFrame(data={'repoId':repo_ids, 'link':links, 
        'text': texts, 'context': contexts, 'linkStart':link_starts, 'linkEnd':link_ends, 'textStart':text_starts, 'textEnd': text_ends})
    print(links_extract_df.head(5))
    print(len(links_extract_df))
    # links_extract_df.to_csv('./res/para_extraction_with_links_XML_parser_no_pdf_link_withID_281123.csv', index=False, sep='|||')
    np_links_extract_df = links_extract_df.to_numpy()
    np.savetxt('./res/para_extraction_with_links_XML_parser_no_pdf_link_withID_131223.csv', np_links_extract_df, fmt='%s',delimiter='<|>')
    print('Unique link number is ', len(links_extract_df['link'].unique()))


extract_link_with_context_XML_parser()
