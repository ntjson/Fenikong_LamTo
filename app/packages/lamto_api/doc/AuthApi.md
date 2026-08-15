# lamto_api.api.AuthApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**authLoginCreate**](AuthApi.md#authlogincreate) | **POST** /api/v1/auth/login |
[**authLogoutAllCreate**](AuthApi.md#authlogoutallcreate) | **POST** /api/v1/auth/logout-all |
[**authLogoutCreate**](AuthApi.md#authlogoutcreate) | **POST** /api/v1/auth/logout |


# **authLoginCreate**
> TokenResponse authLoginCreate(loginRequest)



### Example
```dart
import 'package:lamto_api/api.dart';

final api = LamtoApi().getAuthApi();
final LoginRequest loginRequest = ; // LoginRequest |

try {
    final response = api.authLoginCreate(loginRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling AuthApi->authLoginCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **loginRequest** | [**LoginRequest**](LoginRequest.md)|  |

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **authLogoutAllCreate**
> authLogoutAllCreate()



Log the user out of all sessions I.E. deletes all auth tokens for the user

### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getAuthApi();

try {
    api.authLogoutAllCreate();
} catch on DioException (e) {
    print('Exception when calling AuthApi->authLogoutAllCreate: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **authLogoutCreate**
> authLogoutCreate(xInstallId, logoutInstallIdRequest)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getAuthApi();
final String xInstallId = xInstallId_example; // String | Stable per-install client id. When present on logout, deactivates that install's FCM Device so push stops for the install. Also accepted as JSON body field install_id.
final LogoutInstallIdRequest logoutInstallIdRequest = ; // LogoutInstallIdRequest |

try {
    api.authLogoutCreate(xInstallId, logoutInstallIdRequest);
} catch on DioException (e) {
    print('Exception when calling AuthApi->authLogoutCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xInstallId** | **String**| Stable per-install client id. When present on logout, deactivates that install's FCM Device so push stops for the install. Also accepted as JSON body field install_id. | [optional]
 **logoutInstallIdRequest** | [**LogoutInstallIdRequest**](LogoutInstallIdRequest.md)|  | [optional]

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
