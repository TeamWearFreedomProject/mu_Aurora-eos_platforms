# Aurora ACPI scaffold (not functional hardware port)

Aurora.dsc and Aurora.fdf now select this local ACPI INF and a local
Selene-derived FADT and Qualcomm header. No active Pixel Watch 2
ACPI device definitions are implemented yet.

The compiled AML inputs remain the upstream SelunaACPI/5100/builtin
and SelunaACPI/common/builtin tables written for SW5100 PW3. These
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
