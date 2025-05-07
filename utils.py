from typing import List
from tiger_utils import read_json
from itertools import combinations

QUESTIONS = {
  'scholarships': [
    'Can I receive at least one of the following scholarship(s):',
    'Can I receive all the following scholarship(s):',
    'What is the maximum number of scholarship(s) I can receive out of the following scholarship(s):'
  ]
}

def split_cond(cond: str, remove_c=False):
  doc_idx, c_idx = cond.split('-')
  doc_idx = int(doc_idx[3:])

  if remove_c:
    c_idx = int(c_idx.replace('c', ''))

  return doc_idx, c_idx

def conds_to_doc_idxs(doc_idxs: List[int], c_idxs: List[str]):
  doc_idxs_2 = set([split_cond(x)[0] for x in c_idxs])
  doc_idxs = set(doc_idxs)
  doc_idxs.update(doc_idxs_2)
  doc_idxs = list(doc_idxs)
  doc_idxs.sort()
  return doc_idxs

def stringfy_doc_idxs(doc_idxs: tuple[int], add_doc=True):
  if add_doc:
    return f'doc{doc_idxs[0]}-doc{doc_idxs[1]}'

  return f'{doc_idxs[0]}-{doc_idxs[1]}'

def load_rels(domain, doc_idxs: List[int]):
  rels_data = read_json(f'./data/{domain}/rels.json')
  
  rels_all = []
  potential_conflicts = []

  for doc_pair in list(combinations(doc_idxs, 2)) + [(doc_idx, doc_idx) for doc_idx in doc_idxs]:
    doc_pair = list(doc_pair)
    doc_pair.sort()
    doc_pair = tuple(doc_pair)
    doc_pair_str = stringfy_doc_idxs(doc_pair, add_doc=False)

    if doc_pair_str in rels_data:
      doc_a, doc_b = doc_pair
      rels = rels_data[doc_pair_str]

      for c_idxs in rels:
        if 'rel' in rels[c_idxs]:
          c_idx_0, c_idx_1 = c_idxs.split('-')
          if rels[c_idxs]['rel'] == 'included':
            rels_all.append((f'doc{doc_b}-{c_idx_1}', f'doc{doc_a}-{c_idx_0}', 'including'))
          elif rels[c_idxs]['rel'] == 'potentially conflicting':
            potential_conflicts.append((f'doc{doc_a}-{c_idx_0}', f'doc{doc_b}-{c_idx_1}'))
          else:
            rels_all.append((f'doc{doc_a}-{c_idx_0}', f'doc{doc_b}-{c_idx_1}', rels[c_idxs]['rel']))

  assert not any(x[-1] == 'included' for x in rels_all)
  
  return rels_all, potential_conflicts