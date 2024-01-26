from zss import simple_distance
import xml.etree.ElementTree as ET
from lxml import etree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io
import logging

class TreeNode:
    def __init__(self, label):
        self.label = label
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

def count_nodes(node):
    """
    统计树中所有节点的数量。
    :param node: 当前访问的TreeNode节点。
    :return: 树中节点的总数。
    """
    if node is None:
        return 0

    # 计数包括当前节点
    count = 1

    # 加上所有子节点的数量
    for child in node.children:
        count += count_nodes(child)

    return count

def print_tree(node, level=0, stream=None):
    """
    打印树中所有节点的信息，使用换行符来表示层级。
    :param node: 当前访问的TreeNode节点。
    :param level: 当前节点的层级，用于格式化输出。
    :param stream: 字符串流对象。
    """
    if stream is None:
        stream = io.StringIO()

    indent = "  " * level
    if level > 0:
        stream.write("\n")
    stream.write(f"{indent}{node.label}")

    for child in node.children:
        print_tree(child, level + 1, stream)

    return stream

def tree_to_string(root):
    """
    将树结构转换为字符串。
    :param root: 树的根节点。
    :return: 树的字符串表示。
    """
    stream = print_tree(root)
    return stream.getvalue()

def tree_to_file(root, filename):
    """
    将树结构输出到文件。
    :param root: 树的根节点。
    :param filename: 输出文件的名称。
    """
    with open(filename, 'w', encoding='utf-8') as file:
        stream = print_tree(root)
        file.write(stream.getvalue())

def element_to_tree(element):
    # 构建包含所需属性的标签字符串

    # attributes = [
    #     f"class: {element.get('class', '')}" ,
    #     f"text: {element.get('text', '')}" ,
    #     f"resource-id: {element.get('resource-id', '')}" ,
    #     f"content-desc: {element.get('content-desc', '')}",
    #     f"bounds: {element.get('bounds', '')}"
    # ]

    attributes = [
        # element.get('class', ''),
        element.get('text', ''),
        element.get('resource-id', ''),
        element.get('content-desc', ''),
        element.get('bounds', '')
    ]
    label = f"{element.tag} {' '.join(attributes)}"
    # label = element.tag
    
    # 创建TreeNode实例
    node = TreeNode(label.strip())

    # 递归处理所有子节点
    for child in element:
        child_node = element_to_tree(child)
        node.add_child(child_node)

    return node

def xml_to_string(file):
    # with open(file, 'r', encoding='utf-8') as f:

    parser = etree.XMLParser(recover=True,encoding='utf-8')  # 使用宽容的解析器
    tree = etree.parse(file, parser)  # 解析 XML
    root = tree.getroot()

    # tree = ET.parse(file, parser=ET.XMLParser(encoding='utf-8'))

    # tree = ET.parse(file)
    # root = tree.getroot()
    return ET.tostring(root, encoding='utf-8', method='xml')

def cosine_distance(xml1, xml2):
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform([xml1, xml2])
    return cosine_similarity(vectors)[0][1]

def tree_edit_distance(xml1, xml2):
    tree1 = element_to_tree(ET.fromstring(xml1))
    tree2 = element_to_tree(ET.fromstring(xml2))
    distance  = simple_distance(tree1, tree2)

    tree_edit_distance_ratio = distance/max(count_nodes(tree1),count_nodes(tree2))
    
    # print("Tree Edit Distance:", distance)
    # print("tree1 node number:", count_nodes(tree1))
    # print("tree2 node number:", count_nodes(tree2))
    # print("ratio:", distance/count_nodes(tree1))
    return distance,tree_edit_distance_ratio

def get_simplfied_tree(xml):
    """获取简化之后的tree"""
    tree = element_to_tree(ET.fromstring(xml))
    return tree

def get_xml_fuzzy_match(xml1_path,xml2_path):
    """"
    根据cossine similarity和tree edit distance match xml
    input xml path
    return true or false
    """
    COSSINE_BOUND = 0.75
    TREE_EDIT_RATIO_BOUND = 0.4

    xml1 = xml_to_string(xml1_path)
    xml2 = xml_to_string(xml2_path)
    logging.info(f"xml similarity COSSINE_BOUND: {COSSINE_BOUND}")
    # # cosine_similarity and tree_edit_distance_ratio
    # cosine_similarity = cosine_distance(tree_to_string(get_simplfied_tree(xml1)), tree_to_string(get_simplfied_tree(xml2)))
    # distance, tree_edit_distance_ratio= tree_edit_distance(xml1, xml2)
    # logging.info(f"fuzzy match: {xml1_path} vs {xml2_path}: cosine_similarity: {cosine_similarity}, tree_edit_distance_ratio: {tree_edit_distance_ratio}")
    # if cosine_similarity > COSSINE_BOUND and tree_edit_distance_ratio < TREE_EDIT_RATIO_BOUND:
    #     return True
    # else:
    #     return False
    
    # cosine_similarity only
    cosine_similarity = cosine_distance(tree_to_string(get_simplfied_tree(xml1)), tree_to_string(get_simplfied_tree(xml2)))
    logging.info(f"fuzzy match: {xml1_path} vs {xml2_path}: cosine_similarity: {cosine_similarity}")
    if cosine_similarity > COSSINE_BOUND:
        return True
    else:
        return False



if __name__ == '__main__':

    xml1 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/10.xml')
    # xml2 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/0.xml')
    xml2 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/7.xml')
    

    distance = tree_edit_distance(xml1, xml2)
    
    similarity = cosine_distance(xml1, xml2)
    print("Cosine Similarity:", similarity)
    
    simp_tree1 = get_simplfied_tree(xml1)
    simp_tree2 = get_simplfied_tree(xml2)

    tree_to_file(simp_tree1, './tree1.txt')
    tree_to_file(simp_tree2, './tree2.txt')
    similarity2 = cosine_distance(tree_to_string(simp_tree1), tree_to_string(simp_tree2))
    print("Cosine Similarity2:", similarity2)
