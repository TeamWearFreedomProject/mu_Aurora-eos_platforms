# Pixel Watch 2 (Aurora) UEFI bring-up

This is an experimental research-only platform derived from Pixel Watch 3 Selene. Compilation and image structure have been checked; live Aurora Wi-Fi bootability has not.

- Display geometry: 384x384 (Aurora panel configuration).
- Platform product / SMBIOS identity: aurora / Aurora.
- Build outputs: `Build/AuroraPkg`.
- The `AuroraPkg.dec` package declaration is required by the upstream EDK2
  DebugMacroCheck pre-build plugin; omitting it causes `Path(None)` during
  package discovery.
- Dedicated Aurora FDF, memory-map library and ACPI package now exist. FDF addresses, Qualcomm drivers and precompiled ACPI AML still inherit unverified Selene/PW3 assumptions.
- **Current research target:** CP2A.260603.001.S1 after the owner's downgrade. CP3A evidence below is historical. Live CP2A ADB is unavailable because watch setup cannot currently be completed.
- **Unverified**: CP2A base DTB / pre-Linux memory ownership, runtime framebuffer mapping, GPIO/button wiring, UEFI relocation, BootShim and remaining firmware dependencies.
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

The shared AOSP-compatible mkbootimg script keeps its default **4096-byte
zero-filled GKI signature placeholder** for existing users, but Aurora packaging
now explicitly selects **signature size 0** to match the uploaded CP2A stock
boot header. This is only a structural match; the experimental image is still
not AVB-verified.

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
validate the target CP3A Aurora Wi-Fi memory layout: the source README itself
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

## Comparison with the supplied newer Watch 2 DTBO (2026 upload)

An uploaded 8 MiB Watch 2 `dtbo.img` (SHA-256:
`1854fda34ad79d7ccc96df1632144ae8d6e0151381303012c41ae80109060c85`)
was read offline without modifying the watch. All 11 overlays, for Eos
and Aurora board-ID families, have **identical six fixed memory reservation
overrides**. The boot image supplied alongside it contains fingerprint
`CP1A.260305.014.W2`, but their shared OTA provenance was not
independently established. No original firmware binaries are committed.

The supplied DTBO extends the modem reservation from the early DTS's
`0x4AB00000..0x50900000` to `0x4AB00000..0x52900000`. Video moves
to `0x52900000..0x53000000`, ADSP to
`0x53000000..0x54900000`, and IPA/GPU regions occupy
`0x54900000..0x54917000`. Some DTBO node names still mention
`@547xxxxx`; the actual `reg` properties are at `0x549xxxxx`.
The existing Aurora `PIL Reserved` span
`0x4AB00000..0x55700000` **already covers both layouts**, so
we preserve that broad reservation, rather than shifting allocations
based on incomplete data. The CI checker now guards the six newer
fixed overrides in addition to the 17 older fixed regions.

**Still unknown:** The DTBO contains overrides, not the complete
effective base DTB. It does not establish where `bootstrap.bin`,
BootShim, the UEFI FD at `0x5FC41000`, the UEFI stack, or other
bootloader/SMEM allocations can safely reside. None of these
new checks makes the experimental image boot-ready.

## Confirmed device identity: CP3A.260905.002.E1 (September 2026)

Read-only reports from the **actual** Watch 2 establish:
```
adb: ro.product.device = aurora
adb: ro.build.fingerprint = google/aurora/aurora:17/CP3A.260905.002.E1/16053217:user/release-keys
fastboot: product aurora / unlocked yes / slot b at observation
fastboot: bootloader eos-6.08-15857178
```
Google's [September 2026 Watch bulletin](https://support.google.com/googlepixelwatch/thread/467479812/google-pixel-watch-update-september-2026) names the same build for Pixel Watch 2. The `eos-` version prefix on the bootloader does not override the `aurora` device ID.

The older uploaded `dtbo.img` (SHA-256 `1854fda34ad79d7ccc96df1632144ae8d6e0151381303012c41ae80109060c85`) was supplied with a **CP1A** boot image. It was not proven to match the running CP3A firmware. The historical 2023 DTS predates both. Neither proves that the inherited `bootstrap.bin`, 0x5FC41000 BootShim/FD relocation, UEFI stack or Watch 3 ACPI tables are compatible with CP3A.

The machine-readable [CP3A target evidence checklist](Research/target_cp3a_verification.json) deliberately marks every hardware compatibility item unverified. An early CI check guards this negative claim. Successful compilation, header parsing and historical fixed-region checks **do not authorize fastboot boot or flashing**. Real CP3A Aurora bootloader + base DTB / DTBO, live SMEM, verified relocation and recovery procedure remain necessary.

## Next: read-only live CP3A reserved-memory evidence (not boot approval)

Google's September 2026 update announcement confirms the CP3A.260905.002.E1
Watch 2 build, but the factory/OTA catalog is terms-gated and no matching
CP3A image or verified CP3A DTBO has been obtained for this project.
Do NOT substitute the older CP1A DTBO, the 2023 DTS, or the PW3 bootstrap.

The optional `tools/collect_cp3a_memory.ps1` script reads ONLY the running
Linux kernel's `/sys/firmware/devicetree/base/reserved-memory` tree over
normal ADB. Run while the watch is normally booted on the exact fingerprint,
from PowerShell in `C:\platform-tools` after copying the script there:

```powershell
.\collect_cp3a_memory.ps1
```

If PowerShell script execution is restricted, do not bypass the restriction;
the same limited evidence can be inspected interactively with:

```powershell
.\adb.exe shell getprop ro.build.fingerprint
.\adb.exe shell ls /sys/firmware/devicetree/base/reserved-memory
```

Then run `python tools/audit_cp3a_runtime.py <snapshot-folder> --output report.json`
on a PC with Python. The audit handles big-endian `reg` cells, dynamically
allocated `size`-only pools, and reports overlaps with current inherited
UEFI FD/stack/heaps. It **never** declares hardware boot safety, even
when it observes zero conflicts. ADB might deny access on a production
watch; never root or modify the device merely to collect this snapshot.
Only share the generated `report.json` if comfortable; no serial number
or raw complete device tree is necessary for the next code review.

**Important:** Running Linux's reserved-memory subtree is neither the
pre-boot physical allocation map nor a complete bootloader/TrustZone
memory layout. CP3A genuine bootloader relocation and ACPI still need
independent evidence before any experimental fastboot boot.

### Old and new reserved-memory nodes in the CP3A live listing

The owner's running CP3A DTFS directory includes both `video_region@50900000`
and `video_region@52900000`, both `adsp_regions@51000000` and
`adsp_regions@53000000`, plus older/newer IPA/GPU node names.
These names **do not establish which ranges are active**; the audit now
checks each node's `status` and ignores explicit `disabled` nodes.
Actual binary `reg` values override the often stale node-name addresses.
A full read-only subtree capture is required to determine overlaps, and
its resulting lack of overlaps still does not establish bootloader safety.

## Verified uploaded CP2A DTBO: 2026 June Aurora Wi-Fi build

A newly user-uploaded **8 MiB** Pixel Watch 2 `dtbo.img` (SHA-256
`5f91d117e34dc554a90891bedf52dfa5dc7ebc3f1c1f94e8edd769e6c70d3b31`) contains the *internal*
`com.android.build.dtbo.fingerprint` value:

```
google/aurora/aurora:17/CP2A.260603.001.S1/15396605:user/release-keys
```

This distinguishes it from the original CP1A DTBO
(`1854fda34ad79d7ccc96df1632144ae8d6e0151381303012c41ae80109060c85`), which contains the CP1A fingerprint. This is
strong **image-internal CP2A provenance**; the original official ZIP and
its checksum have not been independently verified.

All 11 overlays (Eos and Aurora board-ID families) have exactly the
**same six fixed reserved-memory `reg` ranges as the supplied CP1A
DTBO**: modem `0x4AB00000..0x52900000`, video
`0x52900000..0x53000000`, ADSP `0x53000000..0x54900000`,
IPA and GPU `0x54900000..0x54917000`. No changes to the
current broad `PIL Reserved` UEFI reservation are required for
these six overlays. The 11 overlays do differ from CP1A in *other*
properties: 15 changed properties, five newly added DT nodes per
overlay, new `google,gpiochipwake0` and GPIO19 MCU crash wiring,
and changed battery charge overrides. Preserve these differences
when later investigating buttons, wake and ACPI GPIO.

CI now separately guards CP1A and CP2A fixed overrides. The original
CP3A device-fingerprint and ADB tools above document the **previous**
firmware; the owner reports having downgraded to CP2A but cannot
complete setup without an Android phone, so a new *live ADB fingerprint*
has not been observed. The CP2A DTBO alone still does NOT contain a
complete base DTB, full early firmware/SMEM allocation map, AVB-verified
matching boot.img, or evidence that inherited Watch 3
`bootstrap.bin` / `0x5FC41000` BootShim relocation is safe.
The experimental UEFI image remains **DO NOT FLASH / DO NOT FASTBOOT BOOT**.

## CP1A -> CP2A: what actually changed for bring-up priority

A complete property-level comparison of all 11 Watch 2 DTBO overlays found
the **same diff pattern on every overlay**: 15 changed properties, five added
nodes, and no removed nodes. The six fixed reserved-memory overrides and the
384x384 panel/splash reservation are unchanged.

That narrows the first-boot problem:

1. **Still critical / unresolved:** inherited `bootstrap.bin`, BootShim copy
   destination `0x5FC41000`, UEFI FD/stack/heap ownership, base DTB/SMEM.
2. **Static evidence improved:** CP2A preserves the CP1A modem/video/ADSP/IPA/GPU
   overlay ranges and `0x5C000000..0x5CF00000` splash reservation.
3. **Later hardware work:** CP2A adds `google,gpiochipwake0` + GPIO19 MCU
   crash/wake pin configuration and changes BMS/GBMS overrides. These matter
   for wake/power/buttons and a future ACPI port, not for proving BootShim safe.

The derived comparison is stored in
`Research/cp1a_cp2a_dtbo_evolution.json` and guarded by CI. This does not
turn the generated image into a hardware-tested image.

## Verified uploaded CP2A stock boot.img: bootstrap mismatch confirmed

The user-uploaded CP2A Watch 2 boot image (SHA-256
`01c93386c44e7e0637c09b24340797d4dbca4986717ba2912f278f991c8ff3c1`)
contains the internal fingerprint:

```
google/aurora/aurora:17/CP2A.260603.001.S1/15396605:user/release-keys
```

It is Android boot header **v4**, 64 MiB total, with a **36,731,392-byte**
kernel, no ramdisk, and **boot signature size 0**. The kernel SHA-256 is
`0ab5d6680d061f3d36f34078668aa2f14f08a5da729e31c19553554f4cbd3b42`
and identifies itself as
`6.6.118-android15-8-ge6d21220be73-ab15042318-4k`.
Its boot security-patch property is `2026-06-05`.

This is a real change from the supplied CP1A Watch 2 boot image:
the CP1A kernel is 36,665,856 bytes and Linux
`6.6.102-android15-8-gb10d63bc1566-ab14419598-4k`; CP2A is exactly
**65,536 bytes larger** and has a different kernel hash.

Most importantly for this UEFI port, the inherited repository
`ImageResources/bootstrap.bin` is **35,520,512 bytes**. Therefore it
cannot be byte-identical to the uploaded CP2A stock kernel
(36,731,392 bytes); the size differs by **1,210,880 bytes**.
The bootstrap is inherited from the upstream Seluna "Base Package A"
packaging flow and its exact Aurora compatibility remains unverified.

There is also a structural packaging mismatch: the uploaded stock CP2A
boot header advertises a v4 boot-signature section size of **0**, while
the current in-tree `mkbootimg.py` always emits a **4096-byte zero-filled**
placeholder for generated v4 images. This does not by itself prove why a
temporary boot would succeed or fail, but it gives us a concrete packaging
difference to fix/test offline before any hardware attempt.

Derived facts are stored in
`Research/supplied_cp2a_boot.json` and guarded by CI. BootShim relocation
at `0x5FC41000`, full base-DTB/SMEM ownership, AVB behavior for the
experimental image, and recovery remain unverified; current output is still
**DO NOT FASTBOOT BOOT / DO NOT FLASH**.

## CP2A boot-header alignment update

Aurora's experimental packaging now passes
`--boot_signature_size 0`, matching the uploaded CP2A stock boot.img's
Android v4 header and omitting the previous 4096-byte zero placeholder.
A regression test verifies both behaviors: the shared mkbootimg default
remains 4096 bytes, while Aurora's opt-in path is 0.

This removes one known **format difference** only. The generated image is
still not a clone of the 64 MiB stock boot partition image: it does not gain
the stock AVB footer merely by changing this field, and it still contains the
inherited Seluna `bootstrap.bin` plus BootShim and UEFI FD rather than the
CP2A stock kernel. The inherited `0x5FC41000` relocation remains the next
critical blocker and is deliberately still marked unverified.

## CP2A BootShim relocation audit: still a blocker

The uploaded CP2A stock kernel's ARM64 Image header reports
`text_offset = 0`, `image_size = 0x23A0000`, flags `0xA`, and
`ARMd` magic. Those values come from the stock kernel itself; they do
**not** provide the inherited UEFI destination `0x5FC41000`.

The current BootShim still copies the UEFI FD to
`0x5FC41000..0x5FF00000`. That range does not overlap the fixed
CP2A DTBO reservations we extracted, and it lies between the historical
DFPS end at `0x5D000000` and the historical stats region at
`0x60000000`. This is only negative overlap evidence. Neither the CP2A
DTBO nor the old 2023 DTS proves that the bootloader, TrustZone, SMEM or
other pre-Linux firmware leaves that gap available.

The machine-readable audit is
`Research/cp2a_bootshim_relocation_audit.json`; CI deliberately fails
if anyone flips `relocation_verified` or `hardware_boot_approved`
without replacing this evidence. The next high-value artifact is a matching
**CP2A `vendor_boot.img`** (if present in the firmware package), because
boot header v4 normally separates vendor data and the DTB from `boot.img`.

## CP2A init_boot + vendor_boot: useful surprise

Two more uploaded CP2A images close several packaging questions:

- `init_boot.img` is Android boot header v4, contains **no kernel**, a
  2,618,142-byte LZ4-legacy ramdisk, and advertises **boot signature size 0**.
  Its ramdisk build.prop and AVB metadata carry the same
  `CP2A.260603.001.S1` Aurora fingerprint.
- `vendor_boot.img` is vendor boot v4 with a single **platform** vendor
  ramdisk (16,802,729 bytes), 4 KiB pages, and the bootconfig lines
  `androidboot.console=ttyMSM0` and `androidboot.memcg=1`.
  Critically, its header says **DTB size = 0**, and there is no FDT magic
  anywhere in the supplied image.

The uploaded CP2A `boot.img` also does **not** solve the base-DTB problem:
its only FDT blob is 72 bytes with zero string-table bytes and a 16-byte
structure block — effectively an empty root-only FDT, not an Aurora hardware
tree. `init_boot.img` contains no FDT either.

So the earlier idea that `vendor_boot.img` would provide the matching base
DTB was wrong for this watch. Public AsteroidOS Aurora packaging at commit
`750506ad678a2b142f044fd4667655b7f1c702ea` documents a separate
`vendor_kernel_boot.img` and says its `vkb-base.dtb` was extracted from
that partition. That public blob is **not CP2A provenance**, so it is only a
map to where the missing evidence lives, not a substitute for the matching
CP2A image.

A matching **CP2A `vendor_kernel_boot.img`** has now been supplied and
analyzed below. It provides the missing base DTBs, but it still does not prove
pre-Linux ownership of `0x5FC41000`; hardware boot approval remains false.

## CP2A vendor_kernel_boot: base DTBs finally obtained

The uploaded 64 MiB CP2A `vendor_kernel_boot.img` has SHA-256
`ea6d8e296cdd66fbb356f1b1563f1ed393b089b3c08e0e5215bcc74a88e47d98`.
Its AVB property carries the same Aurora fingerprint
`CP2A.260603.001.S1/15396605`.

The vendor-boot-v4 header contains a **463,814-byte DTB section**, which is
exactly two concatenated base FDTs:

- **MonacoP**: `qcom,monacop`, MSM ID `0x205`, 231,933 bytes,
  SHA-256 `dc3be209b62212779c6da1e4ec53c73fc1a3c5e72bca80c1c5b6b36e167fbf4e`.
- **Monaco**: `qcom,monaco`, MSM ID `0x1e6`, 231,881 bytes,
  SHA-256 `5468ec96fb2bd663866741ce318a52911364db68e19696921382919e26621c38`.

They are almost identical: only five properties differ (root model,
compatible, MSM ID, and two IPA status properties). Their fixed
`/reserved-memory` layout is identical. Combined with the matching CP2A
DTBO, we can now build a much stronger effective fixed-memory picture.

### Important bug found in our UEFI map

All **11 CP2A overlays** add:

- `ramoops@61F00000`: `0x61F00000..0x62300000` (4 MiB, no-map)
- `kinfo_mem@62400000`: `0x62400000..0x62401000` (4 KiB, no-map)

The previous Aurora UEFI map exposed those addresses as allocatable RAM when
memory serial output was disabled, and it exposed the 4 KiB kinfo hole even
when PStore was enabled. That is a real static conflict. The map now always
reserves the 4 MiB ramoops/PStore area and splits RAM around the 4 KiB kinfo
hole. CI checks all **19 effective fixed CP2A regions** and has regression
tests that fail if either address becomes allocatable again.

This is the first CP2A evidence that required an actual memory-map correction,
rather than merely confirming an inherited reservation.

### Why 0x5FC41000 is still not verified

The good news: neither CP2A base DTB has a fixed reserved-memory region
overlapping `0x5FC41000..0x5FF00000`.

The bad news: both base DTBs have `/memory/reg = <0 0 0 0>`, meaning usable
RAM is expected to be patched at runtime, and their FDT memreserve tables are
empty. They also describe active size-only dynamic reserved-memory pools with
broad allocation ranges. Therefore absence of a fixed DT node at
`0x5FC41000` is **not proof** that the bootloader/TrustZone/firmware leaves
that range available before UEFI runs.

So the missing artifact is no longer a DTB. The remaining blocker is
**authoritative pre-Linux memory ownership / runtime-patched memory evidence**.
Generated images remain DO-NOT-BOOT / DO-NOT-FLASH.

## CP2A SoC audit: GIC/UART/MMIO mostly line up; ACPI does not

The CP2A base DTBs now let us audit the inherited low-level register map.

Confirmed exact matches include the GICv3 distributor at `0x0F200000`,
redistributor at `0x0F300000`, TLMM at `0x00500000`, DISP_CC at
`0x05F00000`, and watchdog at `0x0F017000`. The existing broader UEFI
windows also cover CP2A GCC, SPMI, QUP, USB, MDSS, SMMU and memory-timer
registers. The debug UART selected by the DTB `serial0` alias is
`qcom,geni-debug-uart@0x04A98000`, exactly matching
`PcdUartSerialBase`. UART output is **not** enabled by this finding: the
current Aurora build still selects the null SerialPortLib in its default
configuration, and clocks/pinctrl are not proven initialized for UEFI use.

One inherited configuration value was clearly wrong for Aurora: the common
SW5100 configuration map said `NumActiveCores=8` and `NumCpus=8`, while
both CP2A base DTBs expose exactly four CPUs with MPIDRs `0,1,2,3`.
Aurora now has its own configuration-map library with both values set to 4;
all other configuration keys remain inherited/unverified.

The larger blocker is ACPI. The inherited Seluna APIC table describes four
CPU MPIDRs as `0,0x100,0x200,0x300`, not CP2A's `0,1,2,3`. Its GTDT also
uses timer GSIVs 29/30/27/26 while the CP2A Monaco DTB encodes the four
architected timer PPIs as 1/2/3/0. GICD/GICR addresses themselves match.
These differences are recorded as **ACPI blockers**, not automatically
rewritten, because the DT PPI-to-ACPI GSIV interpretation must be reviewed
before generating Aurora-specific MADT/GTDT tables.

### CP2A MMIO follow-up: VIDC/VENUS window corrected

A second pass over the base DTB found one inherited MMIO window that was
too small rather than merely broader than the DTB. The CP2A node
`qcom,vidc@5a00000` publishes `reg = <0x05A00000 0x00200000>`, while
Aurora still inherited a `VENUS` MMIO descriptor of only
`0x05A00000..0x05AF0000` (0xF0000 bytes).

Aurora now maps the full CP2A **2 MiB** VIDC window
`0x05A00000..0x05C00000`. It does not overlap the next named UEFI MMIO
window (MDSS starts at `0x05E00000`). CI now requires the full VIDC
range to remain covered.

This is a static MMIO-map correction only. It does not prove that the
inherited Qualcomm VIDC driver is usable on Aurora, nor does it change the
remaining ACPI and pre-Linux relocation blockers.

## Aurora ACPI milestone: MADT + GTDT split from Seluna

Aurora now generates its own MADT/APIC and GTDT instead of packaging the
inherited PW3 copies.

From the matching CP2A base DTBs:
- CPU MPIDRs are **0,1,2,3**.
- PMU PPI6 maps to **GSIV 22**.
- GIC maintenance PPI9 maps to **GSIV 25**.
- Architected timer PPIs **1,2,3,0** map to GSIV
  **17,18,19,16** and are level-low.
- The memory timer remains at `0x0F120000` with GSIV **40/39**.
- GICD/GICR remain `0x0F200000` / `0x0F300000`.

The generator checks ACPI length/checksum and CI verifies the exact CPU,
GIC and timer fields. The inherited MSI frame is intentionally preserved
as **unverified** rather than deleted on absence-of-DT evidence.

This removes two of the largest known Seluna ACPI mismatches, but the
remaining ACPI tables and `0x5FC41000` pre-Linux ownership remain
research blockers. Output remains DO-NOT-BOOT / DO-NOT-FLASH.

## ACPI generator CI fix

The first Aurora-local GTDT build failed before EDK2 compilation because the
Python `struct.pack()` format for the fixed GTDT body encoded only eight
32-bit fields between its two 64-bit addresses, while ACPI GTDT revision 2
requires nine: Reserved plus four interrupt/flag pairs. The generator passed
13 values to a 12-field format and raised
`struct.error: pack expected 12 items for packing (got 13)`.

The format is corrected to `<QIIIIIIIIIQII`, matching the 60-byte fixed
GTDT body used by the inherited 0x9C-byte table layout. CI now executes both
the generator's `--check-only` path and `check_aurora_acpi.py` before
installing build dependencies, so generator/layout regressions fail early.

### MADT validator offset fix

After the GTDT pack-format fix, the new preflight correctly exposed a second
generator-test bug before any expensive build work. The GICC
`Virtual GIC Interrupt` field is at byte offset **56 (0x38)** within an
80-byte ARM GICC MADT subtable, as confirmed by the inherited decoded APIC
layout. The validator had incorrectly read offset 60, which is the beginning
of the following redistributor-address field. The generated GICC binary
layout itself was unchanged; only the assertion offset was corrected.

## ACPI separation checkpoint

Aurora now owns its CP2A-derived MADT/APIC and GTDT, plus its local FADT
scaffold. That is meaningful progress, but it is not a mostly-finished ACPI
port. A full audit of the remaining inherited tables found:

- inherited DSDT CPU UIDs are structurally compatible;
- DBG2's UART/USB addresses line up with CP2A, namespace semantics unverified;
- inherited PPTT cache topology conflicts with CP2A;
- inherited IORT SMMU bases do not match either CP2A SMMU;
- inherited MCFG advertises ECAM windows with no CP2A PCI/PCIe node evidence.

The machine-readable result lives in
`Research/cp2a_remaining_acpi_audit.json`. CI keeps these remaining
IORT/PPTT/MCFG issues marked as blockers. **IORT is the next major porting
target.**

## CP2A fastboot-format candidate artifact

CI now publishes two explicitly named Android boot-v4 candidate images:

- `aurora_cp2a_secureboot_fastboot_candidate_UNVERIFIED.img`
- `aurora_cp2a_nosb_fastboot_candidate_UNVERIFIED.img`

They are byte-for-byte aliases of the structurally validated Aurora images
built from the current CP2A-local ACPI/MMIO/memory-map work. Each has a
SHA-256 sidecar and JSON manifest. The manifest marks the image as a
`FASTBOOT_BOOT_IMAGE_FORMAT_CANDIDATE`, but deliberately leaves temporary
boot acceptance and boot success **unverified**.

This wording matters: Android boot header v4 packaging can be checked offline,
but the current project still lacks authoritative evidence for the inherited
`bootstrap.bin`, the `0x5FC41000..0x5FF00000` pre-Linux relocation
ownership, the post-downgrade live target state, and the watch bootloader's
temporary-boot acceptance policy. Therefore the candidate artifact is a
build result, not a claim that real hardware will enter UEFI.

## First real-hardware milestone: fastboot handoff to UFP-like USB

A 2026-09-29 temporary-boot test of the **no-Secure-Boot CP2A candidate**
(source commit `239711b777f94da4713395c6c90c52c02dfce11c`) produced a new,
important observation:

- host fastboot reported both **Sending OKAY** and **Booting OKAY**;
- the watch showed a logo but no further visible UI;
- the device then disappeared from the fastboot device list;
- Windows enumerated a healthy WinUSB device at **VID 045E / PID 066B**.

This is not the repository's fastboot USB identity: the in-tree fastboot
descriptor uses **045E:0C2F**. By contrast, WOA-Device-Manager's UFP
playground opens **045E:066B** with `UnifiedFlashingPlatformTransport`.
The bundled `SelunaPkg/UFP/ufpdevicefw.efi` also contains the exact
little-endian 045E:066B descriptor pair twice, plus UFP/Microsoft/Flashing
strings.

Therefore the best current interpretation is that the candidate **left
fastboot and progressed into the UEFI/UFP path**. That is strong positive
runtime evidence for the BootShim/FD path, but it is not proof of complete
memory safety, stable UEFI execution, a working console/frontpage, or a
Windows boot.

The redacted machine-readable observation is in
`Research/hardware_observation_2026-09-29_ufp.json`. Device serial numbers
are intentionally not committed. A read-only Windows collector,
`tools/collect_ufp_usb_readonly.ps1`, records PnP metadata without sending
commands to the device.

At this milestone, `fastboot devices` returning no entry **after the
handoff is expected** because the USB transport identity changed away from
fastboot. The next debugging target is the visible UEFI/console path and
where execution stalls after UFP enumeration, not the Android fastboot
transport itself.

### Windows PnP follow-up for the 045E:066B handoff

A second read-only Windows PnP capture confirms that the post-handoff device
is healthy at the USB/PnP layer:

- hardware ID: `USB\VID_045E&PID_066B` (REV 0100);
- service/driver: Microsoft `WINUSB` / `winusb.inf`;
- matching ID: `USB\MS_COMP_WINUSB`;
- compatible interface class: vendor-specific `FF/FF/FF`;
- PnP problem code: **0**, device present, no problem reported.

The instance-specific serial and malformed bus-reported string are intentionally
not stored. This strengthens the conclusion that the watch reached a deliberate
WinUSB/UFP-style USB function after leaving Android fastboot. It still does
not identify where execution stops after UFP enumeration, so the next work
remains read-only console/frontpage/runtime-path diagnosis rather than sending
UFP commands or making persistent changes.

## Real-hardware follow-up: both fastboot candidate variants reach UFP-like USB

The owner tested both generated CP2A candidate variants using temporary
fastboot handoff. The non-secureboot and secureboot variants were each
accepted by the existing fastboot transport and, after handoff, both appeared
to Windows as **VID 045E / PID 066B** with the Microsoft WinUSB driver.

That VID/PID is not the repository fastboot descriptor (which uses PID
`0x0C2F`). It matches the bundled UFP application and the
WOA-Project/WOA-Device-Manager example for
`UnifiedFlashingPlatformTransport`. This is therefore strong evidence that
both candidates execute far enough to enter the UEFI/UFP path.

The identical UFP-like result for both variants means the current visible
stall is **not distinguished by the candidate's secure-boot toggle**. The
remaining investigation should focus on what happens after UFP/UEFI handoff
(display/frontpage/console and later boot stages), while keeping relocation
safety and persistent flashing unapproved.
