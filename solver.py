# this file implements the solver that solve things on the atomic condition level (implemented in parser.json)

import json
import pyeda.inter as pyeda_tool
import re
from copy import deepcopy
from typing import List

def populate_bool_expr(domain: str, doc_idx: int) -> str:
  '''Given the dataset domain and the document index, returns the boolean expression (string) that indicates the overall satisfiability condition for the given document'''
  
  with open(f'./data/{domain}/parsed.json', encoding='utf-8') as f:
    docs = json.load(f)
  
  conds = docs[doc_idx]['conditions']
  expr_dict = {}

  for c_idx in conds:
    if not c_idx.startswith('c'):
      _expr = []

      for c_idx_2 in conds[c_idx]:
        if c_idx_2.startswith('c'):
          # use 's' as a separator between doc_idx and c_idx (pyeda doesn't allow non-characters)
          _expr.append(f'doc{doc_idx}s{c_idx_2}')
        else:
          _expr.append(expr_dict[c_idx_2])
      _expr = ' | '.join(_expr) if c_idx.startswith('or') else ' & '.join(_expr)
      _expr = f'({_expr})'
      expr_dict[c_idx] = _expr
  
  expr_all = expr_dict['all (and)']
  return expr_all

def populate_vals(expr: str, c_idxs: List[str], value: List[bool], rels):
  '''Given a boolean expression, c_idxs and their boolean values, as well as the condition relationships of this set of conditions,
  populate the boolean expression with the correct values of the c_idx.
  '''

  # replace conditions that directly appear in the boolean expression with the value
  for i, c_idx in enumerate(c_idxs):
    expr_c_idx = c_idx.replace('-', 's')
    if expr_c_idx in expr:
      expr = re.sub(fr"\b{expr_c_idx}\b", '1' if value[i] else '0', expr)

    for rel in rels:
      if c_idx in rel:
        other_idx = [x for x in rel[:2] if x != c_idx][0]
        expr_other_idx = other_idx.replace('-', 's')
        if expr_other_idx in expr:
          assert rel[-1] != 'included'

          if rel[-1] == 'conflicting' and value[i]:
            # we need to check for conflicts, if one of the values in the conflict is set to True, the other is definitely False
            # because there's no conflicting combs sampled, we don't have to worry about the values set twice
            expr = re.sub(fr"\b{expr_other_idx}\b", '0', expr)
          elif rel[-1] == 'equivalent':
            # two conditions are equivalent share the same value
            expr = re.sub(fr"\b{expr_other_idx}\b", '1' if value[i] else '0', expr)
          elif rel[-1] == 'including':
            # if condition A includes condition B, then B is True means A is true
            if c_idx == rel[1] and value[i]:
              expr = re.sub(fr"\b{expr_other_idx}\b", '1', expr)
            # or if A is False, then B is false
            elif c_idx == rel[0] and not value[i]:
              expr = re.sub(fr"\b{expr_other_idx}\b", '0', expr)
  return expr

def merge_expr(exprs: List[str]):
  '''Given multiple input boolean expressions, return an expression that merges all input expressions.'''
  return ' & '.join(exprs)

def forward_pass(expr:str):
  '''Given the input boolean expression, return the list of possible values that can be used to satisfy the input expression.'''
  raw_result = list(pyeda_tool.expr(expr).satisfy_all())
  if len(raw_result) == 0:
    return 'Infeasible'

  result = []
  for _r in raw_result:
    _r_new = [str(x).replace('s', '-') for x in _r if _r[x] == 1]
    _r_new.sort()
    result.append(_r_new)

  return result

# TODO: finish equivalence
def simplify_cond(cond, rels):
  cond_new = deepcopy(cond)
  
  for rel in rels:
    if rel[0] in cond_new and rel[1] in cond_new:
      if rel[-1] == 'including':
        cond_new.remove(rel[0])
      # elif rel[-1] == 'equivalent':
      #   deepcopy(cond).remove(rel[0])
      #   deepcopy(cond).remove(rel[1])
  return [cond_new]

def postprocess_output(conds, rels, check_conflicts: bool=True, simplify: bool=True):
  '''Given the answer from `forward_pass`, post_process the answers. If `check_conflicts=True`, remove condition groups that include
  conflicting conditions. If `simplify=True`, only keep one of the equivalent conditions and keep the included condition.
  If the output of the function is None, this means none of the condition groups can be satisfied. Otherwise, the output is a non-empty list.
  '''
  if conds == 'Infeasible':
    return None

  assert len(conds) != 0
  
  if all(len(x) == 0 for x in conds):
    return conds
  
  # simplify is only applied when check_conflicts is applied
  assert not (not check_conflicts and simplify)

  if not check_conflicts:
    return conds

  correct_conds = None
  for cond in conds:
    is_correct = True

    for rel in rels:
      if rel[0] in cond and rel[1] in cond and rel[-1] == 'conflicting':
        is_correct = False
        break
    
    if is_correct:
      if correct_conds is None:
        correct_conds = []
      
      if simplify:
        correct_conds += simplify_cond(cond, rels)
      else:
        correct_conds.append(cond)
  return correct_conds