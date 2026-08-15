# lamto_api.model.Problem

## Load the model package
```dart
import 'package:lamto_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **String** | Problem type URI reference; usually about:blank. |
**title** | **String** | Short human-readable summary (HTTP status phrase). |
**status** | **int** | HTTP status code. |
**code** | **String** | Stable machine code for client branching (e.g. validation_failed, authentication_failed, not_authenticated, permission_denied, not_found, occupancy_selection_required, throttled). |
**detail** | **String** | Developer-English explanation; not shown raw to residents. | [optional]
**errors** | [**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md) | Per-field validation errors when code is validation_failed. Values are lists of {message, code} objects (may nest for non-field errors). | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
