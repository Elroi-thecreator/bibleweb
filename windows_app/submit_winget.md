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

## ⚠️ Important: First-Time Package Submission (v1.0.0)

> Automated CI/CD tools (like `Komac`) are **package updaters**. Microsoft requires any brand-new package identifier (like `ElroiTheCreator.HolyBible`) to be added to `microsoft/winget-pkgs` for the first time via a standard pull request.
> 
> **Once this initial v1.0.0 PR is merged into `microsoft/winget-pkgs`, your GitHub Actions workflow will handle every future release (v1.0.1, v1.1.0, etc.) 100% automatically via Komac!**

### How to Submit the Initial v1.0.0 Package (Takes 2 minutes):

Your GitHub Action release automatically created and attached **`winget-manifests.zip`** to the release!

1. Download **`winget-manifests.zip`** from your GitHub release.
2. Unzip it. You will see:
   `manifests/e/ElroiTheCreator/HolyBible/1.0.0/`
   - `ElroiTheCreator.HolyBible.yaml`
   - `ElroiTheCreator.HolyBible.installer.yaml`
   - `ElroiTheCreator.HolyBible.locale.en-US.yaml`
3. Go to **[https://github.com/microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs)** and click **Fork** (top-right).
4. Navigate into the `manifests/` folder on your fork (or click **Add file** -> **Upload files**).
5. Upload the folder `e/ElroiTheCreator/HolyBible/1.0.0/` with the 3 YAML files.
6. Commit to a new branch (e.g. `add-holybible-1.0.0`).
7. Click **Contribute** -> **Open pull request**.
   - PR Title: `New package: ElroiTheCreator.HolyBible version 1.0.0`
8. Microsoft's automated bots (`winget-bot`) will validate the manifests, test-install the executable in a sandbox, and merge the PR.

---

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
