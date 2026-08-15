# lamto_api.api.ProposalsApi

## Load the API package
```dart
import 'package:lamto_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**proposalDetail**](ProposalsApi.md#proposaldetail) | **GET** /api/v1/proposals/{id} |
[**proposalList**](ProposalsApi.md#proposallist) | **GET** /api/v1/proposals |
[**proposalsRatingCreate**](ProposalsApi.md#proposalsratingcreate) | **POST** /api/v1/proposals/{id}/rating |


# **proposalDetail**
> Proposal proposalDetail(id, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getProposalsApi();
final int id = 56; // int |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.proposalDetail(id, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ProposalsApi->proposalDetail: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**Proposal**](Proposal.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **proposalList**
> PaginatedProposalList proposalList(xLamToOccupancy, cursor)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getProposalsApi();
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.
final String cursor = cursor_example; // String | The pagination cursor value.

try {
    final response = api.proposalList(xLamToOccupancy, cursor);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ProposalsApi->proposalList: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]
 **cursor** | **String**| The pagination cursor value. | [optional]

### Return type

[**PaginatedProposalList**](PaginatedProposalList.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **proposalsRatingCreate**
> ProposalRatingResult proposalsRatingCreate(id, caseRatingRequest, xLamToOccupancy)



### Example
```dart
import 'package:lamto_api/api.dart';
// TODO Configure API key authorization: knoxApiToken
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKey = 'YOUR_API_KEY';
// uncomment below to setup prefix (e.g. Bearer) for API key, if needed
//defaultApiClient.getAuthentication<ApiKeyAuth>('knoxApiToken').apiKeyPrefix = 'Bearer';

final api = LamtoApi().getProposalsApi();
final int id = 56; // int |
final CaseRatingRequest caseRatingRequest = ; // CaseRatingRequest |
final int xLamToOccupancy = 56; // int | Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404.

try {
    final response = api.proposalsRatingCreate(id, caseRatingRequest, xLamToOccupancy);
    print(response);
} catch on DioException (e) {
    print('Exception when calling ProposalsApi->proposalsRatingCreate: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  |
 **caseRatingRequest** | [**CaseRatingRequest**](CaseRatingRequest.md)|  |
 **xLamToOccupancy** | **int**| Active occupancy id for the authenticated resident. Required when the caller has multiple active occupancies; omitted when exactly one is auto-selected. Invalid or foreign ids yield 404. | [optional]

### Return type

[**ProposalRatingResult**](ProposalRatingResult.md)

### Authorization

[knoxApiToken](../README.md#knoxApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json, application/problem+json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
