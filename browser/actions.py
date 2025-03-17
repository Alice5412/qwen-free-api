"""
浏览器操作相关函数，包括初始化浏览器、页面交互等
"""

import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from config import CONFIG
from utils.retry import retry_on_failure
from utils.text import sanitize_text

def init_browser():
    """
    初始化 Chrome 浏览器实例，并返回浏览器对象及其对应的 WebDriverWait 对象

    Returns:
        driver: 初始化后的 Chrome WebDriver 对象
        wait: 关联的 WebDriverWait 对象，用于显式等待
    """
    chrome_options = Options()  # 创建 Chrome 配置选项对象
    if CONFIG.get("headless", False):  # 根据配置判断是否启用无头模式
        chrome_options.add_argument("--headless=new")  # 添加无头模式参数（新版 Chrome 可能需要）
    
    user_data_dir = os.path.join(os.getcwd(), "selenium_user_data")  # 构造用户数据目录路径
    if not os.path.exists(user_data_dir):  # 如果目录不存在
        os.makedirs(user_data_dir)  # 则创建该目录
    
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')  # 指定用户数据目录
    chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用 /dev/shm 使用，提高资源利用率
    chrome_options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
    chrome_options.add_argument('--ignore-ssl-errors')  # 忽略 SSL 错误
    chrome_options.add_argument('--disable-webgl')  # 禁用 WebGL 加速
    chrome_options.add_argument('--disable-software-rasterizer')  # 禁用软件光栅化
    chrome_options.add_argument('--disable-extensions')  # 禁用浏览器扩展
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 排除日志相关开关
    chrome_options.add_argument('--log-level=3')  # 设置日志级别为 3（只输出错误）
    
    # 添加性能优化参数
    chrome_options.add_argument('--disable-features=TranslateUI')  # 禁用翻译 UI
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')  # 禁用站点隔离
    chrome_options.add_argument('--disable-site-isolation-trials')  # 禁用站点隔离试验
    chrome_options.add_argument('--disable-infobars')  # 禁用信息提示栏
    chrome_options.add_argument('--disable-notifications')  # 禁用通知
    chrome_options.add_argument('--disable-popup-blocking')  # 禁用弹窗拦截
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片加载以加快加载速度
    chrome_options.add_argument('--js-flags=--expose-gc')  # 启用垃圾回收
    chrome_options.add_argument('--disable-default-apps')  # 禁用默认应用
    
    # 添加更多性能优化参数
    chrome_options.add_argument('--disable-javascript')  # 如果不需要JS可以禁用
    chrome_options.add_argument('--disk-cache-size=1')  # 限制磁盘缓存
    chrome_options.add_argument('--media-cache-size=1')  # 限制媒体缓存
    chrome_options.add_argument('--aggressive-cache-discard')  # 激进的缓存清理
    chrome_options.add_argument('--disable-application-cache')  # 禁用应用缓存
    
    service = Service()  # 创建 ChromeDriver 服务对象（使用默认设置）
    driver = webdriver.Chrome(service=service, options=chrome_options)  # 使用指定服务和配置选项启动 Chrome 浏览器
    driver.set_page_load_timeout(CONFIG["page_load_timeout"])  # 设置页面加载超时时间
    wait = WebDriverWait(driver, CONFIG["wait_timeout"], poll_frequency=CONFIG["poll_interval"])  # 创建 WebDriverWait 对象
    return driver, wait  # 返回浏览器和等待对象

@retry_on_failure  # 应用重试装饰器
def new_chat(driver, wait):
    """
    创建新对话

    参数：
        driver: Chrome WebDriver 对象
        wait: WebDriverWait 对象
    """
    try:
        # 等待新对话按钮可点击，并点击
        new_chat_button = wait.until(EC.element_to_be_clickable((By.ID, "sidebar-new-chat-button")))  # 等待新对话按钮可点击
        new_chat_button.click()  # 点击新对话按钮
        sleep(0.3)  # 等待 0.3 秒
    except Exception as e:
        print(f"创建新对话失败: {e}")  # 输出错误信息
        raise  # 抛出异常以便重试

@retry_on_failure  # 应用重试装饰器
def clear_auto_greeting(driver, wait):
    """
    清除自动问候消息

    参数：
        driver: Chrome WebDriver 对象
        wait: WebDriverWait 对象
    """
    try:
        sleep(0.5)  # 等待 0.5 秒以确保页面加载完成
        # 查找包含 "profile" 和 "Qwen" 的元素，认为是自动问候消息
        greetings = driver.find_elements(By.XPATH, "//*[contains(text(), 'profile') and contains(text(), 'Qwen')]")  # 查找自动问候消息元素
        for elem in greetings:  # 遍历所有找到的元素
            driver.execute_script("arguments[0].remove();", elem)  # 使用 JavaScript 移除该元素
    except Exception as e:
        print(f"清除自动问候失败: {e}")  # 输出错误信息

@retry_on_failure  # 应用重试装饰器
def send_message(driver, wait, message):
    """
    发送消息到聊天输入框

    参数：
        driver: Chrome WebDriver 对象
        wait: WebDriverWait 对象
        message: 需要发送的消息文本
    """
    try:
        # 等待聊天输入框出现
        input_box = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@id='chat-input']")))
        # 设置输入框的值，先进行文本清洗
        driver.execute_script("arguments[0].value = arguments[1]", input_box, sanitize_text(message))
        # 触发输入事件，确保前端能检测到变化
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", input_box)
        
        # 等待发送按钮可点击
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='send-message-button']")))
        driver.execute_script("arguments[0].click();", send_button)  # 点击发送按钮
    except Exception as e:
        print(f"发送消息失败: {e}")  # 输出错误信息
        raise  # 抛出异常以便重试

@retry_on_failure  # 应用重试装饰器
def get_response_non_stream(driver, wait):
    """
    获取非流式模式下的响应文本

    参数：
        driver: Chrome WebDriver 对象
        wait: WebDriverWait 对象

    返回：
        response_text: 获取到的响应文本
    """
    try:
        # 等待发送按钮处于禁用状态（带有 disabled 属性和类），表示响应已生成
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@id='send-message-button' and @disabled and contains(@class, 'disabled')]")
        ))
        
        # 查找所有响应内容的容器
        responses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#response-content-container")))
        if not responses:  # 如果未找到响应容器
            raise Exception("未找到响应内容")
            
        latest_response = responses[-1]  # 获取最新的响应容器
        paragraphs = latest_response.find_elements(By.TAG_NAME, "p")  # 查找所有段落元素
        response_text = "\n".join(p.text for p in paragraphs if p.text)  # 拼接段落文本
        
        if not response_text:  # 如果响应文本为空
            raise Exception("响应内容为空")
            
        return response_text  # 返回响应文本
    except Exception as e:
        print(f"获取响应失败: {e}")  # 输出错误信息
        raise  # 抛出异常以便重试 