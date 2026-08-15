# lamto_api.api.MeApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**meNotificationPreferencesPartialUpdate**](MeApi.md#menotificationpreferencespartialupdate) | **PATCH** /api/v1/me/notification-preferences |
[**meRetrieve**](MeApi.md#meretrieve) | **GET** /api/v1/me |


# **meNotificationPreferencesPartialUpdate**
> BuiltList<NotificationPreference> meNotificationPreferencesPartialUpdate(patchedNotificationPreferenceUpdateRequest)



PATCH resident email/push preferences per event code (Flutter Account).

### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getMeApi();
final PatchedNotificationPreferenceUpdateRequest patchedNotificationPreferenceUpdateRequest = ; // PatchedNotificationPreferenceUpdateRequest |

try {
    final response = api.meNotificationPreferencesPartialUpdate(patchedNotificationPreferenceUpdateRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling MeApi->meNotificationPreferencesPartialUpdate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedNotificationPreferenceUpdateRequest** | [**PatchedNotificationPreferenceUpdateRequest**](PatchedNotificationPreferenceUpdateRequest.md)|  | [optional]

### Return type

[**BuiltList&lt;NotificationPreference&gt;**](NotificationPreference.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **meRetrieve**
> Me meRetrieve()



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getMeApi();

try {
    final response = api.meRetrieve();
    print(response);
} catch on DioException (e) {
    print('Exception when calling MeApi->meRetrieve: $e\n');
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Me**](Me.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
