# lamto_api.api.RegistrationApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**registrationCreate**](RegistrationApi.md#registrationcreate) | **POST** /api/v1/registration-requests |
[**registrationOptions**](RegistrationApi.md#registrationoptions) | **GET** /api/v1/registration/options |
[**registrationStatus**](RegistrationApi.md#registrationstatus) | **GET** /api/v1/registration-requests/status |


# **registrationCreate**
> RegistrationSubmission registrationCreate(registrationCreateRequest)



### Example
```dart
import 'package:lamto_api/api.dart';

final api = LamtoApi().getRegistrationApi();
final RegistrationCreateRequest registrationCreateRequest = ; // RegistrationCreateRequest |

try {
    final response = api.registrationCreate(registrationCreateRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RegistrationApi->registrationCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **registrationCreateRequest** | [**RegistrationCreateRequest**](RegistrationCreateRequest.md)|  |

### Return type

[**RegistrationSubmission**](RegistrationSubmission.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **registrationOptions**
> BuiltList<RegistrationBuilding> registrationOptions()



### Example
```dart
import 'package:lamto_api/api.dart';

final api = LamtoApi().getRegistrationApi();

try {
    final response = api.registrationOptions();
    print(response);
} catch on DioException (e) {
    print('Exception when calling RegistrationApi->registrationOptions: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**BuiltList&lt;RegistrationBuilding&gt;**](RegistrationBuilding.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **registrationStatus**
> RegistrationStatus registrationStatus(xRegistrationStatusToken)



### Example
```dart
import 'package:lamto_api/api.dart';

final api = LamtoApi().getRegistrationApi();
final String xRegistrationStatusToken = xRegistrationStatusToken_example; // String |

try {
    final response = api.registrationStatus(xRegistrationStatusToken);
    print(response);
} catch on DioException (e) {
    print('Exception when calling RegistrationApi->registrationStatus: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xRegistrationStatusToken** | **String**|  |

### Return type

[**RegistrationStatus**](RegistrationStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
