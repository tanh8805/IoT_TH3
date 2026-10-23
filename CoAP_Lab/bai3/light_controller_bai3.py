"""Bai 3 - Light Controller Client: dieu khien den bang PUT, doc trang thai bang GET.

Cach dung: python light_controller_bai3.py [host]
"""
import asyncio
import json
import sys

import aiocoap
from aiocoap import Code

HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"
URI = f"coap://{HOST}:5683/iot/lab/light01/status"
DEVICE_ID = "light01"
TIMEOUT = 5


async def request(context, code, payload=b""):
    msg = aiocoap.Message(code=code, uri=URI, payload=payload)
    if payload:
        msg.opt.content_format = 50
    try:
        return await asyncio.wait_for(context.request(msg).response, timeout=TIMEOUT)
    except asyncio.TimeoutError:
        print("Loi: Server khong phan hoi (timeout)")
    except Exception as exc:
        print(f"Loi ket noi: {exc}")
    return None


async def main():
    context = await aiocoap.Context.create_client_context()
    try:
        while True:
            line = await asyncio.get_running_loop().run_in_executor(
                None, input, "\nNhap lenh (ON/OFF/STATUS/EXIT): ")
            cmd = line.strip().upper()
            if cmd == "EXIT":
                break
            if cmd in ("ON", "OFF"):
                print("\nSending PUT request...")
                payload = json.dumps({"device_id": DEVICE_ID, "command": cmd}).encode("utf-8")
                response = await request(context, Code.PUT, payload)
                if response is not None:
                    print(f"Response Code: {response.code}")
                    print(response.payload.decode("utf-8", errors="replace"))
            elif cmd == "STATUS":
                print("\nSending GET request...")
                response = await request(context, Code.GET)
                if response is not None:
                    print("Response:")
                    print(response.payload.decode("utf-8", errors="replace"))
            elif cmd:
                print("Lenh khong hop le. Chi chap nhan: ON, OFF, STATUS, EXIT")
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        await context.shutdown()
        print("\nController stopped")


if __name__ == "__main__":
    asyncio.run(main())
