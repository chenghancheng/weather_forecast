from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression


def _train_temp_linear_regression(df: pd.DataFrame) -> LinearRegression:
	data = df.copy()
	# 仅使用有温度与日期的样本
	data = data[["date", "temperature_c"]].dropna()
	data["date"] = pd.to_datetime(data["date"]).map(pd.Timestamp.toordinal)
	dates = data["date"].values.reshape(-1, 1)
	temp = data["temperature_c"].astype(float).values
	model = LinearRegression()
	model.fit(dates, temp)
	return model


def _train_rf_risk_classifier(df: pd.DataFrame) -> RandomForestClassifier:
	"""使用规则合成历史标签，并训练随机森林做二分类（低/高风险）。对缺失值做填充。"""
	data = df.copy()
	# 确保列存在
	for col, default in [
		("temperature_c", 20.0),
		("precipitation_mm", 0.0),
		("wind_speed_ms", 3.0),
		("humidity", 60.0),
	]:
		if col not in data:
			data[col] = default
	# 转为数值并填充缺失
	for col in ["temperature_c", "precipitation_mm", "wind_speed_ms", "humidity"]:
		data[col] = pd.to_numeric(data[col], errors="coerce").fillna(data[col].median()).fillna(0.0)

	X = data[["temperature_c", "precipitation_mm", "wind_speed_ms", "humidity"]].values
	# 合成标签：低温/高温/大雨视为高风险
	labels = (
		(data["temperature_c"] < 0)
		| (data["temperature_c"] > 35)
		| (data["precipitation_mm"] > 10)
		| (data["wind_speed_ms"] > 8)
	)
	y = labels.astype(int).values
	model = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42)
	model.fit(X, y)
	return model


def generate_alerts(history_df: pd.DataFrame, forecast_list: List[dict]) -> List[dict]:
	"""生成未来几天的天气风险预警。对历史数据先做缺失清洗，避免训练报错。"""
	data = history_df.copy()
	# 清洗缺失与列缺失
	for col, default in [
		("temperature_c", 20.0),
		("precipitation_mm", 0.0),
		("humidity", 60.0),
		("wind_speed_ms", 3.0),
	]:
		if col not in data:
			data[col] = default
		data[col] = pd.to_numeric(data[col], errors="coerce").fillna(default)
	data["date"] = pd.to_datetime(data["date"], errors="coerce").fillna(method="ffill").fillna(method="bfill")

	lin = _train_temp_linear_regression(data)
	rf = _train_rf_risk_classifier(data)

	results: List[dict] = []
	for item in forecast_list:
		date_str = item["date"]
		date_ord = pd.Timestamp(date_str).toordinal()
		baseline_temp = float(lin.predict([[date_ord]])[0])

		feat = np.array([
			item.get("temperature_c", baseline_temp),
			item.get("precipitation_mm", 0.0),
			item.get("wind_speed_ms", 3.0),
			item.get("humidity", 60.0),
		]).reshape(1, -1)
		pred = int(rf.predict(feat)[0])
		level = "高风险" if pred == 1 else "低风险"

		reasons = []
		if item.get("temperature_c", 0) < -5:
			reasons.append("极端低温")
		if item.get("temperature_c", 100) > 35:
			reasons.append("极端高温")
		if item.get("precipitation_mm", 0) > 10:
			reasons.append("强降水")
		if item.get("wind_speed_ms", 0) > 8:
			reasons.append("大风")
		if not reasons and level == "高风险":
			reasons.append("综合风险较高")

		results.append({
			"date": date_str,
			"level": level,
			"baseline_temp": baseline_temp,
			"reasons": reasons,
		})

	return results
