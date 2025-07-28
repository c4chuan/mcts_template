import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def extract_doc_tree_from_pdf(pdf_path, page_numbers, regex_list):
    """
    根据 PDF 的页码范围提取文本，并利用 regex_list 指定的各级切分符构建文本树。

    参数：
      pdf_path: PDF 文件路径
      page_numbers: (起始页, 终止页) 注意：页码从1开始
      regex_list: 正则表达式列表，不同的正则表达式表示不同层级的分隔符，
                  顺序表示从高层到低层。例如：
                  [
                      "^[一二三四五六七八九十]+、$",   # 第一层标题，如 “一、”
                      "（[一二三四五六七八九十]+）",    # 第二层标题，如 “（一）”
                      "^\d+\.$"                     # 第三层标题，如 “1.”
                  ]

    返回：
      文本树，形如：
      [
          {
              "value": "一、  厂站、线路调度命名原则",
              "children": [
                  {
                      "value": "(一)  发电厂、变电站",
                      "children": [
                          {
                              "value": "1、  发电厂、变电站的调度命名一般以电厂、变电站所在地的实际地名（2~3个汉字）命名。",
                              "children": []
                          }
                      ]
                  }
              ]
          }
      ]
    """
    all_text_list = []
    # 注意：extract_pages 的 page_numbers 参数中页码是从 0 开始的
    for page_layout in extract_pages(pdf_path, page_numbers=range(page_numbers[0] - 1, page_numbers[1])):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                all_text_list.append(element.get_text())
    # 将所有页的文本合并成一个大字符串
    all_text = ''.join(all_text_list)

    def build_tree(text, regex_list):
        """
        递归构建文本树：
          - regex_list[0]为当前层级的标题切分符，
          - 在找到的每个标题处，将该部分文本作为一个节点，
            再用 regex_list[1:] 递归处理标题后的内容生成子节点。
        """
        # 如果没有更多切分规则，则返回整个文本作为一个叶子节点
        if not regex_list:
            return [{"value": text.strip(), "children": []}] if text.strip() else []

        current_pattern = regex_list[0]
        # 在当前文本中寻找本级标题的匹配位置
        matches = list(re.finditer(current_pattern, text))
        nodes = []

        # 如果当前级别未匹配到标题，则尝试用下一级的规则继续切分，
        # 如果下级也没有，则直接作为叶子节点返回
        if not matches:
            lower_nodes = build_tree(text, regex_list[1:])
            if lower_nodes:
                return lower_nodes
            else:
                return [{"value": text.strip(), "children": []}] if text.strip() else []

        # 如果标题前还有未切分的部分，也作为一个节点加入（例如前言、引言）——不加入
        # if matches[0].start() > 0:
        #     pre_text = text[:matches[0].start()].strip()
        #     if pre_text:
        #         nodes.append({"value": pre_text, "children": []})

        # 逐个遍历匹配到的标题，划分区段
        for i, match in enumerate(matches):
            section_start = match.start()
            section_end = matches[i+1].start() if i + 1 < len(matches) else len(text)
            section_text = text[section_start:section_end].strip()

            # 为了区分“标题内容”和“子节点内容”，我们在当前区段中查找下一层（如果有）的标题标记
            if len(regex_list) > 1:
                next_pattern = regex_list[1]
                m = re.search(next_pattern, section_text)
                if m:
                    header = section_text[:m.start()].strip()
                    content = section_text[m.start():].strip()
                else:
                    header = section_text
                    content = ""
            else:
                header = section_text
                content = ""

            # 递归构建子节点（下一级规则）
            children = build_tree(content, regex_list[1:]) if content else []
            nodes.append({"value": header, "children": children})

        return nodes

    tree = build_tree(all_text, regex_list)
    return tree

