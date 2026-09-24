# Aurora ACPI scaffold (not functional hardware port)

Aurora.dsc and Aurora.fdf now select this local ACPI INF and a local
Selene-derived FADT and Qualcomm header. No active Pixel Watch 2
ACPI device definitions are implemented yet.

The compiled AML inputs remain the upstream SelunaACPI/5100/builtin
and SelunaACPI/common/builtin tables written for SW5100 PW3. These
must be compared with **the exact Aurora LTE device tree and current
firmware**, including GPIO/button IRQs, display/IOMMU, WLAN, storage,
power, and I2C bus topology. Existing FADT ResetReg/PSCI fields and
all AML are unverified; no Windows boot testing is authorized by
a successful build.
