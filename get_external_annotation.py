import csv
import json
from pprint import pprint
import pandas as pd
import numpy as np


def get_external_annotation(filepath, anno_type=None):
    # anno_type should be either None, confirmed or data
    try:
        with open(filepath, 'r') as fr:
            content = json.load(fr)
            content = {int(k): content[k] for k in content if content[k] != []}  
            print('The annotated repo number is {}'.format(len(content)))
            for i in list(content.keys())[:2]:
                k = list(content.keys())[i]
                print('RepoID', k) 
                pprint(content[k])

            linktypes = set()
            for k in content:
                for anno in content[k]:
                    linktypes.add(anno['linkType'])
            print('Unique link types are ', list(linktypes))
            
            datasets_anno = []
            for k in content:
                for anno in content[k]:
                    if anno_type == 'data':
                        if anno['linkType'] in ['dataset_landing_page', 'dataset_direct_link']:
                            datasets_anno.append((k, anno))
                    elif anno_type == 'confirmed':
                        if anno['linkType'] in ['dataset_landing_page', 'dataset_direct_link', 'other', 'software']:
                            datasets_anno.append((k, anno))
                    elif anno_type is None:
                        datasets_anno.append((k, anno))
            print('Total annotated dataset entry number is', len(datasets_anno))
            # pprint(datasets_anno[:3])
            datasets_anno_df = pd.DataFrame.from_dict({
                'repoID': [t[0] for t in datasets_anno],
                'description': [t[1]['description'] for t in datasets_anno],
                'link': [t[1]['destination'] for t in datasets_anno],
                'linkType': [t[1]['linkType'] for t in datasets_anno]
                })

        return datasets_anno_df
    except Exception as e:
        raise(e)

def match_dataset_URL(csv_filepath, datasets_anno=None):
    csv_content = pd.read_csv(csv_filepath)
    # print(csv_content.tail())
    # with open(csv_filepath, 'r') as fr:
    #     line = fr.readline().split(',')
    #     while line:
    #         pass

    print(len(csv_content), len(csv_content['link'].unique()))
    nodup_csv_content = csv_content.drop_duplicates(subset=['link'])
    if datasets_anno is None:
        return
    # print(datasets_anno.head())
    print(len(datasets_anno), len(datasets_anno['link'].unique()))
    nodup_datasets_anno = datasets_anno.drop_duplicates(subset=['link'])
    print(nodup_csv_content['link'].head())
    print(nodup_datasets_anno['link'].head())
    # joined = nodup_csv_content.merge(nodup_datasets_anno, how='inner', on='link')
    joined = csv_content.merge(nodup_datasets_anno, how='inner', on='link')
    print('Matched annotation count is',len(joined))
    # joined.to_csv('./res/joined.csv')

    repoIDs = list(nodup_datasets_anno['repoID'].unique())
    filtered_csv_content = csv_content[csv_content['repoId'].isin(repoIDs)]
    print('Autolabeled entry count in those repos is', len(filtered_csv_content))
    joined_1 = filtered_csv_content.merge(nodup_datasets_anno, how='inner', on='link')
    print('Matched annotation within those repos counts ',len(joined_1))


def match_URL(df_link_context, datasets_anno):
    print(len(df_link_context))
    joined = df_link_context.merge(datasets_anno, how='inner', on='link')
    print('Matched annotation count is',len(joined))
    return joined

def read_csv(filepath, sep='|||',names=None):
    cnt = 0
    res_dict = {}
    if names is not None:
        for name in names:
            res_dict[name] = []
    with open(filepath, 'r') as fr:
        line = fr.readline()
        while line:
            # print(cnt, line)
            line = line.strip().split(sep)
            cnt += 1
            if names is not None:
                if len(line) != len(names):
                    raise Exception("Line {} does not have the right format".format(cnt))
                for idx in range(len(line)):
                    res_dict[names[idx]].append(line[idx])
            else:
                pass
            line = fr.readline()
    res = pd.DataFrame.from_dict(res_dict)
    return res


# csv_filepath = './res/links_extraction_no_pdf_link_withID.csv'
csv_filepath = './res/para_extraction_with_links_XML_parser_no_pdf_link_withID_131223.csv'
datasets_anno = get_external_annotation('./res/links_annotated.json', anno_type='confirmed')
print('Total count of annos: ', len(datasets_anno))
nodup_datasets_anno = datasets_anno.drop_duplicates(subset=['link', 'linkType'])
print('Nodup: ', len(nodup_datasets_anno))
# print(datasets_anno.head())
nodup_datasets_anno_1 = datasets_anno.drop_duplicates(subset=['link'])
print('Nodup1 : ', len(nodup_datasets_anno_1))
# grouped_datasets_anno = datasets_anno.groupby(['link', 'linkType'])['description'].apply(lambda x: list(set(list(x)))).reset_index(name="description_option")
# print(grouped_datasets_anno.head(50))

columns = ['repoID', 'link', 'description', 'context', 'link_start', 'link_end', 'text_start', 'text_end']
# df_link_context = pd.read_csv(csv_filepath, sep='\|\|\|', header=None, names=columns)
# print(df_link_context.head())
# match_dataset_URL(csv_filepath, datasets_anno)
df_link_context = read_csv(csv_filepath, sep='<|>', names=columns)
# print(df_link_context.head())

matched_res = match_URL(df_link_context, nodup_datasets_anno[['repoID','link', 'linkType']])
np_matched_res= matched_res.drop_duplicates().to_numpy()
np.savetxt('./res/matched_annotated_link_withID_131223.csv', np_matched_res, fmt='%s',delimiter='<|>')
# print(matched_res.tail())
pprint(np_matched_res[-15:-10])
pprint([e for e in np_matched_res if e[0] == '6999'])
print('Annotated dataset related count: ', len([1 for e in np_matched_res if 'data' in e[-1]]))
