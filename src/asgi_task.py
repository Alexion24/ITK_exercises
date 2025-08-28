# Приложение должно отдавать курс валюты к доллару используя стороннее АПИ
# https://api.exchangerate-api.com/v4/latest/{currency}
# Например, в ответ на http://localhost:8000/USD должен возвращаться ответ вида:
# {"provider":"https://www.exchangerate-api.com",
# "WARNING_UPGRADE_TO_V6":"https://www.exchangerate-api.com/docs/free",
# "terms":"https://www.exchangerate-api.com/terms","base":"USD","date":"2024-09-18","time_last_updated":1726617601,
# "rates":{"USD":1,"AED":3.67,"AFN":69.45,"ALL":89.49, "AMD":387.39,"ANG":1.79,"AOA":939.8, ... }
# Данные, соотвественно, для доллара должны браться из https://api.exchangerate-api.com/v4/latest/USD
# Для решения задачи запрещено использовать фреймворки.


import asyncio
import json
import urllib.request
from typing import Any, Dict

API_URL_PATTERN = "https://api.exchangerate-api.com/v4/latest/{currency}"
PROVIDER = "https://www.exchangerate-api.com"
WARNING_UPGRADE_TO_V6 = "https://www.exchangerate-api.com/docs/free"
TERMS = "https://www.exchangerate-api.com/terms"


async def app(scope: Dict, receive: Any, send: Any) -> None:
    assert scope["type"] == "http"
    path = scope.get("path", "/")
    if not path or len(path) < 2:
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")],
            }
        )
        await send(
            {"type": "http.response.body", "body": b"Currency code required like /USD"}
        )
        return
    currency_code = path[1:].upper()
    if not currency_code.isalpha() or len(currency_code) != 3:
        await send(
            {
                "type": "http.response.start",
                "status": 400,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")],
            }
        )
        await send({"type": "http.response.body", "body": b"Invalid currency code"})
        return
    try:
        data = await fetch_exchange_rates(currency_code)
    except Exception as e:
        await send(
            {
                "type": "http.response.start",
                "status": 502,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": f"Failed to get rates from provider: {e}".encode("utf-8"),
            }
        )
        return
    result = {
        "provider": PROVIDER,
        "WARNING_UPGRADE_TO_V6": WARNING_UPGRADE_TO_V6,
        "terms": TERMS,
        "base": data["base"],
        "date": data["date"],
        "time_last_updated": data["time_last_updated"],
        "rates": data["rates"],
    }
    body = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def fetch_exchange_rates(currency_code: str) -> Dict[str, Any]:
    url = API_URL_PATTERN.format(currency=currency_code)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None,
        lambda: json.loads(
            urllib.request.urlopen(url, timeout=5).read().decode("utf-8")
        ),
    )
    return data


# -------------------------------
# Как запустить это ASGI-приложение:
#
# 1. Убедитесь, что зависимости установлены через uv:
#      uv install
#
# 2. Запустите приложение через uv:
#      uv run uvicorn asgi_task:app --host 0.0.0.0 --port 8000
#
# 3. Теперь GET-запросы вида http://localhost:8000/USD будут возвращать курсы в нужном формате.
# -------------------------------
