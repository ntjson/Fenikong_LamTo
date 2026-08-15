# lamto_api.model.Proposal

## Load the model package
```dart
import 'package:lamto_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  |
**caseId** | **int** |  |
**buildingId** | **int** |  |
**status** | **String** |  |
**completedAt** | [**DateTime**](DateTime.md) |  |
**closedAt** | [**DateTime**](DateTime.md) |  |
**purpose** | **String** |  |
**proposedAction** | **String** |  |
**amountVnd** | **int** |  |
**fundCode** | **String** |  |
**contractorName** | **String** |  |
**expectedSchedule** | **String** |  |
**versions** | [**BuiltList&lt;ProposalVersion&gt;**](ProposalVersion.md) |  |
**progress** | [**BuiltList&lt;ProposalProgress&gt;**](ProposalProgress.md) |  |
**settlement** | [**ProposalSettlement**](ProposalSettlement.md) |  |
**canRate** | **bool** |  |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
