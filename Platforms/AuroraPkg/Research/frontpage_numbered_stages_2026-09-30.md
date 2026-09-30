# Aurora numbered FrontPage stages — 2026-09-30

## Evidence and purpose

The blue-hold diagnostic at commit `81e9339fb61bd5b4ef8d995bddb82b5950e00a0e`
(run 36706737467) displayed blue for approximately 60 seconds, according to
the owner, with no recognized USB device. The temporary-boot command log and
image hash were not collected. This is evidence that a static GOP marker can
remain visible at the priority hook. It does not prove safe/stable UEFI execution.

The preceding direct-FrontPage test displayed blue briefly, then lost display
and USB recognition. That test was accidentally flashed to boot_b and stock
boot was subsequently restored by the owner. The differing installation method
and unverified live firmware must be retained when comparing these results.

## Current behavior

Aurora's priority hook again directly attempts FrontPage, bypassing buttons
and normal UFP/default boot selection. It displays the plain blue BDS marker
for about two seconds first. On option-preparation failure or FrontPage return,
the hook displays a plain red marker and holds without normal fallback.

FrontPage has optional numbered GOP markers. They are gated by
`PcdAuroraFrontPageStageDiagnostic`, default **FALSE** in SelunaPkg.dec and
enabled **TRUE** only in the Aurora secureboot/nosb DSCs. Other platforms
retain their normal FrontPage behavior unless explicitly enabling this feature.

Numbers are drawn as 5x7 bitmaps using GOP rectangle fills. They do not depend
on console text, HII fonts, the window manager or UI toolkit. Each marker
reacquires GOP and makes a best-effort draw followed by a two-second Stall.
The marker does not validate a failing operation or repair any display state.

## Marker map

| Marker | Point reached | Next unmarked work |
| --- | --- | --- |
| Plain blue | BDS diagnostic priority hook | Prepare/load/start FrontPage, including application library constructors |
| 1, white | FrontPage UefiMain entry | BootNext deletion, watchdog disable, settings and secureboot key-store lookup |
| 2, yellow | Immediately before ConnectAll | EfiBootManagerConnectAll |
| 3, green | ConnectAll returned | SetGraphicsConsoleMode |
| 4, cyan | Console-mode call returned | Locate GOP/font/window manager/OSK and configure OSK |
| 5, magenta | Protocol/OSK path passed, before console clear | Disable cursor and ClearScreen |
| 6, orange | Console clear returned | InitializeUIToolKit |
| 7, violet | UI-toolkit initialization returned successfully | InitializeStringSupport and InitializeFrontPage |
| 8, teal | String/HII initialization calls returned | InitializeFrontPageUI |
| 9, light blue | FrontPage UI initialization returned successfully | CallFrontPage/form display and subsequent processing |
| 10, red with number | FrontPage is at its Exit label | Return to BDS; a plain red hold should follow |
| Plain red | FrontPage creation/execution returned to diagnostic hook | CpuDeadLoop; no normal UFP/default boot fallback |

A last visible number identifies the last observed marker, not necessarily the
exact failing instruction. Between markers, display might be cleared or disabled,
GOP might become unavailable, execution might hang/reset, or the marker itself
might not be visible. Number 10/plain red can also follow a normal menu exit.

## Collecting a useful observation

Use the nosb image from `aurora-CP2A-frontpage-stages-diagnostic-UNVERIFIED`.
Record the watch screen on video starting before temporary fastboot boot.
Report the last readable number, any later color/number, whether a menu appears,
and any restart/logo or USB identity. Allow about 60 seconds in total.

The marker delays change timing and may expose or hide a race. If the
instrumented menu works, a later comparison without the delays is required.
No new USB function is started by the marker helper, so absence of host USB
enumeration alone does not identify a failed stage.

Disable the FrontPage feature PCDs to remove in-app markers. Restore the
blue-hold priority hook from commit `81e9339fb61bd5b4ef8d995bddb82b5950e00a0e`
to return to the preceding control experiment.
