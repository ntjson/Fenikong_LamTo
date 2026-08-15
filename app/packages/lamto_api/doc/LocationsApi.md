# lamto_api.api.LocationsApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**locationsRetrieve**](LocationsApi.md#locationsretrieve) | **GET** /api/v1/locations |


# **locationsRetrieve**
> BuiltList<Location> locationsRetrieve(xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getLocationsApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.locationsRetrieve(xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling LocationsApi->locationsRetrieve: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**BuiltList&lt;Location&gt;**](Location.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
