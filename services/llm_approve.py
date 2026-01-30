import asyncio
import json

from log import logger
from services.llm_client import client


async def send_request(model_name: str, system_prompt: str, content: str):
    with open("models.json", "r", encoding="utf-8") as f:
        models = json.load(f)
    try:
        model_config = models[model_name]
        model_id = model_config["model"]
        extra_params = {k: v for k, v in model_config.items() if k != "model"}

        chat_completion = await client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            stream=True,
            **extra_params,
        )

        result_content = ""

        async for chunk in chat_completion:
            if (
                chunk.choices
                and len(chunk.choices) > 0
                and chunk.choices[0].delta.content is not None
            ):
                content_chunk = chunk.choices[0].delta.content
                result_content += content_chunk

        logger.info(f"模型 {model_id} 完整返回内容: {result_content}")

        lines = result_content.split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        if len(lines) != 2:
            raise Exception("返回内容解析失败")
        approve, reason = lines
        if approve == "同意":
            approve = True
        elif approve == "拒绝":
            approve = False
        else:
            raise Exception("返回内容解析失败")
        result = {"approve": approve, "reason": reason}
    except Exception as e:
        logger.exception(f"模型 {model_id} 请求发生错误: {str(e)}")
        result = {"approve": None, "error_message": str(e)}
    result["model_name"] = model_name
    return result


async def review(prompt: str, content: str):
    with open("models.json", "r", encoding="utf-8") as f:
        models = json.load(f)
    tasks = [send_request(model_id, prompt, content) for model_id in models.keys()]
    return [await coro for coro in asyncio.as_completed(tasks)]
