"""Bai 2 - Monitoring CoAP Client: GET dinh ky du lieu cam bien moi 3 giay.

Cach dung: python monitor_client_bai2.py [device_id] [host]
Vi du:     python monitor_client_bai2.py sensor02 192.168.1.10
"""
import asyncio
import csv
import json
import os
import sys
import time
from datetime import datetime

import aiocoap
from aiocoap import Code

DEVICE_ID = sys.argv[1] if len(sys.argv) > 1 else "sensor01"
HOST = sys.argv[2] if len(sys.argv) > 2 else "localhost"
URI = f"coap://{HOST}:5683/iot/lab/{DEVICE_ID}/data"
INTERVAL = 3          # giay
TIMEOUT = 5           # giay cho phan hoi
TEMP_LIMIT = 35.0     # canh bao nhiet do cao
HUMIDITY_LIMIT = 40.0  # canh bao do am thap
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_log.csv")


def log_csv(row):
    new_file = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["time", "device_id", "temperature", "humidity"])
        writer.writerow(row)


async def main():
    context = await aiocoap.Context.create_client_context()
    print(f"Monitoring {URI} (Ctrl+C de dung)\n")
    requests = 0
    total_rtt = 0.0
    try:
        while True:
            now = f"{datetime.now():%H:%M:%S}"
            try:
                start = time.monotonic()
                request = aiocoap.Message(code=Code.GET, uri=URI)
                response = await asyncio.wait_for(context.request(request).response,
                                                  timeout=TIMEOUT)
                rtt = time.monotonic() - start
            except asyncio.TimeoutError:
                print(f"[{now}] Loi: Server khong phan hoi (timeout)\n")
                await asyncio.sleep(INTERVAL)
                continue
            except Exception as exc:
                print(f"[{now}] Loi ket noi: {exc}\n")
                await asyncio.sleep(INTERVAL)
                continue

            if not response.code.is_successful():
                print(f"[{now}] Server tra ve loi: {response.code}\n")
                await asyncio.sleep(INTERVAL)
                continue

            try:
                data = json.loads(response.payload.decode("utf-8"))
                device = data["device_id"]
                temperature = float(data["temperature"])
                humidity = float(data["humidity"])
            except (ValueError, KeyError, TypeError) as exc:
                print(f"[{now}] Payload khong hop le: {exc}\n")
                await asyncio.sleep(INTERVAL)
                continue

            requests += 1
            total_rtt += rtt
            print(f"[{now}] Received sensor data\n")
            print(f"Device: {device}")
            print(f"Temperature: {temperature} C")
            print(f"Humidity: {humidity} %\n")
            warned = False
            if temperature > TEMP_LIMIT:
                print("CANH BAO: Nhiet do cao")
                warned = True
            if humidity < HUMIDITY_LIMIT:
                print("CANH BAO: Do am thap")
                warned = True
            if not warned:
                print("Trang thai: Binh thuong")
            print(f"(So lan GET: {requests}, thoi gian phan hoi TB: "
                  f"{total_rtt / requests * 1000:.1f} ms)")
            print("\n" + "-" * 30 + "\n")
            log_csv([now, device, temperature, humidity])
            await asyncio.sleep(INTERVAL)
    finally:
        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
