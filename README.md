# Làm Tổ

**Từ tấm ảnh của cư dân đến một khoản chi Quỹ bảo trì kiểm chứng được.**

![Django 5.2](https://img.shields.io/badge/Django-5.2-2f3a8f?style=flat-square)
![Flutter](https://img.shields.io/badge/Flutter-iOS%20%2B%20Android-2f3a8f?style=flat-square)
![Solidity 0.8.27](https://img.shields.io/badge/Solidity-0.8.27-2f3a8f?style=flat-square)
![Besu QBFT](https://img.shields.io/badge/Besu-QBFT%204%20validator-2f3a8f?style=flat-square)

## Vấn đề

Cư dân gửi phản ánh, rồi vài tuần sau thấy một khoản chi trong quỹ tòa nhà.
Không ai biết hai thứ đó có liên quan gì với nhau không.

## Cách Làm Tổ giải quyết

Nối chúng thành một chuỗi truy vết được, không ai sửa được về sau:

```text
phản ánh → phân loại → thi công → đề xuất → thanh toán → sổ quỹ công khai
```

Ba nguyên tắc:

- **Người quyết định, AI chỉ gợi ý.** AI đề xuất hạng mục, mức khẩn, hạn xử lý,
  khoảng giá. Người ký tên vào quyết định luôn là cán bộ quản lý.
- **Không sửa, chỉ ghi thêm.** Dữ liệu đã công bố không sửa được; đính chính
  được ghi nối tiếp.
- **Giải thích trước, chứng minh sau.** Cư dân thấy trạng thái bằng tiếng Việt
  dễ hiểu trước, mã băm và chữ ký nằm bên dưới cho ai muốn kiểm chứng.

Làm Tổ không giữ và không chuyển tiền.

## Sản phẩm gồm gì

**Ứng dụng cư dân (Flutter, iOS + Android)**
Gửi phản ánh kèm ảnh và vị trí · theo dõi tiến độ · đánh giá kết quả · đọc sổ quỹ
và bằng chứng từng khoản chi · xem hóa đơn, quét QR xác nhận thanh toán · đăng ký
khuôn mặt và biển số để qua cổng.

**Trang quản lý (web, `/s/`)**
Hộp việc cần làm · phân loại phản ánh · yêu cầu xử lý · đề xuất chi · thanh toán
· công bố sổ quỹ · xác minh toàn vẹn · hóa đơn · thông báo · duyệt đăng ký cư dân
· duyệt cổng · xuất dữ liệu.

**Hai chỗ dùng AI**
- *Phân loại phản ánh:* mô hình đọc nội dung, vị trí và các phản ánh đang mở gần
  đó, rồi gợi ý hạng mục, mức khẩn, bộ phận tiếp nhận, hạn xử lý và phản ánh
  trùng. Cán bộ quản lý duyệt hoặc sửa — phần sửa được lưu lại.
- *Khoảng giá dự đoán:* khi nhập báo giá, mô hình đưa ra mức giá hợp lý kèm một
  câu lý giải. Số tiền báo giá được giấu khỏi mô hình, nên nó không thể "nói theo"
  con số sắp bị đem ra so sánh. Kết quả so sánh được đóng băng lúc công bố và cho
  cư dân xem.

**Chuỗi bằng chứng (blockchain)**
Mỗi lần công bố và mỗi lần thanh toán đều được băm SHA-256, ký EIP-712 và neo vào
hợp đồng `EvidenceRegistry` trên mạng Besu QBFT bốn validator. Mạng có trục trặc
thì việc neo chỉ chậm lại, không mất và không nhân đôi bản ghi. Một trang công
khai cho bất kỳ ai mở xem trọn chuỗi bằng chứng của một khoản chi.

**Nhận diện tại cổng**
Khuôn mặt (InsightFace, mã hóa khi lưu) và biển số xe Việt Nam, đối chiếu với cư
dân đã đăng ký.

## Kiến trúc

```text
Ứng dụng Flutter ──► API ──┐
                           ├──► Django + PostgreSQL ──► MinIO + ClamAV
Web quản lý ───────────────┘             │
                                         ▼
                outbox đã ký ──► EvidenceRegistry (Besu QBFT)
```

Một worker nền (`manage.py run_worker`) lo phân loại, neo bằng chứng, hoàn tất
công bố, kiểm tra toàn vẹn và đẩy thông báo.

## Chạy thử

Cần Docker, Python 3.12+ và [`uv`](https://docs.astral.sh/uv/).

```bash
docker compose up -d          # Postgres, MinIO, ClamAV
uv sync

set -a; source .env.example; set +a
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
export DEBUG=1 EVIDENCE_ANCHORING_BACKEND=disabled

POSTGRES_USER=Làm Tổ_owner POSTGRES_PASSWORD=Làm Tổ-owner \
  .venv/bin/python manage.py migrate
PILOT_ALLOW_FIXTURES=1 .venv/bin/python manage.py seed_pilot --fixture

.venv/bin/python manage.py run_worker &
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Mở <http://127.0.0.1:8000/s/> — đăng nhập `pilot-management-1@pilot.Làm Tổ.test`
/ `pilot-test-secret`.

Ứng dụng cư dân (cần Flutter stable):

```bash
cd app && flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000   # iOS/desktop: 127.0.0.1
```

Tài khoản cư dân `pilot-resident@pilot.Làm Tổ.test`, cùng mật khẩu.

Hai tùy chọn khi demo:
- Bật AI: đặt `AI_TRIAGE_URL`, `AI_TRIAGE_TOKEN`, `AI_TRIAGE_MODEL`.

## Kịch bản demo

1. Cư dân gửi phản ánh kèm ảnh.
2. AI gợi ý phân loại, cán bộ quản lý duyệt hoặc sửa.
3. Cán bộ nhập báo giá, xem đối chiếu khoảng giá AI, nộp chứng từ thanh toán,
   công bố khoản chi.
4. Cư dân đối chiếu từ khoản chi về đúng phản ánh ban đầu.
5. Thử sửa trộm dữ liệu → hệ thống báo sai lệch, còn bằng chứng đã neo trên các
   validator độc lập vẫn nguyên vẹn.


## Trạng thái

Mọi tòa nhà, cư dân, tài liệu và số tiền đi kèm đều là dữ
liệu mẫu — không dùng cho môi trường thật.