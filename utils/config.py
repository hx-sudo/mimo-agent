import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_api_config() -> dict:
    config = load_config()
    return {
        "base_url": config["api"]["base_url"],
        "api_key": config["api"]["api_key"],
    }


def get_models() -> list[dict]:
    config = load_config()
    return config["models"]


def get_default_model() -> str:
    config = load_config()
    return config["default_model"]


def get_agent_config() -> dict:
    config = load_config()
    return config["agent"]
