import asyncio
from threading import Thread

from bot_client import forward_messages, get_stranger_info, send_message
from config import approve_requirements
from log import logger
from services.llm_approve import review

def handle(data):
    """处理入群请求"""
    logger.info("处理入群请求")
    group_id = data.get("group_id")
    comment = data["comment"]
    user_id = data["user_id"]

    # 如果comment为空字符串或只包含空白字符，直接通过审核
    # 这是因为邀请群员加群时，审核消息为空
    if not comment or comment.strip() == "":
        logger.info(f"用户 {user_id} 的入群申请comment为空，直接通过审核")
        return {"approve": True}

    llm_summary = []

    if group_id in approve_requirements:
        level = approve_requirements[group_id].get("level", 0)
        if level > 0:
            stranger_data = get_stranger_info(user_id)
            if stranger_data["level"] <= level:
                send_message(
                    group_id,
                    f"申请者{stranger_data['nickname']}（{user_id}）等级过低，不处理",
                )
                return {}

        filename = approve_requirements[group_id]["prompt"]
        with open(f"system_prompts/{filename}.md", "r", encoding="utf-8") as f:
            prompt = f.read()
        results = asyncio.run(review(prompt, comment))

        approve_votes = 0
        reject_votes = 0

        for res in results:
            model_name = res["model_name"]
            if res["approve"]:
                approve_votes += 1
                reason = res.get("reason", "无")
                llm_summary.append(f"{model_name}同意加群：\n{reason}")
            elif res["approve"] is False:
                reject_votes += 1
                reason = res.get("reason", "无")
                llm_summary.append(f"{model_name}反对加群：\n{reason}")
            else:
                error = res.get("error_message", "未知错误")
                llm_summary.append(f"{model_name}请求发生错误：{error}")

        llm_message = f"LLM投票结果为{approve_votes}:{reject_votes}\n"
        if approve_votes > reject_votes:
            final_approve_action = True
            llm_message += "同意"
        elif reject_votes > approve_votes:
            final_approve_action = False
            llm_message += "拒绝"
        else:
            final_approve_action = None
            llm_message += "不处理"
        llm_message += f"{user_id}的入群申请：\n{comment}"

        def send_llm_results():
            forward_messages(group_id, llm_summary)
            send_message(group_id, llm_message)

        Thread(target=send_llm_results).start()

        if final_approve_action is not None:
            return {"approve": final_approve_action}

    return {}
