import json
from pprint import pprint

from utils import partial_match, parse_answer


# evaluation for one pair of annotation of predict and gold standard according to SemEval definition
class anno_eval:
    def __init__(self, predict_gold_pairs):
        self.pred_gold_pairs = predict_gold_pairs
        # print('Point: 1')
        self.mapped_pairs = self._anno_mapping()
        # print('Point: 2')
        self.cor, self.inc, self.mis, self.par, self.spr = [{'strict':0, 'exact':0, 'partial':0, 'type':0} for i in range(5)]
        pass

    def _anno_mapping(self):
        res = []
        # print('Point: 3')
        for anno_pair in self.pred_gold_pairs:
            # print('Point: 4')
            pred, gold = anno_pair[0], anno_pair[1]
            if isinstance(pred, list):
                # match the URL strings: prioritize exact match, then partial 
                # each URL can only be matched once
                matched_pred = set()
                # print('Point: 5')
                for idx_gold, URL_label_gold in enumerate(gold):
                    # print('Point: 6')
                    URL_gold = URL_label_gold['URL']
                    candid_pred = list(set(range(len(pred))) - matched_pred)
                    candid_res = []
                    if len(candid_pred) == 0:
                        empty_URL_label = {"URL": "", "label":""}
                        res.append((empty_URL_label, URL_label_gold))
                        break
                    if len(candid_pred) == 1:
                        selected_idx_pred = candid_pred[0]
                        matched_pred.add(selected_idx_pred)
                        res.append((pred[selected_idx_pred], URL_label_gold))
                        break
                    for idx_pred in candid_pred:
                        # print('Point: 7')
                        URL_label_pred = pred[idx_pred]
                        URL_pred = URL_label_pred['URL']
                        if URL_pred == URL_gold:
                            candid_res.append((idx_pred,1))
                            break
                        else:
                            # print('Point: 8')
                            partial_score = partial_match(URL_pred, URL_gold)
                            candid_res.append((idx_pred, partial_score))
                    if candid_res[-1][1] == 1:
                        selected_idx_pred = candid_res[-1][0]
                    else:
                        candid_res = sorted(candid_res, key= lambda x: x[1])
                        selected_idx_pred = candid_res[-1][0]
                    matched_pred.add(selected_idx_pred)
                    res.append((pred[selected_idx_pred], URL_label_gold))
                candid_pred = list(set(range(len(pred))) - matched_pred)
                if len(candid_pred) > 0:
                    empty_URL_label = {"URL": "", "label":""}
                    for idx_pred in candid_pred:
                        res.append((pred[idx_pred], empty_URL_label))
            elif isinstance(pred, dict):
                if len(gold) == 1:
                    res.append((pred, gold[0]))
                elif len(gold) == 0:
                    empty_URL_label = {"URL": "", "label":""}
                    res.append((pred, empty_URL_label))
                else:
                    for idx_gold, URL_label_gold in enumerate(gold):
                        URL_gold = URL_label_gold['URL']
                        URL_pred = URL_label_pred['URL']
                        candid_res = []
                        if URL_pred == URL_gold:
                            candid_res.append((idx_gold,1))
                            break
                        else: 
                            partial_score = partial_match(URL_pred, URL_gold)
                            candid_res.append((idx_gold, partial_score))
                    if candid_res[-1][1] == 1:
                        selected_idx_gold = candid_res[-1][0]
                    else:
                        candid_res = sorted(candid_res, key= lambda x: x[1])
                        selected_idx_gold = candid_res[-1][0]
                    res.append((pred, gold[selected_idx_pred]))
        return res
        
    def cal_muc_types(self):
        assert len(self.mapped_pairs) > 0
        self.cor, self.inc, self.mis, self.par, self.spr = [{'strict':0, 'exact':0, 'partial':0, 'type':0} for i in range(5)]
        for pred_gold in self.mapped_pairs:
            pred, gold = pred_gold[0], pred_gold[1]
            # print('gold: ', gold)
            pred_URL, pred_label = pred['URL'], pred['label']
            try:
                gold_URL, gold_label = gold['URL'], gold['gold_label']
            except Exception as e:
                gold_URL, gold_label = gold['URL'], gold['label']
                # print(gold)
            if pred_URL == '':
                self.mis = {k: v+1 for k,v in self.mis.items()}
                continue
            elif gold_URL == '':
                self.spr = {k: v+1 for k,v in self.spr.items()}
                continue
            else:
                if pred_label == gold_label:
                    self.cor['type'] += 1
                    if pred_URL == gold_URL:
                        self.cor['strict'] += 1
                        self.cor['exact'] += 1
                        self.cor['partial'] += 1
                    else:
                        self.inc['strict'] += 1
                        self.inc['exact'] += 1
                        if pred_URL in gold_URL:
                            self.par['partial'] += 1
                        else:
                            self.inc['partial'] += 1
                else:
                    self.inc['type'] += 1
                    self.inc['strict'] += 1
                    if pred_URL == gold_URL:
                        self.cor['exact'] += 1
                        self.cor['partial'] += 1
                    else:
                        self.inc['exact'] += 1
                        if pred_URL in gold_URL:
                            self.par['partial'] += 1
                        else:
                            self.inc['partial'] += 1
        pass
        
    def precision(self, mode='strict'):
        if mode == 'strict' or mode == 'exact':
            return self.cor[mode]/(self.cor[mode]+self.inc[mode]+self.par[mode]+self.mis[mode])
        else: 
            return (self.cor[mode]+ 0.5*self.par[mode])/(self.cor[mode]+self.inc[mode]+self.par[mode]+self.mis[mode])
        pass

    def recall(self, mode='strict'):
        if mode == 'strict' or mode == 'exact':
            return self.cor[mode]/(self.cor[mode]+self.inc[mode]+self.par[mode]+self.spr[mode])
        else: 
            return (self.cor[mode]+ 0.5*self.par[mode])/(self.cor[mode]+self.inc[mode]+self.par[mode]+self.spr[mode])
        pass

    def f1_score(self, mode='strict'):
        pass



with open('./res/prompting_res/llama_2_static_fewshot_prompt_with_target_short_output_1.json', 'r') as fr:
    llm_output = json.load(fr)

# llm_output = [e for e in llm_output if int(e['repoID']) < 7100]
predict_gold_pairs = []

for i in range(0,len(llm_output)):
    test_str = llm_output[i]['answer']
    URL_label_gold = llm_output[i]['URL_gold_label']
    parsed_ans = parse_answer(test_str)
    if not isinstance(parsed_ans, str):
        # parsed_outputs.append({'predict': parsed_ans, 'URL_gold_label':llm_output[i]['URL_gold_label']})
        predict_gold_pairs.append((parsed_ans, URL_label_gold))
        pass

eval = anno_eval(predict_gold_pairs)
eval.cal_muc_types()
print(eval.precision(mode='strict'), eval.recall(mode='strict'))
print(eval.precision(mode='exact'), eval.recall(mode='exact'))
print(eval.precision(mode='partial'), eval.recall(mode='partial'))
print(eval.precision(mode='type'), eval.recall(mode='type'))
