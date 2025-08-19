# NEW-110
import json
from typing import Any, Dict
from loguru import logger

def parse_callback_data(callback_data: str) -> Dict[str, Any]:
    """
    Callback data stringini lug'atga parslaydi.
    """
    try:
        data = json.loads(callback_data)
        if not isinstance(data, dict):
            return {"action": callback_data, "raw_data": callback_data}
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Callback data JSON formatida emas: {callback_data}. Xato: {e}")
        return {"action": callback_data, "raw_data": callback_data}

def build_callback_data(action: str, **kwargs: Any) -> str:
    """
    Lug'atdan callback data stringini quradi.
    """
    data = {"action": action, **kwargs}
    return json.dumps(data)