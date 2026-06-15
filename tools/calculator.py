from tools.base import BaseTool


class Calculator(BaseTool):
    """计算器工具"""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "计算数学表达式，支持加减乘除、幂运算等"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如 '2 + 3 * 4'",
                },
            },
            "required": ["expression"],
        }

    def execute(self, expression: str) -> str:
        try:
            # 只允许安全的数学运算
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return "错误: 表达式包含不允许的字符"
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"计算出错: {e}"
