#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气建议Web应用
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import random
from chat_system import WeatherChatSystem

app = Flask(__name__)
CORS(app)

# 初始化聊天系统
chat_system = WeatherChatSystem()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/weather_advice', methods=['POST'])
def get_weather_advice():
    """获取天气建议API"""
    try:
        data = request.get_json()
        
        # 提取天气数据
        weather_data = {
            "temperature": data.get("temperature", 20),
            "weather": data.get("weather", "晴天"),
            "air_quality": data.get("air_quality", 50)
        }
        
        # 获取建议
        advice = chat_system.get_advice(weather_data)
        
        return jsonify({
            "success": True,
            "advice": advice,
            "weather_data": weather_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """对话API"""
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        
        # 处理用户输入
        response = chat_system.chat(user_input)
        
        return jsonify({
            "success": True,
            "response": response
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/alternative_advice', methods=['POST'])
def get_alternative_advice():
    """获取替代建议API"""
    try:
        data = request.get_json()
        category = data.get("category", "")
        weather_data = data.get("weather_data", None)
        previous_advice = data.get("previous_advice", None)
        
        # 获取替代建议，传递天气数据和之前的建议
        alternative = chat_system.get_alternative(category, weather_data, previous_advice)
        
        return jsonify({
            "success": True,
            "alternative": alternative
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
