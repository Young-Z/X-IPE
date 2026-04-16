# User Manual — Mobile App Mixin

> Additional sections and extraction patterns for mobile applications.
> The `provide_framework` operation merges these into the base playbook when `app_type: mobile`.

---

## Additional Sections

### A. App Store Installation

**Replace Section 2 — Installation & Setup with mobile-oriented structure.**

- **App Store Links** — iOS App Store and Google Play Store URLs
- **Supported Devices** — Minimum OS versions, device compatibility
- **Storage Requirements** — App size, data storage needs
- **Update Policy** — Auto-update behavior, how to check for updates

**Knowledge request patterns (for request_knowledge):**
- "Find app download locations from store links, distribution config, fastlane metadata"
- "Extract minimum OS requirements from minSdkVersion, MinimumOSVersion, deployment target"
- "Find app size from app bundle size, release notes"
- "Extract update mechanism from OTA updates, store release process"

### B. Permissions

**Insert into Section 2 — Installation & Setup.**

- **Required Permissions** — Permissions the app needs to function (camera, location, storage)
- **Optional Permissions** — Permissions for enhanced features
- **Permission Rationale** — Why each permission is needed
- **Managing Permissions** — How to grant/revoke permissions in device settings

**Knowledge request patterns:**
- "Extract app permissions from AndroidManifest.xml, Info.plist NSUsageDescription keys"
- "Find permission rationale from usage descriptions, permission handling code"
- "Check for runtime permission requests from permission dialogs"

### C. Touch Gestures & Navigation

**Insert into Section 4 — Core Features as first subsection.**

- **Gesture Guide** — Tap, swipe, pinch-zoom, long-press behaviors
- **Navigation Pattern** — Tab bar, drawer, stack navigation structure
- **Pull-to-Refresh** — Where and how pull-to-refresh works
- **Back Navigation** — Hardware back button behavior (Android), swipe-back (iOS)

**Knowledge request patterns:**
- "Extract gesture support from gesture handlers, GestureDetector, UIGestureRecognizer"
- "Find navigation structure from navigation config, tab bar setup, drawer navigator"
- "Check for custom gestures from custom gesture implementations"

### D. Offline Mode

**Insert after Section 4 — Core Features.**

- **Offline Capabilities** — What works without internet
- **Data Sync** — How data syncs when connectivity resumes
- **Storage Limits** — How much offline data can be stored
- **Offline Indicators** — How the app communicates offline status

**Knowledge request patterns:**
- "Check offline support from cache strategy, local database, SQLite/Realm/CoreData usage"
- "Extract sync logic from conflict resolution, queue-based sync"
- "Find offline indicators from connectivity listeners, network status UI"

### E. Push Notifications

**Insert into Section 6 — Configuration.**

- **Notification Types** — What notifications the app can send
- **Notification Settings** — How to customize notification preferences in-app
- **Quiet Hours** — Do Not Disturb or scheduled quiet time
- **Device Settings** — How to manage notifications in OS settings

**Knowledge request patterns:**
- "Check push notification support from FCM/APNs config, push token handling"
- "Extract notification types from notification channels, notification categories"
- "Find notification preferences from settings screen, preferences UI"

---

## Section Overlay Patterns

These augment the base collection template when `app_type: mobile`:

### For Section 3 (Getting Started)
- "Describe onboarding flow from onboarding screens, tutorial overlays, walkthrough"
- "Check if account creation is required from login-required flags, guest mode"

### For Section 6 (Configuration)
- "Find in-app settings from settings screen, preferences activity/view controller"
- "Check biometric authentication options from fingerprint, face ID config"

### For Section 7 (Troubleshooting)
- "Document how to clear app cache from cache clearing option in settings"
- "Describe force close and restart steps"
- "Find in-app bug report feature from feedback/bug report button"
