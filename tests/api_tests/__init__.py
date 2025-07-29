"""
API测试包
========
基于API测试优先级文档生成的完整测试套件

测试分类：
- 核心业务接口测试 (🔥 最高优先级)
- 重要业务接口测试 (⚠️ 高优先级)  
- 功能业务接口测试 (📊 中优先级)
- 系统管理接口测试 (🔧 低优先级)

使用方法：
1. 运行所有API测试：
   pytest tests/api_tests/

2. 运行特定优先级测试：
   pytest tests/api_tests/ -m "core"      # 核心接口
   pytest tests/api_tests/ -m "important" # 重要接口
   pytest tests/api_tests/ -m "functional" # 功能接口
   pytest tests/api_tests/ -m "system"    # 系统接口

3. 运行特定功能测试：
   pytest tests/api_tests/ -k "chat"      # 聊天相关
   pytest tests/api_tests/ -k "payment"   # 支付相关
   pytest tests/api_tests/ -k "session"   # 会话相关

4. 生成测试报告：
   pytest tests/api_tests/ --html=reports/api_test_report.html
   pytest tests/api_tests/ --alluredir=reports/allure
"""

__version__ = "1.0.0"
__author__ = "API Testing Team"
__description__ = "Comprehensive API test suite based on priority guidelines" 