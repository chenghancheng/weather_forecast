from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "weather_prediction_dataset.csv"

# 数据来源标记（open-meteo-recent / open-meteo-archive / csv / synthetic）
LAST_SOURCE: str = "unknown"

# 常用城市坐标（可扩展）
CITY_COORDS = {
	"北京": (39.9042, 116.4074),
	"上海": (31.2304, 121.4737),
	"广州": (23.1291, 113.2644),
	"深圳": (22.5431, 114.0579),
	"杭州": (30.2741, 120.1551),
	"成都": (30.5728, 104.0668),
	"天津": (39.3434, 117.3616),
	"南京": (32.0603, 118.7969),
	"武汉": (30.5928, 114.3055),
	"西安": (34.3416, 108.9398),
	"重庆": (29.5630, 106.5516),
	"苏州": (31.2989, 120.5853),
	"青岛": (36.0662, 120.3826),
	"沈阳": (41.8057, 123.4315),
	"大连": (38.9140, 121.6147),
	"厦门": (24.4798, 118.0894),
	"南宁": (22.8170, 108.3669),
}


def _geocode_city(name: str) -> Optional[Tuple[float, float]]:
	"""使用 Open-Meteo 地理编码将任意城市名称解析为坐标（缓存）。

	- 仅保留中国结果（country_code == 'CN'）
	- 支持在名称后追加省份提示（如 "南阳,河南"）以精确匹配
	- 在多个结果时按行政级别与人口排序
	"""
	try:
		raw = name.replace("，", ",").strip()
		parts = raw.split(",", 1)
		query = parts[0].strip()
		admin_hint = parts[1].strip() if len(parts) > 1 else ""

		url = (
			"https://geocoding-api.open-meteo.com/v1/search?name="
			+ requests.utils.quote(query)
			+ "&count=10&language=zh"
		)
		r = requests.get(url, timeout=15)
		r.raise_for_status()
		items = r.json().get("results") or []
		if not items:
			return None

		# 仅中国
		items = [it for it in items if it.get("country_code") == "CN"] or items

		# 省份提示优先
		if admin_hint:
			filtered = [it for it in items if admin_hint in str(it.get("admin1", ""))]
			if filtered:
				items = filtered

		rank = {"PPLC": 5, "PPLA": 4, "PPLA2": 4, "PPLA3": 4, "PPLA4": 4, "PPL": 3}
		items.sort(key=lambda it: (rank.get((it.get("feature_code") or "").upper(), 1), int(it.get("population") or 0)), reverse=True)
		top = items[0]
		return float(top.get("latitude")), float(top.get("longitude"))
	except Exception:
		return None


@lru_cache(maxsize=256)
def _coords_for(city: str) -> Tuple[float, float]:
	name = (city or "北京").strip()
	if name in CITY_COORDS:
		return CITY_COORDS[name]
	# 若不在内置表，尝试地理编码（支持中文/拼音/英文）
	coords = _geocode_city(name)
	if coords:
		return coords
	# default
	return CITY_COORDS["北京"]


def get_city_coords(city: str) -> Tuple[float, float]:
	"""公开的坐标获取函数，供其他模块使用。"""
	return _coords_for(city)


def _fetch_open_meteo_recent(lat: float, lon: float, past_days: int = 90) -> Optional[pd.DataFrame]:
	"""使用 forecast 接口的 past_days 获取近90天左右的历史与未来预测更一致的数据。"""
	past_days = int(max(1, min(past_days, 92)))
	url = (
		"https://api.open-meteo.com/v1/forecast"
		f"?latitude={lat}&longitude={lon}"
		"&past_days=" + str(past_days) +
		"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean"
		"&timezone=Asia%2FShanghai"
	)
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		d = r.json().get("daily", {})
		times = d.get("time", [])
		if not times:
			return None
		tmax = np.asarray(d.get("temperature_2m_max", []), dtype=float)
		tmin = np.asarray(d.get("temperature_2m_min", []), dtype=float)
		prec = np.asarray(d.get("precipitation_sum", []), dtype=float)
		wind_kmh = np.asarray(d.get("windspeed_10m_max", []), dtype=float)
		hum = np.asarray(d.get("relative_humidity_2m_mean", []), dtype=float)
		tavg = (tmax + tmin) / 2.0
		wind_ms = wind_kmh / 3.6
		return pd.DataFrame({
			"date": pd.to_datetime(times),
			"temperature_c": tavg,
			"tmin": tmin,
			"tmax": tmax,
			"precipitation_mm": prec,
			"humidity": hum if hum.size else [60.0] * len(times),
			"wind_speed_ms": wind_ms if wind_ms.size else [3.0] * len(times),
		})
	except Exception:
		return None


def _fetch_open_meteo_daily(lat: float, lon: float, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
	"""从 Open-Meteo 归档拉取日度数据。"""
	url = (
		"https://archive-api.open-meteo.com/v1/era5"
		f"?latitude={lat}&longitude={lon}"
		"&start_date=" + start_date + "&end_date=" + end_date +
		"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean"
		"&timezone=Asia%2FShanghai"
	)
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		daily = r.json().get("daily", {})
		dates = daily.get("time", [])
		if not dates:
			return None
		tmax = np.asarray(daily.get("temperature_2m_max", []), dtype=float)
		tmin = np.asarray(daily.get("temperature_2m_min", []), dtype=float)
		prec = np.asarray(daily.get("precipitation_sum", []), dtype=float)
		wind = np.asarray(daily.get("windspeed_10m_max", []), dtype=float)
		hum = np.asarray(daily.get("relative_humidity_2m_mean", []), dtype=float)
		tavg = (tmax + tmin) / 2.0
		wind_ms = wind / 3.6
		return pd.DataFrame({
			"date": pd.to_datetime(dates),
			"temperature_c": tavg,
			"tmin": tmin,
			"tmax": tmax,
			"precipitation_mm": prec,
			"humidity": hum if hum.size else [60.0] * len(dates),
			"wind_speed_ms": wind_ms if wind_ms.size else [3.0] * len(dates),
		})
	except Exception:
		return None


@lru_cache(maxsize=12)
def load_city_weather(city: str = "北京") -> pd.DataFrame:
	"""加载指定城市的历史天气数据。优先 API，其次本地 CSV，最后合成。"""
	global LAST_SOURCE
	lat, lon = _coords_for(city)

	# 1) 近 90 天
	df_recent = _fetch_open_meteo_recent(lat, lon, 90)
	if df_recent is not None and len(df_recent) >= 30:
		LAST_SOURCE = "open-meteo-recent"
		return df_recent.sort_values("date").reset_index(drop=True)

	# 2) 归档一年
	end_date = pd.Timestamp.today().normalize().date().isoformat()
	start_date = (pd.Timestamp.today().normalize() - pd.Timedelta(days=365)).date().isoformat()
	df_api = _fetch_open_meteo_daily(lat, lon, start_date, end_date)
	if df_api is not None:
		LAST_SOURCE = "open-meteo-archive"
		return df_api.sort_values("date").reset_index(drop=True)

	# 3) 本地 CSV 尝试（结构兼容）
	if DATA_FILE.exists():
		try:
			df = pd.read_csv(DATA_FILE)
			column_map = {c.lower().strip(): c for c in df.columns}
			def pick(*candidates):
				for name in candidates:
					if name in column_map:
						return column_map[name]
				return None

			date_col = pick("date", "ds", "time", "day")
			temp_col = pick("temperature_c", "temp", "temperature")
			prec_col = pick("precipitation_mm", "precipitation", "rain", "precip")
			hum_col = pick("humidity", "hum")
			wind_col = pick("wind_speed_ms", "wind", "wind_speed")

			need_synth = False
			if not date_col or not temp_col:
				need_synth = True
			else:
				df = df.rename(columns={
					date_col: "date",
					temp_col: "temperature_c",
					prec_col: "precipitation_mm" if prec_col else None,
					hum_col: "humidity" if hum_col else None,
					wind_col: "wind_speed_ms" if wind_col else None,
				})
				df = df[[c for c in ["date", "temperature_c", "precipitation_mm", "humidity", "wind_speed_ms"] if c in df.columns]]
				df["date"] = pd.to_datetime(df["date"])  # 解析时间
				df = df.sort_values("date").reset_index(drop=True)
				for col, default in [("precipitation_mm", 0.0), ("humidity", 60.0), ("wind_speed_ms", 3.0)]:
					if col not in df:
						df[col] = default

			if not need_synth:
				LAST_SOURCE = "csv"
				return df
		except Exception:
			pass

	# 4) 合成季节性数据（根据月份粗略分布）
	period_days = 365
	end_date_ts = pd.Timestamp.today().normalize()
	dates = pd.date_range(end=end_date_ts, periods=period_days, freq="D")
	month = dates.month.values
	monthly_baseline = {
		1: -2, 2: 1, 3: 7, 4: 15, 5: 21, 6: 26,
		7: 29, 8: 28, 9: 23, 10: 16, 11: 7, 12: 0,
	}
	base = np.array([monthly_baseline[int(m)] for m in month], dtype=float)
	temp = base + 2.0 * np.sin(2 * np.pi * np.arange(period_days) / 30.0) + np.random.normal(0, 1.5, period_days)
	tmin = temp - np.random.uniform(3.0, 5.0, period_days)
	tmax = temp + np.random.uniform(3.0, 5.0, period_days)
	prec = np.clip(np.random.gamma(shape=1.2, scale=2.0, size=period_days) * (0.2 + (temp - temp.min()) / (temp.max() - temp.min() + 1e-6)), 0, None)
	hum = np.clip(60 + 10 * np.sin(2 * np.pi * np.arange(period_days) / 10) + np.random.normal(0, 4, period_days), 45, 90)
	wind = np.clip(3 + 2 * np.sin(2 * np.pi * np.arange(period_days) / 12) + np.random.normal(0, 0.8, period_days), 1, 9)

	df = pd.DataFrame({
		"date": dates,
		"temperature_c": temp,
		"tmin": tmin,
		"tmax": tmax,
		"precipitation_mm": prec,
		"humidity": hum,
		"wind_speed_ms": wind,
	})
	LAST_SOURCE = "synthetic"
	return df


def get_data_source() -> str:
	return LAST_SOURCE


def refresh_data(city: str = "北京") -> str:
	"""清空缓存并重新拉取数据，返回新的数据来源标记。"""
	global LAST_SOURCE
	load_city_weather.cache_clear()
	_ = load_city_weather(city)
	return LAST_SOURCE


# 兼容旧函数名
@lru_cache(maxsize=1)
def load_beijing_weather() -> pd.DataFrame:
	return load_city_weather("北京")
