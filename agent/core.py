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
        self.summary_token_limit = agent_config.get("summary_token_limit", 40000)
        self.summary_keep_tokens = agent_config.get("summary_keep_tokens", 8000)
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

        # 检查是否需要压缩历史
        self._maybe_compress()

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

    def _estimate_tokens(self, text: str) -> int:
        """简单估算 token 数（中文约 1.5 字/token，英文约 4 字符/token）"""
        if not text:
            return 0
        cn_chars = sum(1 for c in text if '一' <= c <= '鿿')
        other_chars = len(text) - cn_chars
        return int(cn_chars / 1.5 + other_chars / 4) + 4  # +4 为 role/format 开销

    def _messages_tokens(self, messages: list) -> int:
        """估算消息列表的总 token 数"""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        total += self._estimate_tokens(part.get("text", ""))
                    elif part.get("type") == "image_url":
                        total += 1000  # 图片固定估算 1000 token
            else:
                total += self._estimate_tokens(content)
            total += 4  # role、格式开销
        return total

    def _build_summary(self, messages_to_summarize: list) -> str:
        """调用 LLM 生成对话摘要"""
        summary_prompt = "请将以下对话总结成一段简短的摘要，保留关键信息、用户的需求和偏好、以及重要的结论。用中文回答。"
        summary_messages = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": json.dumps(messages_to_summarize, ensure_ascii=False, indent=2)},
        ]
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": summary_messages,
                    "temperature": 0.3,
                },
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return ""

    def _maybe_compress(self):
        """检查是否需要压缩，超过 token 限制时自动摘要"""
        total = self._messages_tokens(self.messages)
        if total <= self.summary_token_limit:
            return

        logger.info(f"当前 token 数: {total}，超过阈值 {self.summary_token_limit}，执行压缩")

        # 从后往前保留最近的消息，直到 token 数接近 keep_tokens
        system_msg = self.messages[0]  # system prompt 始终保留
        remaining = self.messages[1:]  # 非 system 消息

        keep_tokens = 0
        split_idx = len(remaining)
        for i in range(len(remaining) - 1, -1, -1):
            msg_tokens = self._messages_tokens([remaining[i]])
            if keep_tokens + msg_tokens > self.summary_keep_tokens:
                split_idx = i + 1
                break
            keep_tokens += msg_tokens

        # 没有需要压缩的部分
        if split_idx == 0:
            return

        to_summarize = remaining[:split_idx]
        to_keep = remaining[split_idx:]

        # 生成摘要
        summary = self._build_summary(to_summarize)
        if not summary:
            logger.warning("摘要生成失败，跳过压缩")
            return

        # 替换消息历史
        summary_msg = {"role": "system", "content": f"[对话摘要] {summary}"}
        self.messages = [system_msg, summary_msg] + to_keep

        new_total = self._messages_tokens(self.messages)
        logger.info(f"压缩完成: {total} → {new_total} token")
