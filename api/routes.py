"""
API路由定义模块，包含所有API接口路由
"""

import json
import uuid
import threading
import psutil
from time import sleep, time as current_time
from flask import request, Response, jsonify
from selenium.webdriver.common.by import By

from config import CONFIG, MAX_QUEUE_SIZE, MAX_WAIT_TIME, logger
from utils.text import merge_messages
from browser import browser_pool
from browser.actions import new_chat, clear_auto_greeting, send_message, get_response_non_stream
from api import app

# 初始化请求队列和队列锁
request_queue = []  # 初始化请求队列，用于存放请求的唯一 ID
queue_lock = threading.Lock()  # 创建线程锁，确保对请求队列操作时的线程安全

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """
    处理聊天补全请求的 API 接口

    接收 JSON 格式请求，处理消息并返回聊天响应。
    支持流式响应和非流式响应。
    """
    start_time = current_time()
    my_id = uuid.uuid4().hex
    
    # 等待队列处理
    while True:
        with queue_lock:
            if len(request_queue) >= MAX_QUEUE_SIZE:
                if current_time() - start_time > MAX_WAIT_TIME:
                    logger.warning(f"请求 {my_id} 等待超时")
                    return jsonify({"error": "Request timeout in queue"}), 408
                sleep(0.1)
                continue
            request_queue.append(my_id)
            break
    
    try:
        req = request.get_json(force=True)  # 强制解析请求 JSON 数据
        model = req.get("model", "gpt-3.5-turbo")  # 获取模型名称，默认 "gpt-3.5-turbo"
        messages = req.get("messages", [])  # 获取消息列表
        stream = req.get("stream", False)  # 获取是否使用流式响应

        _ = req.get("temperature")  # 获取温度参数（未使用）
        _ = req.get("top_p")  # 获取 top_p 参数（未使用）
        _ = req.get("stream_options")  # 获取流选项（未使用）

        _ = request.headers.get("apikey", "")  # 获取请求头中的 API key（未使用）
        _ = request.args.get("base_url", "")  # 获取查询参数 base_url（未使用）

        merged_message = merge_messages(messages)  # 合并消息列表，构造待发送文本
        if not merged_message:  # 如果合并后的文本为空
            return jsonify({"error": "No valid content in messages"}), 400  # 返回错误和 400 状态码

        chat_id = "chatcmpl-" + uuid.uuid4().hex  # 生成聊天会话 ID
        created_ts = int(current_time())  # 获取当前时间戳
        
        # 从浏览器池中获取一个浏览器实例
        driver, wait = browser_pool.get_browser()
        
        if stream:  # 如果请求流式响应
            def generate():
                """
                生成器函数，用于流式发送响应数据
                """
                first_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": model,
                    "choices": [{
                        "delta": {"role": "assistant"},
                        "index": 0,
                        "finish_reason": None
                    }]
                }
                # 发送首个 chunk，标记角色为 assistant
                yield "data: " + json.dumps(first_chunk) + "\n\n"

                new_chat(driver, wait)  # 创建新对话
                clear_auto_greeting(driver, wait)  # 清除自动问候消息
                send_message(driver, wait, merged_message)  # 发送合并后的消息

                last_text = ""  # 初始化记录上一次响应文本为空
                while True:
                    # 查找所有响应内容容器
                    responses = driver.find_elements(By.CSS_SELECTOR, "div#response-content-container")
                    if not responses:  # 如果未找到响应内容
                        sleep(CONFIG["poll_interval"])  # 等待轮询间隔后继续
                        continue
                    latest_response = responses[-1]  # 获取最新的响应容器
                    paragraphs = latest_response.find_elements(By.TAG_NAME, "p")  # 查找段落元素
                    current_text = "\n".join(p.text for p in paragraphs if p.text)  # 拼接当前响应文本
                    if current_text != last_text:  # 如果响应内容更新
                        new_text = current_text[len(last_text):]  # 提取新增部分
                        chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created_ts,
                            "model": model,
                            "choices": [{
                                "delta": {"content": new_text},
                                "index": 0,
                                "finish_reason": None
                            }]
                        }
                        yield "data: " + json.dumps(chunk) + "\n\n"  # 发送新增部分的响应 chunk
                        last_text = current_text  # 更新记录的响应文本

                    # 检查发送按钮是否处于禁用状态（响应结束标志）
                    send_button = driver.find_elements(
                        By.XPATH,
                        "//button[@id='send-message-button' and @disabled and contains(@class, 'disabled')]"
                    )
                    if send_button:  # 如果找到禁用状态的发送按钮
                        final_chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created_ts,
                            "model": model,
                            "choices": [{
                                "delta": {},
                                "index": 0,
                                "finish_reason": "stop"
                            }]
                        }
                        yield "data: " + json.dumps(final_chunk) + "\n\n"  # 发送结束标识的 chunk
                        yield "data: [DONE]\n\n"  # 发送结束标识
                        break  # 跳出循环，结束流式响应
                    sleep(CONFIG["poll_interval"])  # 等待一段时间后继续轮询
            
            response = Response(generate(), mimetype="text/event-stream")  # 构造流式响应
            @response.call_on_close  # 注册响应关闭时的回调函数
            def on_close():
                browser_pool.return_browser(driver, wait)  # 将浏览器实例归还到池中
            return response  # 返回流式响应
        else:
            # 非流式响应处理流程
            new_chat(driver, wait)  # 创建新对话
            clear_auto_greeting(driver, wait)  # 清除自动问候消息
            send_message(driver, wait, merged_message)  # 发送合并后的消息
            response_text = get_response_non_stream(driver, wait)  # 获取完整响应文本
            full_response = {
                "id": chat_id,
                "object": "chat.completion",
                "created": created_ts,
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": response_text},
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            browser_pool.return_browser(driver, wait)  # 将浏览器实例归还到池中
            return jsonify(full_response)  # 返回完整的响应 JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 捕获异常并返回 500 状态码及错误信息
    finally:
        # 请求处理完成后，从队列中移除当前请求，并输出队列状态
        with queue_lock:
            if request_queue and request_queue[0] == my_id:
                request_queue.pop(0)  # 移除队首请求
            print(f"请求 {my_id} 已处理完成，当前队列长度：{len(request_queue)}")

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    try:
        # 检查浏览器池状态
        with browser_pool.lock:
            active_browsers = len(browser_pool.pool)
            queue_length = len(request_queue)
        
        return jsonify({
            "status": "healthy",
            "active_browsers": active_browsers,
            "queue_length": queue_length,
            "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024  # MB
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500 