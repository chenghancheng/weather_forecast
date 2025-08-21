## 天气智能网站（前后端一体，含智能预报/预警/助手）

### 运行环境
- 操作系统：Windows 10/11、macOS、Linux 均可
- Python：3.10+（推荐 3.11）
- 浏览器：Chrome/Edge/Safari/Firefox 最新版

### 一键运行（本地开发）
```bash
# 1) 创建并激活虚拟环境（Windows PowerShell）
python -m venv .venv
. .venv/Scripts/Activate.ps1

# 2) 安装依赖（无需安装深度学习框架即可运行）
pip install -r requirements.txt

# 3) 启动服务（Windows 上 --reload 可能与中文路径冲突，建议先不用）
uvicorn app.__init__:app --host 0.0.0.0 --port 8000
```

打开浏览器访问 `http://127.0.0.1:8000`。

### 功能模块
- 天气展示：未来 7 天卡片式预报、近 14 天温度与降水可视化
- 极端天气：基于预测和阈值的高/低风险提示
- 生活助手：支持“穿什么/要不要带伞/需不需要防晒”等中文问答
- 城市能力：
  - 右上角下拉选择、搜索（中文/拼音/英文均可）
  - 首次进入支持 IP 推断和浏览器定位，自动设置并持久化到 LocalStorage
  - 默认城市为“北京”，若无历史记录会自动填写
- 主题与多语言：中英双语；浅色/深色/系统主题切换

数据来源：
- 历史数据：优先 Open‑Meteo（近 90 天 → ERA5 归档），其次本地 CSV，最后合成季节性数据
- 未来 7 天：外部预测 85% + 本地 ARIMA/LSTM 15% 融合

### 目录结构
```
app/
  __init__.py
  main.py
  data_loader.py
  forecasting.py
  alerts.py
  recommend.py
  nlp.py
  clustering.py
frontend/
  index.html
  style.css
  app.js
```

### 使用说明
- 首次打开自动定位城市：
  - 后端 `/api/ip-city` 多源 IP（ipapi / ipwho.is / ip-api）→ 获取经纬度 → 反向地理编码（Open‑Meteo）→ 选取最近的中国城市
  - 若 IP 出口在省会（如郑州），反向地理编码会以经纬度匹配最近城市（可纠正到南阳等地级市）
  - 也可授权浏览器定位（更精准），或在右上角搜索框输入“城市,省份”进行消歧，选中后会写入 LocalStorage
- 主题与语言：右上角切换，选择会持久化；“系统”主题会跟随 OS 变化
- 刷新数据：历史图表下方“刷新数据”，会清理缓存并重新拉取

### API（部分）
- `GET /api/health`：服务健康检查
- `GET /api/history?city=北京&days=14`：历史天气（默认城市北京）
- `GET /api/forecast?city=北京&days=7`：未来 7 天预测
- `GET /api/alerts/summary?city=北京&days=7`：极端天气摘要
- `GET /api/recommend?city=北京&days=1`：穿衣/防雨/防晒建议
- `GET /api/nlp?q=明天要带伞吗&city=北京`：生活助手问答
- `GET /api/ip-city`：根据访问 IP 推断城市

### 生产部署建议
1) 使用 `uvicorn` 或 `gunicorn` + `uvicorn.workers.UvicornWorker` 启动 ASGI：
```bash
pip install "uvicorn[standard]" gunicorn
gunicorn -k uvicorn.workers.UvicornWorker app.__init__:app -b 0.0.0.0:8000 --workers 2 --threads 8
```
2) 前置 Nginx 反向代理与静态缓存（可将 `frontend/` 作为静态资源目录缓存，接口转发到 8000 端口）。
3) 若在内网或教育网部署，请开放外网访问地理/气象 API 或加代理。

### 开发技巧
- Windows 若执行激活脚本报策略限制，可用：`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- PowerShell 无法运行虚拟环境命令：使用 `& .\.venv\Scripts\python.exe -m ...`
- Windows 热重载异常退出：去掉 `--reload`
- 若想重新验证“默认北京”，清空浏览器 LocalStorage 中的 `city`

### 常见问题
- 终端出现 `ValueWarning: No frequency information...`：代码已设定日频处理，可忽略
