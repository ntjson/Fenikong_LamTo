# lamto_api.api.CasesApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**casesRatingCreate**](CasesApi.md#casesratingcreate) | **POST** /api/v1/cases/{id}/rating |


# **casesRatingCreate**
> CaseRatingResult casesRatingCreate(id, caseRatingRequest)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getCasesApi();
final int id = 56; // int |
final CaseRatingRequest caseRatingRequest = ; // CaseRatingRequest |

try {
    final response = api.casesRatingCreate(id, caseRatingRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling CasesApi->casesRatingCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **caseRatingRequest** | [**CaseRatingRequest**](CaseRatingRequest.md)|  |

### Return type

[**CaseRatingResult**](CaseRatingResult.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
