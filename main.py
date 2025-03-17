"""
主入口文件，负责启动服务器和初始化资源
"""

import atexit
import threading
import requests
from time import sleep

from config import CONFIG, logger
from browser import browser_pool
from api import app

# 导入路由模块，确保路由被注册
import api.routes

def self_call():
    """
    自调用函数，在服务器启动后自动发送一次 API 请求，用于测试或预热
    """
    sleep(3)  # 等待 3 秒，确保服务器已启动
    url = "http://127.0.0.1:5000/v1/chat/completions"  # 自调用的 API URL
    payload = {  # 构造请求负载
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
        ],
        "stream": True,
        "stream_options": {"include_usage": True}
    }
    headers = {  # 构造请求头
        "Content-Type": "application/json",
        "apikey": "dummy_api_key"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)  # 发送 POST 请求，启用流式响应
        for line in response.iter_lines(decode_unicode=True):  # 逐行迭代响应内容
            if line:
                print(line)  # 打印每行响应数据
    except Exception as e:
        print("自调用异常：", e)  # 如果请求异常则输出错误信息

def cleanup():
    """
    清理资源，在程序退出时关闭所有浏览器实例
    """
    browser_pool.close_all()  # 调用浏览器池的关闭方法关闭所有实例

if __name__ == "__main__":
    # 注册清理函数，确保程序退出时关闭浏览器
    atexit.register(cleanup)
    
    # 启动自调用线程，作为守护线程在后台运行
    threading.Thread(target=self_call, daemon=True).start()
    
    # 启动 Flask 服务器
    app.run(
        host=CONFIG["host"],
        port=CONFIG["port"],
        threaded=True
    ) 