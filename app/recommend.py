from __future__ import annotations

from typing import List

import numpy as np
from sklearn.neighbors import NearestNeighbors


_PROTOTYPES = [
	{"label": "冬装（羽绒服/保暖内衣）", "vec": [ -5, 0, 3, 55 ]},
	{"label": "春秋装（卫衣/外套）", "vec": [ 12, 0, 3, 55 ]},
	{"label": "夏装（短袖/短裤）", "vec": [ 28, 0, 2, 60 ]},
	{"label": "雨具（雨衣/雨伞）", "vec": [ 18, 12, 2, 70 ]},
	{"label": "防风（风衣/夹克）", "vec": [ 10, 0, 7, 55 ]},
]


def _knn_recommend(vec, top_k: int = 2) -> List[str]:
	X = np.array([p["vec"] for p in _PROTOTYPES], dtype=float)
	labels = [p["label"] for p in _PROTOTYPES]
	nbrs = NearestNeighbors(n_neighbors=min(top_k, len(_PROTOTYPES)), metric="euclidean")
	nbrs.fit(X)
	dist, idx = nbrs.kneighbors(np.array(vec, dtype=float).reshape(1, -1))
	recs = []
	for i in idx[0]:
		recs.append(labels[i])
	return recs


def recommend_outfit(temperature_c: float, precipitation_mm: float, wind_speed_ms: float, humidity: float) -> List[str]:
	"""结合 KNN 与规则输出穿衣建议。"""
	recs = []
	# 规则优先
	if temperature_c < 5:
		recs.append("羽绒服/厚外套/保暖内衣")
	elif temperature_c < 12:
		recs.append("外套/毛衣/长裤")
	elif temperature_c > 28:
		recs.append("短袖/薄裙/防晒")
	else:
		recs.append("衬衫/薄外套/长裤")

	if precipitation_mm > 5:
		recs.append("携带雨伞或雨衣")
	if wind_speed_ms > 6:
		recs.append("防风外套/帽子")

	# KNN 补充
	vec = [temperature_c, precipitation_mm, wind_speed_ms, humidity]
	knn_items = _knn_recommend(vec, top_k=2)
	for item in knn_items:
		if item not in recs:
			recs.append(item)

	return recs
