from __future__ import annotations

from typing import Dict, Optional

import re
import datetime as dt

_DOMAIN = {
	"forecast": ["预测", "预报", "温度", "降水", "明天", "后天"],
	"alerts": ["预警", "风险", "暴雨", "高温", "低温", "大风"],
	"recommend": ["穿衣", "穿什么", "出门", "衣服", "打扮"],
	"clusters": ["聚类", "模式", "历史", "分析"],
	"greeting": ["你好", "您好", "在吗", "帮助"],
}


def _extract_keywords(text: str) -> Dict[str, int]:
	text = text.strip().lower()
	counts: Dict[str, int] = {}
	for intent, kws in _DOMAIN.items():
		for kw in kws:
			if re.search(kw, text):
				counts[kw] = counts.get(kw, 0) + 1
	return counts


def parse_intent(q: str = "") -> Dict:
	"""简易中文意图识别：基于关键词命中估计意图类别。返回 intent 与置信度近似值。"""
	if not q:
		return {"intent": "unknown", "confidence": 0.0, "keywords": {}}
	kw_counts = _extract_keywords(q)

	scores = {k: 0 for k in _DOMAIN}
	for intent, kws in _DOMAIN.items():
		for kw in kws:
			scores[intent] += kw_counts.get(kw, 0)

	intent = max(scores, key=scores.get)
	max_score = scores[intent]
	confidence = float(min(1.0, max_score / 2.0)) if max_score > 0 else 0.0
	return {"intent": intent if max_score > 0 else "unknown", "confidence": confidence, "keywords": kw_counts}


def is_tomorrow_outfit_query(q: str) -> bool:
	text = q.strip().lower()
	return ("明天" in text) and ("穿" in text or "穿什么" in text or "穿啥" in text)


def parse_outfit_target(q: str) -> Optional[dt.date]:
	"""识别“今天/明天/后天/具体日期”的问句，返回目标日期。若无法识别返回 None。"""
	text = q.strip().lower()
	wear_kw = ("穿" in text or "穿什么" in text or "穿啥" in text or "穿衣" in text or "伞" in text or "防晒" in text)
	if not wear_kw:
		return None
	# 日期解析
	today = dt.date.today()
	if "今天" in text:
		return today
	if "明天" in text:
		return today + dt.timedelta(days=1)
	if "后天" in text:
		return today + dt.timedelta(days=2)
	# 匹配 8.23 / 8-23 / 08-23 / 2025-08-23 等
	m = re.search(r"(?:(\d{4})[-/.])?(\d{1,2})[-/.](\d{1,2})", text)
	if m:
		year = int(m.group(1)) if m.group(1) else today.year
		month = int(m.group(2))
		day = int(m.group(3))
		try:
			return dt.date(year, month, day)
		except ValueError:
			return None
	return None


def parse_assistant_topic(q: str) -> str:
	"""返回 assistant 主题：umbrella/sunscreen/outfit。"""
	text = q.strip().lower()
	if any(k in text for k in ["带伞", "需不需要伞", "要不要伞", "雨伞", "下雨", "会下雨", "下不下雨", "雨"]):
		return "umbrella"
	if any(k in text for k in ["防晒", "晒", "太阳", "紫外"]):
		return "sunscreen"
	return "outfit"
