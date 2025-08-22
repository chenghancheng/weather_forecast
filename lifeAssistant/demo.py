#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能天气建议系统演示
"""

from chat_system import WeatherChatSystem
from weather_bert import WeatherBERTModel

def demo_weather_advice():
    """演示天气建议功能"""
    print("🌤️ 天气建议演示")
    print("=" * 50)
    
    chat = WeatherChatSystem()
    
    # 演示不同天气条件下的建议
    weather_scenarios = [
        {
            "name": "寒冷雪天",
            "data": {"temperature": -10, "weather": "大雪", "air_quality": 30}
        },
        {
            "name": "凉爽多云",
            "data": {"temperature": 15, "weather": "多云", "air_quality": 60}
        },
        {
            "name": "炎热晴天",
            "data": {"temperature": 35, "weather": "晴天", "air_quality": 80}
        },
        {
            "name": "雨天潮湿",
            "data": {"temperature": 20, "weather": "中雨", "air_quality": 45}
        }
    ]
    
    for scenario in weather_scenarios:
        print(f"\n📊 {scenario['name']}")
        print(f"天气数据: 温度{scenario['data']['temperature']}°C, {scenario['data']['weather']}, 空气质量{scenario['data']['air_quality']}")
        
        advice = chat.get_advice(scenario['data'])
        for category, suggestion in advice.items():
            print(f"  {category}: {suggestion}")

def demo_chat_interaction():
    """演示对话交互功能"""
    print("\n\n💬 智能对话演示")
    print("=" * 50)
    
    chat = WeatherChatSystem()
    
    # 模拟对话流程
    conversations = [
        "今天天气怎么样？",
        "对穿衣建议不满意",
        "谢谢，建议很好",
        "明天适合户外活动吗？"
    ]
    
    for user_input in conversations:
        print(f"\n👤 用户: {user_input}")
        response = chat.chat(user_input)
        print(f"🤖 机器人: {response}")

def demo_alternative_suggestions():
    """演示替代建议功能"""
    print("\n\n🔄 替代建议演示")
    print("=" * 50)
    
    chat = WeatherChatSystem()
    
    categories = ["clothing", "travel", "health", "activity"]
    
    for category in categories:
        alternative = chat.get_alternative(category)
        category_name = {
            "clothing": "穿衣建议",
            "travel": "出行建议", 
            "health": "健康提醒",
            "activity": "活动规划"
        }[category]
        
        print(f"\n{category_name}:")
        print(f"  替代建议: {alternative}")

def demo_bert_model():
    """演示BERT模型功能"""
    print("\n\n🤖 BERT模型演示")
    print("=" * 50)
    
    model = WeatherBERTModel()
    
    # 测试边缘情况
    edge_cases = [
        {"temperature": -20, "weather": "暴雪", "air_quality_index": 20},
        {"temperature": 45, "weather": "酷热", "air_quality_index": 150},
        {"temperature": 0, "weather": "雾霾", "air_quality_index": 200}
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"  极端天气: 温度{case['temperature']}°C, {case['weather']}, 空气质量{case['air_quality_index']}")
        
        advice = model.predict_advice(case)
        for category, suggestion in advice.items():
            print(f"  {category}: {suggestion}")

def main():
    """主演示函数"""
    print("🚀 智能天气建议系统 - 功能演示")
    print("=" * 60)
    
    try:
        # 演示各个功能模块
        demo_weather_advice()
        demo_chat_interaction()
        demo_alternative_suggestions()
        demo_bert_model()
        
        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("\n🎯 系统特点:")
        print("  • 智能天气分析")
        print("  • 个性化建议生成")
        print("  • 自然语言交互")
        print("  • 用户反馈学习")
        print("  • 替代建议提供")
        
        print("\n🚀 下一步:")
        print("  1. 运行 'python generate_corpus.py' 生成语料库")
        print("  2. 运行 'python app.py' 启动Web应用")
        print("  3. 访问 http://localhost:5000 使用系统")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
