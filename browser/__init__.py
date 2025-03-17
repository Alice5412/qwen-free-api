"""
浏览器模块，包含浏览器操作和管理相关功能
"""

from browser.pool import BrowserPool
from browser.actions import init_browser, new_chat, clear_auto_greeting, send_message, get_response_non_stream

# 创建浏览器池实例
browser_pool = BrowserPool(size=1) 