import math
from abc import ABC, abstractmethod
from collections import defaultdict

class MCTS(ABC):
    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int) # Q存储每个节点历史积累的奖励值
        self.N = defaultdict(int) # N存储每个节点被访问的次数
        self.children = dict()
        self.exploration_weight = exploration_weight

    def _select(self, node):
        """"""
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]: # 如果这个节点没被expand过或者没有子节点，则返回路径
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)

    def _expand(self, node):
        """将node的子节点加入到树中"""
        if node in self.children:
            return
        self.children[node] = node.find_children()

    def _rollout(self,node): # 等同于simulate
        """从node出发，随机选择子节点，直到到达叶节点计算reward值"""
        while True:
            if node.is_terminal():
                return node.reward()
            node = node.find_random_child()

    def _backpropagate(self, path, reward):
        """将reward值回传到所有父节点"""
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward

    def do_iteration(self,node):
        """匹配蒙特卡洛树搜索的过程"""
        path = self._select(node)
        leaf = path[-1]
        self._expand(leaf)
        reward = self._rollout(leaf)
        self._backpropagate(path, reward)

    def choose(self, node):
        """选择一个奖励值高的node执行"""
        if node not in self.children: # 如果没有被探索过，那只能随即找了
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float('inf')
            return self.Q[n] / self.N[n]
        return max(self.children[node], key=score)

    def _uct_select(self,node):
        """选择该节点下，uct值最大的那个节点"""
        # 判断是不是要选择的节点都是探索过的
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])
        def uct(n):
            return n.Q[n] / n.N[n] + self.exploration_weight * math.sqrt(log_N_vertex / n.N[n]) # 平均奖励+探索程度
        return max(self.children[node], key=uct) # 返回这个节点下面的子节点中，uct值最大的那个节点



class Node(ABC):
    """任意一种可用于上述MCTS搜索框架的node应该实现以下方法"""
    @abstractmethod
    def find_children(self):
        pass

    @abstractmethod
    def find_random_child(self):
        pass

    @abstractmethod
    def is_terminal(self):
        pass

    @abstractmethod
    def reward(self):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    def __eq__(node1, node2):
        pass