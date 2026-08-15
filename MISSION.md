# Mission: Blockchain trong LamTo

> Đổi ngày 2026-08-02. Mục tiêu cũ — bảo vệ đồ án trước hội đồng — đã được
> **thay thế**, không phải bổ sung. Xem [LR-0007](learning-records/0007-doi-mission-sang-hackathon.md).
>
> Sửa scope ngày 2026-08-09: **không dựng lại từ đầu**. Repo hiện tại là thứ
> mang đi; 24 giờ ở sự kiện dùng để **build thêm** lên trên, rồi pitch + demo.

## Why

Mang LamTo đi **Hackathon**, còn ~1 tuần (sự kiện khoảng 2026-08-16). Repo hiện
tại đi cùng — **24 giờ ở sự kiện là để build thêm lên nền đã có**, không phải
dựng lại. Sau 24 giờ mới tới pitch + demo. **Đội bốn người, người học là người
duy nhất làm kỹ thuật**; ba người kia lo kinh doanh, pitch, thiết kế.

Chấm theo thang 55–60 điểm kiểu Guy Kawasaki: kỹ thuật chỉ ~10 điểm (slide 4
*Underlying Magic* + slide 11 *Technical Demo*), kinh doanh 20 điểm. Nên vai của
người học **không phải tối đa hoá chiều sâu kỹ thuật** — mà là **khử rủi ro cho
demo** và làm người dịch kỹ thuật cho cả đội.

## Success looks like

- **Nền demo đã chạy được trước khi vào sự kiện**: báo cáo → đề xuất → neo →
  quyết toán → cư dân kiểm chứng. 24 giờ chỉ được **cộng thêm** vào đường này,
  không được làm nó gãy.
- **Màn phá hoại chạy được trên sân khấu**: sửa lén database → kiểm chứng →
  `MISMATCH`, hash cũ và hash mới hiện cạnh nhau.
- **Có video dự phòng** — demo hỏng thì pitch không gãy nhịp.
- Đọc duyệt được slide của đồng đội và **chặn mọi lời hứa không demo được**.
- Dạy được người pitch nói đúng **một câu** Underlying Magic, và không bao giờ
  nói "bất biến" / "không thể sửa" / "tự động phát hiện gian lận".
- Trả lời gọn ~35 giây mỗi câu kỹ thuật trong 3 phút hỏi đáp.
- Chỉ được vào đúng dòng code đứng sau mỗi khẳng định.

## Constraints

- **24 giờ. Đội 4 người nhưng chỉ 1 người code** — phần build vẫn là một mình.
  ~15 giờ code; 3 giờ cuối bắt buộc dành cho tập demo.
- **Repo hiện tại là sàn.** 24 giờ chỉ cộng thêm. Mọi ticket ở sự kiện phải
  **bỏ được**: dừng ở bất kỳ điểm nào, demo vẫn phải chạy nguyên vẹn.
- Trước khi vào sự kiện: **tag trạng thái chạy được**, build trên branch riêng,
  và tập trước đường lui về tag. Video dự phòng quay từ trạng thái trước sự
  kiện, không quay trong lúc build.
- Tiếng Việt, giữ nguyên thuật ngữ tiếng Anh như trong code.
- **Mô hình hai bên** ở tầng ứng dụng (quyết định của người học: BQT và đơn vị
  quản lý đã họp thống nhất ngoài hệ thống), **bốn node làm chứng**.
- Người học là **điểm chết duy nhất** về kỹ thuật — phải tự vá bằng repo chung,
  demo chạy được từ máy thứ hai, và video dự phòng.
- Mỗi khẳng định phải neo được vào code thật, dẫn `file:line`.

## Out of scope

- **Bốn slide kinh doanh** (Target Market · Marketing · Competitive · Financial,
  20 điểm) — việc của ba đồng đội, không phải của người học. Vai của người học
  ở đó chỉ là **đọc duyệt và phủ quyết** những khẳng định không demo được.
- **Bảo vệ đồ án trước hội đồng** — mục tiêu cũ, đã thay thế. Mười bài học vẫn
  dùng được; xem `reference/05-dung-bo-bai-cho-hackathon.html` để biết bài nào
  dùng lúc nào.
- Gate/nhận diện khuôn mặt, notifications, billing — **không build thêm**
  trong 24 giờ. Chúng đã tồn tại trong repo; chỉ là không đụng tới. (MFA của
  Management đã gỡ hẳn theo ADR 0001: đăng nhập workspace chỉ cần mật khẩu.)
- Tokenomics, DeFi, ví cư dân, tối ưu gas.

> **Chưa quyết:** Flutter app trước đây nằm trong danh sách này vì "không dựng
> lại". Giờ app đã có sẵn, mà `README.md` nói cư dân **không có mặt web** — nên
> bước "cư dân kiểm chứng xanh" trong kịch bản demo (thẻ 05, phút 1:00–2:15)
> phải chạy trên app. Phải chốt: demo bước đó bằng Flutter app, hay bằng một
> màn hình staff-side?

## Vấn đề mở đã biết

- `MaintenanceFund` là `OneToOneField` → chưa tách được quỹ bảo trì 2% khỏi phí
  vận hành. Khuyến nghị cũ là làm đúng từ đầu ở bản dựng mới — **không còn bản
  dựng mới**, nên chỉ còn đường retrofit, và **retrofit bị bác** (2026-08-09):
  `fund_balance` dùng `.first()` (`src/lamto/finance/fund.py:224`) nên với hai
  quỹ sẽ trả số sai **mà không báo lỗi**, qua 25 chỗ gọi — hỏng đúng luận điểm
  của bài pitch. Để nguyên một quỹ, trả lời thẳng nếu bị hỏi.
- `fund_code` **đã bị gỡ**: một toà nhà chỉ có một Quỹ bảo trì, nên không có
  nguồn nào để chọn (xem mục *Maintenance Fund* trong `CONTEXT.md`). Trước đó
  nó nằm trong `snapshot` được băm vào `proposal_snapshot_hash` của payload
  được neo — tức là *có* ảnh hưởng tới
  `payloadHash` (`src/lamto/evidence/canonical.py:34`). Vì vậy dữ liệu chain cũ
  không xác minh lại được và **phải seed lại**; xem ADR 0002 cho cùng lý do ở
  phía settlement (`settlement.v2`).
- Mười bài chuẩn bị cho soi xét kỹ thuật, **không** cho soi xét kinh doanh.
