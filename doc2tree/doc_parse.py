from doc2tree.pdf_tools import extract_doc_tree_from_pdf
from mcts_base.mcts_doc_tree import LLMNode
import numpy as np
import os

class DocTree:
    def __init__(self,config):
        self.data_path = config.data_path
        self.name = config.name
        self.save_parse = config.save_parse
        self.load_parse = config.load_parse
        self.root = LLMNode("root")
        self.API_KEY = config.api_key
        if self.load_parse:
            self._check_catalogs()

    def _get_rule_pages(self):
        """
        自动(现在还是手动定义分隔符)识别分隔符和页数
        :return:
        """
        # 这个自动识别页数和分隔符还需要调整
        # kimi = CallKimi(self.API_KEY)
        # content = kimi.call_with_file(GET_RULE_PAGE_NUMS,os.path.join(self.data_path,self.name))
        pages = (12,32)
        spliters = ["[一二三四五六七八九十]+、", "\([一二三四五六七八九十]+\)", "\d[、.] "]

        return pages,spliters

    def _check_catalogs(self):
        """
        检查需要parse的文档是否有对应的目录了，如果
        没有则新建一个，如果有则load
        :return:
        """
        if os.path.exists(os.path.join(self.data_path,self.name[:-4]+'.npy')):
            doc_tree = self._load_doc_tree()
            self._build_rule_tree(self.root, doc_tree)
            return self.root

    def _load_doc_tree(self):
        """
        从已存储的字典中load整颗文档树
        :return:
        """
        doc_tree_arr = np.load(os.path.join(self.data_path,self.name[:-4]+'.npy'),allow_pickle=True)
        return doc_tree_arr.tolist()

    def _save_doc_tree(self,doc_tree):
        """
        将整颗文档树保存到本地
        :return:
        """
        doc_tree_arr = np.array(doc_tree)
        np.save(os.path.join(self.data_path,self.name[:-4]+'.npy'),doc_tree_arr,allow_pickle=True)

    def parse_doc_tree(self):
        """
        解析整颗文档树，生成规则树
        :return:
        """
        pages,spliters = self._get_rule_pages()
        # 注意这里的spliters一定是按照标题等级来的
        doc_tree = extract_doc_tree_from_pdf(os.path.join(self.data_path,self.name),pages,spliters)
        if self.save_parse:
            self._save_doc_tree(doc_tree)
        self._build_rule_tree(self.root,doc_tree)
        return self.root

    def _build_rule_tree(self,parent_node,children_relations):
        for children_relation in children_relations:
            temp_child = LLMNode(children_relation["value"])
            temp_child.parent = parent_node
            parent_node.add_child(temp_child)
            self._build_rule_tree(temp_child,children_relation["children"])

    def print_tree(self):
        print(self.root)



