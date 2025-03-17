"""
重试装饰器模块，提供自动重试功能
"""

from time import sleep
from config import CONFIG

def retry_on_failure(func, max_retries=None, delay=None):
    """
    重试装饰器，用于在函数调用失败时自动重试指定次数

    参数：
        func: 需要重试的目标函数
        max_retries: 最大重试次数（默认为 CONFIG["retry_max"]）
        delay: 重试之间的延迟时间（默认为 CONFIG["retry_delay"]）

    返回：
        包装后的函数，在调用时如果出现异常会自动重试
    """
    max_retries = max_retries or CONFIG["retry_max"]  # 若未提供重试次数，则使用默认值
    delay = delay or CONFIG["retry_delay"]  # 若未提供延迟时间，则使用默认值

    def wrapper(*args, **kwargs):  # 定义包装函数
        for attempt in range(max_retries):  # 尝试执行最多 max_retries 次
            try:
                return func(*args, **kwargs)  # 尝试调用目标函数，成功则返回结果
            except Exception as e:  # 捕获异常
                if attempt == max_retries - 1:  # 如果已达到最大重试次数
                    raise e  # 抛出异常
                sleep(delay)  # 否则等待一段时间后重试
        return None  # 如果全部重试后仍失败，返回 None
    return wrapper  # 返回包装后的函数 