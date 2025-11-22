# NothingMotivate build guide

This project is an Android app inspired by the Nothing Essential aesthetic. To produce an APK locally:

1. Install the Android SDK and set `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) so Gradle can find platform tools.
2. Ensure Java 17+ is available on your PATH.
3. From the repo root, run `gradle assembleDebug` (or `assembleRelease` with your own keystore) to build the app.
4. The resulting APK will be at `app/build/outputs/apk/debug/app-debug.apk`.

## Get an APK from GitHub Actions

If you cannot or prefer not to build locally, trigger the `Build APK` workflow in GitHub Actions (it runs on every push to `main` too). The workflow:

- Sets up JDK 17 and the Android SDK (API 34, Build Tools 34.0.0).
- Uses Gradle 8.2.1 to run `assembleDebug`.
- Publishes `app/build/outputs/apk/debug/app-debug.apk` as a downloadable artifact named `NothingMotivate-debug-apk`.

> Note: The current container cannot download the Android Gradle Plugin from the internet, so the APK cannot be generated here. Download the artifact from Actions or build on a networked machine.
