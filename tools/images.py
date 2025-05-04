import os
import hashlib

def calculate_file_hash(file_path):
    """计算文件的哈希值"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicate_images(directory):
    """遍历目录并删除内容相同的png图片"""
    hash_map = {}
    for root, _, files in os.walk(directory):
        for file in files:
            # 删除文件名以 valid_NA_ 开头的文件
            if file.startswith("valid_NA_"):
                file_path = os.path.join(root, file)
                print(f"删除文件: {file_path}")
                os.remove(file_path)
                continue

            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                file_hash = calculate_file_hash(file_path)
                if file_hash in hash_map:
                    print(f"删除重复文件: {file_path}")
                    os.remove(file_path)
                else:
                    hash_map[file_hash] = file_path

# 调用函数
images_directory = "images"  # 替换为你的目录路径
remove_duplicate_images(images_directory)

