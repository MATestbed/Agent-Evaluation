import logging 
import os
from get_checkpoint_list import Checkpoint
import pandas as pd

def check_install(checkpoint_installed_ls,captured_dir):
    """
    function: check agent install task is success or not
    input: checkpoint_installed_ls: each element is a checkpoint object
           captured_dir: captured data dir
    output: True or False
    """
    captured_installed_fp = os.path.join(captured_dir, "captured_data", "installed_apps", "installed_apps.txt")
    captured_installed_packages = []
    with open(captured_installed_fp, "r") as f:
        for line in f.readlines():
            captured_installed_packages.append(line.strip().lower())
    
    checkpoint_installed_packages = []
    app_package_map = pd.read_csv("/data/jxq/mobile-agent/comparison_algorithm/app_package_map.csv")
    for i in range(len(checkpoint_installed_ls)):
        package = app_package_map[app_package_map["app_name"] == checkpoint_installed_ls[i].node_id]["package_name"].values[0]
        checkpoint_installed_packages.append(package)
    
    if set(checkpoint_installed_packages) in set(captured_installed_packages):
        logging.info(f"check install{str(checkpoint_installed_packages)} task success!")
        if set(checkpoint_installed_packages) != set(captured_installed_packages):
            logging.info(f"checkpoint package:{str(checkpoint_installed_packages)}")
            logging.info(f"captured package:{str(captured_installed_packages)}")
            logging.info("installed other apps!")
        return True
    else:
        logging.info(f"checkpoint package:{str(checkpoint_installed_packages)}")
        logging.info(f"captured package:{str(captured_installed_packages)}")
        logging.info("check install task failed!")
        return False
    

    
    

    


if __name__ == "__main__":
    captured_dir = "/data/jxq/mobile-agent/AgentEnv_copy/captured_data/84143002711104077"
    ls = [Checkpoint(1, "check_install", "ebay",)]
    status = check_install(ls, captured_dir)
    if status:
        print("hello world")

