# lamto_api.api.LedgerApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ledgerList**](LedgerApi.md#ledgerlist) | **GET** /api/v1/ledger |
[**ledgerRetrieve**](LedgerApi.md#ledgerretrieve) | **GET** /api/v1/ledger/{id} |


# **ledgerList**
> PaginatedLedgerEntryListList ledgerList(xLamToOccupancy, cursor, month, year)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getLedgerApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.
final String cursor = cursor_example; // String | The pagination cursor value.
final int month = 56; // int |
final int year = 56; // int |

try {
    final response = api.ledgerList(xLamToOccupancy, cursor, month, year);
    print(response);
} catch on DioException (e) {
    print('Exception when calling LedgerApi->ledgerList: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]
 **cursor** | **String**| The pagination cursor value. | [optional]
 **month** | **int**|  | [optional]
 **year** | **int**|  | [optional]

### Return type

[**PaginatedLedgerEntryListList**](PaginatedLedgerEntryListList.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ledgerRetrieve**
> LedgerEntryDetail ledgerRetrieve(id, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getLedgerApi();
final int id = 56; // int |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.ledgerRetrieve(id, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling LedgerApi->ledgerRetrieve: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**LedgerEntryDetail**](LedgerEntryDetail.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
