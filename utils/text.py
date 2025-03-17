"""
文本处理相关的工具函数
"""

def sanitize_text(text):
    """
    清洗文本，移除或替换不支持的字符

    参数：
        text: 原始文本字符串
    返回：
        处理后的文本字符串
    """
    # 过滤掉 Unicode 编码大于 0x10000 的字符
    return ''.join(char for char in text if ord(char) < 0x10000)

def merge_messages(messages):
    """
    合并消息列表，并添加角色前缀

    参数：
        messages: 包含多条消息的列表，每条消息为字典，包含 "role" 和 "content"
    返回：
        合并后的消息字符串，每条消息之间用双换行分隔
    """
    merged_parts = []  # 初始化存储合并结果的列表
    for msg in messages:  # 遍历每条消息
        role = msg.get("role")  # 获取消息角色
        content = msg.get("content", "").strip()  # 获取消息内容并去除首尾空白
        if not content:  # 如果内容为空则跳过
            continue
        content = sanitize_text(content)  # 清洗消息内容
        if role == "system":  # 如果角色为 system
            merged_parts.append(f"System: {content}")  # 添加带有角色标识的消息
        elif role == "user":  # 如果角色为 user
            merged_parts.append(f"Human: {content}")  # 添加带有角色标识的消息
        elif role == "assistant":  # 如果角色为 assistant
            merged_parts.append(f"Assistant: {content}")  # 添加带有角色标识的消息
        else:
            merged_parts.append(content)  # 其他角色直接添加内容
    return "\n\n".join(merged_parts)  # 使用双换行符连接所有消息 