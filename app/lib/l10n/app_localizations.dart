import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_vi.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('vi'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Làm Tổ'**
  String get appTitle;

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginTitle;

  /// No description provided for @loginIdentifier.
  ///
  /// In en, this message translates to:
  /// **'Phone or email'**
  String get loginIdentifier;

  /// No description provided for @loginPassword.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get loginPassword;

  /// No description provided for @loginSubmit.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginSubmit;

  /// No description provided for @loginMissingFields.
  ///
  /// In en, this message translates to:
  /// **'Enter your phone/email and password. Nothing was submitted.'**
  String get loginMissingFields;

  /// No description provided for @loginShowPassword.
  ///
  /// In en, this message translates to:
  /// **'Show password'**
  String get loginShowPassword;

  /// No description provided for @loginHidePassword.
  ///
  /// In en, this message translates to:
  /// **'Hide password'**
  String get loginHidePassword;

  /// No description provided for @registrationOpen.
  ///
  /// In en, this message translates to:
  /// **'Register as a resident'**
  String get registrationOpen;

  /// No description provided for @registrationTitle.
  ///
  /// In en, this message translates to:
  /// **'Resident registration'**
  String get registrationTitle;

  /// No description provided for @registrationFullName.
  ///
  /// In en, this message translates to:
  /// **'Full name'**
  String get registrationFullName;

  /// No description provided for @registrationPhone.
  ///
  /// In en, this message translates to:
  /// **'Phone'**
  String get registrationPhone;

  /// No description provided for @registrationEmail.
  ///
  /// In en, this message translates to:
  /// **'Email (optional)'**
  String get registrationEmail;

  /// No description provided for @registrationPassword.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get registrationPassword;

  /// No description provided for @registrationBuilding.
  ///
  /// In en, this message translates to:
  /// **'Building'**
  String get registrationBuilding;

  /// No description provided for @registrationUnit.
  ///
  /// In en, this message translates to:
  /// **'Unit'**
  String get registrationUnit;

  /// No description provided for @registrationRequired.
  ///
  /// In en, this message translates to:
  /// **'Required'**
  String get registrationRequired;

  /// No description provided for @registrationSubmit.
  ///
  /// In en, this message translates to:
  /// **'Submit request'**
  String get registrationSubmit;

  /// No description provided for @registrationPendingTitle.
  ///
  /// In en, this message translates to:
  /// **'Registration pending'**
  String get registrationPendingTitle;

  /// No description provided for @registrationPendingBody.
  ///
  /// In en, this message translates to:
  /// **'Management is reviewing your request.'**
  String get registrationPendingBody;

  /// No description provided for @registrationRejectedTitle.
  ///
  /// In en, this message translates to:
  /// **'Registration rejected'**
  String get registrationRejectedTitle;

  /// No description provided for @registrationApprovedTitle.
  ///
  /// In en, this message translates to:
  /// **'Registration approved'**
  String get registrationApprovedTitle;

  /// No description provided for @registrationApprovedBody.
  ///
  /// In en, this message translates to:
  /// **'Your account is ready. Continue to sign in.'**
  String get registrationApprovedBody;

  /// No description provided for @registrationExpiredTitle.
  ///
  /// In en, this message translates to:
  /// **'Request expired'**
  String get registrationExpiredTitle;

  /// No description provided for @registrationExpiredBody.
  ///
  /// In en, this message translates to:
  /// **'This registration request has expired.'**
  String get registrationExpiredBody;

  /// No description provided for @registrationRefresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get registrationRefresh;

  /// No description provided for @registrationNewRequest.
  ///
  /// In en, this message translates to:
  /// **'Submit a new request'**
  String get registrationNewRequest;

  /// No description provided for @registrationContinueLogin.
  ///
  /// In en, this message translates to:
  /// **'Continue to sign in'**
  String get registrationContinueLogin;

  /// No description provided for @apiBaseUrlTitle.
  ///
  /// In en, this message translates to:
  /// **'API server'**
  String get apiBaseUrlTitle;

  /// No description provided for @apiBaseUrlLabel.
  ///
  /// In en, this message translates to:
  /// **'API URL'**
  String get apiBaseUrlLabel;

  /// No description provided for @apiBaseUrlHelp.
  ///
  /// In en, this message translates to:
  /// **'Paste your Cloudflare tunnel URL (https://….trycloudflare.com). No APK rebuild needed when the tunnel changes. Saving signs you out.'**
  String get apiBaseUrlHelp;

  /// No description provided for @apiBaseUrlSave.
  ///
  /// In en, this message translates to:
  /// **'Save URL'**
  String get apiBaseUrlSave;

  /// No description provided for @apiBaseUrlReset.
  ///
  /// In en, this message translates to:
  /// **'Default'**
  String get apiBaseUrlReset;

  /// No description provided for @apiBaseUrlInvalid.
  ///
  /// In en, this message translates to:
  /// **'Invalid URL. Use https://… or http://…'**
  String get apiBaseUrlInvalid;

  /// No description provided for @apiBaseUrlSaved.
  ///
  /// In en, this message translates to:
  /// **'Server URL saved.'**
  String get apiBaseUrlSaved;

  /// No description provided for @occupancyPickerTitle.
  ///
  /// In en, this message translates to:
  /// **'Choose your home'**
  String get occupancyPickerTitle;

  /// No description provided for @signOut.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get signOut;

  /// No description provided for @noOccupancyTitle.
  ///
  /// In en, this message translates to:
  /// **'No home linked'**
  String get noOccupancyTitle;

  /// No description provided for @noOccupancyBody.
  ///
  /// In en, this message translates to:
  /// **'Your account is signed in, but no apartment is linked yet. Contact your building management, or sign out and try another account.'**
  String get noOccupancyBody;

  /// No description provided for @errAuthFailed.
  ///
  /// In en, this message translates to:
  /// **'The phone/email or password is incorrect. Nothing was submitted. Please try again.'**
  String get errAuthFailed;

  /// No description provided for @errThrottled.
  ///
  /// In en, this message translates to:
  /// **'Too many attempts. Nothing was submitted. Please wait a few minutes and try again.'**
  String get errThrottled;

  /// No description provided for @errOccupancyRequired.
  ///
  /// In en, this message translates to:
  /// **'Please choose which home this applies to.'**
  String get errOccupancyRequired;

  /// No description provided for @errNetwork.
  ///
  /// In en, this message translates to:
  /// **'No connection. Your action was not sent. Check your network and retry.'**
  String get errNetwork;

  /// No description provided for @errServer.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong on our side. Your action may not have been saved. Please try again shortly.'**
  String get errServer;

  /// No description provided for @errGeneric.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong. Please try again.'**
  String get errGeneric;

  /// No description provided for @tabHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get tabHome;

  /// No description provided for @tabReport.
  ///
  /// In en, this message translates to:
  /// **'Report'**
  String get tabReport;

  /// No description provided for @tabIssues.
  ///
  /// In en, this message translates to:
  /// **'Issues'**
  String get tabIssues;

  /// No description provided for @tabLedger.
  ///
  /// In en, this message translates to:
  /// **'Ledger'**
  String get tabLedger;

  /// No description provided for @tabAccount.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get tabAccount;

  /// No description provided for @locationPickerTitle.
  ///
  /// In en, this message translates to:
  /// **'Where is the issue?'**
  String get locationPickerTitle;

  /// No description provided for @locationChooseHere.
  ///
  /// In en, this message translates to:
  /// **'Choose this area'**
  String get locationChooseHere;

  /// No description provided for @commonRetry.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get commonRetry;

  /// No description provided for @reportFormTitle.
  ///
  /// In en, this message translates to:
  /// **'Report an issue'**
  String get reportFormTitle;

  /// No description provided for @reportTextLabel.
  ///
  /// In en, this message translates to:
  /// **'What happened?'**
  String get reportTextLabel;

  /// No description provided for @reportLocationLabel.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get reportLocationLabel;

  /// No description provided for @reportLocationEmpty.
  ///
  /// In en, this message translates to:
  /// **'Choose a location'**
  String get reportLocationEmpty;

  /// No description provided for @reportPhotosLabel.
  ///
  /// In en, this message translates to:
  /// **'Photos (up to {max})'**
  String reportPhotosLabel(int max);

  /// No description provided for @reportAddPhoto.
  ///
  /// In en, this message translates to:
  /// **'Add photo'**
  String get reportAddPhoto;

  /// No description provided for @reportPhotoCamera.
  ///
  /// In en, this message translates to:
  /// **'Take a photo'**
  String get reportPhotoCamera;

  /// No description provided for @reportPhotoGallery.
  ///
  /// In en, this message translates to:
  /// **'Choose from gallery'**
  String get reportPhotoGallery;

  /// No description provided for @reportSubmit.
  ///
  /// In en, this message translates to:
  /// **'Send report'**
  String get reportSubmit;

  /// No description provided for @reportDraftSaving.
  ///
  /// In en, this message translates to:
  /// **'Saving draft…'**
  String get reportDraftSaving;

  /// No description provided for @reportDraftSaved.
  ///
  /// In en, this message translates to:
  /// **'Draft saved'**
  String get reportDraftSaved;

  /// No description provided for @reportDraftSaveFailed.
  ///
  /// In en, this message translates to:
  /// **'The draft could not be saved. Your text is still on screen; check your device and try again.'**
  String get reportDraftSaveFailed;

  /// No description provided for @reportSubmitted.
  ///
  /// In en, this message translates to:
  /// **'Your report was received.'**
  String get reportSubmitted;

  /// No description provided for @reportPhotosPending.
  ///
  /// In en, this message translates to:
  /// **'Some photos did not upload. Your report text is saved — retry each photo below.'**
  String get reportPhotosPending;

  /// No description provided for @reportPhotoRetry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get reportPhotoRetry;

  /// No description provided for @reportConflict.
  ///
  /// In en, this message translates to:
  /// **'This report was already sent. Your edits will be sent as a new report — tap Send again.'**
  String get reportConflict;

  /// No description provided for @reportMissingFields.
  ///
  /// In en, this message translates to:
  /// **'Please describe the issue and choose a location. Nothing was sent yet.'**
  String get reportMissingFields;

  /// No description provided for @reportViewIssue.
  ///
  /// In en, this message translates to:
  /// **'View this issue'**
  String get reportViewIssue;

  /// No description provided for @reportAnother.
  ///
  /// In en, this message translates to:
  /// **'Report another issue'**
  String get reportAnother;

  /// No description provided for @reportEnableNotifications.
  ///
  /// In en, this message translates to:
  /// **'Get update notifications'**
  String get reportEnableNotifications;

  /// No description provided for @privateToggleTitle.
  ///
  /// In en, this message translates to:
  /// **'Private request'**
  String get privateToggleTitle;

  /// No description provided for @privateToggleSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Only you and Management can see this request. Private requests never appear in the public proposals or ledger.'**
  String get privateToggleSubtitle;

  /// No description provided for @privateBadge.
  ///
  /// In en, this message translates to:
  /// **'Private'**
  String get privateBadge;

  /// No description provided for @issuesTitle.
  ///
  /// In en, this message translates to:
  /// **'My issues'**
  String get issuesTitle;

  /// No description provided for @issuesEmpty.
  ///
  /// In en, this message translates to:
  /// **'You have not reported any issues yet.'**
  String get issuesEmpty;

  /// No description provided for @issuesLoadMore.
  ///
  /// In en, this message translates to:
  /// **'Load more'**
  String get issuesLoadMore;

  /// No description provided for @statusSubmitted.
  ///
  /// In en, this message translates to:
  /// **'Submitted'**
  String get statusSubmitted;

  /// No description provided for @statusInReview.
  ///
  /// In en, this message translates to:
  /// **'In review'**
  String get statusInReview;

  /// No description provided for @statusNeedsInfo.
  ///
  /// In en, this message translates to:
  /// **'Needs your information'**
  String get statusNeedsInfo;

  /// No description provided for @statusDeclined.
  ///
  /// In en, this message translates to:
  /// **'Not proceeding'**
  String get statusDeclined;

  /// No description provided for @statusInProgress.
  ///
  /// In en, this message translates to:
  /// **'In progress'**
  String get statusInProgress;

  /// No description provided for @statusProposed.
  ///
  /// In en, this message translates to:
  /// **'Proposal created'**
  String get statusProposed;

  /// No description provided for @statusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get statusCompleted;

  /// No description provided for @statusClosed.
  ///
  /// In en, this message translates to:
  /// **'Closed'**
  String get statusClosed;

  /// No description provided for @issueDetailTitle.
  ///
  /// In en, this message translates to:
  /// **'Report #{id}'**
  String issueDetailTitle(int id);

  /// No description provided for @timelineSubmitted.
  ///
  /// In en, this message translates to:
  /// **'Report submitted'**
  String get timelineSubmitted;

  /// No description provided for @timelineTriagePending.
  ///
  /// In en, this message translates to:
  /// **'Waiting for staff review'**
  String get timelineTriagePending;

  /// No description provided for @timelineTriageDone.
  ///
  /// In en, this message translates to:
  /// **'Reviewed by staff'**
  String get timelineTriageDone;

  /// No description provided for @timelineCase.
  ///
  /// In en, this message translates to:
  /// **'Grouped into case: {category}'**
  String timelineCase(String category);

  /// No description provided for @timelineCaseNoCategory.
  ///
  /// In en, this message translates to:
  /// **'Grouped into a maintenance case'**
  String get timelineCaseNoCategory;

  /// No description provided for @categoryElevator.
  ///
  /// In en, this message translates to:
  /// **'Elevator'**
  String get categoryElevator;

  /// No description provided for @categoryWaterLeak.
  ///
  /// In en, this message translates to:
  /// **'Water leak'**
  String get categoryWaterLeak;

  /// No description provided for @categoryElectricalFault.
  ///
  /// In en, this message translates to:
  /// **'Electrical fault'**
  String get categoryElectricalFault;

  /// No description provided for @categoryHeatingCooling.
  ///
  /// In en, this message translates to:
  /// **'Heating / cooling'**
  String get categoryHeatingCooling;

  /// No description provided for @categoryLighting.
  ///
  /// In en, this message translates to:
  /// **'Lighting'**
  String get categoryLighting;

  /// No description provided for @categoryDoorLock.
  ///
  /// In en, this message translates to:
  /// **'Door / lock'**
  String get categoryDoorLock;

  /// No description provided for @categoryAppliance.
  ///
  /// In en, this message translates to:
  /// **'Appliance'**
  String get categoryAppliance;

  /// No description provided for @categoryStructural.
  ///
  /// In en, this message translates to:
  /// **'Structural'**
  String get categoryStructural;

  /// No description provided for @categoryCleanliness.
  ///
  /// In en, this message translates to:
  /// **'Cleanliness'**
  String get categoryCleanliness;

  /// No description provided for @categoryNoise.
  ///
  /// In en, this message translates to:
  /// **'Noise'**
  String get categoryNoise;

  /// No description provided for @categoryOther.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get categoryOther;

  /// No description provided for @timelineWork.
  ///
  /// In en, this message translates to:
  /// **'Work order {status}, deadline {deadline}'**
  String timelineWork(String status, String deadline);

  /// No description provided for @timelineCompleted.
  ///
  /// In en, this message translates to:
  /// **'Work completed'**
  String get timelineCompleted;

  /// No description provided for @progressTitle.
  ///
  /// In en, this message translates to:
  /// **'Work progress'**
  String get progressTitle;

  /// No description provided for @progressEmpty.
  ///
  /// In en, this message translates to:
  /// **'No progress updates yet.'**
  String get progressEmpty;

  /// No description provided for @progressCompleted.
  ///
  /// In en, this message translates to:
  /// **'Work completed'**
  String get progressCompleted;

  /// No description provided for @declinedTitle.
  ///
  /// In en, this message translates to:
  /// **'Management decided not to proceed'**
  String get declinedTitle;

  /// No description provided for @declinedCorrectedReportCta.
  ///
  /// In en, this message translates to:
  /// **'File a corrected report'**
  String get declinedCorrectedReportCta;

  /// No description provided for @rateWorkCta.
  ///
  /// In en, this message translates to:
  /// **'Rate this work'**
  String get rateWorkCta;

  /// No description provided for @rateWorkTitle.
  ///
  /// In en, this message translates to:
  /// **'How was the work?'**
  String get rateWorkTitle;

  /// No description provided for @rateSatisfied.
  ///
  /// In en, this message translates to:
  /// **'Satisfied'**
  String get rateSatisfied;

  /// No description provided for @rateNotSatisfied.
  ///
  /// In en, this message translates to:
  /// **'Not satisfied'**
  String get rateNotSatisfied;

  /// No description provided for @rateCommentLabel.
  ///
  /// In en, this message translates to:
  /// **'Comment (optional)'**
  String get rateCommentLabel;

  /// No description provided for @rateSubmit.
  ///
  /// In en, this message translates to:
  /// **'Send rating'**
  String get rateSubmit;

  /// No description provided for @rateThanks.
  ///
  /// In en, this message translates to:
  /// **'Thank you for your rating.'**
  String get rateThanks;

  /// No description provided for @infoRequestTitle.
  ///
  /// In en, this message translates to:
  /// **'Management needs more information'**
  String get infoRequestTitle;

  /// No description provided for @infoReplyHint.
  ///
  /// In en, this message translates to:
  /// **'Write your reply…'**
  String get infoReplyHint;

  /// No description provided for @infoReplySubmit.
  ///
  /// In en, this message translates to:
  /// **'Send reply'**
  String get infoReplySubmit;

  /// No description provided for @infoReplyPhotosHint.
  ///
  /// In en, this message translates to:
  /// **'You can also add photos from the photo section below.'**
  String get infoReplyPhotosHint;

  /// No description provided for @infoReplySavedPhotos.
  ///
  /// In en, this message translates to:
  /// **'Your reply was received. {uploaded}/{total} photos attached.'**
  String infoReplySavedPhotos(int uploaded, int total);

  /// No description provided for @infoReplyPhotosPending.
  ///
  /// In en, this message translates to:
  /// **'Your reply was received. Some photos did not upload — retry each photo below.'**
  String get infoReplyPhotosPending;

  /// No description provided for @infoReplyNotSent.
  ///
  /// In en, this message translates to:
  /// **'Nothing was sent yet. Your reply and photos are still here — try again.'**
  String get infoReplyNotSent;

  /// No description provided for @infoReplyPendingPhotosTitle.
  ///
  /// In en, this message translates to:
  /// **'Reply photos not yet uploaded — retry each photo.'**
  String get infoReplyPendingPhotosTitle;

  /// No description provided for @infoReplyClose.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get infoReplyClose;

  /// No description provided for @photoNofM.
  ///
  /// In en, this message translates to:
  /// **'Photo {n} of {m}'**
  String photoNofM(int n, int m);

  /// No description provided for @photoUploadFailed.
  ///
  /// In en, this message translates to:
  /// **'Not uploaded'**
  String get photoUploadFailed;

  /// No description provided for @photoLoading.
  ///
  /// In en, this message translates to:
  /// **'Loading photo…'**
  String get photoLoading;

  /// No description provided for @photoLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'The photo could not be loaded.'**
  String get photoLoadFailed;

  /// No description provided for @photoBeforeRepair.
  ///
  /// In en, this message translates to:
  /// **'Photo before the repair'**
  String get photoBeforeRepair;

  /// No description provided for @photoAfterRepair.
  ///
  /// In en, this message translates to:
  /// **'Photo after the repair'**
  String get photoAfterRepair;

  /// No description provided for @workStatusAssigned.
  ///
  /// In en, this message translates to:
  /// **'Assigned'**
  String get workStatusAssigned;

  /// No description provided for @workStatusInProgress.
  ///
  /// In en, this message translates to:
  /// **'In progress'**
  String get workStatusInProgress;

  /// No description provided for @workStatusAwaiting.
  ///
  /// In en, this message translates to:
  /// **'Awaiting acceptance'**
  String get workStatusAwaiting;

  /// No description provided for @workStatusAccepted.
  ///
  /// In en, this message translates to:
  /// **'Accepted'**
  String get workStatusAccepted;

  /// No description provided for @workStatusClosed.
  ///
  /// In en, this message translates to:
  /// **'Closed'**
  String get workStatusClosed;

  /// No description provided for @workStatusCancelled.
  ///
  /// In en, this message translates to:
  /// **'Cancelled'**
  String get workStatusCancelled;

  /// No description provided for @homeFundTitle.
  ///
  /// In en, this message translates to:
  /// **'Maintenance fund'**
  String get homeFundTitle;

  /// No description provided for @homeAnnouncementTitle.
  ///
  /// In en, this message translates to:
  /// **'Building announcement'**
  String get homeAnnouncementTitle;

  /// No description provided for @homeFundInflows.
  ///
  /// In en, this message translates to:
  /// **'In (30d)'**
  String get homeFundInflows;

  /// No description provided for @homeFundOutflows.
  ///
  /// In en, this message translates to:
  /// **'Out (30d)'**
  String get homeFundOutflows;

  /// No description provided for @homeFundChartCaption.
  ///
  /// In en, this message translates to:
  /// **'Fund balance · last 6 months'**
  String get homeFundChartCaption;

  /// No description provided for @homeActiveReports.
  ///
  /// In en, this message translates to:
  /// **'My open reports'**
  String get homeActiveReports;

  /// No description provided for @homeRecentSpending.
  ///
  /// In en, this message translates to:
  /// **'Recently published spending'**
  String get homeRecentSpending;

  /// No description provided for @homeNoActiveReports.
  ///
  /// In en, this message translates to:
  /// **'No open reports.'**
  String get homeNoActiveReports;

  /// No description provided for @homeNoSpending.
  ///
  /// In en, this message translates to:
  /// **'No published spending yet.'**
  String get homeNoSpending;

  /// No description provided for @homeReportsLoading.
  ///
  /// In en, this message translates to:
  /// **'Loading reports…'**
  String get homeReportsLoading;

  /// No description provided for @homeSpendingLoading.
  ///
  /// In en, this message translates to:
  /// **'Loading spending…'**
  String get homeSpendingLoading;

  /// No description provided for @notificationsTitle.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notificationsTitle;

  /// No description provided for @notificationsEmpty.
  ///
  /// In en, this message translates to:
  /// **'No notifications yet.'**
  String get notificationsEmpty;

  /// No description provided for @notificationsLoadMore.
  ///
  /// In en, this message translates to:
  /// **'Load more'**
  String get notificationsLoadMore;

  /// No description provided for @notificationsUnreadCount.
  ///
  /// In en, this message translates to:
  /// **'{n} unread notifications'**
  String notificationsUnreadCount(int n);

  /// No description provided for @notificationUnread.
  ///
  /// In en, this message translates to:
  /// **'Unread'**
  String get notificationUnread;

  /// No description provided for @notificationRead.
  ///
  /// In en, this message translates to:
  /// **'Read'**
  String get notificationRead;

  /// No description provided for @ledgerTitle.
  ///
  /// In en, this message translates to:
  /// **'Building ledger'**
  String get ledgerTitle;

  /// No description provided for @ledgerDetailTitle.
  ///
  /// In en, this message translates to:
  /// **'Expenditure details'**
  String get ledgerDetailTitle;

  /// No description provided for @ledgerEmpty.
  ///
  /// In en, this message translates to:
  /// **'No published spending for this period.'**
  String get ledgerEmpty;

  /// No description provided for @ledgerAllTime.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get ledgerAllTime;

  /// No description provided for @ledgerYearLabel.
  ///
  /// In en, this message translates to:
  /// **'Year'**
  String get ledgerYearLabel;

  /// No description provided for @ledgerMonthLabel.
  ///
  /// In en, this message translates to:
  /// **'Month'**
  String get ledgerMonthLabel;

  /// No description provided for @ledgerLoadMore.
  ///
  /// In en, this message translates to:
  /// **'Load more'**
  String get ledgerLoadMore;

  /// No description provided for @ledgerPublishedOn.
  ///
  /// In en, this message translates to:
  /// **'Published {date}'**
  String ledgerPublishedOn(String date);

  /// No description provided for @ledgerAmount.
  ///
  /// In en, this message translates to:
  /// **'Amount'**
  String get ledgerAmount;

  /// No description provided for @ledgerContractor.
  ///
  /// In en, this message translates to:
  /// **'Contractor'**
  String get ledgerContractor;

  /// No description provided for @ledgerWhatFixed.
  ///
  /// In en, this message translates to:
  /// **'What was fixed'**
  String get ledgerWhatFixed;

  /// No description provided for @ledgerWhy.
  ///
  /// In en, this message translates to:
  /// **'Why'**
  String get ledgerWhy;

  /// No description provided for @ledgerApprovers.
  ///
  /// In en, this message translates to:
  /// **'Approved by'**
  String get ledgerApprovers;

  /// No description provided for @ledgerApproverBoard.
  ///
  /// In en, this message translates to:
  /// **'Board: {name}'**
  String ledgerApproverBoard(String name);

  /// No description provided for @ledgerApproverRep.
  ///
  /// In en, this message translates to:
  /// **'Resident representative: {name}'**
  String ledgerApproverRep(String name);

  /// No description provided for @ledgerApproverEmergency.
  ///
  /// In en, this message translates to:
  /// **'Emergency authorization: {name}'**
  String ledgerApproverEmergency(String name);

  /// No description provided for @ledgerApproverGeneric.
  ///
  /// In en, this message translates to:
  /// **'{name}'**
  String ledgerApproverGeneric(String name);

  /// No description provided for @ledgerVerifiedBy.
  ///
  /// In en, this message translates to:
  /// **'Payment verified by {name}'**
  String ledgerVerifiedBy(String name);

  /// No description provided for @ledgerNotVerified.
  ///
  /// In en, this message translates to:
  /// **'Payment not yet verified'**
  String get ledgerNotVerified;

  /// No description provided for @ledgerConclusionVerified.
  ///
  /// In en, this message translates to:
  /// **'This expense has been verified'**
  String get ledgerConclusionVerified;

  /// No description provided for @ledgerConclusionVerifiedBody.
  ///
  /// In en, this message translates to:
  /// **'The transfer proof and record integrity were independently confirmed.'**
  String get ledgerConclusionVerifiedBody;

  /// No description provided for @ledgerConclusionUnverified.
  ///
  /// In en, this message translates to:
  /// **'This expense is not fully verified'**
  String get ledgerConclusionUnverified;

  /// No description provided for @ledgerConclusionUnverifiedBody.
  ///
  /// In en, this message translates to:
  /// **'The expense was published, but a verification step is incomplete. Review the accountability chain below.'**
  String get ledgerConclusionUnverifiedBody;

  /// No description provided for @ledgerConclusionMismatch.
  ///
  /// In en, this message translates to:
  /// **'This record does not match its anchored evidence'**
  String get ledgerConclusionMismatch;

  /// No description provided for @ledgerConclusionMismatchBody.
  ///
  /// In en, this message translates to:
  /// **'The published record differs from the evidence that was anchored for it. Report this expense to the management board.'**
  String get ledgerConclusionMismatchBody;

  /// No description provided for @ledgerChainTitle.
  ///
  /// In en, this message translates to:
  /// **'Accountability chain'**
  String get ledgerChainTitle;

  /// No description provided for @ledgerChainHint.
  ///
  /// In en, this message translates to:
  /// **'The expense moves from report to independent verification in the steps below.'**
  String get ledgerChainHint;

  /// No description provided for @ledgerChainReports.
  ///
  /// In en, this message translates to:
  /// **'Reports and rationale'**
  String get ledgerChainReports;

  /// No description provided for @ledgerChainWork.
  ///
  /// In en, this message translates to:
  /// **'Work completed'**
  String get ledgerChainWork;

  /// No description provided for @ledgerChainApprovals.
  ///
  /// In en, this message translates to:
  /// **'Approvals'**
  String get ledgerChainApprovals;

  /// No description provided for @ledgerChainPayment.
  ///
  /// In en, this message translates to:
  /// **'Transfer proof'**
  String get ledgerChainPayment;

  /// No description provided for @ledgerChainVerification.
  ///
  /// In en, this message translates to:
  /// **'Independent verification'**
  String get ledgerChainVerification;

  /// No description provided for @ledgerCorrections.
  ///
  /// In en, this message translates to:
  /// **'Corrections'**
  String get ledgerCorrections;

  /// No description provided for @ledgerCorrectionRecorded.
  ///
  /// In en, this message translates to:
  /// **'Adjustment recorded'**
  String get ledgerCorrectionRecorded;

  /// No description provided for @ledgerDocuments.
  ///
  /// In en, this message translates to:
  /// **'Documents'**
  String get ledgerDocuments;

  /// No description provided for @ledgerDocumentOpen.
  ///
  /// In en, this message translates to:
  /// **'Preview or download'**
  String get ledgerDocumentOpen;

  /// No description provided for @ledgerDocumentOffline.
  ///
  /// In en, this message translates to:
  /// **'You are offline. The document was not downloaded. Reconnect and try again.'**
  String get ledgerDocumentOffline;

  /// No description provided for @ledgerDocumentUnauthorized.
  ///
  /// In en, this message translates to:
  /// **'You are not authorized to open this document. No file was downloaded.'**
  String get ledgerDocumentUnauthorized;

  /// No description provided for @ledgerDocumentFailure.
  ///
  /// In en, this message translates to:
  /// **'The document could not be opened. No file was downloaded; please try again.'**
  String get ledgerDocumentFailure;

  /// No description provided for @documentShare.
  ///
  /// In en, this message translates to:
  /// **'Share or save'**
  String get documentShare;

  /// No description provided for @documentShareFailed.
  ///
  /// In en, this message translates to:
  /// **'The file could not be shared. The document is still open — try again.'**
  String get documentShareFailed;

  /// No description provided for @documentNoPreview.
  ///
  /// In en, this message translates to:
  /// **'This file cannot be previewed here. Share it to open it in another app.'**
  String get documentNoPreview;

  /// No description provided for @ledgerProofTitle.
  ///
  /// In en, this message translates to:
  /// **'Verification details'**
  String get ledgerProofTitle;

  /// No description provided for @ledgerProofHash.
  ///
  /// In en, this message translates to:
  /// **'Record hash'**
  String get ledgerProofHash;

  /// No description provided for @ledgerProofEvents.
  ///
  /// In en, this message translates to:
  /// **'Signed events'**
  String get ledgerProofEvents;

  /// No description provided for @evidenceExplorer.
  ///
  /// In en, this message translates to:
  /// **'Evidence explorer'**
  String get evidenceExplorer;

  /// No description provided for @evidenceChain.
  ///
  /// In en, this message translates to:
  /// **'Anchored on the blockchain'**
  String get evidenceChain;

  /// No description provided for @evidenceLocal.
  ///
  /// In en, this message translates to:
  /// **'Signed — blockchain anchoring off'**
  String get evidenceLocal;

  /// No description provided for @evidencePending.
  ///
  /// In en, this message translates to:
  /// **'Waiting for blockchain anchoring'**
  String get evidencePending;

  /// No description provided for @evidenceMismatch.
  ///
  /// In en, this message translates to:
  /// **'Data mismatch detected'**
  String get evidenceMismatch;

  /// No description provided for @integrityVerified.
  ///
  /// In en, this message translates to:
  /// **'Record verified'**
  String get integrityVerified;

  /// No description provided for @integrityMismatch.
  ///
  /// In en, this message translates to:
  /// **'Integrity mismatch detected'**
  String get integrityMismatch;

  /// No description provided for @integrityUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Integrity check unavailable'**
  String get integrityUnavailable;

  /// No description provided for @integrityUnchecked.
  ///
  /// In en, this message translates to:
  /// **'Published — integrity not yet checked'**
  String get integrityUnchecked;

  /// No description provided for @accountOccupancies.
  ///
  /// In en, this message translates to:
  /// **'My homes'**
  String get accountOccupancies;

  /// No description provided for @accountPreferences.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get accountPreferences;

  /// No description provided for @accountPrefAll.
  ///
  /// In en, this message translates to:
  /// **'Receive all notifications'**
  String get accountPrefAll;

  /// No description provided for @accountSignOutAll.
  ///
  /// In en, this message translates to:
  /// **'Sign out of all devices'**
  String get accountSignOutAll;

  /// No description provided for @signOutUnsentWorkWarning.
  ///
  /// In en, this message translates to:
  /// **'The report you are drafting and any unsent photos on this device will be deleted.'**
  String get signOutUnsentWorkWarning;

  /// No description provided for @commonCancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get commonCancel;

  /// No description provided for @gateAccountAction.
  ///
  /// In en, this message translates to:
  /// **'Register plate and face'**
  String get gateAccountAction;

  /// No description provided for @gateRegistrationTitle.
  ///
  /// In en, this message translates to:
  /// **'Gate registration'**
  String get gateRegistrationTitle;

  /// No description provided for @gatePlateLabel.
  ///
  /// In en, this message translates to:
  /// **'License plate'**
  String get gatePlateLabel;

  /// No description provided for @gateSubmitPlate.
  ///
  /// In en, this message translates to:
  /// **'Submit plate for approval'**
  String get gateSubmitPlate;

  /// No description provided for @gateRevokePlate.
  ///
  /// In en, this message translates to:
  /// **'Revoke plate'**
  String get gateRevokePlate;

  /// No description provided for @gateFaceTitle.
  ///
  /// In en, this message translates to:
  /// **'Face'**
  String get gateFaceTitle;

  /// No description provided for @gateNotRegistered.
  ///
  /// In en, this message translates to:
  /// **'Not registered'**
  String get gateNotRegistered;

  /// No description provided for @gateCaptureFace.
  ///
  /// In en, this message translates to:
  /// **'Take registration photo'**
  String get gateCaptureFace;

  /// No description provided for @gateRevokeFace.
  ///
  /// In en, this message translates to:
  /// **'Revoke face'**
  String get gateRevokeFace;

  /// No description provided for @gateRetentionNotice.
  ///
  /// In en, this message translates to:
  /// **'The photo is retained only for management review and deleted after a decision.'**
  String get gateRetentionNotice;

  /// No description provided for @gateRevokeConfirmBody.
  ///
  /// In en, this message translates to:
  /// **'This information will no longer be used for gate recognition.'**
  String get gateRevokeConfirmBody;

  /// No description provided for @gateRevokeConfirm.
  ///
  /// In en, this message translates to:
  /// **'Revoke'**
  String get gateRevokeConfirm;

  /// No description provided for @gateStatusPending.
  ///
  /// In en, this message translates to:
  /// **'Awaiting approval'**
  String get gateStatusPending;

  /// No description provided for @gateStatusApproved.
  ///
  /// In en, this message translates to:
  /// **'Approved'**
  String get gateStatusApproved;

  /// No description provided for @gateStatusRejected.
  ///
  /// In en, this message translates to:
  /// **'Rejected: {note}'**
  String gateStatusRejected(String note);

  /// No description provided for @gateStatusExpired.
  ///
  /// In en, this message translates to:
  /// **'Photo expired; please submit another'**
  String get gateStatusExpired;

  /// No description provided for @gateStatusUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown status'**
  String get gateStatusUnknown;

  /// No description provided for @gateErrorNoFace.
  ///
  /// In en, this message translates to:
  /// **'No face found. Take another photo.'**
  String get gateErrorNoFace;

  /// No description provided for @gateErrorMultipleFaces.
  ///
  /// In en, this message translates to:
  /// **'The photo must contain one face only.'**
  String get gateErrorMultipleFaces;

  /// No description provided for @gateErrorFaceTooSmall.
  ///
  /// In en, this message translates to:
  /// **'The face is too small. Move closer.'**
  String get gateErrorFaceTooSmall;

  /// No description provided for @gateErrorFaceTooBlurry.
  ///
  /// In en, this message translates to:
  /// **'The photo is too blurry. Take another.'**
  String get gateErrorFaceTooBlurry;

  /// No description provided for @gateErrorFaceUnusable.
  ///
  /// In en, this message translates to:
  /// **'The photo cannot be used for face registration.'**
  String get gateErrorFaceUnusable;

  /// No description provided for @gateErrorPhotoRejected.
  ///
  /// In en, this message translates to:
  /// **'The photo was rejected before processing.'**
  String get gateErrorPhotoRejected;

  /// No description provided for @gateErrorPhotoTooLarge.
  ///
  /// In en, this message translates to:
  /// **'The photo exceeds the size limit.'**
  String get gateErrorPhotoTooLarge;

  /// No description provided for @gateErrorPlateRegistered.
  ///
  /// In en, this message translates to:
  /// **'This plate is already registered. Contact management.'**
  String get gateErrorPlateRegistered;

  /// No description provided for @gateErrorUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Recognition is temporarily unavailable. Try again later.'**
  String get gateErrorUnavailable;

  /// No description provided for @gateReaderTitle.
  ///
  /// In en, this message translates to:
  /// **'Gate reader'**
  String get gateReaderTitle;

  /// No description provided for @gateReaderServer.
  ///
  /// In en, this message translates to:
  /// **'Server address'**
  String get gateReaderServer;

  /// No description provided for @gateReaderCredential.
  ///
  /// In en, this message translates to:
  /// **'Device credential'**
  String get gateReaderCredential;

  /// No description provided for @gateReaderActivate.
  ///
  /// In en, this message translates to:
  /// **'Activate reader'**
  String get gateReaderActivate;

  /// No description provided for @gateReaderInvalidUrl.
  ///
  /// In en, this message translates to:
  /// **'The server URL is invalid. Start it with https:// or http://.'**
  String get gateReaderInvalidUrl;

  /// No description provided for @gateReaderPlateUnreadable.
  ///
  /// In en, this message translates to:
  /// **'The plate could not be read. Try again.'**
  String get gateReaderPlateUnreadable;

  /// No description provided for @gateReaderUnit.
  ///
  /// In en, this message translates to:
  /// **'Unit {unit}'**
  String gateReaderUnit(String unit);

  /// No description provided for @gateReaderNoMatch.
  ///
  /// In en, this message translates to:
  /// **'No match found'**
  String get gateReaderNoMatch;

  /// No description provided for @gateReaderScanPlate.
  ///
  /// In en, this message translates to:
  /// **'Scan plate'**
  String get gateReaderScanPlate;

  /// No description provided for @gateReaderScanFace.
  ///
  /// In en, this message translates to:
  /// **'Scan face'**
  String get gateReaderScanFace;

  /// No description provided for @gateReaderClearDevice.
  ///
  /// In en, this message translates to:
  /// **'Clear device credential'**
  String get gateReaderClearDevice;

  /// No description provided for @gateReaderDeviceRevoked.
  ///
  /// In en, this message translates to:
  /// **'The device credential was revoked.'**
  String get gateReaderDeviceRevoked;

  /// No description provided for @gateReaderDeviceExpired.
  ///
  /// In en, this message translates to:
  /// **'The device credential expired.'**
  String get gateReaderDeviceExpired;

  /// No description provided for @gateReaderDeviceInvalid.
  ///
  /// In en, this message translates to:
  /// **'The device credential is invalid.'**
  String get gateReaderDeviceInvalid;

  /// No description provided for @gateReaderThrottled.
  ///
  /// In en, this message translates to:
  /// **'Actions are too frequent. Please wait.'**
  String get gateReaderThrottled;

  /// No description provided for @fundChartTitle.
  ///
  /// In en, this message translates to:
  /// **'Fund balance'**
  String get fundChartTitle;

  /// No description provided for @fundChartFlowsTitle.
  ///
  /// In en, this message translates to:
  /// **'Inflows and outflows'**
  String get fundChartFlowsTitle;

  /// No description provided for @fundChartSemantics.
  ///
  /// In en, this message translates to:
  /// **'Fund balance chart'**
  String get fundChartSemantics;

  /// No description provided for @fundChartBalanceValue.
  ///
  /// In en, this message translates to:
  /// **'balance {amount}'**
  String fundChartBalanceValue(String amount);

  /// No description provided for @fundChartInflowValue.
  ///
  /// In en, this message translates to:
  /// **'inflow {amount}'**
  String fundChartInflowValue(String amount);

  /// No description provided for @fundChartOutflowValue.
  ///
  /// In en, this message translates to:
  /// **'outflow {amount}'**
  String fundChartOutflowValue(String amount);

  /// No description provided for @fundChartInflowLabel.
  ///
  /// In en, this message translates to:
  /// **'Inflows'**
  String get fundChartInflowLabel;

  /// No description provided for @fundChartOutflowLabel.
  ///
  /// In en, this message translates to:
  /// **'Outflows'**
  String get fundChartOutflowLabel;

  /// No description provided for @fundChartRange30d.
  ///
  /// In en, this message translates to:
  /// **'30 days'**
  String get fundChartRange30d;

  /// No description provided for @fundChartRange6m.
  ///
  /// In en, this message translates to:
  /// **'6 months'**
  String get fundChartRange6m;

  /// No description provided for @fundChartRange12m.
  ///
  /// In en, this message translates to:
  /// **'12 months'**
  String get fundChartRange12m;

  /// No description provided for @proposalsSegment.
  ///
  /// In en, this message translates to:
  /// **'Proposals'**
  String get proposalsSegment;

  /// No description provided for @ledgerSegment.
  ///
  /// In en, this message translates to:
  /// **'Ledger'**
  String get ledgerSegment;

  /// No description provided for @proposalStatusPublished.
  ///
  /// In en, this message translates to:
  /// **'Published'**
  String get proposalStatusPublished;

  /// No description provided for @proposalStatusInProgress.
  ///
  /// In en, this message translates to:
  /// **'In progress'**
  String get proposalStatusInProgress;

  /// No description provided for @proposalStatusNotProceeding.
  ///
  /// In en, this message translates to:
  /// **'Not proceeding'**
  String get proposalStatusNotProceeding;

  /// No description provided for @proposalStatusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get proposalStatusCompleted;

  /// No description provided for @proposalStatusClosed.
  ///
  /// In en, this message translates to:
  /// **'Closed'**
  String get proposalStatusClosed;

  /// No description provided for @proposalStatusDraft.
  ///
  /// In en, this message translates to:
  /// **'Draft'**
  String get proposalStatusDraft;

  /// No description provided for @proposalProblem.
  ///
  /// In en, this message translates to:
  /// **'Problem or need'**
  String get proposalProblem;

  /// No description provided for @proposalAction.
  ///
  /// In en, this message translates to:
  /// **'Proposed action'**
  String get proposalAction;

  /// No description provided for @proposalCost.
  ///
  /// In en, this message translates to:
  /// **'Estimated cost'**
  String get proposalCost;

  /// No description provided for @proposalContractor.
  ///
  /// In en, this message translates to:
  /// **'Contractor'**
  String get proposalContractor;

  /// No description provided for @proposalSchedule.
  ///
  /// In en, this message translates to:
  /// **'Expected schedule'**
  String get proposalSchedule;

  /// No description provided for @proposalVersions.
  ///
  /// In en, this message translates to:
  /// **'Published versions'**
  String get proposalVersions;

  /// No description provided for @proposalVersion.
  ///
  /// In en, this message translates to:
  /// **'Version {number}'**
  String proposalVersion(String number);

  /// No description provided for @proposalSettlement.
  ///
  /// In en, this message translates to:
  /// **'Payment settlement'**
  String get proposalSettlement;

  /// No description provided for @proposalSettled.
  ///
  /// In en, this message translates to:
  /// **'Paid'**
  String get proposalSettled;

  /// No description provided for @proposalViewFromLedger.
  ///
  /// In en, this message translates to:
  /// **'View proposal'**
  String get proposalViewFromLedger;

  /// No description provided for @proposalRateCta.
  ///
  /// In en, this message translates to:
  /// **'Rate the result'**
  String get proposalRateCta;

  /// No description provided for @homeBillTitle.
  ///
  /// In en, this message translates to:
  /// **'Building bill'**
  String get homeBillTitle;

  /// No description provided for @homeBillLoading.
  ///
  /// In en, this message translates to:
  /// **'Loading building bill…'**
  String get homeBillLoading;

  /// No description provided for @billsTitle.
  ///
  /// In en, this message translates to:
  /// **'Bills'**
  String get billsTitle;

  /// No description provided for @billAmountLabel.
  ///
  /// In en, this message translates to:
  /// **'Amount'**
  String get billAmountLabel;

  /// No description provided for @billDueLabel.
  ///
  /// In en, this message translates to:
  /// **'Due'**
  String get billDueLabel;

  /// No description provided for @billOverdue.
  ///
  /// In en, this message translates to:
  /// **'Overdue'**
  String get billOverdue;

  /// No description provided for @billViewFile.
  ///
  /// In en, this message translates to:
  /// **'View bill'**
  String get billViewFile;

  /// No description provided for @billPayAction.
  ///
  /// In en, this message translates to:
  /// **'I\'ve paid'**
  String get billPayAction;

  /// No description provided for @billPayExplainer.
  ///
  /// In en, this message translates to:
  /// **'Scanning records a transfer you already made — it does not pay the bill.'**
  String get billPayExplainer;

  /// No description provided for @billPayStep1.
  ///
  /// In en, this message translates to:
  /// **'1. Transfer the amount in your banking app.'**
  String get billPayStep1;

  /// No description provided for @billPayStep2.
  ///
  /// In en, this message translates to:
  /// **'2. Come back here and scan the QR on the bill to record it.'**
  String get billPayStep2;

  /// No description provided for @billStatusIssued.
  ///
  /// In en, this message translates to:
  /// **'Unpaid'**
  String get billStatusIssued;

  /// No description provided for @billStatusPaid.
  ///
  /// In en, this message translates to:
  /// **'Payment recorded'**
  String get billStatusPaid;

  /// No description provided for @billStatusVoid.
  ///
  /// In en, this message translates to:
  /// **'Voided'**
  String get billStatusVoid;

  /// No description provided for @billScanTitle.
  ///
  /// In en, this message translates to:
  /// **'Scan payment QR'**
  String get billScanTitle;

  /// No description provided for @billScanInstruction.
  ///
  /// In en, this message translates to:
  /// **'Point the camera at the bill QR to record your payment.'**
  String get billScanInstruction;

  /// No description provided for @billInvalidQr.
  ///
  /// In en, this message translates to:
  /// **'That QR code is not a Làm Tổ bill.'**
  String get billInvalidQr;

  /// No description provided for @billPaymentRecorded.
  ///
  /// In en, this message translates to:
  /// **'Payment recorded'**
  String get billPaymentRecorded;

  /// No description provided for @billPaymentVoided.
  ///
  /// In en, this message translates to:
  /// **'This bill was voided. No payment was recorded.'**
  String get billPaymentVoided;

  /// No description provided for @billPaymentUnknown.
  ///
  /// In en, this message translates to:
  /// **'We could not confirm whether the payment was recorded. Check the bill status before trying again.'**
  String get billPaymentUnknown;

  /// No description provided for @billCameraUnavailable.
  ///
  /// In en, this message translates to:
  /// **'The camera is unavailable. Allow camera access in device settings, then try again.'**
  String get billCameraUnavailable;

  /// No description provided for @billNone.
  ///
  /// In en, this message translates to:
  /// **'No bills.'**
  String get billNone;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'vi'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'vi':
      return AppLocalizationsVi();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
