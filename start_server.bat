@echo off
echo 正在启动天气智能网站服务器...
echo.

REM 设置环境变量来禁用TensorFlow警告
set TF_CPP_MIN_LOG_LEVEL=2
set TF_ENABLE_ONEDNN_OPTS=0

REM 激活虚拟环境并启动服务器
call .\.venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
