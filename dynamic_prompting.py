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
        
        examples = ""
    	for i, idx in enumerate(indices):
        	_text, _urls, _labels = new_context_anno_df['context'].iloc[idx], new_context_anno_df['link'].iloc[idx], new_context_anno_df['link_type'].iloc[idx]
            examples += '# Example {}\nInput: '.format(i+1) +_text +'\nOutput: {}'.format(str([{"URL": url, "label":label} for url, label in zip(_urls, _labels)]))
        if i < len(indices):
            examples += "\n\n"   


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
    """ + examples + """[/INST]
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
        
        examples = ""
    	for i, idx in enumerate(indices):
        	_text, _urls, _labels = new_context_anno_df['context'].iloc[idx], new_context_anno_df['link'].iloc[idx], new_context_anno_df['link_type'].iloc[idx]
        	examples += '# Example {}\nInput: '.format(i+1) + '{"context":"' +_text + '",' + '"target_URLs":[' + ','.join(['"' +e+ '"' for e in _urls]) + ']}\n'+'Output: {}'.format(str([{"URL": url, "label":label} for url, label in zip(_urls, _labels)]))
        	if i < len(indices):
            	examples += "\n\n" 


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
    """ + examples +"""[/INST]
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


 
