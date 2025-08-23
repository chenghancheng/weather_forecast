Write-Host "正在启动天气智能网站服务器..." -ForegroundColor Green
Write-Host ""

# 设置环境变量来禁用TensorFlow警告
$env:TF_CPP_MIN_LOG_LEVEL = "2"
$env:TF_ENABLE_ONEDNN_OPTS = "0"

# 激活虚拟环境并启动服务器
& "\.venv\Scripts\Activate.ps1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

Read-Host "按回车键退出"
