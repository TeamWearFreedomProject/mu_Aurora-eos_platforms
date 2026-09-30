# Aurora blue display hold diagnostic — 2026-09-30

## Purpose

The preceding direct-FrontPage diagnostic (commit
`3472bc8ae45224ac0e9e58a7f8762094a83136da`, run 36702325252)
displayed the blue marker briefly, then the screen disappeared and the owner
reported no recognized USB device. That test was accidentally flashed to
`boot_b`; fastboot access remained available and the owner reports restoring
stock boot. It must not be described as a temporary-boot observation.

The blue marker demonstrates that the diagnostic priority hook was reached
and could draw through GOP. USB absence is consistent with bypassing UFP,
but does not establish successful FrontPage entry or a crash.

This control experiment holds at the same priority hook without preparing or
starting FrontPage, UFP, LinuxLoader or another boot application.

## Behavior

- Request disabling the UEFI watchdog with `SetWatchdogTimer(0,0,0,NULL)`.
- Draw the same central blue rectangle once.
- Enter `CpuDeadLoop` immediately, with no console print or clear after drawing.

The framebuffer is not repainted repeatedly. This preserves evidence if it
is subsequently cleared or the panel stops displaying it. Interrupts,
already-scheduled events, inherited hardware watchdogs and earlier drivers
remain active as before; `CpuDeadLoop` is not a proof of whole-device inactivity.
The inherited GOP marker helper is best-effort and its absence is inconclusive.

The local library file retains its earlier `AuroraFrontPageDiagnostic` name
to keep the Aurora DSC binding unchanged. Its current priority-hook behavior
is **blue hold**, not direct FrontPage execution. Shared Seluna code is unchanged.

## Hardware observation to collect

Use temporary `fastboot boot` and the nosb image from the distinctly named
`aurora-CP2A-blue-hold-diagnostic-UNVERIFIED` artifact. Compare this test with
the preceding direct-FrontPage result, noting the differing installation method.

Observe for about 60 seconds and record:

- whether blue appears and how long it remains;
- whether the inherited logo returns or the watch visibly restarts;
- whether Windows recognizes any USB function and its VID/PID if present.

| Observation | Supported interpretation |
| --- | --- |
| Blue remains visible for 60 seconds | A static GOP image can remain visible at this BDS stop point. The additional FrontPage path, including image loading/constructors, ConnectAll, console mode and UI initialization, becomes the next comparison target. |
| Blue appears and then disappears | FrontPage execution is not required to reproduce display loss. Earlier/inherited display behavior, events, interrupts, reset or watchdog activity remain candidates. |
| No blue appears | Inconclusive: verify the image and investigate progress to the hook and GOP availability. |
| UFP-like USB is recognized | Not expected through this non-returning hook; verify image identity and other launch paths. |
| No USB is recognized | Expected possibility because no USB boot application is started; it does not distinguish success from failure. |

No result alone establishes safe relocation, a correct memory map or stable
UEFI execution. Restoring the earlier direct-FrontPage hook is a source change,
not a hardware partition operation.
