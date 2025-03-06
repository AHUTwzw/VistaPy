import shutil
import subprocess

import chardet
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from datetime import datetime

from core.command import read_requirements, update_pip, write_requirements, install_requirements, find_process_by_name
from core.database import get_all_files, insert_file_record, init_db, get_file, delete, update_file_record
from core.file_utils import FileUtils

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['LOGS_PATH'] = 'logs'

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    files = get_all_files()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        project_name = request.form.get('project_name', '').strip()
        if not project_name:
            project_name = os.path.splitext(file.filename)[0]
        subfolder = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
        server_path = os.path.join(subfolder, file.filename)
        python_version = request.form.get('python_version', '').strip()
        if not python_version:
            python_version = '3.9'
        # 检查工程是否已存在
        existing_project = get_file(project_name)

        if existing_project:
            # 删除旧文件
            if os.path.exists(subfolder):
                for f in os.listdir(subfolder):
                    os.remove(os.path.join(subfolder, f))
                os.rmdir(subfolder)
            # 删除旧记录
            delete(project_name)

        # 创建新工程
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)
        file.save(server_path)
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = request.form.get('description', '').strip()
        insert_file_record(project_name, description, python_version, upload_time, server_path)
        FileUtils.extract_archive_and_delete(server_path, subfolder)
    return redirect(url_for('index'))

@app.route('/edit/<project>')
def edit_file(project):
    project = get_file(project)
    if not project:
        return f"{project} is not exists..."
    subfolder = os.path.join(app.config['UPLOAD_FOLDER'], project[1])
    escaped_path = subfolder.replace("\\", "\\\\")
    return render_template('editor.html', directory=escaped_path)

@app.route('/start')
def start_file():
    """启动目标项目。"""
    project_name = request.args.get("project")
    project = get_file(project_name)
    processes = find_process_by_name(project)
    if processes is not None and len(processes) != 0:
        return jsonify({"status": "error", "message": "项目已经在运行中。"})

    log_subfolder = os.path.join(app.config['LOGS_PATH'], project_name)
    FileUtils.ensure_logs_directory(log_subfolder)
    LOG_FILE = os.path.join(log_subfolder, '%s.log' % project_name)
    TARGET_SCRIPT = project[6]
    # 启动目标项目，并将输出重定向到日志文件
    with open(LOG_FILE, "a") as log_fd:
        try:
            process = subprocess.Popen(
                ["python", TARGET_SCRIPT],
                stdout=log_fd,
                stderr=subprocess.STDOUT,
                text=True,
            )
            print(f"已启动新进程，PID: {process.pid}")
            # 等待进程完成并获取输出
            stdout, stderr = process.communicate()
            if stdout:
                print("标准输出:\n", stdout)
            if stderr:
                print("标准错误:\n", stderr)

            # 获取进程的返回码
            return_code = process.returncode
            print(f"进程结束，返回码: {return_code}")
        except Exception as e:
            print(f"启动新进程时出错: {e}")
    update_file_record(project_name, 'UP', process.pid)
    return jsonify({"status": "success", "message": f"项目已启动，PID: {process.pid}"})

@app.route('/stop')
def stop_file():
    project = request.args.get("project")
    """停止目标项目。"""
    processes = find_process_by_name(project)
    if processes is None:
        return jsonify({"status": "error", "message": "项目未运行。"})

    # 终止进程
    for process in processes:
        process.terminate()
        try:
            process.wait(timeout=5)  # 等待进程结束
        except subprocess.TimeoutExpired:
            process.kill()  # 如果超时，强制终止
    update_file_record(project, 'DOWN', '')
    return jsonify({"status": "success", "message": "项目已停止。"})

@app.route('/delete/<project>')
def delete_file(project):
    """停止目标项目。"""
    processes = find_process_by_name(project)
    if processes:
        return jsonify({"status": "error", "message": "项目运行中禁止删除。"})
    subfolder = os.path.join(app.config['UPLOAD_FOLDER'], project)
    shutil.rmtree(subfolder)
    delete(project)
    return redirect(url_for('index'))

@app.route('/logs')
def view_logs():
    """获取最近的 10 条日志。"""
    try:
        project = request.args.get("project")
        subfolder = os.path.join(app.config['LOGS_PATH'], project)
        log_file = os.path.join(subfolder, '%s.log' % project)
        # 读取日志文件
        with open(log_file, "r") as f:
            lines = f.readlines()

        # 获取最后 10 条日志
        logs = lines[-10:]
        return jsonify({"logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    """列出目录中的文件"""
    directory = request.args.get('directory')
    if not directory or not os.path.isdir(directory):
        return jsonify({'error': '目录无效'}), 400
    files = os.listdir(directory)
    return jsonify({'files': files})

@app.route('/load_file', methods=['GET'])
def load_file():
    """加载文件内容"""
    directory = request.args.get('directory')
    file_path = request.args.get('file')
    file_path = os.path.join(directory, file_path)
    if not file_path or not os.path.isfile(file_path):
        return jsonify({'error': '文件无效'}), 400
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/save_file', methods=['POST'])
def save_file():
    """保存文件内容"""
    directory = request.json.get('directory')
    file_path = request.json.get('file')
    file_path = os.path.join(directory, file_path)
    content = request.json.get('content')
    if not file_path or not content:
        return jsonify({'error': '参数无效'}), 400
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': '文件保存成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_requirements', methods=['GET'])
def get_requirements():
    content = read_requirements()
    lines = content.splitlines() if isinstance(content, str) else []
    return jsonify({
        "content": content,
        "lines": lines
    })

@app.route('/update_pip_source', methods=['POST'])
def update_pip_source():
    update_result = update_pip()
    return jsonify(update_result)

@app.route('/save_requirements', methods=['POST'])
def save_requirements():
    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({"error": "No content provided"}), 400

    write_result = write_requirements(content)
    if write_result:
        return jsonify({"error": write_result}), 500

    install_result = install_requirements()
    return jsonify(install_result)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)