"""Bai 1 - CoAP Server: GET/POST tren tai nguyen /iot/lab/message."""
import asyncio
import os
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code

PORT = 5683
BIND_HOST = os.environ.get("COAP_BIND_HOST", "::")  # "::" = moi dia chi (IPv4 + IPv6)
WELCOME = "Xin chao tu CoAP Server"


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.last_message = None  # thong diep POST gan nhat

    async def render_get(self, request):
        print("\nGET request received: /iot/lab/message")
        # Neu da co thong diep POST thi tra ve thong diep do, nguoc lai tra loi chao
        payload = self.last_message or WELCOME
        return aiocoap.Message(code=Code.CONTENT, payload=payload.encode("utf-8"))

    async def render_post(self, request):
        message = request.payload.decode("utf-8", errors="replace").strip()
        if not message:
            return aiocoap.Message(code=Code.BAD_REQUEST,
                                   payload="Payload rong".encode("utf-8"))
        self.last_message = message
        print("\nPOST request received:")
        print(f"Payload: {message}")
        print(f"Time: {datetime.now():%H:%M:%S}")
        return aiocoap.Message(code=Code.CHANGED,
                               payload="Server da nhan thong diep".encode("utf-8"))


async def main():
    root = resource.Site()
    root.add_resource(["iot", "lab", "message"], MessageResource())
    # Tai nguyen khong ton tai se tu dong nhan ma 4.04 Not Found
    await aiocoap.Context.create_server_context(root, bind=(BIND_HOST, PORT))
    print(f"CoAP Server started on port {PORT}")
    await asyncio.get_running_loop().create_future()  # chay den khi Ctrl+C


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
