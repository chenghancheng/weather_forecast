from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .data_loader import load_city_weather, get_data_source, refresh_data
from .forecasting import forecast_temperature_and_precipitation
from .alerts import generate_alerts
from .recommend import recommend_outfit
from .nlp import parse_intent, parse_outfit_target, parse_assistant_topic
from .clustering import compute_weather_clusters

app = FastAPI(title="天气智能网站", version="0.2.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
	app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
def index():
	index_file = frontend_dir / "index.html"
	if index_file.exists():
		return FileResponse(str(index_file))
	return {"message": "前端资源未找到，请访问 /api/* 接口"}


@app.get("/api/health")
def health():
	return {"status": "ok", "data_source": get_data_source()}


@app.get("/api/ip-city")
def ip_city():
	"""服务端基于来访 IP 猜测城市名称。精细化流程：
	1) 多源 IP 服务拿到 city 与经纬度
	2) 反向地理编码（Open‑Meteo）选取最近的中国城市
	3) 返回原始 city、经纬度与归一化中文名
	"""
	import math
	import requests as _rq

	def _try(url, pick):
		try:
			r = _rq.get(url, timeout=6)
			r.raise_for_status()
			j = r.json()
			return pick(j)
		except Exception:
			return None

	# 1) IP -> 粗定位
	info = _try(
		"https://ipapi.co/json/",
		lambda j: {
			"city": j.get("city") or j.get("region_city"),
			"lat": j.get("latitude"),
			"lon": j.get("longitude"),
		},
	)
	if not info:
		info = _try(
			"https://ipwho.is/",
			lambda j: None if (j is None or j.get("success") is False) else {"city": j.get("city"), "lat": j.get("latitude"), "lon": j.get("longitude")},
		)
	if not info:
		info = _try(
			"http://ip-api.com/json/?fields=status,city,lat,lon&lang=zh-CN",
			lambda j: ({"city": j.get("city"), "lat": j.get("lat"), "lon": j.get("lon")} if j and j.get("status") == "success" else None),
		)

	city = (info or {}).get("city")
	lat = (info or {}).get("lat")
	lon = (info or {}).get("lon")

	# 2) 反向地理编码：取最近的中国城市
	def _reverse(lat_: float, lon_: float):
		if lat_ is None or lon_ is None:
			return None
		resp = _try(
			f"https://geocoding-api.open-meteo.com/v1/reverse?latitude={lat_}&longitude={lon_}&language=zh&count=10",
			lambda j: j,
		)
		if not resp:
			return None
		items = resp.get("results") or []
		if not items:
			return None
		# 优先中国、城市级别（PPL* 或 PPLA/PPLC）并按距离近排序
		def _score(it: dict):
			code = (it.get("feature_code") or "").upper()
			rank = {"PPLC": 5, "PPLA": 4, "PPLA2": 4, "PPLA3": 3, "PPLA4": 3}
			lvl = rank.get(code, 2 if code.startswith("PPL") else 1)
			# 近者优先；接口里可能没有距离，自己算一下
			try:
				la = float(it.get("latitude")); lo = float(it.get("longitude"))
				# 粗略球面距离
				d = (la - float(lat_)) ** 2 + (lo - float(lon_)) ** 2
			except Exception:
				d = 9e9
			return (1 if it.get("country_code") == "CN" else 0, lvl, -d)
		items.sort(key=_score, reverse=True)
		return items[0]

	best = _reverse(lat, lon)
	normalized = best.get("name") if best else None

	# 3) 若仍无 normalized，则退化到 name 搜索归一化
	if not normalized and city:
		geo = _try(
			f"https://geocoding-api.open-meteo.com/v1/search?name={city}&language=zh&count=5",
			lambda j: j,
		)
		try:
			items = (geo or {}).get("results") or []
			cn_items = [it for it in items if it.get("country_code") == "CN"] or items
			if cn_items:
				normalized = cn_items[0].get("name")
		except Exception:
			pass

	return {"city": city, "lat": lat, "lon": lon, "normalized": normalized}


@app.get("/api/refresh")
def refresh(city: str = Query("北京")):
	source = refresh_data(city)
	return {"refreshed": True, "data_source": source}


@app.get("/api/history")
def history(city: str = Query("北京"), days: int = Query(30, ge=7, le=90)):
	df = load_city_weather(city)
	df = df.sort_values("date").tail(days)
	return {
		"city": city,
		"data_source": get_data_source(),
		"history": [
			{
				"date": str(row.date.date() if hasattr(row.date, 'date') else row.date),
				"temperature_c": float(row.temperature_c),
				"tmin": float(getattr(row, 'tmin', row.temperature_c)),
				"tmax": float(getattr(row, 'tmax', row.temperature_c)),
				"precipitation_mm": float(row.precipitation_mm),
				"humidity": float(row.humidity),
				"wind_speed_ms": float(row.wind_speed_ms),
			}
			for row in df.itertuples(index=False)
		],
	}


@app.get("/api/forecast")
def forecast(city: str = Query("北京"), days: int = Query(7, ge=1, le=14)):
	df = load_city_weather(city)
	forecast_list = forecast_temperature_and_precipitation(df, days=days, city=city)
	return {"city": city, "days": days, "forecast": forecast_list, "data_source": get_data_source()}


@app.get("/api/alerts")
def alerts(city: str = Query("北京"), days: int = Query(7, ge=1, le=14)):
	df = load_city_weather(city)
	forecast_list = forecast_temperature_and_precipitation(df, days=days, city=city)
	alerts_list = generate_alerts(df, forecast_list)
	return {"city": city, "alerts": alerts_list, "data_source": get_data_source()}


@app.get("/api/alerts/summary")
def alerts_summary(city: str = Query("北京"), days: int = Query(7, ge=1, le=14)):
	df = load_city_weather(city)
	forecast_list = forecast_temperature_and_precipitation(df, days=days, city=city)
	alerts_list = generate_alerts(df, forecast_list)
	extremes = []
	for i, a in enumerate(alerts_list):
		d = forecast_list[i]
		if a["level"] == "高风险" or d.get("tmax", 0) >= 35 or d.get("tmin", 999) <= -5 or d.get("precipitation_mm", 0) >= 20:
			extremes.append({
				"date": a["date"],
				"level": a["level"],
				"tmin": d.get("tmin"),
				"tmax": d.get("tmax"),
				"precipitation_mm": d.get("precipitation_mm"),
				"reasons": a.get("reasons", []),
			})
	return {"city": city, "extremes": extremes, "data_source": get_data_source()}


@app.get("/api/recommend")
def outfit_recommend(city: str = Query("北京"), days: int = Query(1, ge=1, le=7)):
	df = load_city_weather(city)
	forecast_list = forecast_temperature_and_precipitation(df, days=days, city=city)
	first_day = forecast_list[0]
	recs = recommend_outfit(
		temperature_c=first_day.get("temperature_c", 18.0),
		precipitation_mm=first_day.get("precipitation_mm", 0.0),
		wind_speed_ms=first_day.get("wind_speed_ms", 2.0),
		humidity=first_day.get("humidity", 50.0),
	)
	return {"city": city, "for_date": first_day.get("date"), "recommendations": recs, "data_source": get_data_source()}


@app.get("/api/nlp")
def nlp_endpoint(q: str = "", city: str = Query("北京")):
	# 生活助手：umbrella/sunscreen/outfit
	target_date = parse_outfit_target(q)
	topic = parse_assistant_topic(q)
	if target_date is not None:
		df = load_city_weather(city)
		forecast_list = forecast_temperature_and_precipitation(df, days=14)
		match = next((d for d in forecast_list if d.get("date") == str(target_date)), None)
		if match is None:
			match = forecast_list[0]
		if topic == "umbrella":
			need = float(match.get("precipitation_mm", 0.0)) >= 1.0
			return {"intent": "umbrella", "city": city, "for_date": match.get("date"), "precipitation_mm": match.get("precipitation_mm", 0.0), "advice": "有降水，记得带伞" if need else "降水概率低，可不带伞"}
		if topic == "sunscreen":
			hot = float(match.get("tmax", match.get("temperature_c", 25))) >= 30
			return {"intent": "sunscreen", "city": city, "for_date": match.get("date"), "tmax": match.get("tmax"), "advice": "气温较高，注意防晒、补水" if hot else "气温适中，基础防晒即可"}
		# outfit 默认
		temp = float(match.get("temperature_c", 20.0))
		prec = float(match.get("precipitation_mm", 0.0))
		advice = []
		if temp >= 26:
			advice.append("短袖/短裤为主，注意防晒")
		elif temp >= 18:
			advice.append("长袖薄衫或T恤+长裤")
		elif temp >= 10:
			advice.append("薄外套/卫衣+长裤")
		else:
			advice.append("厚外套/毛衣，注意保暖")
		advice.append("有降水，记得带伞" if prec >= 1.0 else "降水概率低，可不带伞")
		return {"intent": "outfit_day", "city": city, "for_date": match.get("date"), "temperature_c": temp, "tmin": match.get("tmin"), "tmax": match.get("tmax"), "precipitation_mm": prec, "advice": advice}
	# 若未识别，返回提示
	return {"intent": "unknown", "message": "请换个方式问问吧"}


@app.get("/api/config/options")
def config_options():
	return {
		"cities": list(["北京", "上海", "广州", "深圳", "杭州", "成都"]),
		"languages": ["zh", "en"],
		"themes": ["light", "dark"],
	}
