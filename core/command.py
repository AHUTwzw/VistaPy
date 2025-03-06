import os
import platform
import subprocess
from datetime import datetime

import chardet

REQUIREMENTS_FILE = 'requirements.txt'
# 虚拟环境的路径（根据你的实际情况修改）
venv_path = ".venv"
# 虚拟环境中的 Python 可执行文件路径
if os.name == "nt":  # Windows
    python_executable = os.path.join(venv_path, "Scripts", "python.exe")
else:  # Linux/macOS
    python_executable = os.path.join(venv_path, "bin", "python")

def read_requirements():
    if not os.path.exists(REQUIREMENTS_FILE):
        return "File not found."

    # 尝试检测文件编码
    try:
        with open(REQUIREMENTS_FILE, 'rb') as file:
            raw_data = file.read()

        detected_encoding = chardet.detect(raw_data)['encoding']
        encoding = detected_encoding if detected_encoding else 'utf-8'

        content = raw_data.decode(encoding)
    except Exception as e:
        return f"Error reading file: {str(e)}"

    return content


def write_requirements(content):
    try:
        with open(REQUIREMENTS_FILE, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        return f"Error writing file: {str(e)}"

def update_pip():
    try:
        result = subprocess.run(
            [python_executable, "-m", "pip", "install", "--upgrade", "pip"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        return {
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def install_requirements():
    try:
        result = subprocess.run(
            [python_executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        return {
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def find_process_by_name(process_name):
    """
    查询指定名称的进程。

    :param process_name: 进程名称（如 "python"）
    :return: 返回包含进程信息的列表，每个元素是一个字典，包含 PID 和命令行信息。
    """
    system = platform.system()

    if system == "Windows":
        # Windows 使用 tasklist 命令
        command = ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV", "/NH"]
        output = subprocess.run(command, capture_output=True, text=True).stdout
        processes = []
        for line in output.splitlines():
            if line.strip():
                parts = line.strip().split('","')
                if len(parts) > 1:
                    pid = int(parts[1].strip('"'))
                    processes.append({"pid": pid, "command": parts[0].strip('"')})
    else:
        # Linux/macOS 使用 ps 命令
        command = ["ps", "-ef"]
        output = subprocess.run(command, capture_output=True, text=True).stdout
        processes = []
        for line in output.splitlines():
            if process_name in line:
                parts = line.split()
                pid = int(parts[1])
                command = " ".join(parts[7:])
                processes.append({"pid": pid, "command": command})

    return processes

def format_log_entry(output, level="INFO", pid=None):
    """
    格式化日志条目。

    :param output: 日志内容。
    :param level: 日志级别（默认为 INFO）。
    :param pid: 进程 ID。
    :return: 格式化后的日志条目。
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pid_info = f"[PID: {pid}]" if pid else ""
    return f"{timestamp} {pid_info} [{level}] {output}"

def run_command_with_custom_logging(command, log_file):
    """
    运行命令并将输出重定向到日志文件，支持定制化日志格式。

    :param command: 要运行的命令（列表形式）。
    :param log_file: 日志文件路径。
    """
    try:
        # 以追加模式打开日志文件
        with open(log_file, "a") as log:
            # 启动子进程，将 stdout 和 stderr 重定向到 PIPE
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,  # 标准输出重定向到 PIPE
                stderr=subprocess.PIPE,  # 标准错误重定向到 PIPE
                text=True                # 以文本模式处理输出
            )
            print(f"已启动子进程，PID: {process.pid}")

            # 实时读取输出并格式化日志
            while True:
                # 读取标准输出
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    # 格式化日志
                    formatted_log = format_log_entry(output.strip(), level="INFO", pid=process.pid)
                    log.write(formatted_log + "\n")  # 写入日志文件
                    sys.stdout.write(formatted_log + "\n")  # 输出到控制台
                    sys.stdout.flush()

                # 读取标准错误
                error = process.stderr.readline()
                if error:
                    # 格式化日志
                    formatted_log = format_log_entry(error.strip(), level="ERROR", pid=process.pid)
                    log.write(formatted_log + "\n")  # 写入日志文件
                    sys.stderr.write(formatted_log + "\n")  # 输出到控制台
                    sys.stderr.flush()

            # 等待进程完成
            process.wait()
            print(f"子进程结束，返回码: {process.returncode}")

    except Exception as e:
        print(f"运行命令时出错: {e}")