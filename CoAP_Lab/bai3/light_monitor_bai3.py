"""Bai 3 - Light Monitoring Client: dang ky CoAP Observe de nhan thong bao khi den doi trang thai.

Cach dung: python light_monitor_bai3.py [host]
Khong dung vong lap GET dinh ky: Server chu dong gui thong bao khi trang thai thay doi.
"""
import asyncio
import json
import sys
from datetime import datetime

import aiocoap
from aiocoap import Code

HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"
URI = f"coap://{HOST}:5683/iot/lab/light01/status"
TIMEOUT = 5  # giay cho phan hoi dau tien


def show(title, response):
    try:
        data = json.loads(response.payload.decode("utf-8"))
        device, status = data["device_id"], data["status"]
    except (ValueError, KeyError, TypeError):
        print(f"[{datetime.now():%H:%M:%S}] Payload khong hop le: {response.payload!r}")
        return
    print(f"\n[{datetime.now():%H:%M:%S}] {title}")
    print(f"Device: {device}")
    print(f"Status: {status}")


async def main():
    context = await aiocoap.Context.create_client_context()
    print("Registering CoAP Observe...")
    request = aiocoap.Message(code=Code.GET, uri=URI, observe=0)  # observe=0: dang ky
    observation = context.request(request)
    try:
        first = await asyncio.wait_for(observation.response, timeout=TIMEOUT)
    except asyncio.TimeoutError:
        print("Loi: Server khong phan hoi (timeout)")
        await context.shutdown()
        return
    except Exception as exc:
        print(f"Loi ket noi: {exc}")
        await context.shutdown()
        return

    if not first.code.is_successful():
        print(f"Dang ky that bai: {first.code}")
        await context.shutdown()
        return
    print("Observe registration successful")
    show("Initial State", first)

    try:
        async for notification in observation.observation:
            show("State Updated", notification)
    except Exception as exc:
        print(f"\nMat ket noi Observe: {exc}")
    finally:
        observation.observation.cancel()
        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
