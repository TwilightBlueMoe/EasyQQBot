import requests

from config import bot_id, post_url
from log import logger

session = requests.Session()


def send_message(group_id, message):
    """发送消息到指定群组"""
    session.post(
        f"{post_url}/send_msg",
        data={
            "group_id": group_id,
            "message": message,
            "auto_escape": True,
        },
    )


def forward_messages(group_id, messages):
    """转发消息到指定群组"""
    contents = [{"type": "text", "data": {"text": msg}} for msg in messages]
    messages = [
        {
            "type": "node",
            "data": {"uin": bot_id, "name": "ee0000", "content": content},
        }
        for content in contents
    ]
    session.post(
        f"{post_url}/send_group_forward_msg",
        json={
            "group_id": group_id,
            "messages": messages,
        },
    )


def set_group_whole_ban(group_id, enable):
    """设置群全体禁言"""
    try:
        session.post(
            f"{post_url}/set_group_whole_ban",
            json={"group_id": group_id, "enable": enable},
        )
        action = "禁言" if enable else "解禁"

        logger.info(f"已对群 {group_id} 进行{action}操作")
    except Exception as e:
        logger.error(f"设置群全体禁言失败: {e}")


def set_group_admin(group_id, user_id, enable):
    """设置群管理员"""
    session.post(
        f"{post_url}/set_group_admin",
        data={
            "group_id": group_id,
            "user_id": user_id,
            "enable": "true" if enable else "false",
        },
    )


def get_stranger_info(user_id):
    """获取陌生人信息"""
    return session.get(
        f"{post_url}/get_stranger_info", params={"user_id": user_id}
    ).json()["data"]
