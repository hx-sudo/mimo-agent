from abc import ABC, abstractmethod


class BaseTool(ABC):
    """工具基类，所有工具都需要继承这个类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述，会传给 LLM"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """参数的 JSON Schema"""
        pass

    @property
    def schema(self) -> dict:
        """OpenAI function calling 格式的 schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """执行工具，返回字符串结果"""
        pass
