# Windows Package Manager (WinGet) Distribution Guide

This guide explains how Holy Bible (வேதம்) is published to Microsoft's official Windows Package Manager repository (`microsoft/winget-pkgs`).

---

## 🎯 Package Details

- **Package Identifier**: `ElroiTheCreator.HolyBible`
- **Package Name**: `Holy Bible - வேதம்`
- **Publisher**: `Elroi-thecreator`
- **Installer Type**: `portable` (standalone single-file executable)
- **Command Alias**: `holybible` (users can launch the app from Command Prompt or PowerShell by running `holybible`)

---

## 🚀 How Releases Work

### 1. Automated via Git Tag (Recommended)
When you are ready to publish a new version, simply create and push a git tag:

```cmd
git tag v1.0.0
git push origin v1.0.0
```

The GitHub Actions workflow (`.github/workflows/release_windows.yml`) will automatically:
1. Spin up a clean `windows-latest` virtual machine.
2. Compile `HolyBible-Portable.exe` using PyInstaller.
3. Compute the SHA256 checksum.
4. Generate the official 3-file WinGet manifest package (`.yaml`).
5. Publish a new GitHub Release with the executable and checksum attached.
6. Submit a pull request to `microsoft/winget-pkgs` (if `WINGET_TOKEN` is configured).

---

### 2. Manual Trigger via GitHub Actions UI
You can also trigger a release manually anytime from GitHub:
1. Navigate to your repository on GitHub.
2. Go to the **Actions** tab.
3. Click on **Release Windows Portable App & WinGet Package** in the left sidebar.
4. Click **Run workflow**, enter the version tag (e.g. `v1.0.0`), and submit.

---

## 🔑 Setting up Automatic WinGet PR Submission (`WINGET_TOKEN`)

Microsoft's `winget-pkgs` repository accepts automated submission pull requests via GitHub Actions.

To enable hands-free auto-submission:
1. Go to your GitHub profile: **Settings -> Developer Settings -> Personal access tokens -> Tokens (classic)**.
2. Click **Generate new token (classic)**:
   - Note: `WinGet Releaser Token`
   - Expiration: Choose desired duration (e.g. 90 days or No expiration)
   - Scope: Check **`public_repo`** (or `repo`)
3. Copy the generated token.
4. Go to your repository: **Settings -> Secrets and variables -> Actions**.
5. Click **New repository secret**:
   - Name: `WINGET_TOKEN`
   - Secret: Paste your token.
6. Click **Add secret**.

Once added, every new release tag will automatically open a submission PR to `microsoft/winget-pkgs` without any manual effort!

---

## 🧪 Testing Manifests Locally

You can test-install your compiled package on your local machine using the generated manifests before pushing:

```powershell
# 1. Generate local manifests
py -3 windows_app/generate_winget_manifest.py --version 1.0.0

# 2. Test-install via WinGet
winget install --manifest windows_app/dist/winget_manifests/manifests/e/ElroiTheCreator/HolyBible/1.0.0/ElroiTheCreator.HolyBible.yaml
```

---

## 🛠️ Alternative: Manual Submission via `wingetcreate` CLI

If you prefer submitting manually using Microsoft's official Windows Package Manager Manifest Creator tool (`wingetcreate`):

1. Install `wingetcreate`:
   ```cmd
   winget install Microsoft.WingetCreate
   ```
2. Submit your GitHub release URL:
   ```cmd
   wingetcreate new https://github.com/Elroi-thecreator/bibleweb/releases/download/v1.0.0/HolyBible-Portable.exe
   ```
3. Follow the interactive prompts to submit directly to `microsoft/winget-pkgs`.
