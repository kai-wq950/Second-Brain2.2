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

### Incredibly detailed, step-by-step GitHub Actions flow
1. **Confirm Actions is enabled**
   - Open the GitHub repository in a browser and click the **Actions** tab. If you see a message that Actions is disabled for the fork/org, enable it or ask an admin to do so.

2. **Locate the workflow**
   - In the Actions tab, find the left sidebar list of workflows and click **Build APK** (this repository already contains `.github/workflows/build-apk.yml`).

3. **Trigger a manual run** (if you don’t want to wait for the next push)
   - Click the **Run workflow** dropdown on the right.
   - In the branch selector, pick the branch you want to build (defaults to `main`).
   - Click the green **Run workflow** button to start the job.
   - If you do not see the button, ensure you are signed in and have write access or Actions permissions for the repo/fork.

4. **Let the workflow fetch dependencies**
   - The run will start with the **Checkout** step, then install **JDK 17**, **Android SDK API 34**, and **Build Tools 34.0.0**.
   - It automatically accepts Android licenses and restores the Gradle cache to speed up builds. No manual input is needed.

5. **Watch the build and confirm success**
   - Open the running workflow (it appears in the history list immediately). You’ll see steps like **Build debug APK** using Gradle 8.2.1.
   - Wait until the job shows a green checkmark. If it fails, expand the failed step to read the log; typical fixes include re-running after transient network hiccups or ensuring the branch actually exists.

6. **Download the APK artifact**
   - Scroll to the bottom of the successful run page to the **Artifacts** section.
   - Click **NothingMotivate-debug-apk** to download a zip file that contains `app/build/outputs/apk/debug/app-debug.apk`.

7. **Extract and install**
   - Unzip the downloaded artifact on your machine.
   - The file `app-debug.apk` is inside the zip; copy or send it to your Android device and install it (enable "Install unknown apps" on the device if prompted).

8. **Repeat builds as needed**
   - Every push to `main` automatically triggers the same workflow. You can re-run any previous workflow run via the **Re-run jobs** button on the run page to regenerate a fresh artifact without pushing new commits.

> Note: The current container cannot download the Android Gradle Plugin from the internet, so the APK cannot be generated here. Download the artifact from Actions or build on a networked machine.
