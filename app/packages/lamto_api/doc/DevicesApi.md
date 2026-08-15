# lamto_api.api.DevicesApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**devicesCreate**](DevicesApi.md#devicescreate) | **POST** /api/v1/devices |
[**devicesDestroy**](DevicesApi.md#devicesdestroy) | **DELETE** /api/v1/devices/{install_id} |


# **devicesCreate**
> Device devicesCreate(deviceRegisterRequest)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getDevicesApi();
final DeviceRegisterRequest deviceRegisterRequest = ; // DeviceRegisterRequest |

try {
    final response = api.devicesCreate(deviceRegisterRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling DevicesApi->devicesCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deviceRegisterRequest** | [**DeviceRegisterRequest**](DeviceRegisterRequest.md)|  |

### Return type

[**Device**](Device.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **devicesDestroy**
> devicesDestroy(installId)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getDevicesApi();
final String installId = installId_example; // String |

try {
    api.devicesDestroy(installId);
} catch on DioException (e) {
    print('Exception when calling DevicesApi->devicesDestroy: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **installId** | **String**|  |

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
