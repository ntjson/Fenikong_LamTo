# lamto_api.model.ReportDetail

## Load the model package
```dart
import 'package:lamto_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  |
**text** | **String** |  |
**status** | [**StatusEnum**](StatusEnum.md) |  |
**declinedReason** | **String** |  |
**isPrivate** | **bool** |  |
**openInfoRequest** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md) |  |
**locationPathSnapshot** | **String** |  |
**unitLabel** | **String** |  |
**createdAt** | [**DateTime**](DateTime.md) |  |
**triageStatus** | **String** |  |
**category** | **String** |  |
**photos** | [**BuiltList&lt;ReportPhoto&gt;**](ReportPhoto.md) |  |
**cases** | [**BuiltList&lt;ReportCase&gt;**](ReportCase.md) |  |
**ledgerEntryIds** | **BuiltList&lt;int&gt;** |  |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
