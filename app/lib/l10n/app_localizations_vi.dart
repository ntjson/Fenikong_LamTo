// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Vietnamese (`vi`).
class AppLocalizationsVi extends AppLocalizations {
  AppLocalizationsVi([String locale = 'vi']) : super(locale);

  @override
  String get appTitle => 'Làm Tổ';

  @override
  String get loginTitle => 'Đăng nhập';

  @override
  String get loginIdentifier => 'Số điện thoại hoặc email';

  @override
  String get loginPassword => 'Mật khẩu';

  @override
  String get loginSubmit => 'Đăng nhập';

  @override
  String get loginMissingFields =>
      'Vui lòng nhập số điện thoại/email và mật khẩu. Chưa có gì được gửi đi.';

  @override
  String get loginShowPassword => 'Hiện mật khẩu';

  @override
  String get loginHidePassword => 'Ẩn mật khẩu';

  @override
  String get registrationOpen => 'Đăng ký cư dân';

  @override
  String get registrationTitle => 'Đăng ký cư dân';

  @override
  String get registrationFullName => 'Họ và tên';

  @override
  String get registrationPhone => 'Số điện thoại';

  @override
  String get registrationEmail => 'Email (không bắt buộc)';

  @override
  String get registrationPassword => 'Mật khẩu';

  @override
  String get registrationBuilding => 'Tòa nhà';

  @override
  String get registrationUnit => 'Căn hộ';

  @override
  String get registrationRequired => 'Bắt buộc';

  @override
  String get registrationSubmit => 'Gửi yêu cầu';

  @override
  String get registrationPendingTitle => 'Đang chờ duyệt đăng ký';

  @override
  String get registrationPendingBody =>
      'Ban quản lý đang xem xét yêu cầu của bạn.';

  @override
  String get registrationRejectedTitle => 'Đăng ký bị từ chối';

  @override
  String get registrationApprovedTitle => 'Đăng ký đã được duyệt';

  @override
  String get registrationApprovedBody =>
      'Tài khoản đã sẵn sàng. Tiếp tục để đăng nhập.';

  @override
  String get registrationExpiredTitle => 'Yêu cầu đã hết hạn';

  @override
  String get registrationExpiredBody => 'Yêu cầu đăng ký này đã hết hạn.';

  @override
  String get registrationRefresh => 'Làm mới';

  @override
  String get registrationNewRequest => 'Gửi yêu cầu mới';

  @override
  String get registrationContinueLogin => 'Tiếp tục đăng nhập';

  @override
  String get apiBaseUrlTitle => 'Máy chủ API';

  @override
  String get apiBaseUrlLabel => 'URL API';

  @override
  String get apiBaseUrlHelp =>
      'Dán URL Cloudflare tunnel (https://….trycloudflare.com). Đổi URL không cần cài APK mới. Lưu xong sẽ đăng xuất.';

  @override
  String get apiBaseUrlSave => 'Lưu URL';

  @override
  String get apiBaseUrlReset => 'Mặc định';

  @override
  String get apiBaseUrlInvalid =>
      'URL không hợp lệ. Cần dạng https://… hoặc http://…';

  @override
  String get apiBaseUrlSaved => 'Đã lưu URL máy chủ.';

  @override
  String get occupancyPickerTitle => 'Chọn căn hộ của bạn';

  @override
  String get signOut => 'Đăng xuất';

  @override
  String get noOccupancyTitle => 'Chưa có căn hộ liên kết';

  @override
  String get noOccupancyBody =>
      'Bạn đã đăng nhập nhưng chưa có căn hộ nào được liên kết. Vui lòng liên hệ ban quản lý tòa nhà, hoặc đăng xuất và thử tài khoản khác.';

  @override
  String get errAuthFailed =>
      'Số điện thoại/email hoặc mật khẩu không đúng. Chưa có gì được gửi đi. Vui lòng thử lại.';

  @override
  String get errThrottled =>
      'Bạn đã thử quá nhiều lần. Chưa có gì được gửi đi. Vui lòng đợi vài phút rồi thử lại.';

  @override
  String get errOccupancyRequired => 'Vui lòng chọn căn hộ áp dụng.';

  @override
  String get errNetwork =>
      'Không có kết nối. Thao tác chưa được gửi. Kiểm tra mạng và thử lại.';

  @override
  String get errServer =>
      'Đã có lỗi từ phía hệ thống. Thao tác có thể chưa được lưu. Vui lòng thử lại sau.';

  @override
  String get errGeneric => 'Đã có lỗi xảy ra. Vui lòng thử lại.';

  @override
  String get tabHome => 'Trang chính';

  @override
  String get tabReport => 'Phản ánh';

  @override
  String get tabIssues => 'Việc của tôi';

  @override
  String get tabLedger => 'Sổ quỹ';

  @override
  String get tabAccount => 'Tài khoản';

  @override
  String get locationPickerTitle => 'Sự cố ở đâu?';

  @override
  String get locationChooseHere => 'Chọn khu vực này';

  @override
  String get commonRetry => 'Thử lại';

  @override
  String get reportFormTitle => 'Gửi phản ánh';

  @override
  String get reportTextLabel => 'Đã xảy ra chuyện gì?';

  @override
  String get reportLocationLabel => 'Vị trí';

  @override
  String get reportLocationEmpty => 'Chọn vị trí';

  @override
  String reportPhotosLabel(int max) {
    return 'Ảnh (tối đa $max)';
  }

  @override
  String get reportAddPhoto => 'Thêm ảnh';

  @override
  String get reportPhotoCamera => 'Chụp ảnh';

  @override
  String get reportPhotoGallery => 'Chọn từ thư viện';

  @override
  String get reportSubmit => 'Gửi phản ánh';

  @override
  String get reportDraftSaving => 'Đang lưu bản nháp…';

  @override
  String get reportDraftSaved => 'Đã lưu bản nháp';

  @override
  String get reportDraftSaveFailed =>
      'Chưa lưu được bản nháp. Nội dung vẫn còn trên màn hình; hãy kiểm tra thiết bị rồi thử lại.';

  @override
  String get reportSubmitted => 'Phản ánh của bạn đã được ghi nhận.';

  @override
  String get reportPhotosPending =>
      'Một số ảnh chưa tải lên được. Nội dung phản ánh đã được lưu — thử lại từng ảnh bên dưới.';

  @override
  String get reportPhotoRetry => 'Thử lại';

  @override
  String get reportConflict =>
      'Phản ánh này đã được gửi trước đó. Nội dung bạn vừa sửa sẽ được gửi thành phản ánh mới — bấm Gửi lần nữa.';

  @override
  String get reportMissingFields =>
      'Vui lòng mô tả sự cố và chọn vị trí. Chưa có gì được gửi đi.';

  @override
  String get reportViewIssue => 'Xem phản ánh này';

  @override
  String get reportAnother => 'Gửi phản ánh khác';

  @override
  String get reportEnableNotifications => 'Nhận thông báo cập nhật';

  @override
  String get privateToggleTitle => 'Yêu cầu riêng tư';

  @override
  String get privateToggleSubtitle =>
      'Chỉ bạn và Ban quản lý xem được yêu cầu này. Yêu cầu riêng tư không xuất hiện trong đề xuất hay sổ quỹ công khai.';

  @override
  String get privateBadge => 'Riêng tư';

  @override
  String get issuesTitle => 'Việc của tôi';

  @override
  String get issuesEmpty => 'Bạn chưa gửi phản ánh nào.';

  @override
  String get issuesLoadMore => 'Tải thêm';

  @override
  String get statusSubmitted => 'Đã gửi';

  @override
  String get statusInReview => 'Đang xem xét';

  @override
  String get statusNeedsInfo => 'Cần bạn bổ sung thông tin';

  @override
  String get statusDeclined => 'Không tiếp nhận';

  @override
  String get statusInProgress => 'Đang xử lý';

  @override
  String get statusProposed => 'Đã lập đề xuất';

  @override
  String get statusCompleted => 'Đã hoàn thành';

  @override
  String get statusClosed => 'Đã đóng';

  @override
  String issueDetailTitle(int id) {
    return 'Phản ánh #$id';
  }

  @override
  String get timelineSubmitted => 'Đã gửi phản ánh';

  @override
  String get timelineTriagePending => 'Đang chờ ban quản lý xem xét';

  @override
  String get timelineTriageDone => 'Ban quản lý đã xem xét';

  @override
  String timelineCase(String category) {
    return 'Đã ghép vào yêu cầu xử lý: $category';
  }

  @override
  String get timelineCaseNoCategory => 'Đã ghép vào yêu cầu xử lý';

  @override
  String get categoryElevator => 'Thang máy';

  @override
  String get categoryWaterLeak => 'Rò rỉ nước';

  @override
  String get categoryElectricalFault => 'Sự cố điện';

  @override
  String get categoryHeatingCooling => 'Điều hòa / sưởi ấm';

  @override
  String get categoryLighting => 'Chiếu sáng';

  @override
  String get categoryDoorLock => 'Cửa / khóa';

  @override
  String get categoryAppliance => 'Thiết bị gia dụng';

  @override
  String get categoryStructural => 'Kết cấu';

  @override
  String get categoryCleanliness => 'Vệ sinh';

  @override
  String get categoryNoise => 'Tiếng ồn';

  @override
  String get categoryOther => 'Khác';

  @override
  String timelineWork(String status, String deadline) {
    return 'Công việc $status, hạn $deadline';
  }

  @override
  String get timelineCompleted => 'Công việc đã hoàn thành';

  @override
  String get progressTitle => 'Tiến độ xử lý';

  @override
  String get progressEmpty => 'Chưa có cập nhật tiến độ.';

  @override
  String get progressCompleted => 'Đã hoàn thành công việc';

  @override
  String get declinedTitle => 'Ban quản lý quyết định không tiếp nhận';

  @override
  String get declinedCorrectedReportCta => 'Gửi phản ánh đã chỉnh sửa';

  @override
  String get rateWorkCta => 'Đánh giá công việc';

  @override
  String get rateWorkTitle => 'Công việc thế nào?';

  @override
  String get rateSatisfied => 'Hài lòng';

  @override
  String get rateNotSatisfied => 'Không hài lòng';

  @override
  String get rateCommentLabel => 'Nhận xét (không bắt buộc)';

  @override
  String get rateSubmit => 'Gửi đánh giá';

  @override
  String get rateThanks => 'Cảm ơn bạn đã đánh giá.';

  @override
  String get infoRequestTitle => 'Ban quản lý cần thêm thông tin';

  @override
  String get infoReplyHint => 'Nhập câu trả lời của bạn…';

  @override
  String get infoReplySubmit => 'Gửi trả lời';

  @override
  String get infoReplyPhotosHint =>
      'Bạn cũng có thể thêm ảnh ở phần ảnh bên dưới.';

  @override
  String infoReplySavedPhotos(int uploaded, int total) {
    return 'Trả lời của bạn đã được ghi nhận. Đã đính kèm $uploaded/$total ảnh.';
  }

  @override
  String get infoReplyPhotosPending =>
      'Trả lời của bạn đã được ghi nhận. Một số ảnh chưa tải lên được — thử lại từng ảnh bên dưới.';

  @override
  String get infoReplyNotSent =>
      'Chưa có gì được gửi đi. Nội dung trả lời và ảnh vẫn còn ở đây — hãy thử lại.';

  @override
  String get infoReplyPendingPhotosTitle =>
      'Ảnh trả lời chưa tải lên được — thử lại từng ảnh.';

  @override
  String get infoReplyClose => 'Đóng';

  @override
  String photoNofM(int n, int m) {
    return 'Ảnh $n/$m';
  }

  @override
  String get photoUploadFailed => 'Chưa tải lên được';

  @override
  String get photoLoading => 'Đang tải ảnh…';

  @override
  String get photoLoadFailed => 'Không tải được ảnh.';

  @override
  String get photoBeforeRepair => 'Ảnh trước khi sửa';

  @override
  String get photoAfterRepair => 'Ảnh sau khi sửa';

  @override
  String get workStatusAssigned => 'Đã giao';

  @override
  String get workStatusInProgress => 'Đang thực hiện';

  @override
  String get workStatusAwaiting => 'Chờ nghiệm thu';

  @override
  String get workStatusAccepted => 'Đã nghiệm thu';

  @override
  String get workStatusClosed => 'Đã đóng';

  @override
  String get workStatusCancelled => 'Đã hủy';

  @override
  String get homeFundTitle => 'Quỹ bảo trì';

  @override
  String get homeAnnouncementTitle => 'Thông báo tòa nhà';

  @override
  String get homeFundInflows => 'Thu (30 ngày)';

  @override
  String get homeFundOutflows => 'Chi (30 ngày)';

  @override
  String get homeFundChartCaption => 'Số dư quỹ · 6 tháng gần nhất';

  @override
  String get homeActiveReports => 'Phản ánh đang mở';

  @override
  String get homeRecentSpending => 'Khoản chi mới công bố';

  @override
  String get homeNoActiveReports => 'Không có phản ánh đang mở.';

  @override
  String get homeNoSpending => 'Chưa có khoản chi nào được công bố.';

  @override
  String get homeReportsLoading => 'Đang tải phản ánh…';

  @override
  String get homeSpendingLoading => 'Đang tải khoản chi…';

  @override
  String get notificationsTitle => 'Thông báo';

  @override
  String get notificationsEmpty => 'Chưa có thông báo nào.';

  @override
  String get notificationsLoadMore => 'Tải thêm';

  @override
  String notificationsUnreadCount(int n) {
    return '$n thông báo chưa đọc';
  }

  @override
  String get notificationUnread => 'Chưa đọc';

  @override
  String get notificationRead => 'Đã đọc';

  @override
  String get ledgerTitle => 'Sổ quỹ tòa nhà';

  @override
  String get ledgerDetailTitle => 'Chi tiết khoản chi';

  @override
  String get ledgerEmpty => 'Không có khoản chi nào trong kỳ này.';

  @override
  String get ledgerAllTime => 'Tất cả';

  @override
  String get ledgerYearLabel => 'Năm';

  @override
  String get ledgerMonthLabel => 'Tháng';

  @override
  String get ledgerLoadMore => 'Tải thêm';

  @override
  String ledgerPublishedOn(String date) {
    return 'Công bố ngày $date';
  }

  @override
  String get ledgerAmount => 'Số tiền';

  @override
  String get ledgerContractor => 'Nhà thầu';

  @override
  String get ledgerWhatFixed => 'Đã sửa gì';

  @override
  String get ledgerWhy => 'Lý do';

  @override
  String get ledgerApprovers => 'Người phê duyệt';

  @override
  String ledgerApproverBoard(String name) {
    return 'Ban quản trị: $name';
  }

  @override
  String ledgerApproverRep(String name) {
    return 'Đại diện cư dân: $name';
  }

  @override
  String ledgerApproverEmergency(String name) {
    return 'Ủy quyền khẩn cấp: $name';
  }

  @override
  String ledgerApproverGeneric(String name) {
    return '$name';
  }

  @override
  String ledgerVerifiedBy(String name) {
    return 'Thanh toán đã được $name xác nhận';
  }

  @override
  String get ledgerNotVerified => 'Thanh toán chưa được xác nhận';

  @override
  String get ledgerConclusionVerified => 'Khoản chi này đã được xác minh';

  @override
  String get ledgerConclusionVerifiedBody =>
      'Chứng từ thanh toán và tính toàn vẹn của bản ghi đã được xác nhận độc lập.';

  @override
  String get ledgerConclusionUnverified =>
      'Khoản chi này chưa được xác minh đầy đủ';

  @override
  String get ledgerConclusionUnverifiedBody =>
      'Khoản chi đã được công bố nhưng còn bước xác minh chưa hoàn tất. Xem chuỗi trách nhiệm bên dưới.';

  @override
  String get ledgerConclusionMismatch =>
      'Bản ghi này không khớp với bằng chứng đã neo';

  @override
  String get ledgerConclusionMismatchBody =>
      'Dữ liệu đã công bố khác với bằng chứng đã neo cho khoản chi này. Hãy báo ban quản lý kiểm tra khoản chi.';

  @override
  String get ledgerChainTitle => 'Chuỗi trách nhiệm';

  @override
  String get ledgerChainHint =>
      'Khoản chi đi từ phản ánh đến xác minh độc lập theo các bước dưới đây.';

  @override
  String get ledgerChainReports => 'Phản ánh và lý do';

  @override
  String get ledgerChainWork => 'Công việc đã hoàn thành';

  @override
  String get ledgerChainApprovals => 'Phê duyệt';

  @override
  String get ledgerChainPayment => 'Chứng từ thanh toán';

  @override
  String get ledgerChainVerification => 'Xác minh độc lập';

  @override
  String get ledgerCorrections => 'Điều chỉnh';

  @override
  String get ledgerCorrectionRecorded => 'Đã ghi nhận điều chỉnh';

  @override
  String get ledgerDocuments => 'Tài liệu';

  @override
  String get ledgerDocumentOpen => 'Xem hoặc tải xuống';

  @override
  String get ledgerDocumentOffline =>
      'Bạn đang ngoại tuyến. Tài liệu chưa được tải. Kết nối mạng rồi thử lại.';

  @override
  String get ledgerDocumentUnauthorized =>
      'Bạn không có quyền mở tài liệu này. Tệp chưa được tải xuống.';

  @override
  String get ledgerDocumentFailure =>
      'Không mở được tài liệu. Tệp chưa được tải xuống; vui lòng thử lại.';

  @override
  String get documentShare => 'Chia sẻ hoặc lưu';

  @override
  String get documentShareFailed =>
      'Chưa chia sẻ được tệp. Tài liệu vẫn đang mở — hãy thử lại.';

  @override
  String get documentNoPreview =>
      'Không xem trước được tệp này tại đây. Hãy chia sẻ để mở bằng ứng dụng khác.';

  @override
  String get ledgerProofTitle => 'Chi tiết xác thực';

  @override
  String get ledgerProofHash => 'Mã băm bản ghi';

  @override
  String get ledgerProofEvents => 'Sự kiện đã ký';

  @override
  String get evidenceExplorer => 'Trình khám phá bằng chứng';

  @override
  String get evidenceChain => 'Đã neo trên blockchain';

  @override
  String get evidenceLocal => 'Đã ký — chưa bật neo blockchain';

  @override
  String get evidencePending => 'Đang chờ neo blockchain';

  @override
  String get evidenceMismatch => 'Phát hiện sai lệch dữ liệu';

  @override
  String get integrityVerified => 'Bản ghi đã xác minh';

  @override
  String get integrityMismatch => 'Phát hiện sai lệch toàn vẹn';

  @override
  String get integrityUnavailable => 'Chưa kiểm tra được tính toàn vẹn';

  @override
  String get integrityUnchecked => 'Đã công bố — chưa kiểm tra toàn vẹn';

  @override
  String get accountOccupancies => 'Căn hộ của tôi';

  @override
  String get accountPreferences => 'Thông báo';

  @override
  String get accountPrefAll => 'Nhận tất cả thông báo';

  @override
  String get accountSignOutAll => 'Đăng xuất mọi thiết bị';

  @override
  String get signOutUnsentWorkWarning =>
      'Phản ánh đang soạn và ảnh chưa gửi trên thiết bị này sẽ bị xóa.';

  @override
  String get commonCancel => 'Hủy';

  @override
  String get gateAccountAction => 'Đăng ký biển số và khuôn mặt';

  @override
  String get gateRegistrationTitle => 'Đăng ký cổng';

  @override
  String get gatePlateLabel => 'Biển số xe';

  @override
  String get gateSubmitPlate => 'Gửi biển số để duyệt';

  @override
  String get gateRevokePlate => 'Thu hồi biển số';

  @override
  String get gateFaceTitle => 'Khuôn mặt';

  @override
  String get gateNotRegistered => 'Chưa đăng ký';

  @override
  String get gateCaptureFace => 'Chụp ảnh đăng ký';

  @override
  String get gateRevokeFace => 'Thu hồi khuôn mặt';

  @override
  String get gateRetentionNotice =>
      'Ảnh chỉ được giữ để ban quản lý xem xét và sẽ bị xóa sau khi có quyết định.';

  @override
  String get gateRevokeConfirmBody =>
      'Thông tin này sẽ không còn dùng để nhận diện tại cổng.';

  @override
  String get gateRevokeConfirm => 'Thu hồi';

  @override
  String get gateStatusPending => 'Đang chờ duyệt';

  @override
  String get gateStatusApproved => 'Đã duyệt';

  @override
  String gateStatusRejected(String note) {
    return 'Bị từ chối: $note';
  }

  @override
  String get gateStatusExpired => 'Ảnh đã hết hạn, vui lòng gửi lại';

  @override
  String get gateStatusUnknown => 'Không rõ trạng thái';

  @override
  String get gateErrorNoFace => 'Không tìm thấy khuôn mặt. Hãy chụp lại.';

  @override
  String get gateErrorMultipleFaces => 'Ảnh chỉ được có một khuôn mặt.';

  @override
  String get gateErrorFaceTooSmall => 'Khuôn mặt quá nhỏ. Hãy lại gần hơn.';

  @override
  String get gateErrorFaceTooBlurry => 'Ảnh quá mờ. Hãy chụp lại.';

  @override
  String get gateErrorFaceUnusable =>
      'Ảnh không thể dùng để đăng ký khuôn mặt.';

  @override
  String get gateErrorPhotoRejected => 'Ảnh bị từ chối trước khi xử lý.';

  @override
  String get gateErrorPhotoTooLarge => 'Ảnh vượt quá dung lượng cho phép.';

  @override
  String get gateErrorPlateRegistered =>
      'Biển số đã được đăng ký. Vui lòng liên hệ ban quản lý.';

  @override
  String get gateErrorUnavailable =>
      'Dịch vụ nhận diện đang tạm ngừng. Hãy thử lại sau.';

  @override
  String get gateReaderTitle => 'Đầu đọc cổng';

  @override
  String get gateReaderServer => 'Địa chỉ máy chủ';

  @override
  String get gateReaderCredential => 'Mã thiết bị';

  @override
  String get gateReaderActivate => 'Kích hoạt đầu đọc';

  @override
  String get gateReaderInvalidUrl =>
      'URL máy chủ không hợp lệ. Cần bắt đầu bằng https:// hoặc http://.';

  @override
  String get gateReaderPlateUnreadable =>
      'Không đọc được biển số. Hãy thử lại.';

  @override
  String gateReaderUnit(String unit) {
    return 'Căn $unit';
  }

  @override
  String get gateReaderNoMatch => 'Không nhận diện được';

  @override
  String get gateReaderScanPlate => 'Quét biển số';

  @override
  String get gateReaderScanFace => 'Quét khuôn mặt';

  @override
  String get gateReaderClearDevice => 'Xóa mã thiết bị';

  @override
  String get gateReaderDeviceRevoked => 'Mã thiết bị đã bị thu hồi.';

  @override
  String get gateReaderDeviceExpired => 'Mã thiết bị đã hết hạn.';

  @override
  String get gateReaderDeviceInvalid => 'Mã thiết bị không đúng.';

  @override
  String get gateReaderThrottled => 'Thao tác quá nhanh. Vui lòng chờ.';

  @override
  String get fundChartTitle => 'Số dư quỹ';

  @override
  String get fundChartFlowsTitle => 'Thu và chi';

  @override
  String get fundChartSemantics => 'Biểu đồ số dư quỹ';

  @override
  String fundChartBalanceValue(String amount) {
    return 'số dư $amount';
  }

  @override
  String fundChartInflowValue(String amount) {
    return 'thu $amount';
  }

  @override
  String fundChartOutflowValue(String amount) {
    return 'chi $amount';
  }

  @override
  String get fundChartInflowLabel => 'Thu';

  @override
  String get fundChartOutflowLabel => 'Chi';

  @override
  String get fundChartRange30d => '30 ngày';

  @override
  String get fundChartRange6m => '6 tháng';

  @override
  String get fundChartRange12m => '12 tháng';

  @override
  String get proposalsSegment => 'Đề xuất';

  @override
  String get ledgerSegment => 'Sổ quỹ';

  @override
  String get proposalStatusPublished => 'Đã công bố';

  @override
  String get proposalStatusInProgress => 'Đang thực hiện';

  @override
  String get proposalStatusNotProceeding => 'Không thực hiện';

  @override
  String get proposalStatusCompleted => 'Đã hoàn thành';

  @override
  String get proposalStatusClosed => 'Đã đóng';

  @override
  String get proposalStatusDraft => 'Bản nháp';

  @override
  String get proposalProblem => 'Vấn đề hoặc nhu cầu';

  @override
  String get proposalAction => 'Phương án đề xuất';

  @override
  String get proposalCost => 'Chi phí dự kiến';

  @override
  String get proposalContractor => 'Nhà thầu';

  @override
  String get proposalSchedule => 'Tiến độ dự kiến';

  @override
  String get proposalVersions => 'Các phiên bản đã công bố';

  @override
  String proposalVersion(String number) {
    return 'Phiên bản $number';
  }

  @override
  String get proposalSettlement => 'Quyết toán thanh toán';

  @override
  String get proposalSettled => 'Đã thanh toán';

  @override
  String get proposalViewFromLedger => 'Xem đề xuất';

  @override
  String get proposalRateCta => 'Đánh giá kết quả';

  @override
  String get homeBillTitle => 'Hóa đơn tòa nhà';

  @override
  String get homeBillLoading => 'Đang tải hóa đơn tòa nhà…';

  @override
  String get billsTitle => 'Hóa đơn';

  @override
  String get billAmountLabel => 'Số tiền';

  @override
  String get billDueLabel => 'Hạn';

  @override
  String get billOverdue => 'Quá hạn';

  @override
  String get billViewFile => 'Xem hóa đơn';

  @override
  String get billPayAction => 'Tôi đã thanh toán';

  @override
  String get billPayExplainer =>
      'Quét QR chỉ ghi nhận khoản tiền bạn đã chuyển — không thực hiện thanh toán.';

  @override
  String get billPayStep1 => '1. Chuyển khoản bằng app ngân hàng.';

  @override
  String get billPayStep2 =>
      '2. Quay lại đây, quét mã QR trên hóa đơn để ghi nhận.';

  @override
  String get billStatusIssued => 'Chưa thanh toán';

  @override
  String get billStatusPaid => 'Đã ghi nhận thanh toán';

  @override
  String get billStatusVoid => 'Đã hủy';

  @override
  String get billScanTitle => 'Quét mã QR thanh toán';

  @override
  String get billScanInstruction =>
      'Hướng máy ảnh vào mã QR trên hóa đơn để ghi nhận thanh toán.';

  @override
  String get billInvalidQr => 'Mã QR không hợp lệ.';

  @override
  String get billPaymentRecorded => 'Đã ghi nhận thanh toán';

  @override
  String get billPaymentVoided =>
      'Hóa đơn này đã bị hủy. Thanh toán chưa được ghi nhận.';

  @override
  String get billPaymentUnknown =>
      'Chưa thể xác nhận thanh toán đã được ghi nhận hay chưa. Hãy kiểm tra trạng thái hóa đơn trước khi thử lại.';

  @override
  String get billCameraUnavailable =>
      'Không thể sử dụng máy ảnh. Hãy cho phép truy cập máy ảnh trong cài đặt thiết bị rồi thử lại.';

  @override
  String get billNone => 'Chưa có hóa đơn.';
}
