#!/usr/bin/env python3
"""
WinGet Manifest Generator for Holy Bible (வேதம்)
================================================
Generates the official 3-file WinGet manifest package adhering to schema v1.6.0:
1. <PackageIdentifier>.yaml (Version manifest)
2. <PackageIdentifier>.installer.yaml (Installer manifest)
3. <PackageIdentifier>.locale.en-US.yaml (Default locale manifest)

Computes the cryptographic SHA256 checksum of the compiled executable
and formats all metadata for submission to microsoft/winget-pkgs.
"""

import os
import sys
import hashlib
import argparse
import zipfile
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PACKAGE_ID = "ElroiTheCreator.HolyBible"
PACKAGE_NAME = "Holy Bible - வேதம்"
PUBLISHER = "Elroi-thecreator"
REPO_DEFAULT = "Elroi-thecreator/bibleweb"
SCHEMA_VERSION = "1.6.0"


def calculate_sha256(filepath):
    """Computes SHA256 hex digest of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def generate_manifests(version, exe_path, output_dir, repo=REPO_DEFAULT):
    """Generates the three WinGet manifest files and a zipped bundle."""
    clean_version = version.lstrip("v")
    tag = f"v{clean_version}" if not version.startswith("v") else version
    
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Executable not found at: {exe_path}")

    sha256_hash = calculate_sha256(exe_path)
    file_size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    installer_url = f"https://github.com/{repo}/releases/download/{tag}/HolyBible-Portable.exe"

    print("=======================================================")
    print("   WinGet Manifest Generator")
    print("=======================================================")
    print(f"Package ID     : {PACKAGE_ID}")
    print(f"Version        : {clean_version} (Tag: {tag})")
    print(f"Executable     : {exe_path}")
    print(f"Size           : {file_size_mb:.2f} MB")
    print(f"SHA256         : {sha256_hash}")
    print(f"Installer URL  : {installer_url}")
    print(f"Output Dir     : {output_dir}\n")

    # Directory layout matching winget-pkgs: manifests/e/ElroiTheCreator/HolyBible/<version>/
    manifest_subfolder = os.path.join(
        output_dir,
        "manifests",
        PACKAGE_ID[0].lower(),
        PACKAGE_ID.split(".")[0],
        PACKAGE_ID.split(".")[1],
        clean_version,
    )
    os.makedirs(manifest_subfolder, exist_ok=True)

    # 1. Version Manifest (<PackageIdentifier>.yaml)
    version_yaml_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.{SCHEMA_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {clean_version}
DefaultLocale: en-US
ManifestType: version
ManifestVersion: {SCHEMA_VERSION}
"""

    # 2. Installer Manifest (<PackageIdentifier>.installer.yaml)
    installer_yaml_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.{SCHEMA_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {clean_version}
InstallerType: portable
Commands:
  - holybible
Installers:
  - Architecture: x64
    InstallerUrl: {installer_url}
    InstallerSha256: {sha256_hash}
ManifestType: installer
ManifestVersion: {SCHEMA_VERSION}
"""

    # 3. Default Locale Manifest (<PackageIdentifier>.locale.en-US.yaml)
    locale_yaml_content = f"""# yaml-language-server: $schema=https://aka.ms/winget-manifest.locale.{SCHEMA_VERSION}.schema.json

PackageIdentifier: {PACKAGE_ID}
PackageVersion: {clean_version}
PackageLocale: en-US
Publisher: {PUBLISHER}
PublisherUrl: https://github.com/{PUBLISHER}
PublisherSupportUrl: https://github.com/{repo}/issues
PackageName: {PACKAGE_NAME}
PackageUrl: https://github.com/{repo}
License: MIT
LicenseUrl: https://github.com/{repo}/blob/main/LICENSE
Copyright: Copyright (c) {PUBLISHER}
ShortDescription: Bilingual Tamil & English Holy Bible desktop reader, presenter, and study app.
Description: |-
  Holy Bible (வேதம்) is a comprehensive bilingual Tamil and English Holy Bible desktop application.
  Features:
  - Protestant (BSI Tamil + KJV) and Catholic (POC திருவிவிலியம் + Douay-Rheims) dual-corpus support
  - 100-Day Read-Along Audio Bible with Microsoft Neural TTS
  - Church projector and presenter mode with fullscreen slides
  - 100 bilingual interactive scripture trivia and quiz questions
  - Custom reading plans, progress checkoffs, and offline bookmarks
Tags:
  - bible
  - tamil-bible
  - scripture
  - christianity
  - holy-bible
  - audio-bible
  - vedham
ReleaseNotesUrl: https://github.com/{repo}/releases/tag/{tag}
ManifestType: defaultLocale
ManifestVersion: {SCHEMA_VERSION}
"""

    # File paths
    file_version = os.path.join(manifest_subfolder, f"{PACKAGE_ID}.yaml")
    file_installer = os.path.join(manifest_subfolder, f"{PACKAGE_ID}.installer.yaml")
    file_locale = os.path.join(manifest_subfolder, f"{PACKAGE_ID}.locale.en-US.yaml")

    with open(file_version, "w", encoding="utf-8") as f:
        f.write(version_yaml_content.strip() + "\n")
    with open(file_installer, "w", encoding="utf-8") as f:
        f.write(installer_yaml_content.strip() + "\n")
    with open(file_locale, "w", encoding="utf-8") as f:
        f.write(locale_yaml_content.strip() + "\n")

    print(f"[OK] Generated: {file_version}")
    print(f"[OK] Generated: {file_installer}")
    print(f"[OK] Generated: {file_locale}")

    # Also create a zip archive of the manifests
    zip_path = os.path.join(output_dir, "winget-manifests.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(os.path.join(output_dir, "manifests")):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, output_dir)
                zipf.write(abs_path, rel_path)

    print(f"[OK] Bundled zip: {zip_path}")
    print("\nManifest generation complete!")
    return sha256_hash, manifest_subfolder, zip_path


def main():
    parser = argparse.ArgumentParser(description="Generate WinGet manifests for Holy Bible desktop app.")
    parser.add_argument("--version", default="1.0.0", help="Version string (e.g. 1.0.0 or v1.0.0)")
    parser.add_argument("--file", default=os.path.join("windows_app", "dist", "HolyBible-Portable.exe"), help="Path to compiled executable")
    parser.add_argument("--output-dir", default=os.path.join("windows_app", "dist", "winget_manifests"), help="Output directory")
    parser.add_argument("--repo", default=REPO_DEFAULT, help="GitHub repository (owner/name)")

    args = parser.parse_args()
    generate_manifests(
        version=args.version,
        exe_path=os.path.abspath(args.file),
        output_dir=os.path.abspath(args.output_dir),
        repo=args.repo,
    )


if __name__ == "__main__":
    main()
