"""Bai 3 - Smart Light CoAP Server: GET / PUT / Observe tren /iot/lab/light01/status."""
import asyncio
import json
import os
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code

PORT = 5683
BIND_HOST = os.environ.get("COAP_BIND_HOST", "::")  # "::" = moi dia chi (IPv4 + IPv6)
DEVICE_ID = "light01"
JSON_FORMAT = 50  # application/json
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "light_log.txt")


class LightResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.status = "OFF"  # trang thai ban dau

    def state_payload(self):
        return json.dumps({"device_id": DEVICE_ID, "status": self.status}).encode("utf-8")

    def log_change(self, old, new):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {DEVICE_ID} {old} -> {new}\n")

    async def add_observation(self, request, serverobservation):
        print("\nNew Observe registration received")
        await super().add_observation(request, serverobservation)

    async def render_get(self, request):
        # Khi request co Observe=0, aiocoap tu dong dang ky va gan Observe vao phan hoi
        return aiocoap.Message(code=Code.CONTENT, payload=self.state_payload(),
                               content_format=JSON_FORMAT)

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode("utf-8"))
            device = data["device_id"]
            command = str(data["command"]).strip().upper()
        except (ValueError, KeyError, TypeError, AttributeError):
            return aiocoap.Message(code=Code.BAD_REQUEST,
                                   payload="Payload JSON khong hop le".encode("utf-8"))
        if device != DEVICE_ID:
            return aiocoap.Message(code=Code.NOT_FOUND,
                                   payload=f"Khong co thiet bi {device}".encode("utf-8"))
        if command not in ("ON", "OFF"):
            return aiocoap.Message(code=Code.BAD_REQUEST,
                                   payload=f"Lenh khong hop le: {command}".encode("utf-8"))

        print("\nPUT request received:")
        print(f"Device: {device}")
        print(f"Command: {command}")

        if command != self.status:
            old, self.status = self.status, command
            print(f"\nLight state changed: {old} -> {self.status}")
            self.log_change(old, self.status)
            self.updated_state()  # thong bao cho tat ca observer
            print(f"Notify observers: {self.status}")
        else:
            print(f"\nLight state unchanged: {self.status}")

        text = "Da bat den" if command == "ON" else "Da tat den"
        return aiocoap.Message(code=Code.CHANGED, payload=f"{text} {DEVICE_ID}".encode("utf-8"))


async def main():
    root = resource.Site()
    root.add_resource(["iot", "lab", DEVICE_ID, "status"], LightResource())
    await aiocoap.Context.create_server_context(root, bind=(BIND_HOST, PORT))
    print("CoAP Smart Light Server started...")
    print(f"Resource: /iot/lab/{DEVICE_ID}/status")
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
