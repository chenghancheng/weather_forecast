#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气建议对话机器人
支持用户反馈和重新生成建议
"""

import json
import random
from weather_bert import WeatherBERTModel

class WeatherChatbot:
    def __init__(self):
        self.model = WeatherBERTModel()
        self.conversation_history = []
        self.last_weather_data = None  # 添加以保存最后一次天气数据
        self.last_advice = None  # 添加以保存最后一次建议
        
        # 用户反馈处理
        self.feedback_responses = {
            "clothing": {
                "positive": ["很高兴这个建议对你有帮助！", "谢谢你的认可！"],
                "negative": ["我理解你的需求，让我重新为你推荐：", "抱歉，让我提供更好的建议："]
            },
            "travel": {
                "positive": ["出行建议得到认可很开心！", "希望你的出行顺利！"],
                "negative": ["让我重新考虑出行方式：", "我会提供更合适的出行建议："]
            },
            "health": {
                "positive": ["健康提醒很重要，谢谢认可！", "祝你身体健康！"],
                "negative": ["让我重新评估健康建议：", "我会提供更准确的健康提醒："]
            },
            "activity": {
                "positive": ["活动建议对你有用就好！", "祝你活动愉快！"],
                "negative": ["让我重新规划活动：", "我会提供更合适的活动建议："]
            }
        }
        
        # 替代建议模板
        self.alternative_suggestions = {
            "clothing": {
                "cold": [
                    "考虑到你的需求，建议穿厚外套配毛衣，既保暖又时尚",
                    "可以尝试羽绒服搭配保暖内衣，轻便又暖和",
                    "建议穿羊毛大衣，既保暖又有型"
                ],
                "warm": [
                    "建议穿薄外套配T恤，舒适又透气",
                    "可以尝试衬衫配休闲裤，既正式又舒适",
                    "建议穿针织衫，既保暖又不会太热"
                ]
            },
            "travel": {
                "rainy": [
                    "考虑到路况，建议乘坐地铁，既快速又安全",
                    "可以尝试打车，避免淋雨和拥堵",
                    "建议错峰出行，选择人少的时间段"
                ],
                "sunny": [
                    "天气很好，建议步行或骑自行车，享受阳光",
                    "可以尝试公交车，既经济又环保",
                    "建议选择有遮阳的出行路线"
                ]
            },
            "health": {
                "good": [
                    "空气质量不错，建议适度户外活动",
                    "可以尝试室内外结合的活动方式",
                    "建议根据个人情况调整活动强度"
                ],
                "poor": [
                    "空气质量较差，建议减少户外活动时间",
                    "可以尝试室内运动，如瑜伽、健身",
                    "建议使用空气净化器，改善室内环境"
                ]
            },
            "activity": {
                "outdoor": [
                    "天气适宜，建议去公园散步或野餐",
                    "可以尝试户外摄影，记录美好时光",
                    "建议组织朋友聚会，享受户外时光"
                ],
                "indoor": [
                    "天气不佳，建议在家看书、听音乐",
                    "可以尝试室内运动，如健身、跳舞",
                    "建议邀请朋友来家里聚会"
                ]
            }
        }
    
    def get_weather_advice(self, weather_data):
        """获取天气建议"""
        advice = self.model.predict_advice(weather_data)
        
        # 格式化建议
        formatted_advice = {
            "穿衣指数": advice["clothing"],
            "出行建议": advice["travel"],
            "健康提醒": advice["health"],
            "活动规划": advice["activity"]
        }
        
        # 记录最后一次的天气数据和建议
        self.last_weather_data = weather_data
        self.last_advice = formatted_advice
        
        # 记录对话历史
        self.conversation_history.append({
            "type": "weather_request",
            "weather_data": weather_data,
            "advice": advice
        })
        
        return formatted_advice
    
    def handle_user_feedback(self, feedback_type, feedback_sentiment, user_preference=None):
        """处理用户反馈"""
        if feedback_type not in self.feedback_responses:
            return "抱歉，我不理解这个反馈类型。"
        
        # 获取反馈响应
        responses = self.feedback_responses[feedback_type][feedback_sentiment]
        response = random.choice(responses)
        
        # 生成替代建议
        alternative_advice = self._generate_alternative_advice(feedback_type, user_preference)
        
        # 记录反馈
        self.conversation_history.append({
            "type": "user_feedback",
            "feedback_type": feedback_type,
            "sentiment": feedback_sentiment,
            "preference": user_preference
        })
        
        return {
            "response": response,
            "alternative_advice": alternative_advice
        }
    
    # 修复_generate_alternative_advice方法
    def _generate_alternative_advice(self, advice_type, user_preference):
        """生成替代建议"""
        try:
            # 如果有历史天气数据，使用它来生成更准确的建议
            if self.last_weather_data:
                temperature = self.last_weather_data.get("temperature", 20)
                weather = self.last_weather_data.get("weather", "晴天")
            else:
                temperature = 20
                weather = "晴天"
            
            if advice_type == "clothing":
                # 当用户不满意或建议相同时，优先基于温度生成不同建议
                if user_preference and ("不满意" in user_preference or "还是一样" in user_preference):
                    if temperature < 0:
                        return random.choice(self.alternative_suggestions["clothing"]["cold"])
                    elif temperature <= 15:
                        return random.choice(self.alternative_suggestions["clothing"]["cold"])
                    else:
                        return random.choice(self.alternative_suggestions["clothing"]["warm"])
                
                # 优先考虑用户偏好
                if user_preference:
                    if "冷" in user_preference:
                        return random.choice(self.alternative_suggestions["clothing"]["cold"])
                    elif "热" in user_preference:
                        return random.choice(self.alternative_suggestions["clothing"]["warm"])
                
                # 根据温度决定推荐的服装类型
                if temperature < 0:
                    return random.choice(self.alternative_suggestions["clothing"]["cold"])
                elif temperature <= 15:
                    return random.choice(self.alternative_suggestions["clothing"]["cold"])
                else:
                    return random.choice(self.alternative_suggestions["clothing"]["warm"])
            
            elif advice_type == "travel":
                if "雪" in weather or "雨" in weather:
                    return random.choice(self.alternative_suggestions["travel"]["rainy"])
                else:
                    return random.choice(self.alternative_suggestions["travel"]["sunny"])
            
            elif advice_type == "health":
                if "雪" in weather or temperature < 0:
                    return random.choice(self.alternative_suggestions["health"]["poor"])
                else:
                    return random.choice(self.alternative_suggestions["health"]["good"])
            
            elif advice_type == "activity":
                if "雪" in weather or "雨" in weather or temperature < 0:
                    return random.choice(self.alternative_suggestions["activity"]["indoor"])
                else:
                    return random.choice(self.alternative_suggestions["activity"]["outdoor"])
            
            return "让我重新为你考虑合适的建议。"
        except Exception as e:
            # 添加错误处理，防止程序崩溃
            print(f"Error generating alternative advice: {e}")
            return "我会为你提供更合适的建议。"
    
    # 改进_extract_weather_from_input方法，更好地处理负温度
    def _extract_weather_from_input(self, user_input):
        """从用户输入中提取天气信息"""
        # 简化的天气信息提取（实际应用中应该使用NLP技术）
        weather_data = {
            "temperature": 20,
            "weather": "晴天",
            "air_quality_index": 50
        }
        
        # 精确处理温度值
        try:
            # 尝试从用户输入中提取具体的温度数值
            if "-" in user_input and "°" in user_input:
                # 识别负温度 - 改进的正则方式
                temp_part = user_input.split("°")[0]
                if temp_part and temp_part[-1].isdigit() and "-" in temp_part:
                    # 找到负号位置
                    minus_pos = temp_part.rfind("-")
                    if minus_pos >= 0 and minus_pos < len(temp_part) - 1:
                        # 提取负号后的数字
                        temp_str = temp_part[minus_pos+1:]
                        if temp_str.isdigit():
                            weather_data["temperature"] = -int(temp_str)
            elif "°" in user_input:
                # 处理正温度
                temp_part = user_input.split("°")[0]
                if temp_part and temp_part[-1].isdigit():
                    # 提取温度数字部分（去掉可能的非数字字符）
                    temp_str = ''.join([c for c in temp_part if c.isdigit()])
                    if temp_str:
                        weather_data["temperature"] = int(temp_str)
            elif "0°" in user_input:
                weather_data["temperature"] = 0
            elif "冷" in user_input or "零下" in user_input:
                weather_data["temperature"] = random.randint(-10, -1)
            elif "热" in user_input or "高温" in user_input:
                weather_data["temperature"] = random.randint(30, 40)
        except Exception as e:
            print(f"温度提取错误: {e}")
            # 如果提取失败，保持默认值
        
        # 处理天气状况
        if "雪" in user_input:
            weather_data["weather"] = random.choice(["小雪", "中雪", "大雪"])
        elif "雨" in user_input:
            weather_data["weather"] = random.choice(["小雨", "中雨", "大雨"])
        elif "雾" in user_input or "霾" in user_input:
            weather_data["weather"] = "雾"
        elif "晴" in user_input:
            weather_data["weather"] = "晴天"
        
        return weather_data
    
    # 增强chat方法中的错误处理
    def chat(self, user_input):
        """主要对话接口"""
        try:
            if "天气" in user_input or "温度" in user_input:
                # 模拟天气数据（实际应用中应该从API获取）
                weather_data = self._extract_weather_from_input(user_input)
                print(f"提取的天气数据: {weather_data}")  # 调试信息
                advice = self.get_weather_advice(weather_data)
                
                response = "根据当前天气情况，我为你提供以下建议：\n"
                for category, suggestion in advice.items():
                    response += f"• {category}：{suggestion}\n"
                
                response += "\n如果对某个建议不满意，请告诉我具体是哪个方面，我会为你重新推荐！"
                return response
            
            elif "不满意" in user_input or "不好" in user_input or "重新" in user_input or "还是一样" in user_input:
                # 处理用户反馈
                feedback_type = self._identify_feedback_type(user_input)
                if feedback_type:
                    result = self.handle_user_feedback(feedback_type, "negative", user_input)
                    return f"{result['response']}\n\n替代建议：{result['alternative_advice']}"
                else:
                    # 即使无法识别具体类型，也要尝试提供帮助
                    return "请告诉我具体对哪个建议不满意（穿衣、出行、健康、活动），我会为你重新推荐。"
            
            elif "问题" in user_input or "怎么了" in user_input:
                return "可能是我在处理你的请求时出现了一些问题。请你具体说明对哪个建议不满意，我会尽力为你解决！"
            
            elif "谢谢" in user_input or "好" in user_input or "满意" in user_input:
                return "很高兴能帮到你！如果还有其他问题，随时告诉我。"
            
            else:
                return "你好！我是天气建议助手。请告诉我天气情况，我会为你提供穿衣、出行、健康和活动建议。"
        except Exception as e:
            # 添加全局错误处理
            print(f"Error in chat: {e}")
            return "抱歉，我遇到了一些问题。请你重新告诉我天气情况，我会尽力为你提供建议！"
    
    def _identify_feedback_type(self, user_input):
        """识别反馈类型"""
        if "穿衣" in user_input or "衣服" in user_input:
            return "clothing"
        elif "出行" in user_input or "交通" in user_input:
            return "travel"
        elif "健康" in user_input or "身体" in user_input:
            return "health"
        elif "活动" in user_input or "运动" in user_input:
            return "activity"
        return None
    
    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history

def main():
    """主函数 - 测试对话系统"""
    chatbot = WeatherChatbot()
    
    print("=== 天气建议对话机器人 ===")
    print("输入 'quit' 退出对话\n")
    
    while True:
        user_input = input("你: ").strip()
        
        if user_input.lower() == 'quit':
            print("再见！")
            break
        
        response = chatbot.chat(user_input)
        print(f"机器人: {response}\n")

if __name__ == "__main__":
    main()
