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
