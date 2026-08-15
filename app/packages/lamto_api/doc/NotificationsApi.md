# lamto_api.api.NotificationsApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**notificationsList**](NotificationsApi.md#notificationslist) | **GET** /api/v1/notifications |
[**notificationsReadCreate**](NotificationsApi.md#notificationsreadcreate) | **POST** /api/v1/notifications/{id}/read |


# **notificationsList**
> PaginatedNotificationFeedList notificationsList(xLamToOccupancy, cursor, eventCode, unread)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getNotificationsApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.
final String cursor = cursor_example; // String | The pagination cursor value.
final String eventCode = eventCode_example; // String |
final bool unread = true; // bool |

try {
    final response = api.notificationsList(xLamToOccupancy, cursor, eventCode, unread);
    print(response);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->notificationsList: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]
 **cursor** | **String**| The pagination cursor value. | [optional]
 **eventCode** | **String**|  | [optional]
 **unread** | **bool**|  | [optional]

### Return type

[**PaginatedNotificationFeedList**](PaginatedNotificationFeedList.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **notificationsReadCreate**
> notificationsReadCreate(id)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getNotificationsApi();
final int id = 56; // int |

try {
    api.notificationsReadCreate(id);
} catch on DioException (e) {
    print('Exception when calling NotificationsApi->notificationsReadCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |

### Return type

void (empty response body)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
