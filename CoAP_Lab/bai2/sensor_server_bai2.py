"""Bai 2 - Sensor CoAP Server: mo phong cam bien nhiet do / do am."""
import asyncio
import json
import os
import random
from datetime import datetime

import aiocoap
import aiocoap.resource as resource
from aiocoap import Code

PORT = 5683
BIND_HOST = os.environ.get("COAP_BIND_HOST", "::")  # "::" = moi dia chi (IPv4 + IPv6)
UPDATE_INTERVAL = 3  # giay
SENSORS = ["sensor01", "sensor02", "sensor03"]
JSON_FORMAT = 50  # Content-Format application/json


class SensorResource(resource.Resource):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.data = {}
        self.update()

    def update(self):
        """Sinh gia tri ngau nhien trong khoang hop ly."""
        self.data = {
            "device_id": self.device_id,
            "temperature": round(random.uniform(20.0, 40.0), 1),
            "humidity": round(random.uniform(30.0, 90.0), 1),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    async def update_loop(self):
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            self.update()
            print(f"[{datetime.now():%H:%M:%S}] {self.device_id} updated: "
                  f"{self.data['temperature']} C, {self.data['humidity']} %")

    async def render_get(self, request):
        print(f"[{datetime.now():%H:%M:%S}] GET /iot/lab/{self.device_id}/data")
        payload = json.dumps(self.data).encode("utf-8")
        return aiocoap.Message(code=Code.CONTENT, payload=payload,
                               content_format=JSON_FORMAT)


async def main():
    root = resource.Site()
    tasks = []
    for device_id in SENSORS:
        sensor = SensorResource(device_id)
        root.add_resource(["iot", "lab", device_id, "data"], sensor)
        tasks.append(asyncio.create_task(sensor.update_loop()))
    await aiocoap.Context.create_server_context(root, bind=(BIND_HOST, PORT))
    print(f"Sensor CoAP Server started on port {PORT}")
    for device_id in SENSORS:
        print(f"Resource: /iot/lab/{device_id}/data")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
