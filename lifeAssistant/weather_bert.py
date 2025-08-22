#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERT天气建议模型
"""

import json
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import jieba

class WeatherBERTModel:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.advice_types = ["clothing", "travel", "health", "activity"]
        
    def predict_advice(self, weather_data):
        """预测天气建议"""
        # 这里简化处理，实际应该加载训练好的模型
        temperature = weather_data.get('temperature', 20)
        weather = weather_data.get('weather', '晴天')
        aqi = weather_data.get('air_quality_index', 50)
        
        # 基于规则的简单建议生成
        advice = {
            "clothing": self._get_clothing_advice(temperature),
            "travel": self._get_travel_advice(weather),
            "health": self._get_health_advice(aqi),
            "activity": self._get_activity_advice(weather)
        }
        
        return advice
    
    def _get_clothing_advice(self, temp):
        if temp < 0:
            return "建议穿羽绒服、厚毛衣、保暖内衣"
        elif temp < 15:
            return "建议穿外套、毛衣、长裤"
        elif temp < 25:
            return "建议穿薄外套、长袖衬衫"
        else:
            return "建议穿短袖、薄衣物"
    
    def _get_travel_advice(self, weather):
        if "雨" in weather:
            return "雨天建议乘坐地铁或公交车，避免开车"
        elif "雪" in weather:
            return "雪天建议乘坐地铁，避免路面湿滑"
        elif "雾" in weather or "霾" in weather:
            return "能见度低，建议乘坐地铁"
        else:
            return "天气适宜，建议步行或骑自行车"
    
    def _get_health_advice(self, aqi):
        if aqi <= 50:
            return "空气质量优秀，适合户外活动"
        elif aqi <= 100:
            return "空气质量良好，可以正常户外活动"
        elif aqi <= 150:
            return "轻度污染，敏感人群减少户外活动"
        else:
            return "空气质量差，建议戴口罩，避免户外活动"
    
    def _get_activity_advice(self, weather):
        if "晴" in weather:
            return "天气晴朗，适合户外野餐、运动"
        elif "雨" in weather or "雪" in weather:
            return "天气不佳，建议室内活动"
        else:
            return "天气适宜，可以安排户外活动"

def main():
    model = WeatherBERTModel()
    
    # 测试数据
    test_weather = {
        "temperature": 25,
        "weather": "晴天",
        "air_quality_index": 45
    }
    
    advice = model.predict_advice(test_weather)
    print("天气建议:")
    for category, suggestion in advice.items():
        print(f"{category}: {suggestion}")

if __name__ == "__main__":
    main()
