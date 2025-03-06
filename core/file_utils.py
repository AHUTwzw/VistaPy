import os
import shutil
import tarfile
import zipfile


class FileUtils:
    """
    文件和目录操作工具类
    """

    @staticmethod
    def delete_file(file_path):
        """
        删除文件
        :param file_path: 文件路径
        """
        try:
            os.remove(file_path)
            print(f"文件 {file_path} 已删除")
        except FileNotFoundError:
            print(f"文件 {file_path} 不存在")
        except Exception as e:
            print(f"删除文件时出错: {e}")

    @staticmethod
    def delete_directory(dir_path):
        """
        删除目录（包括非空目录）
        :param dir_path: 目录路径
        """
        try:
            shutil.rmtree(dir_path)
            print(f"目录 {dir_path} 已删除")
        except FileNotFoundError:
            print(f"目录 {dir_path} 不存在")
        except Exception as e:
            print(f"删除目录时出错: {e}")

    @staticmethod
    def rename_file(old_path, new_name):
        """
        重命名文件
        :param old_path: 原文件路径
        :param new_name: 新文件名
        """
        try:
            dir_path = os.path.dirname(old_path)
            new_path = os.path.join(dir_path, new_name)
            os.rename(old_path, new_path)
            print(f"文件 {old_path} 已重命名为 {new_path}")
        except FileNotFoundError:
            print(f"文件 {old_path} 不存在")
        except Exception as e:
            print(f"重命名文件时出错: {e}")

    @staticmethod
    def rename_directory(old_path, new_name):
        """
        重命名目录
        :param old_path: 原目录路径
        :param new_name: 新目录名
        """
        try:
            dir_path = os.path.dirname(old_path)
            new_path = os.path.join(dir_path, new_name)
            os.rename(old_path, new_path)
            print(f"目录 {old_path} 已重命名为 {new_path}")
        except FileNotFoundError:
            print(f"目录 {old_path} 不存在")
        except Exception as e:
            print(f"重命名目录时出错: {e}")

    @staticmethod
    def move_file(src_path, dest_path):
        """
        移动文件
        :param src_path: 源文件路径
        :param dest_path: 目标路径
        """
        try:
            shutil.move(src_path, dest_path)
            print(f"文件 {src_path} 已移动到 {dest_path}")
        except FileNotFoundError:
            print(f"文件 {src_path} 不存在")
        except Exception as e:
            print(f"移动文件时出错: {e}")

    @staticmethod
    def move_directory(src_path, dest_path):
        """
        移动目录
        :param src_path: 源目录路径
        :param dest_path: 目标路径
        """
        try:
            shutil.move(src_path, dest_path)
            print(f"目录 {src_path} 已移动到 {dest_path}")
        except FileNotFoundError:
            print(f"目录 {src_path} 不存在")
        except Exception as e:
            print(f"移动目录时出错: {e}")

    @staticmethod
    def create_directory(dir_path):
        """
        创建目录
        :param dir_path: 目录路径
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"目录 {dir_path} 已创建")
        except Exception as e:
            print(f"创建目录时出错: {e}")

    @staticmethod
    def list_directory(dir_path):
        """
        列出目录内容
        :param dir_path: 目录路径
        :return: 目录内容列表
        """
        try:
            return os.listdir(dir_path)
        except FileNotFoundError:
            print(f"目录 {dir_path} 不存在")
            return []
        except Exception as e:
            print(f"列出目录内容时出错: {e}")
            return []

    @staticmethod
    def ensure_logs_directory(path):
        """确保日志目录存在。"""
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def extract_archive_and_delete(archive_path, extract_dir):
        """
        解压 .zip 或 .tar.gz 文件并删除压缩包。

        :param archive_path: 压缩包路径。
        :param extract_dir: 解压目标目录。
        """
        try:
            # 确保目标目录存在
            os.makedirs(extract_dir, exist_ok=True)

            # 根据文件类型解压
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.endswith('.tar.gz'):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                raise ValueError("不支持的文件格式")

            print(f"文件已解压到: {extract_dir}")

            # 删除压缩包
            os.remove(archive_path)
            print(f"压缩包已删除: {archive_path}")

        except Exception as e:
            print(f"解压或删除文件时出错: {e}")

    @staticmethod
    def get_directory_structure(root_dir):
        """
        获取目录结构。

        :param root_dir: 根目录路径。
        :return: 包含目录和文件信息的字典。
        """
        structure = {"name": os.path.basename(root_dir), "type": "directory", "children": []}
        for item in os.listdir(root_dir):
            item_path = os.path.join(root_dir, item)
            if os.path.isdir(item_path):
                structure["children"].append(get_directory_structure(item_path))  # 递归获取子目录
            else:
                structure["children"].append({"name": item, "type": "file"})
        return structure