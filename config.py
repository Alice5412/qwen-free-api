"""
配置管理模块，负责加载和管理应用配置
"""

import yaml
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qwen_browser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "headless": True,
    "page_load_timeout": 20,
    "wait_timeout": 15,
    "retry_max": 3,
    "retry_delay": 0.5,
    "poll_interval": 0.2,
    "host": "0.0.0.0",
    "port": 5000
}

# 请求队列配置
MAX_QUEUE_SIZE = 5  # 定义请求队列最大请求数为 5
MAX_WAIT_TIME = 30  # 最大等待时间（秒）

def load_config():
    """加载配置文件，如果失败则使用默认配置"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:  # 明确指定使用 UTF-8 编码
            config = yaml.safe_load(f)
        # 合并默认配置和文件配置
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return DEFAULT_CONFIG  # 使用默认配置

# 加载配置
CONFIG = load_config() 