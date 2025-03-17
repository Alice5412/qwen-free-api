from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import atexit
from selenium.common.exceptions import TimeoutException

# 执行登录操作
def login(driver, wait, email, password):
    driver.get("https://chat.qwen.ai/")  # 打开通义千问的网页
    print("正在加载页面...")

    try:
        # 点击登录按钮
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'登录')]"))).click()
        # 输入邮箱
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))).send_keys(email)
        # 输入密码
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))).send_keys(password)
        # 点击提交按钮
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        # 等待登录成功，检测到聊天输入框
        wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[contains(@class,'_textAreaBoxWeb_17fi3_89')]")))
        print("登录成功！")
    except TimeoutException:
        print("登录超时，请检查网络或登录信息！")
    except Exception as e:
        print("登录过程中出现异常！", e)

def init_browser():
    chrome_options = Options()
    user_data_dir = os.path.join(os.getcwd(), "selenium_user_data")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    # chrome_options.add_argument('--headless')

    # 常见的无头模式配置
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-webgl')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--log-level=3')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    # 注册程序退出时的清理函数
    atexit.register(safe_quit, driver)
    
    return driver, wait

# 安全关闭浏览器的函数
def safe_quit(driver):
    try:
        driver.quit()
        print("浏览器已安全关闭")
    except Exception as e:
        print(f"关闭浏览器时出现错误: {e}")

def main():
    # 请在此处填写您的登录信息
    email = "your_email@example.com"  # 替换为您的邮箱
    password = "your_password"        # 替换为您的密码

    driver, wait = init_browser()  # 初始化浏览器
    login(driver, wait, email, password)  # 执行登录
    
    # 在这里添加您的其他操作...
    
    # 程序结束时会自动调用注册的safe_quit函数，不需要在这里显式调用driver.quit()
    input("按Enter键退出程序...")

# 程序入口点
if __name__ == "__main__":
    main()