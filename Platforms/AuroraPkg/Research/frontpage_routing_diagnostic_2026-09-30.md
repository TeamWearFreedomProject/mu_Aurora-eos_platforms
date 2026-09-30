# Aurora FrontPage routing diagnostic — 2026-09-30

## Observation

The timer-PCD diagnostic at source commit `77a7011e098c7e1b56f79955a795987b678c726f`
was accepted by temporary fastboot boot on an unlocked Aurora, active slot b.
The screen disappeared after a short interval and Windows again enumerated
Microsoft WinUSB `045E:066B`. The live firmware fingerprint remains unverified:
the watch cannot currently complete setup and ADB is unavailable.
No device serial is included here.

## What source inspection establishes

- `SelunaPkg/Library/MsBootPolicyLib/MsBootPolicyLib.c` requests priority UFP
  through the volume-up button state.
- `SelunaPkg/Library/MsBootOptionsLib/MsBootOptionsLib.c` also registers UFP
  (`FFU Loader`) as an active normal boot option, after internal/USB/network
  policy options and before the "Bootloader Menu" option. Thus UFP can be
  reached without a button request.
- The pinned `microsoft/mu_basecore` BDS implementation
  (`a18a672778fc28b2cf99642ca2571d3fdfef3ed3`,
  `MdeModulePkg/Universal/BdsDxe/BdsEntry.c`) walks active boot-category
  options. Existing variables can change the actual order.
- The "Bootloader Menu" PCD defaults to GUID
  `f536d559-459f-48fa-8bbc-43b554ecae8d`: the in-tree LinuxLoader, whose
  entry currently sets `BootIntoFastboot = TRUE`. It is not the separate
  mass-storage menu shown in the upstream guide.
- `SimpleFbDxe` clears the inherited framebuffer during its initialization.
  This occurs before the later BDS logo draw; that clear alone does not
  establish the cause of a post-logo black screen.
- Actual UFP internals are a bundled binary, so its display behavior is not
  established by this C-source audit.

The observed USB identity is consistent with reaching UFP through priority
selection OR normal fallback. Neither path has been measured directly.
This is a routing hypothesis, not proof that the display driver is correct.

## Diagnostic change

Aurora's secureboot and nosb DSCs select a local DeviceBootManagerLib wrapper.
All inherited hooks are retained, except the priority-boot hook:

1. Draw a blue central GOP rectangle as a best-effort entry marker.
2. Build the existing FrontPage load option and call
   `EfiBootManagerBoot` directly, bypassing button and default-boot selection.
3. If option creation fails or FrontPage returns, print its status, draw a
   red central rectangle and enter `CpuDeadLoop`.

FrontPage can immediately clear the blue marker. The marker is not a timer
test, and its absence does not prove that the hook was never entered.
There is no timeout-based wait. No additional partition flash, UFP command,
mass-storage setup or boot-variable write is introduced by this wrapper.
Earlier inherited initialization and variable handling remain in place.

The pinned `microsoft/mu_plus` priority caller
(`2761c3a83e441f439fb3d90e61972801495b1196`,
`MsCorePkg/Library/PlatformBootManagerLib/MsPlatform.c`) runs after the
console stage. The diagnostic does not return to that caller, preventing
subsequent normal fallback even if FrontPage fails or exits.

## How to interpret a future temporary-boot observation

| Observation | Supported conclusion |
| --- | --- |
| FrontPage becomes visible | Direct FrontPage execution can display a UI; the original routing remains to be measured. |
| Red rectangle/status appears | The diagnostic hook executed and FrontPage creation or execution returned. Record the status. |
| Blue appears, then screen goes black without UFP USB | The hook was reached; FrontPage rendering/initialization or inherited display lifetime remains unresolved. |
| Black screen and no marker/USB | Inconclusive: execution, console/GOP availability, display lifetime and marker visibility remain possible explanations. |
| The same UFP USB appears | This conflicts with the intended non-returning hook. Verify exact image hash/build, library selection and other UFP launch paths before inferring a display failure. |

UFP USB is not expected through the bypassed boot-manager paths. Lack of USB
alone is not proof of successful FrontPage entry. Recovery/reset or an
inherited watchdog may still restart the watch.

To restore the prior route, remove only the local DeviceBootManagerLib
overrides at the end of both Aurora DSCs. Shared Seluna sources remain unchanged.
Current candidates remain experimental; build success does not prove runtime safety.
