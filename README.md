# NothingMotivate build guide

This project is an Android app inspired by the Nothing Essential aesthetic.

## Build an APK locally
1. Install the Android SDK and set `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) so Gradle can find platform tools.
2. Ensure Java 17+ is available on your PATH.
3. From the repo root, run `./gradlew assembleDebug` (or `assembleRelease` with your own keystore) to build the app.
4. The resulting APK will be at `app/build/outputs/apk/debug/app-debug.apk`.

## Get an APK from GitHub Actions
If you cannot or prefer not to build locally, use the `Build APK` workflow in GitHub Actions (it also runs on every push to `main`). The workflow:
- Sets up JDK 17 and the Android SDK (API 34, Build Tools 34.0.0).
- Uses Gradle 8.2.1 to run `assembleDebug`.
- Publishes `app/build/outputs/apk/debug/app-debug.apk` as a downloadable artifact named `NothingMotivate-debug-apk`.

### Trigger the workflow and download the APK
1. Go to **Actions → Build APK** in your GitHub repo.
2. Click **Run workflow** (choose the branch if prompted) and start the run, or wait for the latest run on `main` to finish.
3. Open the run, scroll to **Artifacts**, and download **NothingMotivate-debug-apk**.
4. Unzip the download; the APK file will be inside.

> Note: The current container cannot download the Android Gradle Plugin from the internet, so the APK cannot be generated here. Download the artifact from Actions or build on a networked machine.
