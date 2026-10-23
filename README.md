# Thực hành buổi 3 – Lập trình Python với giao thức CoAP

## 1. Thông tin sinh viên

| Mã sinh viên | Họ tên |
|--------------|--------|
| B23DCCN012   | Bùi Tuấn Anh |
| B23DCCN152   | Trịnh Quốc Đạt |

## 2. Môi trường

- Python 3.x (đã chạy thử với Python 3.13)
- Thư viện: `aiocoap` (xem `CoAP_Lab/requirements.txt`)

```bash
pip install aiocoap   # hoặc: pip install -r CoAP_Lab/requirements.txt
```

## 3. Cấu trúc thư mục

```
CoAP_Lab/
|-- bai1/
|   |-- coap_server_bai1.py
|   |-- coap_client_bai1.py
|-- bai2/
|   |-- sensor_server_bai2.py
|   |-- monitor_client_bai2.py
|-- bai3/
|   |-- light_server_bai3.py
|   |-- light_controller_bai3.py
|   |-- light_monitor_bai3.py
|-- requirements.txt
|-- README.md
```

## 4. Địa chỉ, cổng và URI

- Giao thức: CoAP over UDP, cổng mặc định **5683**
- Địa chỉ mặc định: `localhost` / `127.0.0.1` (Server và Client chạy cùng máy)
- Chạy trên hai máy: dùng IP của máy chạy Server làm tham số dòng lệnh cho Client và cho phép UDP cổng 5683 trên tường lửa.

| Bài | URI | Phương thức |
|-----|-----|-------------|
| 1 | `coap://localhost:5683/iot/lab/message` | GET, POST |
| 2 | `coap://localhost:5683/iot/lab/sensor01/data` (thêm `sensor02`, `sensor03`) | GET |
| 3 | `coap://localhost:5683/iot/lab/light01/status` | GET, PUT, Observe |

## 5. Cách chạy

Mỗi chương trình chạy trong một terminal riêng, **chạy Server trước**.

### Bài 1
```bash
cd CoAP_Lab/bai1
python coap_server_bai1.py        # terminal 1
python coap_client_bai1.py        # terminal 2
```
Client thực hiện GET → POST (lần lượt hai sinh viên) → GET lại (nhận thông điệp POST gần nhất).
Có thể truyền URI khác: `python coap_client_bai1.py coap://<ip>:5683/iot/lab/message`.

### Bài 2
```bash
cd CoAP_Lab/bai2
python sensor_server_bai2.py                       # terminal 1
python monitor_client_bai2.py                      # terminal 2 (mặc định sensor01)
python monitor_client_bai2.py sensor02 192.168.1.10   # chọn thiết bị và IP Server
```
Nhấn `Ctrl+C` để dừng. Dữ liệu nhận được được ghi vào `sensor_log.csv`.

### Bài 3
```bash
cd CoAP_Lab/bai3
python light_server_bai3.py        # terminal 1
python light_monitor_bai3.py       # terminal 2 (có thể mở nhiều cửa sổ)
python light_controller_bai3.py    # terminal 3, nhập ON / OFF / STATUS / EXIT
```
Client nhận tham số tuỳ chọn là IP Server: `python light_monitor_bai3.py 192.168.1.10`.

## 6. Kết quả đạt được

### Bài 1 – Gửi/nhận thông điệp CoAP cơ bản
- Server hỗ trợ GET (trả về lời chào, hoặc thông điệp POST gần nhất) và POST (hiển thị nội dung, thời điểm nhận, trả `2.04 Changed`).
- Client gửi GET, nhiều POST liên tiếp và hiển thị mã/payload phản hồi.
- Truy cập URI không tồn tại → `4.04 Not Found`; Server không chạy → báo lỗi timeout/kết nối, không bị treo.

### Bài 2 – Cảm biến nhiệt độ/độ ẩm
- Server mô phỏng `sensor01`, `sensor02`, `sensor03`; mỗi 3 giây sinh lại nhiệt độ (20–40 °C), độ ẩm (30–90 %) ngẫu nhiên.
- Payload JSON (Content-Format `application/json`), có thêm trường `timestamp`.
- Client GET mỗi 3 giây, hiển thị mã thiết bị, nhiệt độ, độ ẩm, thời điểm nhận; cảnh báo khi nhiệt độ > 35 °C hoặc độ ẩm < 40 %.
- Thống kê số lần GET và thời gian phản hồi trung bình; ghi CSV; xử lý timeout/payload lỗi và tiếp tục giám sát.

### Bài 3 – Đèn thông minh với CoAP Observe
- Server `light01` (trạng thái đầu `OFF`) hỗ trợ GET, PUT (`ON`/`OFF`) và Observe (`ObservableResource`).
- Chỉ thông báo cho các observer khi trạng thái **thực sự thay đổi**; ghi nhật ký thay đổi vào `light_log.txt`.
- Lệnh/JSON sai → `4.00 Bad Request`; sai `device_id` → `4.04 Not Found`.
- Monitoring Client dùng Observe (không dùng vòng lặp GET); nhiều Monitoring Client cùng nhận thông báo.

## 7. Log minh chứng

**Bài 1 – Client**
```
CoAP Client
Sending GET request...
URI: coap://localhost:5683/iot/lab/message

Response:
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN012 - Bui Tuan Anh

Response:
Code: 2.04 Changed
Payload: Server da nhan thong diep
```

**Bài 1 – Server**
```
CoAP Server started on port 5683

GET request received: /iot/lab/message

POST request received:
Payload: Xin chao tu CoAP Client - B23DCCN012 - Bui Tuan Anh
Time: 13:04:53
```

**Bài 2 – Monitoring Client**
```
[13:05:19] Received sensor data

Device: sensor02
Temperature: 23.4 C
Humidity: 37.6 %

CANH BAO: Do am thap

------------------------------

[13:05:22] Received sensor data

Device: sensor02
Temperature: 28.9 C
Humidity: 56.4 %

Trang thai: Binh thuong
```

**Bài 3 – Smart Light Server**
```
CoAP Smart Light Server started...
Resource: /iot/lab/light01/status

New Observe registration received

PUT request received:
Device: light01
Command: ON

Light state changed: OFF -> ON
Notify observers: ON
```

**Bài 3 – Monitoring Client**
```
Registering CoAP Observe...
Observe registration successful

[13:06:06] Initial State
Device: light01
Status: OFF

[13:06:09] State Updated
Device: light01
Status: ON
```
