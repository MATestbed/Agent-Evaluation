import os

class Checkpoint:
    def __init__(self, pic_id, keyword, node_id):
        self.pic_id = pic_id
        self.keyword = keyword
        self.node_id = node_id
        self.matched = False
        self.capture_id = None

class Checkpoints:
    def __init__(self, checkpoint_dir):
        self.checkpoint_ls,self.installed_ls = _get_checkpoint_list(checkpoint_dir) 

    #     # return checkpoint pic_id list
    # def get_fuzzy_match_list(self):
    #     fuzzy_match_list = []
    #     for i in range(len(self.checkpoint_list)):
    #         if self.checkpoint_list[i].pic_id not in fuzzy_match_list:
    #             fuzzy_match_list.append(self.checkpoint_list[i].pic_id)
    #     return fuzzy_match_list
    
    def get_pic_exactly_match_list(self, pic_id):
        """
        function: 根据pic_id, 返回该pic_id下的exactly checkpoint list
        input: pic_id 标准流程中的某一步的state
        output: exactly_match_list: 该pic_id下的exactly checkpoint list
        """
        exactly_match_list = []
        for i in range(len(self.checkpoint_ls)):
            if self.checkpoint_ls[i].pic_id == pic_id:
                exactly_match_list.append(self.checkpoint_ls[i])
        return exactly_match_list


def _get_checkpoint_list(checkpoint_dir):
    """
    function: 根据标注完的文件夹, 返回checkpoint列表
    input: checkpoint_dir: 标注完之后的文件夹
    output: checkpoint_list: checkpoint列表
    """
    checkpoint_file_list = [f for f in os.listdir(checkpoint_dir) if f.split(".")[-1] == "text"]
    checkpoint_file_list.sort(key=lambda x: int(x.split(".")[0][:-7]))
    checkpoint_ls = []
    installed_ls = []
    for checkpoint_file in checkpoint_file_list:
        pic_id = checkpoint_file.split(".")[0][:-7]
        # 每个文件中的内容格式为 "keyword<content>|keyword<content>|keyword<content>|..."
        checkpoint_file_path = os.path.join(checkpoint_dir, checkpoint_file)
        with open(checkpoint_file_path, "r") as f:
            content = f.read()
            split_content = [item.strip() for item in content.split('|') if item]
            # 进一步解析每个字符串
            # parsed_content = []
            for item in split_content:
                # 格式总是 "keyword<content>"
                parts = item.split('<')
                if len(parts) == 2:
                    keyword, content = parts[0], parts[1].rstrip('>')
                    keyword = keyword.strip().lower()
                    if keyword == "check_install":
                        installed_ls.append(Checkpoint(int(pic_id), keyword, str(content).lower()))
                    else:
                        checkpoint_ls.append(Checkpoint(int(pic_id), keyword, int(content)))
                    # parsed_content.append(Checkpoint(int(pic_id), keyword, int(content)))
        # checkpoint_list = checkpoint_ls + parsed_content
    
    return checkpoint_ls, installed_ls


def _print_checkpoint_list(checkpoint_list):
    """
    function: 打印checkpoint列表
    input: checkpoint_list: checkpoint列表
    """
    for i in range(len(checkpoint_list)):
        print(f"checkpoint {i}:")
        print(f"pic_id: {checkpoint_list[i].pic_id}")
        print(f"keyword: {checkpoint_list[i].keyword}")
        print(f"node_id: {checkpoint_list[i].node_id}")
        print(f"matched: {checkpoint_list[i].matched}")
        print(f"capture_id: {checkpoint_list[i].capture_id}")
        print("-------------------------")


    
if __name__ == "__main__":
    checkpoint_dir = "/data/jxq/mobile-agent/aitw_replay_data/trace_24"
    checkpoint_ls = Checkpoints(checkpoint_dir)
    _print_checkpoint_list(checkpoint_ls.checkpoint_ls)
    _print_checkpoint_list(checkpoint_ls.installed_ls)
