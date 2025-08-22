#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能天气建议系统启动脚本
提供菜单选择不同的功能
"""

import os
import sys
import subprocess

def print_banner():
    """打印系统横幅"""
    print("=" * 60)
    print("🌤️  智能天气建议系统")
    print("=" * 60)
    print("基于AI技术的个性化天气建议系统")
    print("支持穿衣、出行、健康和活动建议")
    print("=" * 60)

def check_dependencies():
    """检查依赖是否安装"""
    print("检查系统依赖...")
    
    required_packages = [
        'flask', 'faker', 'torch', 'transformers', 
        'pandas', 'numpy', 'scikit-learn', 'jieba'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("\n所有依赖检查完成！")
    return True

def generate_corpus():
    """生成语料库"""
    print("\n开始生成语料库...")
    try:
        from generate_corpus import WeatherAdviceCorpusGenerator
        
        generator = WeatherAdviceCorpusGenerator()
        corpus = generator.generate_corpus(size=1000)  # 生成1000条测试数据
        
        print(f"✓ 成功生成 {len(corpus)} 条天气建议数据")
        print("✓ 语料库已保存到 weather_advice_corpus.json")
        print("✓ 训练数据已保存到 training_data.json")
        
        return True
    except Exception as e:
        print(f"✗ 语料库生成失败: {e}")
        return False

def start_web_app():
    """启动Web应用"""
    print("\n启动Web应用...")
    print("系统将在 http://localhost:5000 启动")
    print("按 Ctrl+C 停止服务")
    
    try:
        import app
        print("✓ Web应用启动成功！")
    except Exception as e:
        print(f"✗ Web应用启动失败: {e}")
        return False

def test_system():
    """测试系统功能"""
    print("\n开始系统测试...")
    try:
        import test_system
        test_system.main()
        return True
    except Exception as e:
        print(f"✗ 系统测试失败: {e}")
        return False

def show_menu():
    """显示主菜单"""
    while True:
        print("\n" + "=" * 40)
        print("请选择要执行的操作:")
        print("1. 检查系统依赖")
        print("2. 生成语料库")
        print("3. 启动Web应用")
        print("4. 运行系统测试")
        print("5. 查看项目说明")
        print("0. 退出系统")
        print("=" * 40)
        
        choice = input("请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("\n感谢使用智能天气建议系统！再见！")
            break
        elif choice == '1':
            check_dependencies()
        elif choice == '2':
            generate_corpus()
        elif choice == '3':
            start_web_app()
        elif choice == '4':
            test_system()
        elif choice == '5':
            show_project_info()
        else:
            print("无效选项，请重新选择")

def show_project_info():
    """显示项目信息"""
    print("\n" + "=" * 50)
    print("项目信息")
    print("=" * 50)
    print("项目名称: 智能天气建议系统")
    print("技术栈: Python + Flask + BERT + Faker")
    print("主要功能:")
    print("  • 穿衣指数建议")
    print("  • 出行方式推荐")
    print("  • 健康提醒")
    print("  • 活动规划")
    print("  • 智能对话交互")
    print("  • 用户反馈处理")
    print("\n文件说明:")
    print("  • generate_corpus.py - 语料库生成器")
    print("  • weather_bert.py - BERT模型")
    print("  • chat_system.py - 对话系统")
    print("  • app.py - Web应用")
    print("  • test_system.py - 系统测试")
    print("=" * 50)

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        sys.exit(1)
    
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    
    # 显示菜单
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，系统退出")
    except Exception as e:
        print(f"\n系统错误: {e}")
        import traceback
        traceback.print_exc()
