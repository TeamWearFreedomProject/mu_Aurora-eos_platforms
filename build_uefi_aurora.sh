#!/usr/bin/env bash
# Build-only packaging of Android boot header v4 images.
# NOT hardware validated. DO NOT FLASH or fastboot boot on a watch.
set -euo pipefail
mkdir -p ImageResources/Aurora
bootstrap=ImageResources/bootstrap.bin
shim=BootShim/BootShim.Aurora.bin
test -s "$bootstrap"
test -s "$shim"

for variant in secureboot nosb; do
    if [[ "$variant" == secureboot ]]; then
        fd=ImageResources/Aurora/SW5100_EFI.fd
    else
        fd=ImageResources/Aurora/SW5100_EFI_NOSB.fd
    fi
    name="aurora_${variant}_EXPERIMENTAL_DO_NOT_FLASH"
    payload="ImageResources/Aurora/${name}.payload.bin"
    img="ImageResources/Aurora/${name}.img"
    manifest="ImageResources/Aurora/${name}.manifest.json"

    test -s "$fd"
    # The 0x002BF000 FD limit and 0x5FC41000 relocation base come
    # from Selene, NOT a validated Aurora bootloader memory map.
    [[ $(stat -c %s "$fd") -eq $((0x002BF000)) ]] || {
        echo "FD size differs from the inherited Selene FDF; refusing to package."
        exit 1
    }
    cat "$bootstrap" "$shim" "$fd" > "$payload"
    # Uploaded CP2A stock boot.img advertises a v4 signature section size of 0.
    # Match that header/data layout only; this does NOT make the image AVB trusted.
    python3 ImageResources/mkbootimg.py --kernel "$payload" -o "$img" \
      --header_version 4 --boot_signature_size 0
    python3 tools/validate_aurora_bootimg.py \
      --bootstrap "$bootstrap" --shim "$shim" --fd "$fd" \
      --payload "$payload" --image "$img" --manifest "$manifest"

    # Publish a clearly named Android boot-v4 image that is structurally
    # suitable as a fastboot temporary-boot *candidate*. This alias does not
    # imply hardware acceptance or boot success.
    candidate="ImageResources/Aurora/aurora_cp2a_${variant}_fastboot_candidate_UNVERIFIED.img"
    candidate_manifest="ImageResources/Aurora/aurora_cp2a_${variant}_fastboot_candidate_UNVERIFIED.manifest.json"
    cp "$img" "$candidate"
    cp "$manifest" "$candidate_manifest"
    sha256sum "$candidate" > "${candidate}.sha256"

    rm -f "$payload"
done
