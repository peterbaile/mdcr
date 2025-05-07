from copy import deepcopy
from itertools import combinations
from typing import List

from utils import load_rels, conds_to_doc_idxs
from solver import populate_bool_expr, populate_vals, forward_pass, postprocess_output, merge_expr

def get_gold_ans_any(gs, scenario: List[str], value: List[bool], rels):
  ans_all = []

  # check satisfiability for each outcome
  for doc_idx in gs:
    gs[doc_idx] = populate_vals(gs[doc_idx], scenario, value, rels)
    ans = postprocess_output(forward_pass(gs[doc_idx]), rels)
    
    if ans:
      ans_all += ans
  if len(ans_all) == 0:
    return {'answer': 'No'}
  
  return {'answer': 'Yes', 'conditions': ans_all}

def get_gold_ans_all(gs, scenario: List[str], value: List[bool], rels):
  g = merge_expr(list(gs.values()))
  g = populate_vals(g, scenario, value, rels)
  ans = postprocess_output(forward_pass(g), rels)
  
  if ans is None:
    return {'answer': 'No'}
  else:
    return {'answer': 'Yes', 'conditions': ans}

def get_gold_ans_max(domain, doc_idxs, scenario: List[str], value: List[bool], rels):
  # check possibility of obtaining each combination of outcomes
  results = {}
  
  for num_docs in range(1, len(doc_idxs) + 1):
    result = {}
    for doc_group in list(combinations(doc_idxs, num_docs)):
      gs = [populate_bool_expr(domain, doc_idx) for doc_idx in doc_group]
      
      if len(gs) >= 2:
        g = merge_expr(gs)
      else:
        g = gs[0]

      g = populate_vals(g, scenario, value, rels)
      ans = postprocess_output(forward_pass(g), rels)
      
      if ans is not None:
        result[tuple(doc_group)] = ans
    
    results[num_docs] = deepcopy(result)

  # check from max number to 0
  for num_docs in range(len(doc_idxs), -1, -1):
    if num_docs == 0:
      ans = {'answer': 0}
      break

    if len(results[num_docs]) != 0:
      ans = {'answer': num_docs, 'conditions': sum(results[num_docs].values(), [])}
      break

  return ans

def get_gold_ans(domain: str, doc_idxs: List[int], q_idx: int, scenario: List[str], value: List[bool]):
  '''Given the domain, question, and question type, returns the conditional answer that includes both a short answer and the corresponding conditions to support the short answer (the conditions are None if the short answer is No or 0).
  specified in utils.py
  q_idx = 0 --> can I receive at least one?\n
  q_idx = 1 --> can I receive all?\n
  q_idx = 2 --> what is the max number?\n'''

  assert q_idx in [0, 1, 2], 'question type has to be either 0, 1, or 2'

  # load condition relationships
  rels, _ = load_rels(domain, conds_to_doc_idxs(doc_idxs, scenario))

  gs = {doc_idx: populate_bool_expr(domain, doc_idx) for doc_idx in doc_idxs}

  if q_idx == 0:
    return get_gold_ans_any(gs, scenario, value, rels)
  
  if q_idx == 1:
    return get_gold_ans_all(gs, scenario, value, rels)
  
  if q_idx == 2:
    return get_gold_ans_max(domain, doc_idxs, scenario, value, rels)
  
if __name__ == '__main__':
  # compute gold answer for each question and question type
  from tiger_utils import read_json
  from tqdm import tqdm
  qs = read_json(f'./data/scholarships/qs.json')
  
  for q_idx, q in enumerate(tqdm(qs)):
    doc_idxs = q['doc_idxs']
    scenario = q['given_conditions']
    value = q['given_values']
    ans = get_gold_ans('scholarships', doc_idxs, 0, scenario, value)
    ans = get_gold_ans('scholarships', doc_idxs, 1, scenario, value)
    ans = get_gold_ans('scholarships', doc_idxs, 2, scenario, value)
