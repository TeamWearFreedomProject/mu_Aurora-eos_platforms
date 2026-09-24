#!/usr/bin/env bash
set -euo pipefail
mkdir -p ImageResources/Aurora
python3 ./Platforms/AuroraPkg/PlatformBuild.py TARGET=RELEASE
cp ./Build/AuroraPkg/RELEASE_CLANGPDB/FV/SW5100_EFI.fd ./ImageResources/Aurora/SW5100_EFI.fd
python3 ./Platforms/AuroraPkg/PlatformBuildNoSb.py TARGET=RELEASE
cp ./Build/AuroraPkg/RELEASE_CLANGPDB/FV/SW5100_EFI.fd ./ImageResources/Aurora/SW5100_EFI_NOSB.fd
