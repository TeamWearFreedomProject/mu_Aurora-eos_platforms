# Pixel Watch 2 (Aurora) UEFI bring-up

This is an experimental research-only platform derived from Pixel Watch 3 Selene. Compilation and image structure have been checked; live Aurora LTE bootability has not.

- Display geometry: 384x384 (Aurora panel configuration).
- Platform product / SMBIOS identity: aurora / Aurora.
- Build outputs: `Build/AuroraPkg`.
- The `AuroraPkg.dec` package declaration is required by the upstream EDK2
  DebugMacroCheck pre-build plugin; omitting it causes `Path(None)` during
  package discovery.
- Dedicated Aurora FDF, memory-map library and ACPI package now exist. FDF addresses, Qualcomm drivers and precompiled ACPI AML still inherit unverified Selene/PW3 assumptions.
- **Unverified**: current firmware/SMEM memory reservations, runtime framebuffer mapping, GPIO/button wiring, UEFI relocation, BootShim and remaining firmware dependencies.
- Successful compilation **does not imply** the image is safe to boot on real hardware.

Never write the generated images to persistent partitions. Before any future temporary boot test,
compare against the exact Pixel Watch 2 firmware, verify the bootloader/recovery state, and
preserve partition backups including the current slot.

Run `bash ./build_fd_aurora.sh` to build the UEFI firmware volume (after installing
the upstream build prerequisites and initializing its submodules). Build image packaging
is separated so a successful .fd build does not automatically produce a boot image.

## Experimental Android boot v4 image packaging (not flash ready)

The `build_bootshim_aurora.sh` and `build_uefi_aurora.sh` scripts
assemble a **structural test** of an Android boot header v4 image from:
`ImageResources/bootstrap.bin` (inherited from the original Watch 3 repository),
an AArch64 BootShim with **Selene's unverified memory addresses**, and
the newly compiled Aurora UEFI firmware volume.

The build workflow packages `aurora_secureboot_EXPERIMENTAL_DO_NOT_FLASH.img`
and `aurora_nosb_EXPERIMENTAL_DO_NOT_FLASH.img`, with a JSON manifest
for each containing SHA256 hashes and the exact assumptions. The image validator
checks the Android header, BootShim's ARM64 header, component ordering, FD size,
payload hash and a preliminary 64 MiB size limit. It **cannot establish device
compatibility**; it does not simulate the bootloader or validate AVB.

Source comparison:
- Current temporary FDF maps the UEFI FD to `0x5FC41000-0x5FF00000`.
- The extracted Aurora DTS publishes a reserved continuous splash framebuffer
  at `0x5C000000-0x5CF00000`; it does not by itself validate the inherited
  UEFI relocation region or all bootloader carve-outs.
- `bootstrap.bin` must be independently checked against the exact Aurora
  firmware version before any hardware testing.
- ACPI is **still Selene-based**; the Aurora GPIO, framebuffer and bootloader
  initialization paths remain unverified.

These image files are research artifacts ONLY. **DO NOT FLASH THEM and DO NOT
attempt a temporary boot** until the actual Pixel Watch 2 memory map,
bootloader behavior, exact firmware compatibility and recovery method are
confirmed and reviewed.

The AOSP-compatible mkbootimg script here appends a **4096-byte zero-filled
GKI boot signature placeholder** to each v4 image. This is not a signed boot
image and does **not** satisfy AVB verification.

## Preliminary Aurora memory and ACPI audit (historical source only)

An [early extracted PW2 DTS](https://github.com/argosphil/aurora/blob/e3d5fc73b4c97ea19ae5a0fd1d4eee1324703ad0/extracted/dts)
dated November 2023 shows ODA (0x45700000–0x45A00000), deep sleep
(0x45A00000–0x45B00000), HYP (0x45B00000–0x45E00000), and an XBL/AOP
reservation starting at 0x45E00000. It also exposes WLAN MSA at
0x46200000–0x46300000, a 15 MiB splash framebuffer from 0x5C000000,
and a 1 MiB DFPS region from 0x5CF00000.

The new Aurora-specific memory library reflects these early **fixed**
reservations, conservatively retains the original PIL range for the modem,
video, ADSP, IPA and GPU areas, and keeps unverified remaining regions
as inherited from Selene. A static CI audit guards 17 historical ranges
against accidental assignment to allocatable RAM. This does **not**
validate the 2026 Aurora LTE memory layout: the source README itself
labels its device WiFi and is unsure of device codename mapping. Its
dynamic DMA pools have no guaranteed fixed addresses.

The Aurora-local FDF and ACPI package are now separate from Selene,
but the FADT reset register and the precompiled SelunaACPI AML are
**still inherited** and cannot be considered Watch 2 drivers. The
UEFI/BootShim relocation address 0x5FC41000 and UEFI stack remain
unverified against the watch's current bootloader; current `.img`
output is still **DO NOT FLASH / DO NOT TEMPORARILY BOOT**.

To make hardware progress, obtain the *exact target firmware's*
bootloader/DTB memory layout and the matching Qualcomm memory
partition/SMEM data, then port display, GPIO, interrupts and I2C
ACPI device entries independently. Keep partition backups and a
known working recovery path before any hardware bring-up.
