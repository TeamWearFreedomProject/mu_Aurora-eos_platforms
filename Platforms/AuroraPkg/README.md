# Pixel Watch 2 (Aurora) UEFI bring-up

This is an experimental, **build-only** starting point copied from the Pixel Watch 3 Selene platform.

- Display geometry: 384x384 (Aurora panel configuration).
- Platform product / SMBIOS identity: aurora / Aurora.
- Build outputs: `Build/AuroraPkg`.
- The `AuroraPkg.dec` package declaration is required by the upstream EDK2
  DebugMacroCheck pre-build plugin; omitting it causes `Path(None)` during
  package discovery.
- **Temporary**: uses Selene's FDF and ACPI components, pending Aurora-specific device verification.
- **Unverified**: RAM carve-outs, framebuffer address, GPIO/button wiring, UEFI relocation, bootshim and firmware dependencies.
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
