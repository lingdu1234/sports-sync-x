from enum import Enum

import requests
from app.utils.sys_config import cfg


class MsgType(Enum):
    TEXT = "text"
    MARKDOWN_V2 = "markdown_v2"


def send_message(content: str, msg_type: MsgType = MsgType.TEXT) -> dict:
    """
    发送企业微信消息

    Args:
        content: 消息内容
        msg_type: 消息类型，支持 MsgType.TEXT 和 MsgType.MARKDOWN_V2

    Returns:
        响应结果
    """
    # 获取企业微信机器人密钥
    bot_key = cfg.QYWX_BOT_KEY
    if not bot_key:
        return {"error": "QYWX_BOT_KEY not configured"}

    # 构建请求URL
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}"

    # 构建请求体
    if msg_type == MsgType.TEXT:
        data = {"msgtype": "text", "text": {"content": content}}
    elif msg_type == MsgType.MARKDOWN_V2:
        data = {"msgtype": "markdown_v2", "markdown_v2": {"content": content}}
    else:
        return {"error": "Unsupported message type"}

    # 发送请求
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
