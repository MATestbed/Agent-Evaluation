from comparison_algorithm import comparison_algorithm
import time
import logging
import os
import pandas as pd

# agent = "auto-ui"
agent = "appagent"
log_dir_path = f"/data/jxq/mobile-agent/comparison_algorithm/log/{agent}"

# 获取当前时间
current_time = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(f'{log_dir_path}/comparison_algorithm_{formatted_time}.log', 'w'),
                            logging.StreamHandler()])

# instruction_fp = "/data/jxq/all_instruction.csv"
instruction_fp = "/data/jxq/all_instruction_appagent.csv"
top_checkpoint_dir = f"/data/jxq/mobile-agent/aitw_replay_data/general/"
# top_capture_dir = "/data/jxq/mobile-agent/agent-captured_data/auto-ui"

#agent_app 
top_capture_dir = "/data/wangshihe/AgentTestbed/AppAgent/tasks-240126-1/"
second_capture_dir_ls = [os.path.join(top_capture_dir,dir) for dir in os.listdir(os.path.join(top_capture_dir)) if os.path.isdir(os.path.join(top_capture_dir,dir))]
captured_epsoide_dir = [os.path.join(second_capture_dir,dir) for second_capture_dir in second_capture_dir_ls for dir in os.listdir(second_capture_dir) if os.path.isdir(os.path.join(second_capture_dir,dir))]


checkpoint_dir_ls = []
captured_dir_ls = []

instruction_data = pd.read_csv(instruction_fp)
total_instruction_num = len(instruction_data)
testbed_judge_success_state = []
output_data = pd.DataFrame(columns=["episode_id", "instruction", "success_flag"])

for index, row in instruction_data.iterrows():
    trace_temp = row["trace_folder_path"].split("/")[-1]
    checkpoint_dir_ls.append(os.path.join(top_checkpoint_dir, trace_temp))
    # captured_dir_ls.append(os.path.join(top_capture_dir, str(row["episode_id"])))
    
    for i in range(len(captured_epsoide_dir)):
        if str(row["episode_id"]) in captured_epsoide_dir[i]:
            captured_dir_ls.append(captured_epsoide_dir[i])
            break



for i, row in instruction_data.iterrows():
    checkpoint_dir = checkpoint_dir_ls[i]
    captured_dir = captured_dir_ls[i]

    logging.info(f"task {i}:{instruction_data.iloc[i]['instruction']}")
    logging.info(f"checkpoint_dir: {checkpoint_dir}")
    logging.info(f"captured_dir: {captured_dir}")

    if comparison_algorithm(checkpoint_dir, captured_dir):
        logging.info(f"comparison_algorithm successfully: {checkpoint_dir} and {captured_dir}")
        testbed_judge_success_state.append(True)
    else:
        logging.info(f"comparison_algorithm failed: {checkpoint_dir} and {captured_dir}")
        testbed_judge_success_state.append(False)

for index, row in instruction_data.iterrows():
    output_data.loc[index] = [str(row["episode_id"]), row["instruction"], testbed_judge_success_state[index]]

output_data.to_csv(f"/data/jxq/mobile-agent/comparison_algorithm/output_data/general/{agent}/{formatted_time}.csv", index=False)
logging.info(f"success_num: {testbed_judge_success_state.count(True)}")
logging.info(f"total_instruction_num: {total_instruction_num}")
logging.info(f"testbed judge success_rate: {testbed_judge_success_state.count(True)/total_instruction_num}")

# human_judegement = pd.read_csv("/data/jxq/mobile-agent/comparison_algorithm/output_data/general/auto-ui-task-human.csv")
# human_judegement_state = list(human_judegement["success_flag"])

# testbed_accuracy_state = [ts == hs for ts, hs in zip(testbed_judge_success_state,human_judegement_state)]
# logging.info(f"testbed_accuracy: {testbed_accuracy_state.count(True)/len(testbed_accuracy_state)}")

# testbed_tp = []
# testbed_fp = []
# testbed_tn = []
# testbed_fn = []

# for ts, hs in zip(testbed_judge_success_state,human_judegement_state):
#     if ts == True and hs == True:
#         testbed_tp.append(True)
#         testbed_fp.append(False)
#         testbed_fn.append(False)
#         testbed_tn.append(False)
#     elif ts == True and hs == False:
#         testbed_tp.append(False)
#         testbed_fp.append(True)
#         testbed_fn.append(False)
#         testbed_tn.append(False)
#     elif ts == False and hs == True:
#         testbed_tp.append(False)
#         testbed_fp.append(False)
#         testbed_fn.append(True)
#         testbed_tn.append(False)
#     elif ts == False and hs == False:
#         testbed_tp.append(False)
#         testbed_fp.append(False)
#         testbed_fn.append(False)
#         testbed_tn.append(True)

# logging.info(f"testbed true positive number: {testbed_tp.count(True)}")
# logging.info(f"testbed false positive numnber: {testbed_fp.count(True)}")
# logging.info(f"testbed false negative number: {testbed_fn.count(True)}")
# logging.info(f"testbed true negative number: {testbed_tn.count(True)}")



    





