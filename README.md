# MyApp

MyApp เป็นระบบหลาย process สำหรับ Windows โดยมี WebApi เป็นจุดเข้าใช้งานจาก browser และมี service ภายในสองตัวคือ DotnetSvc กับ py-svc แต่ละ process ใช้พอร์ต loopback ของตัวเอง และทำตามสัญญากลางใน [CONTRACT.md](CONTRACT.md)

## โครงสร้าง

- `src/Launcher/` — พื้นที่สำหรับ launcher ที่จะพัฒนาภายหลัง
- `src/WebApi/` — WebApi และ `client/` สำหรับ React ในอนาคต
- `src/DotnetSvc/` — .NET service ภายใน
- `src/py-svc/` — Python service ภายใน
- `scripts/run-dev.ps1` — เปิด service ที่พร้อมพัฒนาใน terminal แยก
- `license/` — พื้นที่เก็บไฟล์ license

## ลำดับการพัฒนา

1. สร้าง DotnetSvc และ py-svc ให้ทำตาม environment, endpoint, auth, logging และ exit code ใน `CONTRACT.md`.
2. สร้าง WebApi ให้บริการ browser, ตรวจ Host และแนบ internal token เมื่อเรียก service ภายใน.
3. เพิ่ม React client ใน `src/WebApi/client/` และเชื่อมผ่าน WebApi.
4. พัฒนา Launcher เพื่อเริ่มและหยุด process ตามลำดับที่เหมาะสม

## รัน dev

เปิด PowerShell ที่โฟลเดอร์ repo แล้วรัน:

```powershell
.\scripts\run-dev.ps1
```

สคริปต์กำหนด `INTERNAL_TOKEN=dev-token`, `DATA_DIR=.\\.devdata`, พอร์ต dev และ URL ของ service ภายใน แล้วเปิดแต่ละ service ในหน้าต่าง terminal แยก หาก project หรือไฟล์ entry point ของ service ยังไม่มี สคริปต์จะแจ้งเตือนและข้าม service นั้น

ค่าเริ่มต้นของพอร์ตคือ WebApi `5000`, DotnetSvc `5101` และ py-svc `5102`. ดูรายละเอียด endpoint และข้อกำหนดทั้งหมดใน [CONTRACT.md](CONTRACT.md).
