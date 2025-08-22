#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气预报建议语料库生成器
使用faker生成各种天气条件下的建议数据
"""

import json
import random
from faker import Faker
from datetime import datetime, timedelta

# 设置中文环境
fake = Faker(['zh_CN'])

class WeatherAdviceCorpusGenerator:
    def __init__(self):
        self.temperature_ranges = [
            (-20, -10, "极寒"),
            (-10, 0, "寒冷"),
            (0, 10, "冷"),
            (10, 20, "凉爽"),
            (20, 30, "温暖"),
            (30, 40, "炎热"),
            (40, 50, "酷热")
        ]
        
        self.weather_conditions = [
            "晴天", "多云", "阴天", "小雨", "中雨", "大雨", "暴雨",
            "小雪", "中雪", "大雪", "雾", "霾", "沙尘暴", "台风"
        ]
        
        self.air_quality_levels = [
            (0, 50, "优", "绿色"),
            (51, 100, "良", "黄色"),
            (101, 150, "轻度污染", "橙色"),
            (151, 200, "中度污染", "红色"),
            (201, 300, "重度污染", "紫色"),
            (301, 500, "严重污染", "褐色")
        ]
        
        self.clothing_suggestions = {
            "极寒": [
                "建议穿羽绒服、厚毛衣、保暖内衣、围巾、手套、帽子",
                "建议穿厚棉衣、羊毛衫、保暖裤、雪地靴",
                "建议穿皮草大衣、高领毛衣、加厚裤子、保暖鞋"
            ],
            "寒冷": [
                "建议穿厚外套、毛衣、保暖内衣、围巾",
                "建议穿棉服、羊毛衫、加厚裤子、保暖鞋",
                "建议穿呢子大衣、高领毛衣、保暖裤"
            ],
            "冷": [
                "建议穿外套、毛衣、长裤",
                "建议穿夹克、针织衫、牛仔裤",
                "建议穿风衣、卫衣、休闲裤"
            ],
            "凉爽": [
                "建议穿薄外套、长袖衬衫、长裤",
                "建议穿针织衫、休闲裤、运动鞋",
                "建议穿卫衣、牛仔裤、帆布鞋"
            ],
            "温暖": [
                "建议穿短袖、薄外套、长裤",
                "建议穿T恤、衬衫、休闲裤",
                "建议穿连衣裙、薄外套、凉鞋"
            ],
            "炎热": [
                "建议穿短袖、短裤、凉鞋",
                "建议穿背心、短裙、拖鞋",
                "建议穿T恤、短裤、运动鞋"
            ],
            "酷热": [
                "建议穿轻薄透气的短袖、短裤",
                "建议穿背心、短裙、凉鞋",
                "建议穿防晒衣、短裤、凉鞋"
            ]
        }
        
        self.travel_suggestions = {
            "晴天": [
                "天气晴朗，建议步行或骑自行车，享受阳光",
                "晴天适合开车出行，注意防晒",
                "建议乘坐公交车，避免长时间暴晒"
            ],
            "多云": [
                "天气适宜，建议步行或骑自行车",
                "多云天气适合各种出行方式",
                "建议乘坐地铁，避免拥堵"
            ],
            "阴天": [
                "天气阴沉，建议乘坐公交车或地铁",
                "阴天适合开车出行，注意安全",
                "建议步行，享受凉爽天气"
            ],
            "小雨": [
                "小雨天气，建议带伞步行或乘坐公交车",
                "建议乘坐地铁，避免淋雨",
                "开车注意路面湿滑，减速慢行"
            ],
            "中雨": [
                "中雨天气，建议乘坐地铁或公交车",
                "建议打车出行，避免淋雨",
                "开车注意积水，谨慎驾驶"
            ],
            "大雨": [
                "大雨天气，建议乘坐地铁，避免外出",
                "建议打车或乘坐公交车",
                "开车危险，建议选择公共交通"
            ],
            "暴雨": [
                "暴雨天气，建议避免外出，选择地铁",
                "建议在家办公，避免出行",
                "开车极其危险，禁止出行"
            ],
            "小雪": [
                "小雪天气，建议步行或乘坐公交车",
                "建议乘坐地铁，避免路面湿滑",
                "开车注意减速，保持车距"
            ],
            "中雪": [
                "中雪天气，建议乘坐地铁或公交车",
                "建议打车出行，避免路面湿滑",
                "开车注意防滑，谨慎驾驶"
            ],
            "大雪": [
                "大雪天气，建议乘坐地铁，避免外出",
                "建议在家办公，避免出行",
                "开车危险，建议选择公共交通"
            ],
            "雾": [
                "雾天能见度低，建议乘坐地铁",
                "建议乘坐公交车，避免开车",
                "开车注意开启雾灯，减速慢行"
            ],
            "霾": [
                "霾天空气质量差，建议乘坐地铁",
                "建议乘坐公交车，减少户外暴露",
                "开车注意开启空气净化器"
            ],
            "沙尘暴": [
                "沙尘暴天气，建议避免外出",
                "建议乘坐地铁，减少户外暴露",
                "开车注意关闭车窗，开启空调"
            ],
            "台风": [
                "台风天气，建议避免外出",
                "建议在家办公，确保安全",
                "禁止开车出行，注意防护"
            ]
        }
        
        self.health_reminders = {
            "优": [
                "空气质量优秀，适合户外活动",
                "空气质量很好，可以正常户外运动",
                "空气质量佳，适合开窗通风"
            ],
            "良": [
                "空气质量良好，可以正常户外活动",
                "空气质量不错，适合户外运动",
                "空气质量尚可，建议适度户外活动"
            ],
            "轻度污染": [
                "空气质量轻度污染，敏感人群减少户外活动",
                "建议戴口罩，减少户外运动时间",
                "敏感人群注意防护，避免长时间户外活动"
            ],
            "中度污染": [
                "空气质量中度污染，建议戴口罩",
                "敏感人群避免户外活动，建议室内运动",
                "建议减少户外活动，注意防护"
            ],
            "重度污染": [
                "空气质量重度污染，建议戴口罩，避免户外活动",
                "敏感人群禁止户外活动，建议室内运动",
                "建议避免户外活动，注意防护"
            ],
            "严重污染": [
                "空气质量严重污染，禁止户外活动",
                "敏感人群禁止外出，建议室内活动",
                "建议避免外出，注意防护"
            ]
        }
        
        self.activity_suggestions = {
            "晴天": [
                "天气晴朗，适合户外野餐",
                "晴天适合户外运动，如跑步、骑行",
                "建议去公园散步，享受阳光",
                "适合户外摄影，光线充足",
                "晴天适合户外烧烤聚会"
            ],
            "多云": [
                "天气适宜，适合户外活动",
                "多云天气适合公园散步",
                "建议户外运动，如慢跑、太极",
                "适合户外野餐，避免暴晒",
                "多云天气适合户外摄影"
            ],
            "阴天": [
                "天气凉爽，适合户外散步",
                "阴天适合户外运动，避免中暑",
                "建议去公园游玩，享受凉爽",
                "适合户外野餐，天气舒适",
                "阴天适合户外摄影，光线柔和"
            ],
            "小雨": [
                "小雨天气，适合室内活动",
                "建议在家看书、听音乐",
                "适合室内运动，如瑜伽、健身",
                "小雨适合泡茶、看电影",
                "建议室内聚会，享受温馨时光"
            ],
            "中雨": [
                "中雨天气，建议室内活动",
                "适合在家办公、学习",
                "建议室内运动，如健身、跳舞",
                "中雨适合煮咖啡、看书",
                "建议室内聚会，避免淋雨"
            ],
            "大雨": [
                "大雨天气，建议室内活动",
                "适合在家休息、放松",
                "建议室内运动，如瑜伽、冥想",
                "大雨适合看电影、听音乐",
                "建议室内聚会，确保安全"
            ],
            "小雪": [
                "小雪天气，适合室内活动",
                "建议在家取暖、休息",
                "适合室内运动，如健身、跳舞",
                "小雪适合煮热茶、看书",
                "建议室内聚会，享受温暖"
            ],
            "中雪": [
                "中雪天气，建议室内活动",
                "适合在家取暖、放松",
                "建议室内运动，如瑜伽、健身",
                "中雪适合煮热饮、看电影",
                "建议室内聚会，避免寒冷"
            ],
            "大雪": [
                "大雪天气，建议室内活动",
                "适合在家取暖、休息",
                "建议室内运动，如健身、跳舞",
                "大雪适合煮热饮、听音乐",
                "建议室内聚会，确保温暖"
            ]
        }

    def generate_temperature(self):
        """生成随机温度"""
        temp_range = random.choice(self.temperature_ranges)
        temperature = random.uniform(temp_range[0], temp_range[1])
        return round(temperature, 1), temp_range[2]

    def generate_weather(self):
        """生成随机天气"""
        return random.choice(self.weather_conditions)

    def generate_air_quality(self):
        """生成随机空气质量"""
        aq_range = random.choice(self.air_quality_levels)
        aqi = random.randint(aq_range[0], aq_range[1])
        return aqi, aq_range[2], aq_range[3]

    def generate_clothing_advice(self, temp_level):
        """生成穿衣建议"""
        suggestions = self.clothing_suggestions.get(temp_level, ["建议根据温度适当增减衣物"])
        return random.choice(suggestions)

    def generate_travel_advice(self, weather):
        """生成出行建议"""
        suggestions = self.travel_suggestions.get(weather, ["建议根据天气情况选择合适出行方式"])
        return random.choice(suggestions)

    def generate_health_reminder(self, aq_level):
        """生成健康提醒"""
        reminders = self.health_reminders.get(aq_level, ["注意关注空气质量变化"])
        return random.choice(reminders)

    def generate_activity_plan(self, weather):
        """生成活动规划"""
        plans = self.activity_suggestions.get(weather, ["建议根据天气情况安排合适活动"])
        return random.choice(plans)

    def generate_weather_data(self):
        """生成单条天气数据"""
        temperature, temp_level = self.generate_temperature()
        weather = self.generate_weather()
        aqi, aq_level, aq_color = self.generate_air_quality()
        
        # 生成时间
        date = fake.date_between(start_date='-30d', end_date='+30d')
        time = fake.time()
        
        # 生成建议
        clothing = self.generate_clothing_advice(temp_level)
        travel = self.generate_travel_advice(weather)
        health = self.generate_health_reminder(aq_level)
        activity = self.generate_activity_plan(weather)
        
        # 生成湿度、风速等额外信息
        humidity = random.randint(30, 95)
        wind_speed = round(random.uniform(0, 20), 1)
        visibility = random.randint(1, 30)
        
        return {
            "id": fake.uuid4(),
            "datetime": f"{date} {time}",
            "temperature": temperature,
            "temperature_level": temp_level,
            "weather": weather,
            "air_quality_index": aqi,
            "air_quality_level": aq_level,
            "air_quality_color": aq_color,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "visibility": visibility,
            "clothing_advice": clothing,
            "travel_advice": travel,
            "health_reminder": health,
            "activity_plan": activity,
            "location": fake.city(),
            "description": f"{temp_level}天气，{weather}，空气质量{aq_level}"
        }

    def generate_corpus(self, size=10000):
        """生成指定大小的语料库"""
        corpus = []
        
        print(f"开始生成{size}条天气建议数据...")
        
        for i in range(size):
            if (i + 1) % 1000 == 0:
                print(f"已生成 {i + 1} 条数据...")
            
            weather_data = self.generate_weather_data()
            corpus.append(weather_data)
        
        print(f"语料库生成完成！共生成 {len(corpus)} 条数据")
        return corpus

    def save_corpus(self, corpus, filename="weather_advice_corpus.json"):
        """保存语料库到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2)
        print(f"语料库已保存到 {filename}")

    def generate_training_data(self, corpus):
        """生成BERT训练数据"""
        training_data = []
        
        for item in corpus:
            # 输入文本：天气描述
            input_text = f"温度{item['temperature']}°C，{item['weather']}，空气质量{item['air_quality_level']}，湿度{item['humidity']}%，风速{item['wind_speed']}m/s"
            
            # 输出文本：综合建议
            output_text = f"穿衣建议：{item['clothing_advice']}。出行建议：{item['travel_advice']}。健康提醒：{item['health_reminder']}。活动规划：{item['activity_plan']}"
            
            training_data.append({
                "input": input_text,
                "output": output_text,
                "metadata": {
                    "temperature": item['temperature'],
                    "weather": item['weather'],
                    "air_quality": item['air_quality_level'],
                    "clothing": item['clothing_advice'],
                    "travel": item['travel_advice'],
                    "health": item['health_reminder'],
                    "activity": item['activity_plan']
                }
            })
        
        return training_data

def main():
    """主函数"""
    generator = WeatherAdviceCorpusGenerator()
    
    # 生成语料库
    corpus = generator.generate_corpus(size=5000)
    
    # 保存原始语料库
    generator.save_corpus(corpus, "weather_advice_corpus.json")
    
    # 生成训练数据
    training_data = generator.generate_training_data(corpus)
    
    # 保存训练数据
    with open("training_data.json", 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print("训练数据已保存到 training_data.json")
    
    # 显示示例数据
    print("\n=== 示例数据 ===")
    for i, item in enumerate(corpus[:3]):
        print(f"\n示例 {i+1}:")
        print(f"时间: {item['datetime']}")
        print(f"温度: {item['temperature']}°C ({item['temperature_level']})")
        print(f"天气: {item['weather']}")
        print(f"空气质量: {item['air_quality_index']} ({item['air_quality_level']})")
        print(f"穿衣建议: {item['clothing_advice']}")
        print(f"出行建议: {item['travel_advice']}")
        print(f"健康提醒: {item['health_reminder']}")
        print(f"活动规划: {item['activity_plan']}")

if __name__ == "__main__":
    main()
