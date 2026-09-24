#!/usr/bin/env bash
# Experimental Aurora BootShim; relocation addresses are inherited from
# Watch 3/Selene and have NOT been validated on real Pixel Watch 2 hardware.
set -euo pipefail
make -C BootShim -B UEFI_BASE=0x5FC41000 UEFI_SIZE=0x002BF000
cp BootShim/BootShim.bin BootShim/BootShim.Aurora.bin
cp BootShim/BootShim.elf BootShim/BootShim.Aurora.elf
test -s BootShim/BootShim.Aurora.bin
