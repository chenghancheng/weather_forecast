from __future__ import annotations

from typing import List, Optional, Tuple

import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# 可选：LSTM（若未安装则自动忽略）
try:
	import tensorflow as tf  # type: ignore
	from tensorflow import keras  # type: ignore
	_TF_AVAILABLE = True
except Exception:
	_TF_AVAILABLE = False

# 从 data_loader 获取任意城市坐标
from .data_loader import get_city_coords

import requests
import time

warnings.filterwarnings(
	"ignore",
	message=r"No frequency information was provided.*inferred frequency",
	category=UserWarning,
)


def _ensure_daily_series(series: pd.Series) -> pd.Series:
	series = pd.Series(series.values, index=pd.to_datetime(series.index))
	series = series.asfreq("D")
	series = series.interpolate(method="time").ffill().bfill()
	return series


def _select_arima_order(series: pd.Series) -> tuple:
	candidates = [(2, 1, 2), (5, 1, 0), (1, 1, 1), (2, 1, 0), (0, 1, 2)]
	best = candidates[0]
	best_aic = float("inf")
	for order in candidates:
		try:
			model = ARIMA(series, order=order)
			res = model.fit()
			if res.aic < best_aic:
				best_aic = res.aic
				best = order
		except Exception:
			continue
	return best


def _arima_forecast(series: pd.Series, steps: int) -> np.ndarray:
	series = _ensure_daily_series(series)
	order = _select_arima_order(series)
	model = ARIMA(series, order=order)
	res = model.fit()
	fc = res.forecast(steps=steps)
	# 简单偏差校正：使用最近14天的拟合残差均值
	try:
		insample = res.get_prediction(start=max(0, len(series) - 14))
		pred_mean = np.asarray(insample.predicted_mean)
		actual = np.asarray(series[-len(pred_mean):])
		bias = float(np.nanmean(actual - pred_mean))
		fc = fc + bias
	except Exception:
		pass
	return np.asarray(fc)


def _lstm_forecast(series: pd.Series, steps: int, lookback: int = 14, epochs: int = 10) -> Optional[np.ndarray]:
	if not _TF_AVAILABLE:
		return None
	try:
		series = _ensure_daily_series(series)
		values = series.astype(float).values.reshape(-1, 1)
		mean = values.mean()
		std = values.std() if values.std() > 1e-6 else 1.0
		norm = (values - mean) / std

		X, y = [], []
		for i in range(len(norm) - lookback):
			X.append(norm[i : i + lookback])
			y.append(norm[i + lookback])
		X = np.array(X)
		y = np.array(y)
		if len(X) < 10:
			return None

		model = keras.Sequential([
			keras.layers.Input(shape=(lookback, 1)),
			keras.layers.LSTM(32),
			keras.layers.Dense(16, activation="relu"),
			keras.layers.Dense(1),
		])
		model.compile(optimizer="adam", loss="mse")
		callbacks = [keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)]
		model.fit(X, y, epochs=epochs, batch_size=16, verbose=0, callbacks=callbacks)

		window = norm[-lookback:].copy()
		preds = []
		for _ in range(steps):
			inp = window.reshape(1, lookback, 1)
			p = model.predict(inp, verbose=0)[0, 0]
			preds.append(p)
			window = np.concatenate([window[1:], np.array([p])])

		preds = np.array(preds) * std + mean
		return preds.reshape(-1)
	except Exception:
		return None


def _fetch_open_meteo_forecast(days: int, city: str) -> Optional[pd.DataFrame]:
	"""尝试获取 Open‑Meteo 的未来预测，包含 tmin/tmax。"""
	try:
		lat, lon = get_city_coords(city)
		url = (
			"https://api.open-meteo.com/v1/forecast"
			f"?latitude={lat}&longitude={lon}"
			"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean"
			"&forecast_days=" + str(min(max(days, 1), 14)) + "&timezone=Asia%2FShanghai"
		)
		js = _http_get_json(url, timeout=20, retries=2)
		d = js.get("daily", {})
		times = d.get("time")
		if not times:
			return None
		t_max = np.asarray(d.get("temperature_2m_max", []), dtype=float)
		t_min = np.asarray(d.get("temperature_2m_min", []), dtype=float)
		prec = np.asarray(d.get("precipitation_sum", []), dtype=float)
		wind_kmh = np.asarray(d.get("windspeed_10m_max", []), dtype=float)
		hum = np.asarray(d.get("relative_humidity_2m_mean", []), dtype=float)
		wind_ms = wind_kmh / 3.6
		t_avg = (t_max + t_min) / 2.0
		df = pd.DataFrame({
			"date": pd.to_datetime(times).date,
			"temperature_c": t_avg,
			"tmax": t_max,
			"tmin": t_min,
			"precipitation_mm": prec,
			"humidity": hum,
			"wind_speed_ms": wind_ms,
		})
		return df
	except Exception:
		return None


# --- HTTP 重试辅助（与 data_loader 一致的轻量实现） ---
def _http_get_json(url: str, timeout: float = 15.0, retries: int = 2, backoff_base: float = 0.5) -> dict:
	for attempt in range(retries + 1):
		try:
			r = requests.get(url, timeout=timeout)
			r.raise_for_status()
			return r.json() or {}
		except Exception:
			if attempt >= retries:
				break
			time.sleep(backoff_base * (2 ** attempt))
	return {}


def _estimate_spread_from_history(df: pd.DataFrame) -> Tuple[float, float]:
	"""估计近30天 tmax/tmin 与日均的平均差值，用于无外部数据时恢复范围。"""
	try:
		dd = df.sort_values("date").tail(30)
		if "tmax" in dd.columns and "tmin" in dd.columns:
			delta_max = float(np.nanmean(dd["tmax"].values - dd["temperature_c"].values))
			delta_min = float(np.nanmean(dd["temperature_c"].values - dd["tmin"].values))
		else:
			delta_max, delta_min = 4.5, 4.5
		return delta_max, delta_min
	except Exception:
		return 4.5, 4.5


def forecast_temperature_and_precipitation(df: pd.DataFrame, days: int = 7, city: str = "北京") -> List[dict]:
	"""融合 Open‑Meteo 外部预测与本地模型的结果，输出日均、最高、最低温。"""
	df = df.sort_values("date").reset_index(drop=True)
	temp_series = pd.Series(df["temperature_c"].values, index=pd.to_datetime(df["date"]))
	prec_series = pd.Series(df["precipitation_mm"].values, index=pd.to_datetime(df["date"]))

	temp_arima = _arima_forecast(temp_series, steps=days)
	prec_arima = _arima_forecast(prec_series, steps=days)

	temp_lstm = _lstm_forecast(temp_series, steps=days)
	if temp_lstm is not None and len(temp_lstm) == days:
		temp_model = (temp_arima + temp_lstm) / 2.0
	else:
		temp_model = temp_arima

	df_ext = _fetch_open_meteo_forecast(days, city)
	use_external = df_ext is not None and len(df_ext) >= days

	mean_humidity = float(pd.Series(df["humidity"].values).tail(7).mean()) if "humidity" in df else 60.0
	mean_wind = float(pd.Series(df["wind_speed_ms"].values).tail(7).mean()) if "wind_speed_ms" in df else 3.0

	delta_max, delta_min = _estimate_spread_from_history(df)

	last_date = pd.to_datetime(df["date"].iloc[-1]).normalize()
	dates = [(last_date + pd.Timedelta(days=i + 1)).date().isoformat() for i in range(days)]

	forecast_list: List[dict] = []
	for i in range(days):
		if use_external:
			ex_date = df_ext["date"].iloc[min(i, len(df_ext)-1)]
			ex_temp = float(df_ext["temperature_c"].iloc[min(i, len(df_ext)-1)])
			ex_prec = float(df_ext["precipitation_mm"].iloc[min(i, len(df_ext)-1)])
			ex_hum = float(df_ext["humidity"].iloc[min(i, len(df_ext)-1)])
			ex_wind = float(df_ext["wind_speed_ms"].iloc[min(i, len(df_ext)-1)])
			ex_tmax = float(df_ext.get("tmax", pd.Series([np.nan]*len(df_ext))).iloc[min(i, len(df_ext)-1)])
			ex_tmin = float(df_ext.get("tmin", pd.Series([np.nan]*len(df_ext))).iloc[min(i, len(df_ext)-1)])
			out_date = str(ex_date)
			base_temp = 0.85 * ex_temp + 0.15 * float(temp_model[i])
			out_prec = max(0.0, 0.85 * ex_prec + 0.15 * float(prec_arima[i]))
			# tmin/tmax 优先用外部，缺失则用 spread 估计
			if np.isfinite(ex_tmax) and np.isfinite(ex_tmin):
				out_tmax = 0.85 * ex_tmax + 0.15 * (base_temp + delta_max)
				out_tmin = 0.85 * ex_tmin + 0.15 * (base_temp - delta_min)
			else:
				out_tmax = base_temp + delta_max
				out_tmin = base_temp - delta_min
			out_temp = base_temp
			out_hum = ex_hum
			out_wind = ex_wind
			
			# 添加详细计算过程
			calculation_details = {
				"external_temp": ex_temp,
				"external_prec": ex_prec,
				"local_temp": float(temp_model[i]),
				"local_prec": float(prec_arima[i]),
				"weights": {"external": 0.85, "local": 0.15},
				"data_source": "external_fusion"
			}
		else:
			out_date = dates[i]
			out_temp = float(temp_model[i])
			out_prec = float(max(0.0, prec_arima[i]))
			out_hum = mean_humidity
			out_wind = mean_wind
			out_tmax = out_temp + delta_max
			out_tmin = out_temp - delta_min
			
			# 添加详细计算过程
			calculation_details = {
				"external_temp": None,
				"external_prec": None,
				"local_temp": float(temp_model[i]),
				"local_prec": float(prec_arima[i]),
				"weights": {"external": 0.0, "local": 1.0},
				"data_source": "local_only"
			}

		forecast_list.append({
			"date": out_date,
			"temperature_c": out_temp,
			"tmax": out_tmax,
			"tmin": out_tmin,
			"precipitation_mm": out_prec,
			"humidity": out_hum,
			"wind_speed_ms": out_wind,
			"calculation_details": calculation_details
		})
	return forecast_list
