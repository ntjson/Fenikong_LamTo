# lamto_api.api.ReportsApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**reportsCreate**](ReportsApi.md#reportscreate) | **POST** /api/v1/reports |
[**reportsInfoReplyCreate**](ReportsApi.md#reportsinforeplycreate) | **POST** /api/v1/reports/{id}/info-reply |
[**reportsList**](ReportsApi.md#reportslist) | **GET** /api/v1/reports |
[**reportsPhotosCreate**](ReportsApi.md#reportsphotoscreate) | **POST** /api/v1/reports/{id}/photos |
[**reportsRetrieve**](ReportsApi.md#reportsretrieve) | **GET** /api/v1/reports/{id} |


# **reportsCreate**
> ReportSummary reportsCreate(reportCreateRequest, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getReportsApi();
final ReportCreateRequest reportCreateRequest = ; // ReportCreateRequest |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.reportsCreate(reportCreateRequest, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ReportsApi->reportsCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reportCreateRequest** | [**ReportCreateRequest**](ReportCreateRequest.md)|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**ReportSummary**](ReportSummary.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reportsInfoReplyCreate**
> InfoReplyResult reportsInfoReplyCreate(id, infoReplyRequest)



Step 1 of the resident's needs-info reply: commit the text. Text-only by design so a dropped connection can never lose the words; the client then attaches any photos one by one via POST /api/v1/reports/{id}/photos. A successful reply resolves the open information request and moves the report from NEEDS_INFO back to IN_REVIEW (photo uploads are not status-gated, so step 2 still works after the flip).

### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getReportsApi();
final int id = 56; // int |
final InfoReplyRequest infoReplyRequest = ; // InfoReplyRequest |

try {
    final response = api.reportsInfoReplyCreate(id, infoReplyRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ReportsApi->reportsInfoReplyCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **infoReplyRequest** | [**InfoReplyRequest**](InfoReplyRequest.md)|  |

### Return type

[**InfoReplyResult**](InfoReplyResult.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reportsList**
> PaginatedReportSummaryList reportsList(cursor)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getReportsApi();
final String cursor = cursor_example; // String | The pagination cursor value.

try {
    final response = api.reportsList(cursor);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ReportsApi->reportsList: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **String**| The pagination cursor value. | [optional]

### Return type

[**PaginatedReportSummaryList**](PaginatedReportSummaryList.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reportsPhotosCreate**
> ReportPhoto reportsPhotosCreate(id, photo)



Attach one photo to a report the caller submitted (active occupancy in the report's building required). There is no report-status gate, so this also serves as step 2 of the needs-info reply choreography, after POST /api/v1/reports/{id}/info-reply commits the text. Uploads are virus-scanned before storage and idempotent per report by content SHA-256: replaying the same file returns 200 with the existing photo instead of creating a duplicate (201), so per-photo retries are safe.

### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getReportsApi();
final int id = 56; // int |
final MultipartFile photo = BINARY_DATA_HERE; // MultipartFile | JPEG/PNG image; scanned by ClamAV before storage.

try {
    final response = api.reportsPhotosCreate(id, photo);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ReportsApi->reportsPhotosCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **photo** | **MultipartFile**| JPEG/PNG image; scanned by ClamAV before storage. |

### Return type

[**ReportPhoto**](ReportPhoto.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reportsRetrieve**
> ReportDetail reportsRetrieve(id)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getReportsApi();
final int id = 56; // int |

try {
    final response = api.reportsRetrieve(id);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ReportsApi->reportsRetrieve: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |

### Return type

[**ReportDetail**](ReportDetail.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
