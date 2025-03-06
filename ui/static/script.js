let modal = document.getElementById("logModal");
let logContent = document.getElementById("logContent");
let intervalId;
// 打开弹窗
function openLogModal(rowData) {
    // 将参数存储为全局变量
    window.globalProjectId = rowData;
    modal.style.display = "flex";
    fetchLogs(); // 首次加载日志
    intervalId = setInterval(fetchLogs, 1000); // 每 1 秒刷新一次日志
}

// 关闭弹窗
function closeLogModal() {
    modal.style.display = "none";
    if (intervalId) {
      clearInterval(intervalId);
    }
}

// 获取日志
function fetchLogs() {
    // 使用全局变量 projectId
    const projectId = window.globalProjectId;
    const url = `/logs?project=${projectId}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.logs) {
                logContent.innerHTML = data.logs.join("<br>"); // 显示日志
            } else if (data.error) {
                logContent.innerHTML = "加载日志失败: " + data.error;
            }
        })
        .catch(error => {
            logContent.innerHTML = "请求失败: " + error;
        });
}