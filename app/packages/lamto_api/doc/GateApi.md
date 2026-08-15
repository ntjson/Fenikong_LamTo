# lamto_api.api.GateApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**gateDeviceRetrieve**](GateApi.md#gatedeviceretrieve) | **GET** /api/v1/gate/device |
[**gateFaceCreate**](GateApi.md#gatefacecreate) | **POST** /api/v1/gate/face |
[**gateFaceDestroy**](GateApi.md#gatefacedestroy) | **DELETE** /api/v1/gate/face |
[**gatePlatesCreate**](GateApi.md#gateplatescreate) | **POST** /api/v1/gate/plates |
[**gatePlatesDestroy**](GateApi.md#gateplatesdestroy) | **DELETE** /api/v1/gate/plates/{id} |
[**gateRecognizeFaceCreate**](GateApi.md#gaterecognizefacecreate) | **POST** /api/v1/gate/recognize/face |
[**gateRecognizePlateCreate**](GateApi.md#gaterecognizeplatecreate) | **POST** /api/v1/gate/recognize/plate |
[**gateRegistrationsRetrieve**](GateApi.md#gateregistrationsretrieve) | **GET** /api/v1/gate/registrations |


# **gateDeviceRetrieve**
> GateDevice gateDeviceRetrieve()



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: GateDevice
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();

try {
    final response = api.gateDeviceRetrieve();
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateDeviceRetrieve: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**GateDevice**](GateDevice.md)

### Authorization

[GateDevice](../README.md#GateDevice)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gateFaceCreate**
> FaceEnrollment gateFaceCreate(photo, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final MultipartFile photo = BINARY_DATA_HERE; // MultipartFile |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.gateFaceCreate(photo, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateFaceCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **photo** | **MultipartFile**|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**FaceEnrollment**](FaceEnrollment.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gateFaceDestroy**
> gateFaceDestroy(xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    api.gateFaceDestroy(xLamToOccupancy);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateFaceDestroy: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gatePlatesCreate**
> VehiclePlate gatePlatesCreate(plateCreateRequest, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final PlateCreateRequest plateCreateRequest = ; // PlateCreateRequest |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.gatePlatesCreate(plateCreateRequest, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gatePlatesCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plateCreateRequest** | [**PlateCreateRequest**](PlateCreateRequest.md)|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**VehiclePlate**](VehiclePlate.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gatePlatesDestroy**
> gatePlatesDestroy(id, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final int id = 56; // int |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    api.gatePlatesDestroy(id, xLamToOccupancy);
} catch on DioException (e) {
    print('Exception when calling GateApi->gatePlatesDestroy: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gateRecognizeFaceCreate**
> RecognitionOutcome gateRecognizeFaceCreate(photo)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: GateDevice
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final MultipartFile photo = BINARY_DATA_HERE; // MultipartFile |

try {
    final response = api.gateRecognizeFaceCreate(photo);
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateRecognizeFaceCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **photo** | **MultipartFile**|  |

### Return type

[**RecognitionOutcome**](RecognitionOutcome.md)

### Authorization

[GateDevice](../README.md#GateDevice)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gateRecognizePlateCreate**
> RecognitionOutcome gateRecognizePlateCreate(plateRecognizeRequest)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: GateDevice
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('GateDevice').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final PlateRecognizeRequest plateRecognizeRequest = ; // PlateRecognizeRequest |

try {
    final response = api.gateRecognizePlateCreate(plateRecognizeRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateRecognizePlateCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plateRecognizeRequest** | [**PlateRecognizeRequest**](PlateRecognizeRequest.md)|  |

### Return type

[**RecognitionOutcome**](RecognitionOutcome.md)

### Authorization

[GateDevice](../README.md#GateDevice)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **gateRegistrationsRetrieve**
> GateRegistrations gateRegistrationsRetrieve(xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getGateApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.gateRegistrationsRetrieve(xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling GateApi->gateRegistrationsRetrieve: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**GateRegistrations**](GateRegistrations.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
