# MyApp Service Contract

เอกสารนี้เป็นสัญญากลางสำหรับ service ทั้งสามตัวที่ทำงานเป็นหลาย process บนเครื่อง Windows เครื่องเดียว: `WebApi`, `DotnetSvc` และ `py-svc`.

## Environment variables

| ตัวแปร | ขอบเขต | ข้อกำหนด |
|---|---|---|
| `PORT` | ทุก service | พอร์ตที่ service ต้อง bind; เป็นค่าบังคับ ถ้าไม่มีหรือใช้ไม่ได้ให้หยุดด้วย exit code `2` |
| `INTERNAL_TOKEN` | ทุก service | token ที่ใช้ตรวจ `X-Internal-Token` สำหรับ endpoint ภายใน |
| `DATA_DIR` | ทุก service | โฟลเดอร์ข้อมูลของ service; service ต้องสร้างโฟลเดอร์นี้เองเมื่อยังไม่มี |
| `DOTNET_SVC_URL` | เฉพาะ WebApi | URL ของ DotnetSvc เช่น `http://127.0.0.1:5101` |
| `PY_SVC_URL` | เฉพาะ WebApi | URL ของ py-svc เช่น `http://127.0.0.1:5102` |

## Network

ทุก service ต้อง bind เฉพาะ `127.0.0.1` เท่านั้น ห้าม bind `0.0.0.0` หรือเปิดรับการเชื่อมต่อจาก network interface อื่น

## Required endpoints

ทุก service ต้องมี endpoint ต่อไปนี้:

| Method | Path | ข้อกำหนด |
|---|---|---|
| `GET` | `/health` | ไม่ต้อง auth; ตอบ `200` พร้อม JSON รูปแบบ `{"status":"ok","service":"<ชื่อ>"}` |
| `POST` | `/shutdown` | ต้องมี `X-Internal-Token` ที่ถูกต้อง; ตอบ `202` แล้วเริ่มปิดโปรเซสอย่างสุภาพ |

ทุก endpoint อื่นต้องตรวจ header `X-Internal-Token` หากไม่มีหรือค่าไม่ตรง ให้ตอบ `401` พร้อม JSON `{"error":"unauthorized"}`

### WebApi browser access

สำหรับ WebApi ให้ยกเว้น static files และ `/api/*` ที่เรียกจาก browser จากการตรวจ `X-Internal-Token` ที่ขอบ WebApi โดยตรวจ `Host` header แทน เช่นอนุญาตเฉพาะ host ใน loopback ที่กำหนดสำหรับการใช้งานบนเครื่องเดียว หาก `Host` ไม่ผ่าน ให้ปฏิเสธคำขอ

เมื่อ WebApi เรียก `DotnetSvc` หรือ `py-svc` ต้องแนบ `X-Internal-Token` เองทุกครั้ง ส่วน endpoint ภายในของ WebApi รวมถึง `/shutdown` ยังคงต้องตรวจ token ตามสัญญานี้

## Logging

เขียน log ไปยัง stdout/stderr เท่านั้น โดยหนึ่งบรรทัดแทนหนึ่ง event และไม่เขียน log ลงไฟล์

## Exit codes

| Code | ความหมาย |
|---:|---|
| `0` | ปิดโปรเซสปกติ |
| `1` | เกิด error อื่น |
| `2` | configuration ผิดหรือค่าบังคับไม่ครบ เช่นไม่มี `PORT` |

## Development defaults

| Service | PORT | INTERNAL_TOKEN |
|---|---:|---|
| WebApi | `5000` | `dev-token` |
| DotnetSvc | `5101` | `dev-token` |
| py-svc | `5102` | `dev-token` |

URL ภายในสำหรับ WebApi ตอน dev: `DOTNET_SVC_URL=http://127.0.0.1:5101` และ `PY_SVC_URL=http://127.0.0.1:5102`.

## Service summary

| ชื่อ | หน้าที่ | พอร์ต dev | คำสั่งรันตอน dev |
|---|---|---:|---|
| WebApi | จุดรับคำขอจาก browser, ให้บริการ static files และ API, เรียก service ภายใน | `5000` | `dotnet run --project src/WebApi` |
| DotnetSvc | service ภายในที่พัฒนาด้วย .NET | `5101` | `dotnet run --project src/DotnetSvc` |
| py-svc | service ภายในที่พัฒนาด้วย Python | `5102` | `python src/py-svc/main.py` |
