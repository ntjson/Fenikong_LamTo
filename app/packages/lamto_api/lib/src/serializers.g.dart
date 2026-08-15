// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'serializers.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

Serializers _$serializers = (Serializers().toBuilder()
      ..add(BillConfirmPaymentRequestRequest.serializer)
      ..add(BillDetail.serializer)
      ..add(BillStatusEnum.serializer)
      ..add(BillSummary.serializer)
      ..add(CaseRatingRequest.serializer)
      ..add(CaseRatingResult.serializer)
      ..add(Device.serializer)
      ..add(DeviceRegisterRequest.serializer)
      ..add(DirectionEnum.serializer)
      ..add(FaceEnrollment.serializer)
      ..add(FundSeries.serializer)
      ..add(FundSeriesPoint.serializer)
      ..add(FundSummary.serializer)
      ..add(GateDevice.serializer)
      ..add(GateRegistrations.serializer)
      ..add(InfoReplyRequest.serializer)
      ..add(InfoReplyResult.serializer)
      ..add(KindEnum.serializer)
      ..add(LedgerDocument.serializer)
      ..add(LedgerEntryDetail.serializer)
      ..add(LedgerEntryList.serializer)
      ..add(Location.serializer)
      ..add(LoginRequest.serializer)
      ..add(LogoutInstallIdRequest.serializer)
      ..add(Me.serializer)
      ..add(NotificationFeed.serializer)
      ..add(NotificationPreference.serializer)
      ..add(NotificationPreferenceUpdateItemRequest.serializer)
      ..add(Occupancy.serializer)
      ..add(PaginatedBillSummaryList.serializer)
      ..add(PaginatedLedgerEntryListList.serializer)
      ..add(PaginatedNotificationFeedList.serializer)
      ..add(PaginatedProposalList.serializer)
      ..add(PaginatedReportSummaryList.serializer)
      ..add(PatchedNotificationPreferenceUpdateRequest.serializer)
      ..add(PlateCreateRequest.serializer)
      ..add(PlateRecognizeRequest.serializer)
      ..add(PlatformEnum.serializer)
      ..add(Problem.serializer)
      ..add(Proof.serializer)
      ..add(ProofEvent.serializer)
      ..add(Proposal.serializer)
      ..add(ProposalProgress.serializer)
      ..add(ProposalRatingResult.serializer)
      ..add(ProposalSettlement.serializer)
      ..add(ProposalSupportingDocument.serializer)
      ..add(ProposalVersion.serializer)
      ..add(RecognitionOutcome.serializer)
      ..add(RegistrationBuilding.serializer)
      ..add(RegistrationCreateRequest.serializer)
      ..add(RegistrationStatus.serializer)
      ..add(RegistrationStatusEnum.serializer)
      ..add(RegistrationSubmission.serializer)
      ..add(RegistrationUnit.serializer)
      ..add(ReportCase.serializer)
      ..add(ReportCreateRequest.serializer)
      ..add(ReportDetail.serializer)
      ..add(ReportPhoto.serializer)
      ..add(ReportSummary.serializer)
      ..add(ReportWorkUpdate.serializer)
      ..add(StatusEnum.serializer)
      ..add(TokenResponse.serializer)
      ..add(VehiclePlate.serializer)
      ..add(Verification.serializer)
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(BillSummary)]),
          () => ListBuilder<BillSummary>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(FundSeriesPoint)]),
          () => ListBuilder<FundSeriesPoint>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(LedgerEntryList)]),
          () => ListBuilder<LedgerEntryList>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(NotificationFeed)]),
          () => ListBuilder<NotificationFeed>())
      ..addBuilderFactory(
          const FullType(BuiltList,
              const [const FullType(NotificationPreferenceUpdateItemRequest)]),
          () => ListBuilder<NotificationPreferenceUpdateItemRequest>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(Occupancy)]),
          () => ListBuilder<Occupancy>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(NotificationPreference)]),
          () => ListBuilder<NotificationPreference>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ProofEvent)]),
          () => ListBuilder<ProofEvent>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(Proposal)]),
          () => ListBuilder<Proposal>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(ProposalSupportingDocument)]),
          () => ListBuilder<ProposalSupportingDocument>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ProposalVersion)]),
          () => ListBuilder<ProposalVersion>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ProposalProgress)]),
          () => ListBuilder<ProposalProgress>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(RegistrationUnit)]),
          () => ListBuilder<RegistrationUnit>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ReportSummary)]),
          () => ListBuilder<ReportSummary>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ReportWorkUpdate)]),
          () => ListBuilder<ReportWorkUpdate>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(VehiclePlate)]),
          () => ListBuilder<VehiclePlate>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType.nullable(JsonObject)]),
          () => ListBuilder<JsonObject?>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType.nullable(JsonObject)]),
          () => ListBuilder<JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(LedgerDocument)]),
          () => ListBuilder<LedgerDocument>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ReportPhoto)]),
          () => ListBuilder<ReportPhoto>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ReportCase)]),
          () => ListBuilder<ReportCase>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(int)]),
          () => ListBuilder<int>()))
    .build();

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
