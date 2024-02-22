import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

from prompt_utils import run_prompt

device = "cuda:0"
torch.cuda.empty_cache()
MODELNAME = "all-MiniLM-L6-v2"
model = SentenceTransformer('{}'.format(model_name)).to(device)

def select_top_n_simi_sents(query_sent, candid_sents, score_func='dot', n=4):
    query_embedding = model.encode(query_sent)
    passage_embedding = model.encode(candid_sents)
    if score_func == 'dot': 
        return torch.topk(util.dot_score(query_embedding, passage_embedding),k=n)
    elif score_func == 'cos':
        return torch.topk(util.cos_sim(query_embedding, passage_embedding),k=n)


def run_extraction_task(modelname, context_anno_df, start_idx, cnt=1, adjust_maxlen=False):
    ans = []
    for i in range(start_idx, len(context_anno_df)):
        text = context_anno_df['context'].iloc[i]
        repoID = context_anno_df['repoID'].iloc[i]

        ## skip table inputs
        if '|:--' in text or '| --' in text or '|--' in text or '| :--' in text:
            ans.append({'text':text,'answer': 'skipped','repoID':repoID,'URL_gold_label':url_type})
            continue


        url_type = [{'URL': url, 'gold_label':link_type} for url, link_type in zip(new_context_anno_df['link'].iloc[i],new_context_anno_df['link_type'].iloc[i])]
        print(i, text)


        ### select 4 examples
        candid_sents = [context_anno_df['context'].iloc[i] for i in range(30)]
        values, indices = select_top_n_simi_sents(text, candid_sents)
        indices = indices.cpu().detach().numpy()[0]

        _prompt = """<s>[INST]<<sys>>You act as a human annotator. First read the instructions and given examples, then only annotate the last given input accordingly without extra words. Your annotation has to use valid JSON syntax.<</sys>>
    
    Annotate the URLs in the input and classify the URLs with the following labels: 
    1. DatasetDirectLink - the URL is for downloading dataset files
    2. DatasetLandingPage - the URL is an introduction or a landing page for some dataset entity
    3. Software - when the URL is for some software entity
    4. Other - the URL does not fall into the above cases
    
    # formatting
    Input: text containing one or more URLs.
    Output: for each URL span, first output the URL span, then output one of the four above labels.
    
    # Examples:
    # Example 1:
    Input: Gowalla https://snap.stanford.edu/data/loc-gowalla.html : the pre-processed data that we used in the paper can be downloaded here http://dawenl.github.io/data/gowalla_pro.zip .
    Output: [{"URL": "https://snap.stanford.edu/data/loc-gowalla.html", "label":"dataset_landing_page"},
    {"URL": "http://dawenl.github.io/data/gowalla_pro.zip", "label": "dataset_direct_link"}]

    # Example 2:
    Input: Next we suggest you look at the comprehensive tutorial http://simongog.github.io/assets/data/sdsl-slides/tutorial  which describes all major features of the library or look at some of the provided examples examples .
    Output: [{"URL":"http://simongog.github.io/assets/data/sdsl-slides/tutorial", "label":"Other"}]

    # Example 3:
    Input: Laboratory for Web Algorithms http://law.di.unimi.it/datasets.php
    Output: [{"URL": "http://law.di.unimi.it/datasets.php", "label":"dataset_landing_page"}]

    # Example 4:
    Input: Validatable http://www.rubydoc.info/github/heartcombo/devise/main/Devise/Models/Validatable : provides validations of email and password. It's optional and can be customized, so you're able to define your own validations.
    Output: [{"URL": "http://www.rubydoc.info/github/heartcombo/devise/main/Devise/Models/Validatable", "label":"Software"}]
    [/INST]
    [INST]
    # to annotate
    Input:""" + text+"\n[/INST]"
        if not adjust_maxlen:
            res = run_prompt(_prompt)
        else:
            res = run_prompt(_prompt, max_length=int(1.25 * len(_prompt)))
        print(res.answer[len(_prompt):])
        # display_answer(res)
        ans.append({'text':text, 
            'answer': res.answer[len(_prompt):],
            'repoID':repoID, 
            'URL_gold_label':url_type})
    
    short_ans = [e for e in ans if len(e['answer'])<1000]

    ## save to file
    if adjust_maxlen:
        with open("./res/prompting_res/{}_static_fewshot_prompt_adjusted_maxlen_force_json_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(ans, f, indent=4, default=int)
        with open("./res/prompting_res/{}_static_fewshot_prompt_adjusted_maxlen_force_json_short_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(short_ans, f, indent=4, default=int)
    else:
        with open("./res/prompting_res/{}_static_fewshot_prompt_force_json_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(ans, f, indent=4, default=int)
        with open("./res/prompting_res/{}_static_fewshot_prompt_force_json_short_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(short_ans, f, indent=4, default=int)


def run_classification_task(modelname, context_anno_df, start_idx, cnt=1, adjust_maxlen=False):
    ans = []
    for i in range(start_idx, len(context_anno_df)):
        text = context_anno_df['context'].iloc[i]
        repoID = context_anno_df['repoID'].iloc[i]

        ## skip table inputs
        if '|:--' in text or '| --' in text or '|--' in text or '| :--' in text:
            ans.append({'text':text,'answer': 'skipped','repoID':repoID,'URL_gold_label':url_type})
            continue
        
        url_type = [{'URL': url, 'gold_label':link_type} for url, link_type in zip(new_context_anno_df['link'].iloc[i],new_context_anno_df['link_type'].iloc[i])]
        # print(text)
        total_input = '{"context":"' +text + '",' + '"target_URLs":[' + ','.join(['"' +e['URL']+ '"' for e in url_type]) + ']}'  
        print(i, 'Total input:', total_input)


        # select 4 examples
        candid_sents = [new_context_anno_df['context'].iloc[i] for i in range(30)]
        values, indices = select_top_n_simi_sents(text, candid_sents)
        indices = indices.cpu().detach().numpy()[0]

        _prompt = """<s>[INST]<<sys>>You act as a human annotator. First read the instructions and given examples, then only annotate the last given input accordingly without extra words. Your annotation has to use valid JSON syntax.<</sys>>
    
    Annotate the URLs given in the input with its context and classify the URLs with the following labels: 
    1. DatasetDirectLink - the URL is for downloading dataset files
    2. DatasetLandingPage - the URL is an introduction or a landing page for some dataset entity
    3. Software - when the URL is for some software entity
    4. Other - the URL does not fall into the above cases
    
    # formatting
    Input: target URL(s) with context 
    Output: for each URL span, first output the URL span, then output one of the four above labels.
    
    # Examples:
    # Example 1:
    Input: {"context": "Gowalla https://snap.stanford.edu/data/loc-gowalla.html : the pre-processed data that we used in the paper can be downloaded here http://dawenl.github.io/data/gowalla_pro.zip .","target_URLs": ["https://snap.stanford.edu/data/loc-gowalla.html", "http://dawenl.github.io/data/gowalla_pro.zip"]}
    Output: [{"URL": "https://snap.stanford.edu/data/loc-gowalla.html", "label":"dataset_landing_page"},
    {"URL": "http://dawenl.github.io/data/gowalla_pro.zip", "label": "dataset_direct_link"}]

    # Example 2:
    Input: {"context": "Next we suggest you look at the comprehensive tutorial http://simongog.github.io/assets/data/sdsl-slides/tutorial  which describes all major features of the library or look at some of the provided examples examples .","target_URLs": ["http://simongog.github.io/assets/data/sdsl-slides/tutorial"]}
    Output: [{"URL":"http://simongog.github.io/assets/data/sdsl-slides/tutorial", "label":"Other"}]

    # Example 3:
    Input: {"context": "Laboratory for Web Algorithms http://law.di.unimi.it/datasets.php", "target_URLs":"http://law.di.unimi.it/datasets.php"}
    Output: [{"URL": "http://law.di.unimi.it/datasets.php", "label":"dataset_landing_page"}]

    # Example 4:
    Input: {"context": "Validatable http://www.rubydoc.info/github/heartcombo/devise/main/Devise/Models/Validatable : provides validations of email and password. It's optional and can be customized, so you're able to define your own validations.", "target_URLs":"http://www.rubydoc.info/github/heartcombo/devise/main/Devise/Models/Validatable"}
    Output: [{"URL": "http://www.rubydoc.info/github/heartcombo/devise/main/Devise/Models/Validatable", "label":"Software"}]
    [/INST]
    [INST]
    # to annotate
    Input:"""+ total_input + "\n[/INST]"

        if not adjust_maxlen:
            res = run_prompt(_prompt)
        else:
            res = run_prompt(_prompt, max_length=int(1.25 * len(_prompt)))
        print(res.answer[len(_prompt):])
        # display_answer(res)
        ans.append({'text':text, 
            'answer': res.answer[len(_prompt):],
            'repoID':repoID, 
            'URL_gold_label':url_type})
    
    short_ans = [e for e in ans if len(e['answer'])<1000]

    ## save to file
    if adjust_maxlen:
        with open("./res/prompting_res/{}_static_fewshot_prompt_adjusted_maxlen_with_target_force_json_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(ans, f, indent=4, default=int)
        with open("./res/prompting_res/{}_static_fewshot_prompt_adjusted_maxlen_with_target_force_json_short_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(short_ans, f, indent=4, default=int)
    else:
        with open("./res/prompting_res/{}_static_fewshot_prompt_with_target_force_json_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(ans, f, indent=4, default=int)
        with open("./res/prompting_res/{}_static_fewshot_prompt_with_target_force_json_short_output_{}.json".format(modelname, cnt), 'w') as f:
            json.dump(short_ans, f, indent=4, default=int)


 
