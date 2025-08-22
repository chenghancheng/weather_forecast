#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气对话系统
"""

import random

class WeatherChatSystem:
    def __init__(self):
        self.alternatives = {
            "穿衣指数": [
                "建议穿厚外套配毛衣，既保暖又时尚",
                "可以尝试羽绒服搭配保暖内衣，轻便又暖和",
                "建议穿羊毛大衣，既保暖又有型",
                "推荐穿加厚卫衣配牛仔裤，舒适又保暖",
                "建议穿皮夹克配高领毛衣，既帅气又保暖"
            ],
            "出行建议": [
                "建议乘坐地铁，既快速又安全",
                "可以尝试打车，避免淋雨和拥堵",
                "建议错峰出行，选择人少的时间段",
                "推荐使用共享单车，既环保又健康",
                "建议选择有遮阳的出行路线"
            ],
            "健康提醒": [
                "建议减少户外活动时间，保护呼吸系统",
                "可以尝试室内运动，如瑜伽、健身",
                "建议使用空气净化器，改善室内环境",
                "推荐多喝水，保持身体水分",
                "建议适当补充维生素C，增强免疫力"
            ],
            "活动规划": [
                "建议去公园散步或野餐，享受自然",
                "可以尝试户外摄影，记录美好时光",
                "建议组织朋友聚会，增进感情",
                "推荐去博物馆或图书馆，增长知识",
                "建议在家烹饪美食，享受生活"
            ]
        }
        self.last_weather_data = None  # 存储最后一次的天气数据
    
    def get_advice(self, weather_data):
        """获取天气建议"""
        self.last_weather_data = weather_data  # 保存天气数据
        advice = {
            "穿衣指数": self._get_clothing(weather_data["temperature"]),
            "出行建议": self._get_travel(weather_data["weather"], weather_data["temperature"], weather_data["air_quality"]),
            "健康提醒": self._get_health(weather_data["air_quality"], weather_data["temperature"], weather_data["weather"]),
            "活动规划": self._get_activity(weather_data["weather"], weather_data["temperature"], weather_data["air_quality"])
        }
        return advice
    
    def _get_clothing(self, temp):
        """获取穿衣建议，添加随机性"""
        if temp < 0:
            suggestions = [
                "建议穿羽绒服、厚毛衣、保暖内衣",
                "推荐穿加厚棉服、羊毛衫、保暖裤",
                "建议穿皮草大衣、高领毛衣、加厚打底裤",
                "推荐穿羊绒大衣、保暖内衣套装"
            ]
        elif temp < 15:
            suggestions = [
                "建议穿外套、毛衣、长裤",
                "推荐穿风衣、针织衫、牛仔裤",
                "建议穿夹克、卫衣、休闲裤",
                "推荐穿西装外套、衬衫、西裤"
            ]
        else:
            suggestions = [
                "建议穿薄外套、长袖衬衫",
                "推荐穿T恤、短裤、凉鞋",
                "建议穿连衣裙、薄开衫",
                "推荐穿运动装、运动鞋"
            ]
        return random.choice(suggestions)
    
    def _get_travel(self, weather, temp=None, aqi=None):
        """获取出行建议，综合考虑天气、温度和空气质量"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的出行建议
            suggestions = [
                "天气寒冷，建议减少不必要的外出",
                "低温天气路滑，建议选择安全的出行方式",
                "寒冷天气建议乘坐有暖气的交通工具",
                "建议错峰出行，避开早晚低温时段"
            ]
            return random.choice(suggestions)
        
        if temp is not None and temp > 35:
            # 炎热天气的出行建议
            suggestions = [
                "天气炎热，建议避免正午时分出行",
                "高温天气建议选择有空调的交通工具",
                "建议在早晚凉爽时段出行",
                "炎热天气注意防暑，多补充水分"
            ]
            return random.choice(suggestions)
        
        if "雪" in weather or "冰" in weather:
            # 雪天/冰天的出行建议
            suggestions = [
                "雪天路滑，建议乘坐公共交通，安全第一",
                "推荐打车出行，避免滑倒",
                "建议减少不必要的外出",
                "推荐选择有除雪设施的路线"
            ]
            return random.choice(suggestions)
        
        if "雨" in weather:
            # 雨天的出行建议
            suggestions = [
                "雨天建议乘坐地铁，避免开车",
                "推荐使用打车软件，避免淋雨",
                "建议错峰出行，避开交通高峰",
                "推荐选择有遮雨设施的路线"
            ]
            return random.choice(suggestions)
        
        if "雾" in weather or "霾" in weather:
            # 雾霾天气的出行建议
            if aqi and aqi > 100:
                suggestions = [
                    "雾霾天气能见度低，建议减少外出",
                    "空气质量差，建议选择密闭的交通工具",
                    "建议戴口罩出行，保护呼吸系统",
                    "雾霾天气建议错峰出行，避开污染高峰"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议减少外出",
                    "建议选择安全的出行方式",
                    "雾天建议错峰出行，避开交通高峰",
                    "建议使用导航设备，确保出行安全"
                ]
            return random.choice(suggestions)
        
        # 正常天气条件下的出行建议
        if aqi and aqi > 100:
            suggestions = [
                "空气质量差，建议减少户外出行时间",
                "建议选择密闭的交通工具，避免吸入有害物质",
                "可以尝试室内外结合的出行方式",
                "建议在空气质量较好的时段出行"
            ]
        else:
            suggestions = [
                "天气适宜，建议步行或骑自行车",
                "推荐使用共享单车，既环保又健康",
                "建议选择风景优美的步行路线",
                "推荐结伴出行，增加安全性"
            ]
        
        return random.choice(suggestions)
    
    def _get_health(self, aqi, temp=None, weather=None):
        """获取健康建议，综合考虑空气质量、温度和天气状况"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的健康建议
            suggestions = [
                "天气寒冷，建议减少户外活动时间，注意保暖",
                "低温天气容易感冒，建议多喝热水，增强免疫力",
                "寒冷天气注意关节保护，避免长时间暴露在低温环境",
                "建议在室内进行适度运动，保持身体活力"
            ]
            return random.choice(suggestions)
        
        if weather and ("雪" in weather or "冰" in weather):
            # 雪天/冰天的健康建议
            suggestions = [
                "雪天路滑，建议减少外出，避免摔倒受伤",
                "雪天空气清新但寒冷，建议在室内活动",
                "雪天注意保暖，避免感冒和冻伤",
                "建议在温暖的室内进行运动，保持健康"
            ]
            return random.choice(suggestions)
        
        if weather and ("雨" in weather):
            # 雨天的健康建议
            suggestions = [
                "雨天潮湿，建议保持室内通风，预防感冒",
                "雨天路滑，建议减少外出，注意安全",
                "雨天适合室内运动，如瑜伽、健身",
                "建议使用除湿设备，保持室内环境舒适"
            ]
            return random.choice(suggestions)
        
        if weather and ("雾" in weather or "霾" in weather):
            # 雾霾天气的健康建议
            if aqi > 100:
                suggestions = [
                    "空气质量差，建议戴口罩，减少户外活动",
                    "雾霾天气对呼吸系统有害，建议使用空气净化器",
                    "建议多吃清肺食物，如梨、百合、银耳",
                    "雾霾天气建议在室内运动，避免吸入有害物质"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议减少外出，注意安全",
                    "建议保持室内通风，使用空气净化设备",
                    "雾天适合室内活动，如看书、听音乐",
                    "建议多喝水，保持呼吸道湿润"
                ]
            return random.choice(suggestions)
        
        # 正常天气条件下的健康建议（主要考虑空气质量）
        if aqi > 100:
            suggestions = [
                "空气质量差，建议戴口罩，减少户外运动时间",
                "建议使用空气净化器，改善室内环境",
                "推荐多吃清肺食物，如梨、百合、银耳",
                "建议在室内进行运动，避免吸入有害物质"
            ]
        elif aqi > 50:
            suggestions = [
                "空气质量一般，建议适度户外活动",
                "可以尝试室内外结合的活动方式",
                "建议根据个人情况调整活动强度",
                "推荐在空气质量较好的时段进行户外活动"
            ]
        else:
            # 空气质量很好，但还要考虑温度
            if temp is not None and temp > 30:
                suggestions = [
                    "天气炎热，建议避免正午时分户外活动",
                    "高温天气注意防暑降温，多补充水分",
                    "建议在早晚凉爽时段进行户外活动",
                    "炎热天气适合室内运动，如游泳、健身"
                ]
            elif temp is not None and temp < 10:
                suggestions = [
                    "天气较冷，建议适度户外活动，注意保暖",
                    "可以尝试室内外结合的活动方式",
                    "建议根据个人体质调整活动强度",
                    "推荐在温暖的室内进行运动"
                ]
            else:
                suggestions = [
                    "空气质量良好，适合户外活动",
                    "推荐进行有氧运动，增强体质",
                    "建议多晒太阳，补充维生素D",
                    "推荐户外散步，呼吸新鲜空气"
                ]
        
        return random.choice(suggestions)
    
    def _get_activity(self, weather, temp=None, aqi=None):
        """获取活动建议，综合考虑天气、温度和空气质量"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的活动建议
            suggestions = [
                "天气寒冷，建议在温暖的室内活动",
                "低温天气适合在家看书、听音乐",
                "建议邀请朋友来家里聚会",
                "寒冷天气适合室内运动，如瑜伽、健身"
            ]
            return random.choice(suggestions)
        
        if temp is not None and temp > 35:
            # 炎热天气的活动建议
            suggestions = [
                "天气炎热，建议避免正午时分户外活动",
                "高温天气适合在室内游泳、健身",
                "建议在早晚凉爽时段进行户外活动",
                "炎热天气适合在家享受空调，看电影"
            ]
            return random.choice(suggestions)
        
        if "雪" in weather or "冰" in weather:
            # 雪天/冰天的活动建议
            suggestions = [
                "雪天路滑，建议在室内活动",
                "雪天适合在家看书、听音乐",
                "建议邀请朋友来家里聚会",
                "雪天适合室内运动，保持身体活力"
            ]
            return random.choice(suggestions)
        
        if "雨" in weather:
            # 雨天的活动建议
            suggestions = [
                "雨天适合在家看书、听音乐",
                "推荐在家烹饪美食，享受生活",
                "建议邀请朋友来家里聚会",
                "推荐在家看电影、玩游戏"
            ]
            return random.choice(suggestions)
        
        if "雾" in weather or "霾" in weather:
            # 雾霾天气的活动建议
            if aqi and aqi > 100:
                suggestions = [
                    "雾霾天气建议在室内活动",
                    "空气质量差，适合在家看书、听音乐",
                    "建议在家做瑜伽、健身",
                    "雾霾天气适合邀请朋友来家里聚会"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议在室内活动",
                    "建议在家看书、听音乐",
                    "雾天适合在家做瑜伽、健身",
                    "建议邀请朋友来家里聚会"
                ]
            return random.choice(suggestions)
        
        # 正常天气条件下的活动建议
        if "晴" in weather:
            if aqi and aqi > 100:
                suggestions = [
                    "虽然天气晴朗，但空气质量较差，建议室内活动",
                    "建议在家看书、听音乐，享受阳光透过窗户",
                    "可以在家做瑜伽、健身，保持健康",
                    "建议邀请朋友来家里聚会，享受室内时光"
                ]
            else:
                suggestions = [
                    "天气晴朗，适合户外野餐",
                    "推荐去公园散步，享受阳光",
                    "建议组织户外烧烤活动",
                    "推荐去郊外踏青，亲近自然"
                ]
        else:
            if aqi and aqi > 100:
                suggestions = [
                    "空气质量较差，建议在室内活动",
                    "建议在家看书、听音乐",
                    "适合在家做瑜伽、健身",
                    "建议邀请朋友来家里聚会"
                ]
            else:
                suggestions = [
                    "天气适宜，建议室内外结合活动",
                    "推荐去博物馆或图书馆",
                    "建议在家做瑜伽或健身",
                    "推荐去咖啡厅看书、工作"
                ]
        
        return random.choice(suggestions)
    
    def get_alternative(self, category, weather_data=None, previous_advice=None):
        """获取替代建议，根据当前天气条件智能生成，避免重复"""
        if weather_data is None:
            # 如果没有提供天气数据，使用默认值
            weather_data = {"temperature": 25, "weather": "晴天", "air_quality": 50}
        
        if category == "穿衣指数":
            return self._get_clothing_alternative(weather_data["temperature"], previous_advice)
        elif category == "出行建议":
            return self._get_travel_alternative(weather_data["weather"], weather_data["temperature"], weather_data["air_quality"], previous_advice)
        elif category == "健康提醒":
            return self._get_health_alternative(weather_data["air_quality"], weather_data["temperature"], weather_data["weather"], previous_advice)
        elif category == "活动规划":
            return self._get_activity_alternative(weather_data["weather"], weather_data["temperature"], weather_data["air_quality"], previous_advice)
        else:
            # 如果类别不匹配，从预定义库中选择
            if category in self.alternatives:
                return random.choice(self.alternatives[category])
            return "让我重新为你考虑建议"
    
    def _get_clothing_alternative(self, temp, previous_advice=None):
        """获取穿衣替代建议，避免重复"""
        if temp < 0:
            suggestions = [
                "建议穿羽绒服、厚毛衣、保暖内衣",
                "推荐穿加厚棉服、羊毛衫、保暖裤",
                "建议穿皮草大衣、高领毛衣、加厚打底裤",
                "推荐穿羊绒大衣、保暖内衣套装"
            ]
        elif temp < 15:
            suggestions = [
                "建议穿外套、毛衣、长裤",
                "推荐穿风衣、针织衫、牛仔裤",
                "建议穿夹克、卫衣、休闲裤",
                "推荐穿西装外套、衬衫、西裤"
            ]
        else:
            suggestions = [
                "建议穿薄外套、长袖衬衫",
                "推荐穿T恤、短裤、凉鞋",
                "建议穿连衣裙、薄开衫",
                "推荐穿运动装、运动鞋"
            ]
        
        # 如果有之前的建议，过滤掉相同的
        if previous_advice:
            suggestions = [s for s in suggestions if s != previous_advice]
        
        # 如果过滤后没有建议了，返回一个通用的替代建议
        if not suggestions:
            if temp < 0:
                return "建议穿厚实的冬季服装，注意保暖"
            elif temp < 15:
                return "建议穿春秋季节的服装，适当增减"
            else:
                return "建议穿轻便的夏季服装，注意防晒"
        
        return random.choice(suggestions)
    
    def _get_travel_alternative(self, weather, temp, aqi, previous_advice=None):
        """获取出行替代建议，避免重复"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的出行建议
            suggestions = [
                "天气寒冷，建议减少不必要的外出",
                "低温天气路滑，建议选择安全的出行方式",
                "寒冷天气建议乘坐有暖气的交通工具",
                "建议错峰出行，避开早晚低温时段"
            ]
        elif temp is not None and temp > 35:
            # 炎热天气的出行建议
            suggestions = [
                "天气炎热，建议避免正午时分出行",
                "高温天气建议选择有空调的交通工具",
                "建议在早晚凉爽时段出行",
                "炎热天气注意防暑，多补充水分"
            ]
        elif "雪" in weather or "冰" in weather:
            # 雪天/冰天的出行建议
            suggestions = [
                "雪天路滑，建议乘坐公共交通，安全第一",
                "推荐打车出行，避免滑倒",
                "建议减少不必要的外出",
                "推荐选择有除雪设施的路线"
            ]
        elif "雨" in weather:
            # 雨天的出行建议
            suggestions = [
                "雨天建议乘坐地铁，避免开车",
                "推荐使用打车软件，避免淋雨",
                "建议错峰出行，避开交通高峰",
                "推荐选择有遮雨设施的路线"
            ]
        elif "雾" in weather or "霾" in weather:
            # 雾霾天气的出行建议
            if aqi > 100:
                suggestions = [
                    "雾霾天气能见度低，建议减少外出",
                    "空气质量差，建议选择密闭的交通工具",
                    "建议戴口罩出行，保护呼吸系统",
                    "雾霾天气建议错峰出行，避开污染高峰"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议减少外出",
                    "建议选择安全的出行方式",
                    "雾天建议错峰出行，避开交通高峰",
                    "建议使用导航设备，确保出行安全"
                ]
        else:
            # 正常天气条件下的出行建议
            if aqi > 100:
                suggestions = [
                    "空气质量差，建议减少户外出行时间",
                    "建议选择密闭的交通工具，避免吸入有害物质",
                    "可以尝试室内外结合的出行方式",
                    "建议在空气质量较好的时段出行"
                ]
            else:
                suggestions = [
                    "天气适宜，建议步行或骑自行车",
                    "推荐使用共享单车，既环保又健康",
                    "建议选择风景优美的步行路线",
                    "推荐结伴出行，增加安全性"
                ]
        
        # 过滤掉相同的建议
        if previous_advice:
            suggestions = [s for s in suggestions if s != previous_advice]
        
        if not suggestions:
            return "建议根据实际情况选择合适的出行方式"
        
        return random.choice(suggestions)
    
    def _get_health_alternative(self, aqi, temp, weather, previous_advice=None):
        """获取健康替代建议，避免重复"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的健康建议
            suggestions = [
                "天气寒冷，建议减少户外活动时间，注意保暖",
                "低温天气容易感冒，建议多喝热水，增强免疫力",
                "寒冷天气注意关节保护，避免长时间暴露在低温环境",
                "建议在室内进行适度运动，保持身体活力"
            ]
        elif weather and ("雪" in weather or "冰" in weather):
            # 雪天/冰天的健康建议
            suggestions = [
                "雪天路滑，建议减少外出，避免摔倒受伤",
                "雪天空气清新但寒冷，建议在室内活动",
                "雪天注意保暖，避免感冒和冻伤",
                "建议在温暖的室内进行运动，保持健康"
            ]
        elif weather and ("雨" in weather):
            # 雨天的健康建议
            suggestions = [
                "雨天潮湿，建议保持室内通风，预防感冒",
                "雨天路滑，建议减少外出，注意安全",
                "雨天适合室内运动，如瑜伽、健身",
                "建议使用除湿设备，保持室内环境舒适"
            ]
        elif weather and ("雾" in weather or "霾" in weather):
            # 雾霾天气的健康建议
            if aqi > 100:
                suggestions = [
                    "空气质量差，建议戴口罩，减少户外活动",
                    "雾霾天气对呼吸系统有害，建议使用空气净化器",
                    "建议多吃清肺食物，如梨、百合、银耳",
                    "雾霾天气建议在室内运动，避免吸入有害物质"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议减少外出，注意安全",
                    "建议保持室内通风，使用空气净化设备",
                    "雾天适合室内活动，如看书、听音乐",
                    "建议多喝水，保持呼吸道湿润"
                ]
        else:
            # 正常天气条件下的健康建议（主要考虑空气质量）
            if aqi > 100:
                suggestions = [
                    "空气质量差，建议戴口罩，减少户外运动时间",
                    "建议使用空气净化器，改善室内环境",
                    "推荐多吃清肺食物，如梨、百合、银耳",
                    "建议在室内进行运动，避免吸入有害物质"
                ]
            elif aqi > 50:
                suggestions = [
                    "空气质量一般，建议适度户外活动",
                    "可以尝试室内外结合的活动方式",
                    "建议根据个人情况调整活动强度",
                    "推荐在空气质量较好的时段进行户外活动"
                ]
            else:
                # 空气质量很好，但还要考虑温度
                if temp is not None and temp > 30:
                    suggestions = [
                        "天气炎热，建议避免正午时分户外活动",
                        "高温天气注意防暑降温，多补充水分",
                        "建议在早晚凉爽时段进行户外活动",
                        "炎热天气适合室内运动，如游泳、健身"
                    ]
                elif temp is not None and temp < 10:
                    suggestions = [
                        "天气较冷，建议适度户外活动，注意保暖",
                        "可以尝试室内外结合的活动方式",
                        "建议根据个人体质调整活动强度",
                        "推荐在温暖的室内进行运动"
                    ]
                else:
                    suggestions = [
                        "空气质量良好，适合户外活动",
                        "推荐进行有氧运动，增强体质",
                        "建议多晒太阳，补充维生素D",
                        "推荐户外散步，呼吸新鲜空气"
                    ]
        
        # 过滤掉相同的建议
        if previous_advice:
            suggestions = [s for s in suggestions if s != previous_advice]
        
        if not suggestions:
            return "建议根据个人情况调整活动强度"
        
        return random.choice(suggestions)
    
    def _get_activity_alternative(self, weather, temp, aqi, previous_advice=None):
        """获取活动替代建议，避免重复"""
        # 首先检查极端天气条件
        if temp is not None and temp < 0:
            # 寒冷天气的活动建议
            suggestions = [
                "天气寒冷，建议在温暖的室内活动",
                "低温天气适合在家看书、听音乐",
                "建议邀请朋友来家里聚会",
                "寒冷天气适合室内运动，如瑜伽、健身"
            ]
        elif temp is not None and temp > 35:
            # 炎热天气的活动建议
            suggestions = [
                "天气炎热，建议避免正午时分户外活动",
                "高温天气适合在室内游泳、健身",
                "建议在早晚凉爽时段进行户外活动",
                "炎热天气适合在家享受空调，看电影"
            ]
        elif "雪" in weather or "冰" in weather:
            # 雪天/冰天的活动建议
            suggestions = [
                "雪天路滑，建议在室内活动",
                "雪天适合在家看书、听音乐",
                "建议邀请朋友来家里聚会",
                "雪天适合室内运动，保持身体活力"
            ]
        elif "雨" in weather:
            # 雨天的活动建议
            suggestions = [
                "雨天适合在家看书、听音乐",
                "推荐在家烹饪美食，享受生活",
                "建议邀请朋友来家里聚会",
                "推荐在家看电影、玩游戏"
            ]
        elif "雾" in weather or "霾" in weather:
            # 雾霾天气的活动建议
            if aqi > 100:
                suggestions = [
                    "雾霾天气建议在室内活动",
                    "空气质量差，适合在家看书、听音乐",
                    "建议在家做瑜伽、健身",
                    "雾霾天气适合邀请朋友来家里聚会"
                ]
            else:
                suggestions = [
                    "雾天能见度低，建议在室内活动",
                    "建议在家看书、听音乐",
                    "雾天适合在家做瑜伽、健身",
                    "建议邀请朋友来家里聚会"
                ]
        else:
            # 正常天气条件下的活动建议
            if "晴" in weather:
                if aqi > 100:
                    suggestions = [
                        "虽然天气晴朗，但空气质量较差，建议室内活动",
                        "建议在家看书、听音乐，享受阳光透过窗户",
                        "可以在家做瑜伽、健身，保持健康",
                        "建议邀请朋友来家里聚会，享受室内时光"
                    ]
                else:
                    suggestions = [
                        "天气晴朗，适合户外野餐",
                        "推荐去公园散步，享受阳光",
                        "建议组织户外烧烤活动",
                        "推荐去郊外踏青，亲近自然"
                    ]
            else:
                if aqi and aqi > 100:
                    suggestions = [
                        "空气质量较差，建议在室内活动",
                        "建议在家看书、听音乐",
                        "适合在家做瑜伽、健身",
                        "建议邀请朋友来家里聚会"
                    ]
                else:
                    suggestions = [
                        "天气适宜，建议室内外结合活动",
                        "推荐去博物馆或图书馆",
                        "建议在家做瑜伽或健身",
                        "推荐去咖啡厅看书、工作"
                    ]
        
        # 过滤掉相同的建议
        if previous_advice:
            suggestions = [s for s in suggestions if s != previous_advice]
        
        if not suggestions:
            return "建议根据个人喜好选择合适的活动"
        
        return random.choice(suggestions)
    
    def _extract_weather_from_chat(self, user_input):
        """从聊天输入中智能提取天气信息"""
        weather_data = {
            "temperature": 20,  # 默认温度
            "weather": "晴天",   # 默认天气
            "air_quality": 50   # 默认空气质量
        }
        
        # 提取温度信息 - 修复负温度识别
        if "气温" in user_input or "温度" in user_input or "°" in user_input:
            import re
            # 匹配各种温度格式：气温0°、温度25度、25°C、-25°等
            temp_patterns = [
                r'气温(-?\d+)[°度]',
                r'温度(-?\d+)[°度]',
                r'(-?\d+)[°度]',
                r'(-?\d+)°C',
                r'(-?\d+)度'
            ]
            
            for pattern in temp_patterns:
                match = re.search(pattern, user_input)
                if match:
                    temp = int(match.group(1))
                    weather_data["temperature"] = temp
                    break
        
        # 提取天气状况部分保持不变...
        
        return weather_data
    
    def _identify_feedback_type(self, user_input):
        """识别用户反馈的类型"""
        if any(keyword in user_input for keyword in ["穿衣", "衣服", "穿着", "穿搭"]):
            return "穿衣指数"
        elif any(keyword in user_input for keyword in ["出行", "交通", "路线", "道路"]):
            return "出行建议"
        elif any(keyword in user_input for keyword in ["健康", "身体", "养生", "保健"]):
            return "健康提醒"
        elif any(keyword in user_input for keyword in ["活动", "运动", "安排", "计划"]):
            return "活动规划"
        return None
    
    def handle_user_feedback(self, feedback_type, feedback_sentiment, user_input):
        """处理用户反馈，生成替代建议"""
        # 反馈响应模板
        feedback_responses = {
            "穿衣指数": {
                "negative": ["我理解你的需求，让我重新为你推荐：", "抱歉，让我提供更好的穿衣建议："],
                "positive": ["很高兴这个穿衣建议对你有帮助！", "谢谢你的认可！"]
            },
            "出行建议": {
                "negative": ["让我重新考虑出行方式：", "我会提供更合适的出行建议："],
                "positive": ["出行建议得到认可很开心！", "希望你的出行顺利！"]
            },
            "健康提醒": {
                "negative": ["让我重新评估健康建议：", "我会提供更准确的健康提醒："],
                "positive": ["健康提醒很重要，谢谢认可！", "祝你身体健康！"]
            },
            "活动规划": {
                "negative": ["让我重新规划活动：", "我会提供更合适的活动建议："],
                "positive": ["活动建议对你有用就好！", "祝你活动愉快！"]
            }
        }
        
        # 获取合适的响应
        response = random.choice(feedback_responses.get(feedback_type, {}).get(feedback_sentiment, ["让我重新为你考虑建议。"]))
        
        # 生成替代建议
        # 使用最后一次的天气数据来生成准确的替代建议
        weather_data = self.last_weather_data if self.last_weather_data else {"temperature": 20, "weather": "晴天", "air_quality": 50}
        
        # 获取替代建议
        alternative_advice = self.get_alternative(feedback_type, weather_data)
        
        return {
            "response": response,
            "alternative_advice": alternative_advice
        }
    
    def chat(self, user_input):
        """对话接口"""
        try:
            if "天气" in user_input or "气温" in user_input or "穿什么" in user_input or "°" in user_input:
                # 从用户输入中提取天气信息
                weather_data = self._extract_weather_from_chat(user_input)
                advice = self.get_advice(weather_data)
                
                response = "根据您提到的天气情况，我为您提供以下建议：\n"
                for category, suggestion in advice.items():
                    response += f"• {category}：{suggestion}\n"
                
                response += "\n如果对某个建议不满意，请告诉我具体是哪个方面，我会为您重新推荐！"
                return response
            
            elif "不满意" in user_input or "不好" in user_input or "重新" in user_input:
                # 处理用户反馈
                try:
                    feedback_type = self._identify_feedback_type(user_input)
                    if feedback_type:
                        result = self.handle_user_feedback(feedback_type, "negative", user_input)
                        return f"{result['response']}\n\n替代建议：{result['alternative_advice']}"
                    else:
                        return "请告诉我具体对哪个建议不满意（穿衣、出行、健康、活动），我会为您重新推荐。"
                except Exception as e:
                    print(f"处理反馈时出错: {e}")
                    return "抱歉，处理您的请求时出现了一些问题，请稍后再试。"
            
            elif "谢谢" in user_input or "好" in user_input or "满意" in user_input:
                return "很高兴能帮到您！如果还有其他问题，随时告诉我。"
            
            else:
                return "您好！我是天气建议助手。请告诉我天气情况（如：气温25度，晴天），我会为您提供穿衣、出行、健康和活动建议。"
        except Exception as e:
            print(f"对话处理出错: {e}")
            return "抱歉，我遇到了一些问题。请您重新告诉我天气情况，我会尽力为您提供建议！"

def main():
    chat = WeatherChatSystem()
    print("天气对话系统")
    print(chat.chat("今天天气怎么样？"))

if __name__ == "__main__":
    main()
