"""
浏览器池管理模块，用于管理和复用 Selenium 浏览器实例
"""

import threading
from time import sleep, time as current_time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from browser.actions import init_browser

class BrowserPool:
    """
    浏览器池管理类，用于管理和复用 Selenium 浏览器实例
    """
    def __init__(self, size=1):
        """
        初始化浏览器池

        参数：
            size: 池中浏览器实例数量，默认为 1
        """
        self.pool = []  # 初始化存储浏览器实例的列表
        self.lock = threading.Lock()  # 创建线程锁，确保池操作线程安全
        self.size = size  # 保存池的大小
        self.active_browsers = 0  # 添加活跃浏览器计数
        self.last_cleanup = current_time()  # 添加最后清理时间
        self.initialize()  # 初始化池中的浏览器实例

    def initialize(self):
        """
        初始化浏览器池，创建指定数量的浏览器实例
        """
        for _ in range(self.size):  # 根据池大小循环创建实例
            driver, wait = init_browser()  # 初始化浏览器和等待对象
            driver.get("https://chat.qwen.ai/")  # 打开目标网站
            try:
                # 等待页面加载完成，直到新对话按钮出现
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "sidebar-new-chat-button"))
                )
            except Exception as e:
                print(f"初始化浏览器失败: {e}")  # 输出错误信息
            self.pool.append((driver, wait))  # 将浏览器实例添加到池中

    def get_browser(self):
        """
        从池中获取一个浏览器实例

        Returns:
            (driver, wait): 浏览器实例和关联的 WebDriverWait 对象
        """
        with self.lock:  # 获取线程锁
            if not self.pool:  # 如果池为空
                driver, wait = init_browser()  # 新建一个浏览器实例
                driver.get("https://chat.qwen.ai/")  # 打开目标网站
                return driver, wait  # 返回新实例
            return self.pool.pop()  # 弹出并返回一个已有实例

    def return_browser(self, driver, wait):
        """
        将使用完的浏览器实例归还到池中

        参数：
            driver: 浏览器实例
            wait: 关联的 WebDriverWait 对象
        """
        with self.lock:  # 获取线程锁
            if len(self.pool) < self.size:  # 如果池中实例数量未达到上限
                self.pool.append((driver, wait))  # 将实例归还到池中
            else:
                driver.quit()  # 否则关闭该实例

    def close_all(self):
        """
        关闭池中所有浏览器实例
        """
        with self.lock:  # 获取线程锁
            for driver, _ in self.pool:  # 遍历所有实例
                driver.quit()  # 关闭每个浏览器实例
            self.pool = []  # 清空池列表

    def cleanup_inactive(self):
        """定期清理长时间未使用的浏览器实例"""
        current = current_time()
        if current - self.last_cleanup > 3600:  # 每小时检查一次
            with self.lock:
                for driver, _ in self.pool:
                    try:
                        driver.current_url  # 测试浏览器是否还活着
                    except:
                        driver.quit()
                        self.pool.remove((driver, _))
                self.last_cleanup = current 