"""
Author: awsl1414 3030994569@qq.com
Date: 2024-08-27 23:47:14
LastEditors: awsl1414 3030994569@qq.com
LastEditTime: 2024-08-27 23:48:03
FilePath: /halo-auto-backup/utils.py
Description: 

"""

from aligo import Aligo


def upload_to_ali(backup_file_path, ali_backup_folder):
    """上传备份文件到阿里云盘
    :param backup_file_path: 备份文件路径
    :param backup_folder_name: 阿里云盘中备份的文件夹名
    """

    ali = Aligo(port=9988)

    file_lsit = ali.get_file_list()

    backup_id = ""
    for file in file_lsit:
        if file.name == ali_backup_folder:
            backup_id = file.file_id
            break
    if not backup_id:
        backup_id = ali.create_folder(ali_backup_folder).file_id

    ali.upload_file(backup_file_path, backup_id)
