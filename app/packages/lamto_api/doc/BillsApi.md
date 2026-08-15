# lamto_api.api.BillsApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**billsConfirmPayment**](BillsApi.md#billsconfirmpayment) | **POST** /api/v1/bills/{id}/confirm-payment |
[**billsList**](BillsApi.md#billslist) | **GET** /api/v1/bills |
[**billsRetrieve**](BillsApi.md#billsretrieve) | **GET** /api/v1/bills/{id} |


# **billsConfirmPayment**
> BillDetail billsConfirmPayment(id, billConfirmPaymentRequestRequest)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getBillsApi();
final int id = 56; // int |
final BillConfirmPaymentRequestRequest billConfirmPaymentRequestRequest = ; // BillConfirmPaymentRequestRequest |

try {
    final response = api.billsConfirmPayment(id, billConfirmPaymentRequestRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillsApi->billsConfirmPayment: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **billConfirmPaymentRequestRequest** | [**BillConfirmPaymentRequestRequest**](BillConfirmPaymentRequestRequest.md)|  |

### Return type

[**BillDetail**](BillDetail.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **billsList**
> PaginatedBillSummaryList billsList(cursor)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getBillsApi();
final String cursor = cursor_example; // String | The pagination cursor value.

try {
    final response = api.billsList(cursor);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillsApi->billsList: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **String**| The pagination cursor value. | [optional]

### Return type

[**PaginatedBillSummaryList**](PaginatedBillSummaryList.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **billsRetrieve**
> BillDetail billsRetrieve(id)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getBillsApi();
final int id = 56; // int |

try {
    final response = api.billsRetrieve(id);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillsApi->billsRetrieve: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |

### Return type

[**BillDetail**](BillDetail.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
