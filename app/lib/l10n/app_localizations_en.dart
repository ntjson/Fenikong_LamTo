// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Làm Tổ';

  @override
  String get loginTitle => 'Sign in';

  @override
  String get loginIdentifier => 'Phone or email';

  @override
  String get loginPassword => 'Password';

  @override
  String get loginSubmit => 'Sign in';

  @override
  String get loginMissingFields =>
      'Enter your phone/email and password. Nothing was submitted.';

  @override
  String get loginShowPassword => 'Show password';

  @override
  String get loginHidePassword => 'Hide password';

  @override
  String get registrationOpen => 'Register as a resident';

  @override
  String get registrationTitle => 'Resident registration';

  @override
  String get registrationFullName => 'Full name';

  @override
  String get registrationPhone => 'Phone';

  @override
  String get registrationEmail => 'Email (optional)';

  @override
  String get registrationPassword => 'Password';

  @override
  String get registrationBuilding => 'Building';

  @override
  String get registrationUnit => 'Unit';

  @override
  String get registrationRequired => 'Required';

  @override
  String get registrationSubmit => 'Submit request';

  @override
  String get registrationPendingTitle => 'Registration pending';

  @override
  String get registrationPendingBody => 'Management is reviewing your request.';

  @override
  String get registrationRejectedTitle => 'Registration rejected';

  @override
  String get registrationApprovedTitle => 'Registration approved';

  @override
  String get registrationApprovedBody =>
      'Your account is ready. Continue to sign in.';

  @override
  String get registrationExpiredTitle => 'Request expired';

  @override
  String get registrationExpiredBody =>
      'This registration request has expired.';

  @override
  String get registrationRefresh => 'Refresh';

  @override
  String get registrationNewRequest => 'Submit a new request';

  @override
  String get registrationContinueLogin => 'Continue to sign in';

  @override
  String get apiBaseUrlTitle => 'API server';

  @override
  String get apiBaseUrlLabel => 'API URL';

  @override
  String get apiBaseUrlHelp =>
      'Paste your Cloudflare tunnel URL (https://….trycloudflare.com). No APK rebuild needed when the tunnel changes. Saving signs you out.';

  @override
  String get apiBaseUrlSave => 'Save URL';

  @override
  String get apiBaseUrlReset => 'Default';

  @override
  String get apiBaseUrlInvalid => 'Invalid URL. Use https://… or http://…';

  @override
  String get apiBaseUrlSaved => 'Server URL saved.';

  @override
  String get occupancyPickerTitle => 'Choose your home';

  @override
  String get signOut => 'Sign out';

  @override
  String get noOccupancyTitle => 'No home linked';

  @override
  String get noOccupancyBody =>
      'Your account is signed in, but no apartment is linked yet. Contact your building management, or sign out and try another account.';

  @override
  String get errAuthFailed =>
      'The phone/email or password is incorrect. Nothing was submitted. Please try again.';

  @override
  String get errThrottled =>
      'Too many attempts. Nothing was submitted. Please wait a few minutes and try again.';

  @override
  String get errOccupancyRequired =>
      'Please choose which home this applies to.';

  @override
  String get errNetwork =>
      'No connection. Your action was not sent. Check your network and retry.';

  @override
  String get errServer =>
      'Something went wrong on our side. Your action may not have been saved. Please try again shortly.';

  @override
  String get errGeneric => 'Something went wrong. Please try again.';

  @override
  String get tabHome => 'Home';

  @override
  String get tabReport => 'Report';

  @override
  String get tabIssues => 'Issues';

  @override
  String get tabLedger => 'Ledger';

  @override
  String get tabAccount => 'Account';

  @override
  String get locationPickerTitle => 'Where is the issue?';

  @override
  String get locationChooseHere => 'Choose this area';

  @override
  String get commonRetry => 'Try again';

  @override
  String get reportFormTitle => 'Report an issue';

  @override
  String get reportTextLabel => 'What happened?';

  @override
  String get reportLocationLabel => 'Location';

  @override
  String get reportLocationEmpty => 'Choose a location';

  @override
  String reportPhotosLabel(int max) {
    return 'Photos (up to $max)';
  }

  @override
  String get reportAddPhoto => 'Add photo';

  @override
  String get reportPhotoCamera => 'Take a photo';

  @override
  String get reportPhotoGallery => 'Choose from gallery';

  @override
  String get reportSubmit => 'Send report';

  @override
  String get reportDraftSaving => 'Saving draft…';

  @override
  String get reportDraftSaved => 'Draft saved';

  @override
  String get reportDraftSaveFailed =>
      'The draft could not be saved. Your text is still on screen; check your device and try again.';

  @override
  String get reportSubmitted => 'Your report was received.';

  @override
  String get reportPhotosPending =>
      'Some photos did not upload. Your report text is saved — retry each photo below.';

  @override
  String get reportPhotoRetry => 'Retry';

  @override
  String get reportConflict =>
      'This report was already sent. Your edits will be sent as a new report — tap Send again.';

  @override
  String get reportMissingFields =>
      'Please describe the issue and choose a location. Nothing was sent yet.';

  @override
  String get reportViewIssue => 'View this issue';

  @override
  String get reportAnother => 'Report another issue';

  @override
  String get reportEnableNotifications => 'Get update notifications';

  @override
  String get privateToggleTitle => 'Private request';

  @override
  String get privateToggleSubtitle =>
      'Only you and Management can see this request. Private requests never appear in the public proposals or ledger.';

  @override
  String get privateBadge => 'Private';

  @override
  String get issuesTitle => 'My issues';

  @override
  String get issuesEmpty => 'You have not reported any issues yet.';

  @override
  String get issuesLoadMore => 'Load more';

  @override
  String get statusSubmitted => 'Submitted';

  @override
  String get statusInReview => 'In review';

  @override
  String get statusNeedsInfo => 'Needs your information';

  @override
  String get statusDeclined => 'Not proceeding';

  @override
  String get statusInProgress => 'In progress';

  @override
  String get statusProposed => 'Proposal created';

  @override
  String get statusCompleted => 'Completed';

  @override
  String get statusClosed => 'Closed';

  @override
  String issueDetailTitle(int id) {
    return 'Report #$id';
  }

  @override
  String get timelineSubmitted => 'Report submitted';

  @override
  String get timelineTriagePending => 'Waiting for staff review';

  @override
  String get timelineTriageDone => 'Reviewed by staff';

  @override
  String timelineCase(String category) {
    return 'Grouped into case: $category';
  }

  @override
  String get timelineCaseNoCategory => 'Grouped into a maintenance case';

  @override
  String get categoryElevator => 'Elevator';

  @override
  String get categoryWaterLeak => 'Water leak';

  @override
  String get categoryElectricalFault => 'Electrical fault';

  @override
  String get categoryHeatingCooling => 'Heating / cooling';

  @override
  String get categoryLighting => 'Lighting';

  @override
  String get categoryDoorLock => 'Door / lock';

  @override
  String get categoryAppliance => 'Appliance';

  @override
  String get categoryStructural => 'Structural';

  @override
  String get categoryCleanliness => 'Cleanliness';

  @override
  String get categoryNoise => 'Noise';

  @override
  String get categoryOther => 'Other';

  @override
  String timelineWork(String status, String deadline) {
    return 'Work order $status, deadline $deadline';
  }

  @override
  String get timelineCompleted => 'Work completed';

  @override
  String get progressTitle => 'Work progress';

  @override
  String get progressEmpty => 'No progress updates yet.';

  @override
  String get progressCompleted => 'Work completed';

  @override
  String get declinedTitle => 'Management decided not to proceed';

  @override
  String get declinedCorrectedReportCta => 'File a corrected report';

  @override
  String get rateWorkCta => 'Rate this work';

  @override
  String get rateWorkTitle => 'How was the work?';

  @override
  String get rateSatisfied => 'Satisfied';

  @override
  String get rateNotSatisfied => 'Not satisfied';

  @override
  String get rateCommentLabel => 'Comment (optional)';

  @override
  String get rateSubmit => 'Send rating';

  @override
  String get rateThanks => 'Thank you for your rating.';

  @override
  String get infoRequestTitle => 'Management needs more information';

  @override
  String get infoReplyHint => 'Write your reply…';

  @override
  String get infoReplySubmit => 'Send reply';

  @override
  String get infoReplyPhotosHint =>
      'You can also add photos from the photo section below.';

  @override
  String infoReplySavedPhotos(int uploaded, int total) {
    return 'Your reply was received. $uploaded/$total photos attached.';
  }

  @override
  String get infoReplyPhotosPending =>
      'Your reply was received. Some photos did not upload — retry each photo below.';

  @override
  String get infoReplyNotSent =>
      'Nothing was sent yet. Your reply and photos are still here — try again.';

  @override
  String get infoReplyPendingPhotosTitle =>
      'Reply photos not yet uploaded — retry each photo.';

  @override
  String get infoReplyClose => 'Close';

  @override
  String photoNofM(int n, int m) {
    return 'Photo $n of $m';
  }

  @override
  String get photoUploadFailed => 'Not uploaded';

  @override
  String get photoLoading => 'Loading photo…';

  @override
  String get photoLoadFailed => 'The photo could not be loaded.';

  @override
  String get photoBeforeRepair => 'Photo before the repair';

  @override
  String get photoAfterRepair => 'Photo after the repair';

  @override
  String get workStatusAssigned => 'Assigned';

  @override
  String get workStatusInProgress => 'In progress';

  @override
  String get workStatusAwaiting => 'Awaiting acceptance';

  @override
  String get workStatusAccepted => 'Accepted';

  @override
  String get workStatusClosed => 'Closed';

  @override
  String get workStatusCancelled => 'Cancelled';

  @override
  String get homeFundTitle => 'Maintenance fund';

  @override
  String get homeAnnouncementTitle => 'Building announcement';

  @override
  String get homeFundInflows => 'In (30d)';

  @override
  String get homeFundOutflows => 'Out (30d)';

  @override
  String get homeFundChartCaption => 'Fund balance · last 6 months';

  @override
  String get homeActiveReports => 'My open reports';

  @override
  String get homeRecentSpending => 'Recently published spending';

  @override
  String get homeNoActiveReports => 'No open reports.';

  @override
  String get homeNoSpending => 'No published spending yet.';

  @override
  String get homeReportsLoading => 'Loading reports…';

  @override
  String get homeSpendingLoading => 'Loading spending…';

  @override
  String get notificationsTitle => 'Notifications';

  @override
  String get notificationsEmpty => 'No notifications yet.';

  @override
  String get notificationsLoadMore => 'Load more';

  @override
  String notificationsUnreadCount(int n) {
    return '$n unread notifications';
  }

  @override
  String get notificationUnread => 'Unread';

  @override
  String get notificationRead => 'Read';

  @override
  String get ledgerTitle => 'Building ledger';

  @override
  String get ledgerDetailTitle => 'Expenditure details';

  @override
  String get ledgerEmpty => 'No published spending for this period.';

  @override
  String get ledgerAllTime => 'All';

  @override
  String get ledgerYearLabel => 'Year';

  @override
  String get ledgerMonthLabel => 'Month';

  @override
  String get ledgerLoadMore => 'Load more';

  @override
  String ledgerPublishedOn(String date) {
    return 'Published $date';
  }

  @override
  String get ledgerAmount => 'Amount';

  @override
  String get ledgerContractor => 'Contractor';

  @override
  String get ledgerWhatFixed => 'What was fixed';

  @override
  String get ledgerWhy => 'Why';

  @override
  String get ledgerApprovers => 'Approved by';

  @override
  String ledgerApproverBoard(String name) {
    return 'Board: $name';
  }

  @override
  String ledgerApproverRep(String name) {
    return 'Resident representative: $name';
  }

  @override
  String ledgerApproverEmergency(String name) {
    return 'Emergency authorization: $name';
  }

  @override
  String ledgerApproverGeneric(String name) {
    return '$name';
  }

  @override
  String ledgerVerifiedBy(String name) {
    return 'Payment verified by $name';
  }

  @override
  String get ledgerNotVerified => 'Payment not yet verified';

  @override
  String get ledgerConclusionVerified => 'This expense has been verified';

  @override
  String get ledgerConclusionVerifiedBody =>
      'The transfer proof and record integrity were independently confirmed.';

  @override
  String get ledgerConclusionUnverified => 'This expense is not fully verified';

  @override
  String get ledgerConclusionUnverifiedBody =>
      'The expense was published, but a verification step is incomplete. Review the accountability chain below.';

  @override
  String get ledgerConclusionMismatch =>
      'This record does not match its anchored evidence';

  @override
  String get ledgerConclusionMismatchBody =>
      'The published record differs from the evidence that was anchored for it. Report this expense to the management board.';

  @override
  String get ledgerChainTitle => 'Accountability chain';

  @override
  String get ledgerChainHint =>
      'The expense moves from report to independent verification in the steps below.';

  @override
  String get ledgerChainReports => 'Reports and rationale';

  @override
  String get ledgerChainWork => 'Work completed';

  @override
  String get ledgerChainApprovals => 'Approvals';

  @override
  String get ledgerChainPayment => 'Transfer proof';

  @override
  String get ledgerChainVerification => 'Independent verification';

  @override
  String get ledgerCorrections => 'Corrections';

  @override
  String get ledgerCorrectionRecorded => 'Adjustment recorded';

  @override
  String get ledgerDocuments => 'Documents';

  @override
  String get ledgerDocumentOpen => 'Preview or download';

  @override
  String get ledgerDocumentOffline =>
      'You are offline. The document was not downloaded. Reconnect and try again.';

  @override
  String get ledgerDocumentUnauthorized =>
      'You are not authorized to open this document. No file was downloaded.';

  @override
  String get ledgerDocumentFailure =>
      'The document could not be opened. No file was downloaded; please try again.';

  @override
  String get documentShare => 'Share or save';

  @override
  String get documentShareFailed =>
      'The file could not be shared. The document is still open — try again.';

  @override
  String get documentNoPreview =>
      'This file cannot be previewed here. Share it to open it in another app.';

  @override
  String get ledgerProofTitle => 'Verification details';

  @override
  String get ledgerProofHash => 'Record hash';

  @override
  String get ledgerProofEvents => 'Signed events';

  @override
  String get evidenceExplorer => 'Evidence explorer';

  @override
  String get evidenceChain => 'Anchored on the blockchain';

  @override
  String get evidenceLocal => 'Signed — blockchain anchoring off';

  @override
  String get evidencePending => 'Waiting for blockchain anchoring';

  @override
  String get evidenceMismatch => 'Data mismatch detected';

  @override
  String get integrityVerified => 'Record verified';

  @override
  String get integrityMismatch => 'Integrity mismatch detected';

  @override
  String get integrityUnavailable => 'Integrity check unavailable';

  @override
  String get integrityUnchecked => 'Published — integrity not yet checked';

  @override
  String get accountOccupancies => 'My homes';

  @override
  String get accountPreferences => 'Notifications';

  @override
  String get accountPrefAll => 'Receive all notifications';

  @override
  String get accountSignOutAll => 'Sign out of all devices';

  @override
  String get signOutUnsentWorkWarning =>
      'The report you are drafting and any unsent photos on this device will be deleted.';

  @override
  String get commonCancel => 'Cancel';

  @override
  String get gateAccountAction => 'Register plate and face';

  @override
  String get gateRegistrationTitle => 'Gate registration';

  @override
  String get gatePlateLabel => 'License plate';

  @override
  String get gateSubmitPlate => 'Submit plate for approval';

  @override
  String get gateRevokePlate => 'Revoke plate';

  @override
  String get gateFaceTitle => 'Face';

  @override
  String get gateNotRegistered => 'Not registered';

  @override
  String get gateCaptureFace => 'Take registration photo';

  @override
  String get gateRevokeFace => 'Revoke face';

  @override
  String get gateRetentionNotice =>
      'The photo is retained only for management review and deleted after a decision.';

  @override
  String get gateRevokeConfirmBody =>
      'This information will no longer be used for gate recognition.';

  @override
  String get gateRevokeConfirm => 'Revoke';

  @override
  String get gateStatusPending => 'Awaiting approval';

  @override
  String get gateStatusApproved => 'Approved';

  @override
  String gateStatusRejected(String note) {
    return 'Rejected: $note';
  }

  @override
  String get gateStatusExpired => 'Photo expired; please submit another';

  @override
  String get gateStatusUnknown => 'Unknown status';

  @override
  String get gateErrorNoFace => 'No face found. Take another photo.';

  @override
  String get gateErrorMultipleFaces => 'The photo must contain one face only.';

  @override
  String get gateErrorFaceTooSmall => 'The face is too small. Move closer.';

  @override
  String get gateErrorFaceTooBlurry => 'The photo is too blurry. Take another.';

  @override
  String get gateErrorFaceUnusable =>
      'The photo cannot be used for face registration.';

  @override
  String get gateErrorPhotoRejected =>
      'The photo was rejected before processing.';

  @override
  String get gateErrorPhotoTooLarge => 'The photo exceeds the size limit.';

  @override
  String get gateErrorPlateRegistered =>
      'This plate is already registered. Contact management.';

  @override
  String get gateErrorUnavailable =>
      'Recognition is temporarily unavailable. Try again later.';

  @override
  String get gateReaderTitle => 'Gate reader';

  @override
  String get gateReaderServer => 'Server address';

  @override
  String get gateReaderCredential => 'Device credential';

  @override
  String get gateReaderActivate => 'Activate reader';

  @override
  String get gateReaderInvalidUrl =>
      'The server URL is invalid. Start it with https:// or http://.';

  @override
  String get gateReaderPlateUnreadable =>
      'The plate could not be read. Try again.';

  @override
  String gateReaderUnit(String unit) {
    return 'Unit $unit';
  }

  @override
  String get gateReaderNoMatch => 'No match found';

  @override
  String get gateReaderScanPlate => 'Scan plate';

  @override
  String get gateReaderScanFace => 'Scan face';

  @override
  String get gateReaderClearDevice => 'Clear device credential';

  @override
  String get gateReaderDeviceRevoked => 'The device credential was revoked.';

  @override
  String get gateReaderDeviceExpired => 'The device credential expired.';

  @override
  String get gateReaderDeviceInvalid => 'The device credential is invalid.';

  @override
  String get gateReaderThrottled => 'Actions are too frequent. Please wait.';

  @override
  String get fundChartTitle => 'Fund balance';

  @override
  String get fundChartFlowsTitle => 'Inflows and outflows';

  @override
  String get fundChartSemantics => 'Fund balance chart';

  @override
  String fundChartBalanceValue(String amount) {
    return 'balance $amount';
  }

  @override
  String fundChartInflowValue(String amount) {
    return 'inflow $amount';
  }

  @override
  String fundChartOutflowValue(String amount) {
    return 'outflow $amount';
  }

  @override
  String get fundChartInflowLabel => 'Inflows';

  @override
  String get fundChartOutflowLabel => 'Outflows';

  @override
  String get fundChartRange30d => '30 days';

  @override
  String get fundChartRange6m => '6 months';

  @override
  String get fundChartRange12m => '12 months';

  @override
  String get proposalsSegment => 'Proposals';

  @override
  String get ledgerSegment => 'Ledger';

  @override
  String get proposalStatusPublished => 'Published';

  @override
  String get proposalStatusInProgress => 'In progress';

  @override
  String get proposalStatusNotProceeding => 'Not proceeding';

  @override
  String get proposalStatusCompleted => 'Completed';

  @override
  String get proposalStatusClosed => 'Closed';

  @override
  String get proposalStatusDraft => 'Draft';

  @override
  String get proposalProblem => 'Problem or need';

  @override
  String get proposalAction => 'Proposed action';

  @override
  String get proposalCost => 'Estimated cost';

  @override
  String get proposalContractor => 'Contractor';

  @override
  String get proposalSchedule => 'Expected schedule';

  @override
  String get proposalVersions => 'Published versions';

  @override
  String proposalVersion(String number) {
    return 'Version $number';
  }

  @override
  String get proposalSettlement => 'Payment settlement';

  @override
  String get proposalSettled => 'Paid';

  @override
  String get proposalViewFromLedger => 'View proposal';

  @override
  String get proposalRateCta => 'Rate the result';

  @override
  String get homeBillTitle => 'Building bill';

  @override
  String get homeBillLoading => 'Loading building bill…';

  @override
  String get billsTitle => 'Bills';

  @override
  String get billAmountLabel => 'Amount';

  @override
  String get billDueLabel => 'Due';

  @override
  String get billOverdue => 'Overdue';

  @override
  String get billViewFile => 'View bill';

  @override
  String get billPayAction => 'I\'ve paid';

  @override
  String get billPayExplainer =>
      'Scanning records a transfer you already made — it does not pay the bill.';

  @override
  String get billPayStep1 => '1. Transfer the amount in your banking app.';

  @override
  String get billPayStep2 =>
      '2. Come back here and scan the QR on the bill to record it.';

  @override
  String get billStatusIssued => 'Unpaid';

  @override
  String get billStatusPaid => 'Payment recorded';

  @override
  String get billStatusVoid => 'Voided';

  @override
  String get billScanTitle => 'Scan payment QR';

  @override
  String get billScanInstruction =>
      'Point the camera at the bill QR to record your payment.';

  @override
  String get billInvalidQr => 'That QR code is not a Làm Tổ bill.';

  @override
  String get billPaymentRecorded => 'Payment recorded';

  @override
  String get billPaymentVoided =>
      'This bill was voided. No payment was recorded.';

  @override
  String get billPaymentUnknown =>
      'We could not confirm whether the payment was recorded. Check the bill status before trying again.';

  @override
  String get billCameraUnavailable =>
      'The camera is unavailable. Allow camera access in device settings, then try again.';

  @override
  String get billNone => 'No bills.';
}
