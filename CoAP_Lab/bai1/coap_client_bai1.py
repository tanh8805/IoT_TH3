"""Bai 1 - CoAP Client: gui GET va POST toi /iot/lab/message."""
import asyncio
import sys

import aiocoap
from aiocoap import Code

HOST = "localhost"
URI = f"coap://{HOST}:5683/iot/lab/message"
STUDENTS = [
    ("B23DCCN012", "Bui Tuan Anh"),
    ("B23DCCN152", "Trinh Quoc Dat"),
]


def show_response(response):
    print("Response:")
    print(f"Code: {response.code}")
    print(f"Payload: {response.payload.decode('utf-8', errors='replace')}")


async def send(context, code, uri, payload=b""):
    request = aiocoap.Message(code=code, uri=uri, payload=payload)
    try:
        return await asyncio.wait_for(context.request(request).response, timeout=10)
    except asyncio.TimeoutError:
        print("Loi: het thoi gian cho (timeout) - Server khong phan hoi")
    except Exception as exc:  # loi ket noi, host sai, ...
        print(f"Loi ket noi: {exc}")
    return None


async def main():
    uri = sys.argv[1] if len(sys.argv) > 1 else URI
    context = await aiocoap.Context.create_client_context()
    print("CoAP Client")

    print("Sending GET request...")
    print(f"URI: {uri}\n")
    response = await send(context, Code.GET, uri)
    if response is None:
        await context.shutdown()
        return
    show_response(response)

    # Gui nhieu thong diep POST lien tiep, sau do GET lai de kiem tra
    messages = [f"Xin chao tu CoAP Client - {sid} - {name}" for sid, name in STUDENTS]
    for text in messages:
        print("\nSending POST request...")
        print(f"Payload: {text}\n")
        response = await send(context, Code.POST, uri, text.encode("utf-8"))
        if response is None:
            break
        show_response(response)

    print("\nSending GET request (kiem tra thong diep gan nhat)...")
    response = await send(context, Code.GET, uri)
    if response is not None:
        show_response(response)

    await context.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
