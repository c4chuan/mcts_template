from doc2tree.doc_parse import DocTree
from mcts_base.mcts_doc_tree import LLMNode
from mcts_base.mcts_backbone import MCTS
from config import config
from llms.call_llms import CallQwenVL
import requests
if __name__ == '__main__':
    doc_tree = DocTree(config.Doc_parse)
    root_node = doc_tree.parse_doc_tree()
    print(root_node)
    mcts = MCTS()
    while True:
        for _ in range(4):
            mcts.do_iteration(root_node)
        best_node = mcts.choose(root_node)
        root_node = best_node
        if best_node.is_terminal():
            break
    print(best_node.value)