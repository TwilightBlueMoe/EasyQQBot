import os

from flask import Flask, request, send_file

from config import listen_port, morfonica_path
from handlers import group_messages, group_notices, group_requests, webhooks
from log import logger
from scheduler_tasks import setup_scheduler

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    """处理QQ机器人主要webhook"""
    data = request.json
    logger.debug(f"接收上报数据：{data}")
    post_type = data.get("post_type")

    if post_type == "request":
        return group_requests.handle(data)
    elif post_type == "message":
        return group_messages.handle(data)
    elif post_type == "notice":
        return group_notices.handle(data)

    return {}


@app.route("/webhook", methods=["POST"])
def webhook():
    """处理Git仓库webhook"""
    return webhooks.handle()


@app.route("/welcome")
def welcome():
    """提供欢迎图片"""
    return send_file("welcome.jpg")


@app.route("/morfonica/<path:filename>")
def serve_morfonica_file(filename):
    """提供Morfonica音乐文件服务"""
    try:
        file_path = os.path.join(morfonica_path, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return {"error": "File not found"}, 404
    except Exception as e:
        logger.error(f"Error serving Morfonica file: {e}")
        return {"error": "Internal server error"}, 500


# 创建并启动调度器
scheduler = setup_scheduler()
scheduler.start()


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=listen_port)
    except KeyboardInterrupt:
        logger.info("正在关闭服务器...")
        scheduler.shutdown()
        logger.info("调度器已关闭")
