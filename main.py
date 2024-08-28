'''
Author: awsl1414 3030994569@qq.com
Date: 2024-08-27 17:21:29
LastEditors: awsl1414 3030994569@qq.com
LastEditTime: 2024-08-28 14:04:03
FilePath: /halo-auto-backup/main.py
Description: 

'''
import base64
import os
import sys
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from utils import upload_to_ali

# 读取配置
load_dotenv()

website = os.getenv("website")
user = os.getenv("user")
password = os.getenv("password")
# halo2备份文件夹路径
backup_halo_path = os.getenv("backup_halo_path")

ali_backup_folder = os.getenv("ali_backup_folder")


if not all([website, user, password, backup_halo_path]):
    print("配置缺失，请检查配置文件信息")
    sys.exit()

backup_api = website + "/apis/migration.halo.run/v1alpha1/backups"
check_api = (
    website
    + "/apis/migration.halo.run/v1alpha1/backups?sort=metadata.creationTimestamp%2Cdesc"
)

# 获取现在的时间 2024-08-27T17:51:03.717Z
now_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

# 构建认证头部
auth_header = "Basic " + base64.b64encode((user + ":" + password).encode()).decode()
payload = json.dumps(
    {
        "apiVersion": "migration.halo.run/v1alpha1",
        "kind": "Backup",
        "metadata": {"generateName": "backup-", "name": ""},
        "spec": {
            "expiresAt": now_time,
        },
    }
)

headers = {
    "User-Agent": "",
    "Content-Type": "application/json",
    "Authorization": "Basic "
    + base64.b64encode((user + ":" + password).encode()).decode(),
}
response = requests.request("POST", backup_api, headers=headers, data=payload)

if response.status_code == 201:
    print("备份请求成功！")
    new_backup_name = ""
    while True:
        check_response = requests.request("GET", check_api, headers=headers)
        if check_response.status_code == 200:
            backup_data = json.loads(check_response.text)

            items = backup_data.get("items", [])
            if items[0]["status"]["phase"] == "SUCCEEDED":
                print("备份完成！")
                new_backup_name = items[0]["status"]["filename"]
                break
            if items[0]["status"]["phase"] == "RUNNING":
                print("正在备份！")
                time.sleep(10)
        else:
            print(f"查询备份请求失败！错误代码：{check_response.status_code}")

        
    # 备份文件夹完整路径
    backup_file_path = os.path.join(backup_halo_path, new_backup_name)
    upload_to_ali(backup_file_path, ali_backup_folder)

else:
    print(f"备份请求失败！错误代码：{response.status_code}")
