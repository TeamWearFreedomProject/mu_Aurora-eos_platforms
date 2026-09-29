# Aurora ACPI scaffold (not functional hardware port)

Aurora.dsc and Aurora.fdf now select this local ACPI INF and a local
Selene-derived FADT and Qualcomm header. No active Pixel Watch 2
ACPI device definitions are implemented yet.

APIC/MADT and GTDT are now generated locally from CP2A evidence. The remaining
compiled AML/binary inputs still include upstream SelunaACPI/5100/builtin and
SelunaACPI/common tables written for the inherited SW5100 platform. These
must be compared with **the exact Aurora Wi-Fi device tree and current
firmware**, including GPIO/button IRQs, display/IOMMU, WLAN, storage,
power, and I2C bus topology. Existing FADT ResetReg/PSCI fields and
all AML are unverified; no Windows boot testing is authorized by
a successful build.

## CP2A DTBO evidence relevant to later ACPI/GPIO work

The verified uploaded CP2A DTBO adds a `google,gpiochipwake0` overlay and
an MCU crash/wake pin on **TLMM GPIO19** (GPIO mux, pull-down, input enabled,
drive strength 2). The same change appears in all 11 Eos/Aurora overlay
variants. CP2A also removes two explicit BMS charge-termination overrides
and removes the overlay-level `disabled` status from
`google,gbms_virt_storage`.

Do **not** translate those facts directly into ACPI devices yet. The current
SelunaACPI SW5100 DSDT only enumerates the four CPUs; it does not provide a
Watch 3 peripheral topology that can simply be renamed for Watch 2.
A real Aurora peripheral ACPI port still needs the effective base DTB,
MMIO/IRQ resources and Windows-driver hardware IDs.

For first UEFI graphics, ACPI is not the immediate blocker:
`SimpleFbDxe` uses the named `Display Reserved` region and 384x384 PCDs.
The CP2A overlay keeps the same splash reservation
`0x5C000000..0x5CF00000` as CP1A. Pixel format/stride and the fact that
the bootloader has actually initialized that framebuffer are still unverified.

## CP2A base-DTB vs inherited APIC/GTDT

The matching CP2A `vendor_kernel_boot.img` changes the ACPI picture
substantially:

- CP2A has four CPU nodes with `reg` / MPIDR values **0, 1, 2, 3**.
  The inherited APIC AML has GICC MPIDRs **0, 0x100, 0x200, 0x300**.
  Those are not equivalent descriptions and are now treated as an Aurora
  ACPI blocker.
- GICv3 **GICD 0x0F200000 / 0x10000** and
  **GICR 0x0F300000 / 0x100000** match the inherited APIC table exactly.
- CP2A's Monaco timer node uses GIC PPI cells **1,2,3,0** at 19.2 MHz.
  The inherited GTDT reports GSIV **29,30,27,26**. Do not mechanically
  replace one with the other until the interrupt-number translation is
  reviewed.
- The inherited APIC also advertises a GIC MSI frame at `0x0F210000`;
  the CP2A base DTB has no corresponding GIC-v2m/MSI-frame node. This is
  therefore unverified rather than accepted as Aurora hardware.

A dedicated Aurora MADT/GTDT should be generated only after these CPU and
timer differences are resolved. Successful UEFI compilation is not evidence
that the inherited ACPI is usable by Windows on Watch 2.

## Aurora-local MADT/APIC and GTDT

The first two high-impact ACPI tables are no longer selected from the
Pixel Watch 3/Seluna binaries. `tools/generate_aurora_acpi.py` generates
Aurora-local raw ACPI tables from the CP2A base-DTB evidence before each
firmware build.

The generated MADT keeps the verified GICv3 distributor/redistributor
addresses, changes the four GICC MPIDRs to **0,1,2,3**, changes the PMU
performance interrupt from inherited GSIV 23 to **22** (CP2A
`GIC_PPI 6`), and keeps the GIC maintenance interrupt at **25**
(`GIC_PPI 9`). The old MSI frame at `0x0F210000` is deliberately
retained but remains **unverified**, because absence from the DTB alone is
not enough evidence to remove it.

The generated GTDT translates the CP2A architected-timer PPI cells
`1,2,3,0` to GIC INTID/GSIV **17,18,19,16** respectively. The timer DT
marks all four PPIs level-low, so the GTDT flags are emitted as
level-triggered / active-low. The memory timer already matched:
`0x0F120000`, physical GSIV 40 and virtual GSIV 39.

This is still only a partial ACPI port. CSRT, DBG2, DSDT, IORT, MCFG,
PPTT and common SSDTs are inherited, and peripheral Windows hardware IDs
are not yet derived for Aurora. Building these tables successfully does
not authorize hardware boot testing.

## Remaining inherited ACPI final audit

The current split is now clear: **CPU/interrupt core ACPI is partially
Aurora-local, peripheral ACPI is not.**

- **DSDT:** low-risk structurally. It only declares CPU0..CPU3 with UIDs
  0..3, which match CP2A and the local MADT. It is still inherited packaging.
- **DBG2:** its UART base `0x04A98000` and USB base `0x04E00000` match
  CP2A MMIO evidence, but the namespace paths `\_SB.UARD` and
  `\_SB.URS0` are not yet verified.
- **PPTT:** blocker. The inherited table makes all four CPU nodes reference
  the same two private cache objects. CP2A has distinct per-core L1 I/D
  cache nodes and one shared 512 KiB L2, so the cache topology is not an
  Aurora description.
- **IORT:** major blocker. Its two SMMU bases are `0x15000000` and
  `0x02CA0000`; CP2A's actual SMMUs are `0x059A0000` (KGSL) and
  `0x0C600000` (apps). There are **zero exact base matches**.
- **MCFG:** blocker. It advertises ECAM at `0x60000000` and
  `0x40000000`, addresses our current memory map treats as reserved/kernel
  memory. The two CP2A base DTBs contain **no PCI/PCIe nodes**. Do not trust
  this inherited table without independent Aurora PCIe evidence.

Therefore the next large ACPI target is **IORT**, not cosmetic DSDT cleanup.
Until Aurora's SMMU/device mappings are rebuilt, Windows DMA/IOMMU behavior
cannot be treated as valid.

## Minimal CP2A ACPI core: inherited binaries quarantined

The audit above found that several inherited tables are not just unverified,
but positively conflict with CP2A evidence. They are therefore no longer
selected in Aurora's active ACPI package.

The active table set is now deliberately small:

- local FADT scaffold (reset semantics still unverified),
- CP2A-derived local MADT/APIC,
- CP2A-derived local GTDT,
- Aurora-local CPU-only DSDT with CPU UIDs 0..3.

The inherited Seluna **CSRT, DBG2, IORT, MCFG, PPTT, SSDT, TPMDev and
SoftwareTpm2Table** are quarantined from the build. This does not mean those
features are implemented; it prevents known-wrong or unevidenced tables from
silently describing Watch 2 hardware.

A new CP2A IOMMU audit records the two real SMMUs from the uploaded
`vendor_kernel_boot.img`: apps-SMMU at `0x0C600000` and KGSL-SMMU at
`0x059A0000`. The base DTB contains 29 nodes with `iommus` properties
and 36 mapping tuples, including stream IDs for USB, QUP/GPI, display, VIDC,
KGSL and crypto. This is enough to begin reconstructing IORT, but **not**
enough to emit a trustworthy Windows IORT: ACPI named-component/namespace
mappings are still missing.

So "Seluna ACPI separation" is now much cleaner: **zero SelunaACPI binary
tables are active**, while peripheral ACPI remains intentionally incomplete.
This is a research/build milestone only; hardware boot approval remains false.
