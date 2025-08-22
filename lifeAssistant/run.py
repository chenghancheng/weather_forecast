#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本
"""

import os
import sys

def main():
    print("智能天气建议系统")
    print("1. 生成语料库")
    print("2. 启动Web应用")
    print("3. 测试系统")
    
    choice = input("选择 (1-3): ")
    
    if choice == "1":
        os.system("python generate_corpus.py")
    elif choice == "2":
        os.system("python app.py")
    elif choice == "3":
        os.system("python test_system.py")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
