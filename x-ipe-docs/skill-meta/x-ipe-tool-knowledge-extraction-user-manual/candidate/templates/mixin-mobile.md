# User Manual — Mobile App Mixin

> Additional sections and extraction prompts for mobile applications.
> Merge these into the base playbook and collection templates when `app_type: mobile`.

---

## Additional Sections

### A. App Store Installation

**Playbook addition** (replace Section 2 — Installation & Setup with mobile-oriented structure):

- **App Store Links** — iOS App Store and Google Play Store URLs
- **Supported Devices** — Minimum OS versions, device compatibility
- **Storage Requirements** — App size, data storage needs
- **Update Policy** — Auto-update behavior, how to check for updates

<!-- EXTRACTION PROMPTS:
- Where can the app be downloaded? (look for store links, distribution config, fastlane metadata)
- What are the minimum OS requirements? (look for minSdkVersion, MinimumOSVersion, deployment target)
- What is the app size? (look for app bundle size, release notes)
- How are updates distributed? (look for update mechanism, OTA updates, store release process)
-->

### B. Permissions

**Playbook addition** (insert into Section 2 — Installation & Setup):

- **Required Permissions** — Permissions the app needs to function (camera, location, storage)
- **Optional Permissions** — Permissions for enhanced features
- **Permission Rationale** — Why each permission is needed
- **Managing Permissions** — How to grant/revoke permissions in device settings

<!-- EXTRACTION PROMPTS:
- What permissions does the app request? (look for AndroidManifest.xml permissions, Info.plist usage descriptions, NSUsageDescription keys)
- Why are permissions needed? (look for permission rationale strings, usage descriptions)
- Are there runtime permission requests? (look for permission request dialogs, permission handling code)
-->

### C. Touch Gestures & Navigation

**Playbook addition** (insert into Section 4 — Core Features as first subsection):

- **Gesture Guide** — Tap, swipe, pinch-zoom, long-press behaviors
- **Navigation Pattern** — Tab bar, drawer, stack navigation structure
- **Pull-to-Refresh** — Where and how pull-to-refresh works
- **Back Navigation** — Hardware back button behavior (Android), swipe-back (iOS)

<!-- EXTRACTION PROMPTS:
- What gestures does the app support? (look for gesture handlers, GestureDetector, UIGestureRecognizer)
- What is the navigation structure? (look for navigation config, tab bar setup, drawer navigator)
- Are there custom gestures? (look for custom gesture implementations, gesture tutorials in docs)
-->

### D. Offline Mode

**Playbook addition** (insert after Section 4 — Core Features):

- **Offline Capabilities** — What works without internet
- **Data Sync** — How data syncs when connectivity resumes
- **Storage Limits** — How much offline data can be stored
- **Offline Indicators** — How the app communicates offline status

<!-- EXTRACTION PROMPTS:
- Does the app work offline? (look for offline mode, cache strategy, local database, SQLite/Realm/CoreData usage)
- How does data sync? (look for sync logic, conflict resolution, queue-based sync)
- Are there offline indicators? (look for connectivity listeners, network status UI)
-->

### E. Push Notifications

**Playbook addition** (insert into Section 5 — Configuration):

- **Notification Types** — What notifications the app can send
- **Notification Settings** — How to customize notification preferences in-app
- **Quiet Hours** — Do Not Disturb or scheduled quiet time
- **Device Settings** — How to manage notifications in OS settings

<!-- EXTRACTION PROMPTS:
- Does the app send push notifications? (look for FCM/APNs config, notification services, push token handling)
- What notification types exist? (look for notification channels, notification categories)
- Can users customize notifications? (look for notification preferences UI, settings screen)
-->

---

## Section Overlay Prompts

These prompts augment the base collection template when `app_type: mobile`:

### For Section 3 (Getting Started)
<!-- ADDITIONAL PROMPTS:
- What does the onboarding flow look like? (look for onboarding screens, tutorial overlays, walkthrough)
- Is account creation required? (look for login-required flags, guest mode)
-->

### For Section 5 (Configuration)
<!-- ADDITIONAL PROMPTS:
- Where are in-app settings? (look for settings screen, preferences activity/view controller)
- What biometric authentication options exist? (look for fingerprint, face ID, biometric config)
-->

### For Section 6 (Troubleshooting)
<!-- ADDITIONAL PROMPTS:
- How to clear app cache? (look for cache clearing option in settings)
- Force close and restart steps?
- How to report a bug from within the app? (look for feedback/bug report feature)
-->
