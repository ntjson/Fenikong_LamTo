import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/providers.dart';

abstract class ProposalsRepository {
  Future<PaginatedProposalList> listProposals({String? cursor});
  Future<Proposal> fetchProposal(int id);
  Future<ProposalRatingResult> rateProposal({
    required int id,
    required bool satisfied,
    String comment = '',
  });
}

class DioProposalsRepository implements ProposalsRepository {
  DioProposalsRepository(Dio dio)
    : _proposals = ProposalsApi(dio, standardSerializers);

  final ProposalsApi _proposals;

  @override
  Future<PaginatedProposalList> listProposals({String? cursor}) async =>
      (await _proposals.proposalList(cursor: cursor)).data!;

  @override
  Future<Proposal> fetchProposal(int id) async =>
      (await _proposals.proposalDetail(id: id)).data!;

  @override
  Future<ProposalRatingResult> rateProposal({
    required int id,
    required bool satisfied,
    String comment = '',
  }) async {
    final response = await _proposals.proposalsRatingCreate(
      id: id,
      caseRatingRequest: CaseRatingRequest(
        (b) => b
          ..satisfied = satisfied
          ..comment = comment,
      ),
    );
    return response.data!;
  }
}

final proposalsRepositoryProvider = Provider<ProposalsRepository>(
  (ref) => DioProposalsRepository(ref.watch(dioProvider)),
);

final proposalDetailProvider = FutureProvider.autoDispose.family<Proposal, int>(
  (ref, id) {
    ref.watch(occupancyScopedProviders);
    return ref.watch(proposalsRepositoryProvider).fetchProposal(id);
  },
);
