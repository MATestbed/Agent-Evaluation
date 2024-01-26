# 首先实现最基础常见的textbox<id>的精确匹配 获取特征 + 搜索xml树 
from lxml import etree
import xml.etree.ElementTree as ET
import json
import os
import logging
import re
from sentence_similarity import check_sentence_similarity

# textbox
def _get_distinct_features_and_text(checkpoint_json_fp,node_id):
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    resource_id = str(checkpoint_json_data[node_id]['resource-id'])
    bounds= str(checkpoint_json_data[node_id]['bounds'])

    text = str(checkpoint_json_data[node_id]['text'])
    content_desc = str(checkpoint_json_data[node_id]['content-desc'])
    if text == "":
        text = content_desc

    distinct_feature = resource_id
    if resource_id == "":
        distinct_feature = bounds

    return distinct_feature, text

def _get_bounds_and_text(checkpoint_json_fp,node_id):
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    bounds= str(checkpoint_json_data[node_id]['bounds'])

    text = str(checkpoint_json_data[node_id]['text'])
    content_desc = str(checkpoint_json_data[node_id]['content-desc'])
    if text == "":
        text = content_desc

    return bounds, text

def _traverse_xml_tree(xml_fp):
    parser = etree.XMLParser(recover=True,encoding='utf-8')  # 使用宽容的解析器
    tree = etree.parse(xml_fp, parser)  # 解析 XML
    root = tree.getroot()

    # tree = ET.parse(xml_fp)
    # root = tree.getroot()
    result = []
    def traverse(node):
        if len(node) == 0:
            if node.get('text') or node.get('content-desc'):
                if 'button' not in str(node.get('class')).lower() and 'image' not in str(node.get('class')).lower():
                    node_data = {
                        'text': node.get('text'),
                        'resource-id': node.get('resource-id'),
                        'content-desc': node.get('content-desc'),
                        'bounds': node.get('bounds')
                    }
                    result.append(node_data)
        else:
            for child in node:
                traverse(child)
    traverse(root)

    return result

def _parse_bounds(bounds):
    """
    input: str([12,14][1080,2274])
    output: list of int [12,14,1080,2274]
    """
    # 首先去除字符串两端的方括号
    bounds = bounds[1:-1]
    
    # 然后以 '][' 分割字符串，得到中间的数字部分
    numbers_str = bounds.split('][')
    
    # 分割每一部分的数字，并将结果扁平化成一个列表
    result = []
    for num_pair in numbers_str:
        nums = num_pair.split(',')
        result.extend([int(num) for num in nums])
    
    return result


def _is_in_bounds(captured_bounds, checkpoint_bounds,expand_ratio=10):
    """
    function: check if captured_bounds is in expand checkpoint_bounds
    input: list of int [x1,y1,x2,y2]
    output: bool
    """

    
    captured_bounds = _parse_bounds(captured_bounds)
    checkpoint_bounds = _parse_bounds(checkpoint_bounds)

    checkpoint_center_x = (checkpoint_bounds[0] + checkpoint_bounds[2]) / 2
    checkpoint_center_y = (checkpoint_bounds[1] + checkpoint_bounds[3]) / 2
    checkpoint_bound_height = checkpoint_bounds[3] - checkpoint_bounds[1]

    expand_bound = [0,0,1080,checkpoint_center_y + checkpoint_bound_height/2 * expand_ratio]

    logging.info(f"textbox search expand_bound: {str(expand_bound)}")

    if captured_bounds[0] >= expand_bound[0] and captured_bounds[1] >= expand_bound[1] and captured_bounds[2] <= expand_bound[2] and captured_bounds[3] <= expand_bound[3]:
        return True
    else:
        return False

def _find_EditText_and_TextView(xml_fp, bounds):
    """
    function : find all EditText class in xml
    input: xml file path, checkpoint bounds example str([0,0][1080,2274])
    output: list of EditText class text 
    """
    # android.widget.EditText
    parser = etree.XMLParser(recover=True,encoding='utf-8')  # 使用宽容的解析器
    tree = etree.parse(xml_fp, parser)  # 解析 XML
    root = tree.getroot()

    result = []
    def traverse(node):
        if len(node) == 0:
            if node.get('class') == 'android.widget.EditText' or node.get('class') == 'android.widget.TextView':
                bounds_temp = node.get('bounds',None)
                if _is_in_bounds(bounds_temp, bounds):
                    text_temp = node.get('text',None)
                    if not text_temp:
                        text_temp = node.get('content-desc',None)
                    result.append(text_temp)
        else:
            for child in node:
                traverse(child)
    traverse(root)

    return result

def _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp):

    bounds, text = _get_bounds_and_text(checkpoint_json_fp, node_id)
    # 遍历captured_xml_fp 找到所有符合条件的节点

    result = _find_EditText_and_TextView(captured_xml_fp, bounds)
    
    logging.info(f"Total EditText number:{len(result)}")
    # 对比
    for edittext in result:
        similarity, status = check_sentence_similarity(text, edittext, threshold=0.8)
        if status:
            logging.info(f"text exactly match successfully: checkpoint text:{text} == captured text:{edittext}")
            return True, edittext
        else:
            logging.info(f"text exactly match failed: checkpoint text:{text} != captured text:{edittext}")
            continue
    
    return False, ""


# def _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp):

#     distinct_feature,text = _get_distinct_features_and_text(checkpoint_json_fp,node_id)
#     # 遍历captured_xml_fp 找到所有符合条件的节点

#     result = _find_EditText(captured_xml_fp)

#     result = _traverse_xml_tree(captured_xml_fp)
    
#     # 对比
#     for node in result:
#         xml_feature = str(node['resource-id'])
#         if str(node['resource-id']) == "":
#             xml_feature = str(node['bounds'])

#         if xml_feature == distinct_feature:
#             similarity, status = check_sentence_similarity(text, str(node['text']), threshold=0.8)
#             # if str(node['text']) == text:
#             if status:
#                 logging.info(f"text exactly match successfully: checkpoint text:{text} == captured text:{node['text']}")
#                 return True, node['text']
#             else:
#                 logging.info(f"text exactly match unsuccessfully: checkpoint text:{text} != captured text:{node['text']}")
#                 return False, ""
            
#     return False, ""

# click
def _get_click_point(captured_action_fp):
    with open(captured_action_fp) as f:
        action_str = f.read()
    # action_str:CLICK|[0.5, 0.2403125]|NULL|1440|3200
    width = int(action_str.split('|')[3])
    height = int(action_str.split('|')[4])
    click_x = eval(action_str.split('|')[1].split(',')[0].split('[')[1])
    click_y = eval(action_str.split('|')[1].split(',')[1].split(']')[0])
    click_x = int(click_x * width)
    click_y = int(click_y * height)
    return click_x, click_y

def _is_click(captured_action_fp):
    with open(captured_action_fp) as f:
        action_str = f.read()
    action = str(action_str.split('|')[0])
    if action.lower() == "click":
        return True
    else:
        return False
    
def _get_bound(checkpoint_json_fp,node_id):
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    bounds= str(checkpoint_json_data[node_id]['bounds'])
    # bounds = "[0,0][1080,1920]"
    x1 = int(bounds.split('[')[1].split(',')[0])
    y1 = int(bounds.split('[')[1].split(',')[1].split(']')[0])
    x2 = int(bounds.split('[')[2].split(',')[0])
    y2 = int(bounds.split('[')[2].split(',')[1].split(']')[0])
    return x1, y1, x2, y2
    
def _click_exact_match(checkpoint_json_fp, node_id, captured_action_fp):
    # 防止最后一个界面fuzzy match成功，但是没有action文件
    if not os.exists(captured_action_fp):
        return False

    if not _is_click(captured_action_fp):
        return False
    
    x1, y1, x2, y2 = _get_bound(checkpoint_json_fp,node_id)
    click_x, click_y = _get_click_point(captured_action_fp)

    if click_x >= x1 and click_x <= x2 and click_y >= y1 and click_y <= y2:
        logging.info(f"click exactly match successfully: ({click_x}, {click_y}) in [{x1}, {y1}][{x2}, {y2}]")
        return True
    else:
        logging.info(f"click exactly match failed: ({click_x}, {click_y}) not in [{x1}, {y1}][{x2}, {y2}]")
        return False

# activity
def _parse_checkpoint_activity(checkpoint_activity_fp):
    with open(checkpoint_activity_fp) as f:
        checkpoint_activity_str = f.read()
    # 使用正则表达式来匹配大括号内的内容
    pattern = r"mObscuringWindow=Window{(.+?)}"
    match = re.search(pattern, checkpoint_activity_str)
    # 如果匹配成功
    if match:
        content_inside_braces = match.group(1)
        checkpoint_activity = content_inside_braces.split()[-1]
    else:
        checkpoint_activity = "No match found."
    return checkpoint_activity


def _activity_exact_match(checkpoint_activity_fp, captured_activity_fp):
    checkpoint_activity = _parse_checkpoint_activity(checkpoint_activity_fp)
    with open(captured_activity_fp) as f:
        captured_activity = f.read()
    if str(checkpoint_activity).lower() == str(captured_activity).lower():
        logging.info(f"activity exactly match successfully: {checkpoint_activity}")
        return True
    else:
        logging.info(f"activity exactly match failed: {checkpoint_activity} != {captured_activity}")
        return False


def exactly_match(checkpoint_dir, pic_id, keyword, node_id, captured_dir, index):
    """
    input:
    checkpoint_dir: 标注完之后的文件夹
    pic_id: 图片id
    keyword: 标注的关键字
    node_id: 节点id
    captured_dir: 抓取的文件夹
    index: 抓取的图片id
    output: return True or False
    """
    keyword = str(keyword).lower()
    if keyword == "textbox":
        checkpoint_json_fp = os.path.join(checkpoint_dir, f"{pic_id}.json")
        captured_xml_fp = os.path.join(captured_dir, "captured_data","xml", f"{index}.xml")
        state, text = _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp)
        return state

    elif keyword == "click":
        checkpoint_json_fp = os.path.join(checkpoint_dir, f"{pic_id}.json")
        captured_action_fp = os.path.join(captured_dir, "captured_data","action", f"{index}.action")
        state = _click_exact_match(checkpoint_json_fp, node_id, captured_action_fp)
        return state
    
    elif keyword == "fuzzy_match":
        # logging.info("fuzzy have matched successfully")
        return True
    
    elif keyword == "activity":
        checkpoint_activity_fp = os.path.join(checkpoint_dir, f"{pic_id}.activity")
        captured_activity_fp = os.path.join(captured_dir, "captured_data","activity", f"{index}.activity")
        state = _activity_exact_match(checkpoint_activity_fp, captured_activity_fp)
        return state
    
if __name__ == "__main__":
    # checkpoint_json_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.json"
    # node_id = 32
    # captured_xml_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.xml"
    # state, text = _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp)
    # if state:
    #     print(f"match successfully: {text}")
    # else:
    #     print("match failed")
    # x,y = _get_click_point("/data/wangshihe/AgentTestbed/AppAgent/tasks/task_Chrome_2024-01-16_21-40-04/151130279482320639/captured_data/action/0.action")
    # print(f"x: {x}, y: {y}")
    # _get_bound("/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.json", 32)

    bounds = _parse_bounds("[0,0][1080,1920]")





