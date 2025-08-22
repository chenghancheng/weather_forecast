#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERT天气建议模型训练器
使用生成的语料库训练BERT模型
"""

import json
import torch
import numpy as np
from transformers import (
    BertTokenizer, 
    BertForSequenceClassification,
    BertConfig,
    AdamW,
    get_linear_schedule_with_warmup
)
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import jieba
import re

class WeatherAdviceDataset(Dataset):
    """天气建议数据集"""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class WeatherAdviceTrainer:
    """天气建议模型训练器"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 初始化tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # 建议类型映射
        self.advice_types = {
            "clothing": 0,      # 穿衣建议
            "travel": 1,        # 出行建议
            "health": 2,        # 健康提醒
            "activity": 3       # 活动规划
        }
        
        # 反向映射
        self.id_to_type = {v: k for k, v in self.advice_types.items()}
        
        # 模型配置
        self.config = BertConfig.from_pretrained(
            model_name,
            num_labels=len(self.advice_types),
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1
        )
        
        # 初始化模型
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            config=self.config
        ).to(self.device)
        
    def preprocess_text(self, text):
        """预处理文本"""
        # 使用jieba分词
        words = jieba.cut(text)
        text = ' '.join(words)
        
        # 清理特殊字符
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def prepare_training_data(self, corpus_file="weather_advice_corpus.json"):
        """准备训练数据"""
        print("正在加载语料库...")
        
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        
        texts = []
        labels = []
        
        print("正在处理训练数据...")
        
        for item in corpus:
            # 输入：天气描述
            weather_desc = f"温度{item['temperature']}°C，{item['weather']}，空气质量{item['air_quality_level']}，湿度{item['humidity']}%，风速{item['wind_speed']}m/s"
            weather_desc = self.preprocess_text(weather_desc)
            
            # 为每种建议类型创建训练样本
            advice_pairs = [
                (item['clothing_advice'], "clothing"),
                (item['travel_advice'], "travel"),
                (item['health_reminder'], "health"),
                (item['activity_plan'], "activity")
            ]
            
            for advice, advice_type in advice_pairs:
                # 组合输入
                combined_text = f"{weather_desc} [SEP] {self.preprocess_text(advice)}"
                texts.append(combined_text)
                labels.append(self.advice_types[advice_type])
        
        print(f"训练数据准备完成，共 {len(texts)} 个样本")
        return texts, labels
    
    def train(self, texts, labels, epochs=3, batch_size=16, learning_rate=2e-5):
        """训练模型"""
        print("开始训练模型...")
        
        # 分割训练集和验证集
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        # 创建数据集
        train_dataset = WeatherAdviceDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = WeatherAdviceDataset(val_texts, val_labels, self.tokenizer)
        
        # 创建数据加载器
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # 优化器和学习率调度器
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=total_steps
        )
        
        # 训练循环
        best_val_acc = 0
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            
            # 训练阶段
            self.model.train()
            total_train_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_train_loss += loss.item()
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
            
            avg_train_loss = total_train_loss / len(train_loader)
            
            # 验证阶段
            self.model.eval()
            total_val_loss = 0
            val_predictions = []
            val_true_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    
                    total_val_loss += outputs.loss.item()
                    
                    logits = outputs.logits
                    predictions = torch.argmax(logits, dim=1)
                    
                    val_predictions.extend(predictions.cpu().numpy())
                    val_true_labels.extend(labels.cpu().numpy())
            
            avg_val_loss = total_val_loss / len(val_loader)
            val_accuracy = accuracy_score(val_true_labels, val_predictions)
            
            print(f"训练损失: {avg_train_loss:.4f}")
            print(f"验证损失: {avg_val_loss:.4f}")
            print(f"验证准确率: {val_accuracy:.4f}")
            
            # 保存最佳模型
            if val_accuracy > best_val_acc:
                best_val_acc = val_accuracy
                self.save_model("best_weather_advice_model")
                print("保存最佳模型")
        
        print(f"\n训练完成！最佳验证准确率: {best_val_acc:.4f}")
    
    def save_model(self, model_path):
        """保存模型"""
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        print(f"模型已保存到 {model_path}")
    
    def load_model(self, model_path):
        """加载模型"""
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model.to(self.device)
        print(f"模型已从 {model_path} 加载")
    
    def predict_advice_type(self, text):
        """预测建议类型"""
        self.model.eval()
        
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 编码
        encoding = self.tokenizer.encode_plus(
            processed_text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=1)
            
            # 获取概率分布
            probs = torch.softmax(logits, dim=1)
            
            predicted_type = self.id_to_type[predictions.item()]
            confidence = probs[0][predictions].item()
            
            return predicted_type, confidence

def main():
    """主函数"""
    # 初始化训练器
    trainer = WeatherAdviceTrainer()
    
    # 准备训练数据
    texts, labels = trainer.prepare_training_data()
    
    # 训练模型
    trainer.train(texts, labels, epochs=3, batch_size=16)
    
    # 测试预测
    test_text = "温度25°C，晴天，空气质量良，湿度60%，风速3m/s"
    predicted_type, confidence = trainer.predict_advice_type(test_text)
    print(f"\n测试预测:")
    print(f"输入: {test_text}")
    print(f"预测建议类型: {predicted_type}")
    print(f"置信度: {confidence:.4f}")

if __name__ == "__main__":
    main()
