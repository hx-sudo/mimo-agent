import json
import requests
from utils.config import get_api_config, get_agent_config
from utils.logger import get_logger

logger = get_logger("agent")


class Agent:
    def __init__(self, model: str):
        api_config = get_api_config()
        agent_config = get_agent_config()

        self.base_url = api_config["base_url"]
        self.api_key = api_config["api_key"]
        self.model = model
        self.temperature = agent_config["temperature"]
        self.max_turns = agent_config["max_turns"]
        self.messages = []

        # 初始化系统提示词
        system_prompt = agent_config["system_prompt"]
        self.messages.append({"role": "system", "content": system_prompt})

        # 工具注册表
        self.tools = []
        self.tool_schemas = []

        logger.info(f"Agent 初始化完成，模型: {model}")

    def register_tool(self, tool):
        self.tools.append(tool)
        self.tool_schemas.append(tool.schema)
        logger.info(f"注册工具: {tool.name}")

    def chat(self, user_input: str, images: list = None) -> dict:
        """与 agent 对话，返回 {"thinking": 思考过程, "content": 最终回复}"""
        logger.info(f"用户输入: {user_input[:100]}")
        if images:
            content = [{"type": "text", "text": user_input}]
            for img in images:
                content.append({"type": "image_url", "image_url": {"url": img}})
            self.messages.append({"role": "user", "content": content})
        else:
            self.messages.append({"role": "user", "content": user_input})

        for turn in range(self.max_turns):
            logger.debug(f"--- 第 {turn + 1} 轮 ---")

            try:
                payload = {
                    "model": self.model,
                    "messages": self.messages,
                    "temperature": self.temperature,
                }
                if self.tool_schemas:
                    payload["tools"] = self.tool_schemas

                resp = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                result = resp.json()

                msg = result["choices"][0]["message"]
                content = msg.get("content", "") or ""
                tool_calls = msg.get("tool_calls") or []
                thinking = msg.get("reasoning_content", "") or ""

                logger.debug(f"LLM 响应: {content[:80] if content else 'tool_call'}")
                if thinking:
                    logger.debug(f"思考过程: {thinking[:80]}")

            except Exception as e:
                logger.error(f"LLM 调用异常: {e}", exc_info=True)
                error_msg = f"调用模型出错: {e}"
                self.messages.append({"role": "assistant", "content": error_msg})
                return {"thinking": "", "content": error_msg}

            # 没有工具调用 → 直接返回
            if not tool_calls:
                self.messages.append({"role": "assistant", "content": content})
                logger.info(f"Agent 回复: {content[:100]}")
                return {"thinking": thinking, "content": content}

            # 有工具调用 → 执行工具
            logger.info(f"调用工具: {[tc['function']['name'] for tc in tool_calls]}")
            self.messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                result = self._execute_tool(tc)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        logger.warning("达到最大轮数")
        return {"thinking": "", "content": "达到最大轮数，对话结束。"}

    def _execute_tool(self, tool_call) -> str:
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        logger.info(f"执行工具: {name}，参数: {args}")

        for tool in self.tools:
            if tool.name == name:
                try:
                    result = tool.execute(**args)
                    logger.info(f"工具结果: {result[:100]}")
                    return result
                except Exception as e:
                    logger.error(f"工具执行出错: {e}")
                    return f"工具执行出错: {e}"

        logger.warning(f"未找到工具: {name}")
        return f"未找到工具: {name}"

    def clear_history(self):
        self.messages = [self.messages[0]]
        logger.info("对话历史已清除")
