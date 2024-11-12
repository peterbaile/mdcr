# MDCR: A Dataset for Multi-Document Conditional Reasoning

If you find our data, code, or the paper useful, please cite the paper:
```
@article{chen2024mdcr,
  title={MDCR: A Dataset for Multi-Document Conditional Reasoning},
  author={Chen, Peter Baile and Zhang, Yi and Liu, Chunwei and Gupta, Sejal and Kim, Yoon and Cafarella, Michael},
  journal={arXiv preprint arXiv:2406.11784},
  year={2024}
}
```


## Dataset

* `docs.json` (list of dictionaries): a list of benefit documents crawled from the open web. Each dictionary includes the document `title` (string), `url` (string), and `contents` (list of strings)
* `parsed.json` (list of dictionaries): a list of conditions generated from sentences in `docs.json` (Some sentences might not be describing conditions and some might include multiple conditions. Details are described in Appendix A.1 in the paper.)
  * `conditions` (dictionary): the key in the form of `c[int]` (1-indexed) refers to a condition mentioned in the document; the other keys that start with `and`/ `or` refer to the *AND/OR* relationships of these conditions. `all (and)` is the expression that represents the entire set of conditions need to be satisfied.
    * Each condition (`c[int]`) is mapped either (1) directly to some sentences in the document or (2) to part of sentences in the document. In case (1), the condition is mapped to an integer/ list of integers that are the indices of sentences in the document. In case (2), the condition is mapped to a string (part of the original sentence). Case (2) exists because some sentences in the document are clearly composed of multiple conditions, and thus we split the sentence into the constituent self-contained conditions.
  * `mapping` (dictionary): the key is the `c_idx`, and the value is the indices of sentences the condition is generated from. This is only needed for conditions that are mapped to strings in `conditions` dictionary (explained above). 
* `qs.json` (list of dictionaries): a list of user scenarios. Each dictionary includes the document indices `doc_ids` (list of integers), the specific conditions `given_conditions` (list of strings) and boolean values of these conditions `given_values` used to generate the scenario, as well as the actual user scenario `scenario` (string).
  * We consider three types of questions, which are defined as `QUESTIONS` in `utils.py`
    ```
    (1) Can I receive at least one of the following scholarship(s):,
    (2) Can I receive all the following scholarship(s):,
    (3) What is the maximum number of scholarship(s) I can receive out of the following scholarship(s):
    ```
* `rels.json` (dictionary): each key-value group describes the relationships among conditions between two documents. The key is a string concatnetation of the two `doc_ids` and the value is another dictionary where key is the string concatneation of the two `c_idx` from the two documents respectively (from `parsed.json`) and `rel` is the type of relationships, which can be *conflicting*, *equivalent*, *including*, and *included*.
  * For instance,
    ```
      {
        "1-2": {
          "c1-c2": {
            "rel": "conflicting"
          }
        }
      }
    ```
    means that `c1` in `doc1` and `c2` in `doc2` are conflicting.


<!-- ## Evaluation

Ground truth answers are not stored in files due to the large size, but they can be readily computed (and saved) by the following.

```python

```

## Benchmarking and analysis -->




## Contact
Your support in improving this dataset is greatly appreciated! If you have any questions or feedback, please send an email to peterbc@mit.edu.