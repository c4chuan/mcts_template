import re
from llms.call_llms import CallQwenVL
from config import config
from utils.prompts import REWARD_PROMPT
import random
class DocTreeNode:
    def __init__(self, value):
        """
        初始化节点，节点的value值代表的是规则文本
        :param value:
        """
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self, level=0):
        """
        递归地返回树的字符串表示，方便打印整个树结构

        :param level: 当前节点所在的层级，用于缩进
        """
        ret = " " * (level * 2) + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

class LLMNode(DocTreeNode):
    def __hash__(self):
        return hash(self.value)
    def __eq__(self, other):
        return self.value == other.value
    def _get_cat_rule(self):
        """将搜索到的规则路径拼接起来"""
        if self.value == "root":
            return ""
        else:
            return self.parent._get_cat_rule()+"\n"+self.value

    def find_children(self):
        return self.children

    def find_random_child(self):
        return random.choice(self.children)

    def is_terminal(self):
        if self.children == []:
            return True
        else:
            return False

    def reward(self):
        qwenvl = CallQwenVL()
        cat_rule = self._get_cat_rule()
        response = qwenvl.infer(config.image_path, REWARD_PROMPT.format(cat_rule))
        reward = re.search(r"分数：\d",response)
        if reward:
            reward = int(reward.group(0)[3:])
        else:
            reward = 0
        # reward = random.randint(0,5)
        return reward