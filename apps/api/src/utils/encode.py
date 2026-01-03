import asyncio
import base64


async def encode_base64(text: str) -> str:
    """
    Асинхронно кодирует текст в Base64.

    Args:
        text (str): Исходная строка.

    Returns:
        str: Base64-представление строки.
    """
    def _encode() -> str:
        data = text.encode("utf-8")
        return base64.b64encode(data).decode("ascii")

    return await asyncio.to_thread(_encode)