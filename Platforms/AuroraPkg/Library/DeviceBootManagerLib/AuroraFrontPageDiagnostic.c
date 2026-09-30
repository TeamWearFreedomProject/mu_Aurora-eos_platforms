/** @file
  Aurora-only diagnostic: draw a blue GOP marker once and hold before boot selection.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

// Keep the inherited implementation for all other device boot manager hooks.
// Rename only its priority hook so Aurora can replace it locally.
#define DeviceBootManagerPriorityBoot SelunaDeviceBootManagerPriorityBoot
#include "../../../SelunaPkg/Library/DeviceBootManagerLib/DeviceBootManagerLib.c"
#undef DeviceBootManagerPriorityBoot

#include <Library/BaseLib.h>
#include <Protocol/GraphicsOutput.h>

STATIC
VOID
AuroraDiagnosticMarker (
  IN UINT8 Red,
  IN UINT8 Green,
  IN UINT8 Blue
  )
{
  EFI_GRAPHICS_OUTPUT_PROTOCOL  *Gop;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL Pixel;
  EFI_STATUS                   Status;
  UINTN                        Width;
  UINTN                        Height;

  Status = gBS->LocateProtocol (&gEfiGraphicsOutputProtocolGuid, NULL, (VOID **)&Gop);
  if (EFI_ERROR (Status) || (Gop == NULL) || (Gop->Mode == NULL) || (Gop->Mode->Info == NULL)) {
    return;
  }

  Width  = Gop->Mode->Info->HorizontalResolution;
  Height = Gop->Mode->Info->VerticalResolution;
  if ((Width == 0) || (Height == 0)) {
    return;
  }

  Pixel.Red      = Red;
  Pixel.Green    = Green;
  Pixel.Blue     = Blue;
  Pixel.Reserved = 0;
  Status = Gop->Blt (
                  Gop, &Pixel, EfiBltVideoFill, 0, 0,
                  Width / 4, Height / 4,
                  Width - (Width / 4) * 2, Height - (Height / 4) * 2, 0
                  );
  DEBUG ((DEBUG_INFO, "[Aurora blue-hold diagnostic] marker: %r\n", Status));
}

EFI_STATUS
EFIAPI
DeviceBootManagerPriorityBoot (
  IN OUT EFI_BOOT_MANAGER_LOAD_OPTION  *BootOption
  )
{
  EFI_STATUS  Status;

  (VOID)BootOption;

  // Control experiment: do not prepare or start any boot application.
  // Disable the UEFI watchdog before drawing; inherited hardware watchdogs,
  // interrupts and previously scheduled events are not changed by this hook.
  Status = gBS->SetWatchdogTimer (0, 0, 0, NULL);
  DEBUG ((DEBUG_INFO, "[Aurora blue-hold diagnostic] disable watchdog: %r\n", Status));

  // Draw once, then hold. Repainting would hide a display-lifetime problem.
  // No console print/clear follows the marker.
  AuroraDiagnosticMarker (0, 80, 255);
  CpuDeadLoop ();
  return EFI_ABORTED;
}
