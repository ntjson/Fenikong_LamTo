# lamto_api.model.ProposalComparison

## Load the model package
```dart
import 'package:lamto_api/api.dart';
```

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**direction** | **String** | Direction of comparison: above, below, or equal. |
**percentage** | **int** | Difference percentage against the predicted price band. |
**range** | **String** | Formatted range string of the predicted price band. |
**reasoning** | **String** | One-sentence Vietnamese reasoning explaining the band. |
**source_** | **String** | Source of the prediction: predicted or fallback. |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
