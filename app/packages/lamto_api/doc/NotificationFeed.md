# lamto_api.model.NotificationFeed

## Load the model package
```dart
import 'package:lamto_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  |
**eventCode** | **String** |  |
**eventKey** | **String** | Deep-link reference '{code}:{entity}:{id}' (spec 6.3/7.4). Entity ids are resident-visible resources the API re-authorizes on fetch. Authorization-neutral and non-sensitive: codes/entity/ids only — no PII, bodies, or tokens. |
**subject** | **String** |  |
**body** | **String** |  |
**createdAt** | [**DateTime**](DateTime.md) |  |
**readAt** | [**DateTime**](DateTime.md) |  |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
