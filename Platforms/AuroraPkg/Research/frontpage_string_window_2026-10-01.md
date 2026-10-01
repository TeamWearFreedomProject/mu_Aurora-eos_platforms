# StringToWindow diagnostic — 2026-10-01

## Hardware observation

The owner's latest photo shows stage 214, BUTTON TEXT / BEFORE CALL. UI BUTTON FILL reports EFI_SUCCESS (0000000000000000); initial authentication remains EFI_DEVICE_ERROR (8000000000000007). The outer border call returned, the inner fill returned success, and the DrawHighlight check completed. Stage 215 (StringToWindow returned) is not observed.

The marker itself is rendered and delayed before calling StringToWindow. The observation narrows the next investigation to this boundary and its call, not a proven font/GOP root cause.

## New boundaries

| Stage | Operation | Boundary |
| --- | --- | --- |
| 271 | PAINT BEGIN | Before rendering-engine SetModeSurface(PAINT_BEGIN) |
| 272 | PAINT BEGIN | Returned; exact EFI status captured |
| 273 | FONT STRING IMAGE | Before HII font StringToImage |
| 274 | FONT STRING IMAGE | Returned; exact EFI status captured |
| 275 | PAINT END | Before rendering-engine SetModeSurface(PAINT_END) |
| 276 | PAINT END | Returned; exact EFI status captured |

StringToWindow's original calls, arguments, ordering and return semantics are preserved. Paint begin/end returns were originally ignored and are now only recorded diagnostically; StringToImage still determines the function's return value.

If 273 persists without 274, StringToImage becomes the next focus, but its implementation may contain both font work and direct screen output. This marker does not separate those internals. If 271 or 275 persists, the corresponding rendering-engine boundary is the next focus. The last UI result remains a previous result until a call returns.

## Cross-driver bridge and gating

Window Manager is a separate UEFI driver, so FrontPage's static library callback cannot by itself expose the internal boundaries. A private volatile diagnostic protocol carries version, IsArmed, Stage and Result callbacks between the modules. Its GUID is 9e7b77f3-b8c4-4d79-a515-835c24307c62.

Diagnostic FrontPage installs the interface at entry under PcdAuroraFrontPageStageDiagnostic and attempts to remove it before returning. Stage 214 arms tracing; stage 215 disarms it. Earlier label rendering is not traced. The Window Manager finds and validates the interface and checks IsArmed before emitting markers. If registration failed, stage 214 instead shows TRACE UNAVAILABLE with TRACE INSTALL status in the UI row.

The shared header is checked into FrontPage and copied to the pinned Window Manager build checkout. The existing build patch validates Canvas, Button and SWM source transformations before writing any C file. Other consumers retain their original rendering flow and do not emit markers unless the private interface is present and armed.

## Validation and use

Patch checks cover exact SWM transformation, repeated application and rejection of changed source before partial C writes. GitHub Actions additionally must compile both firmware variants and structurally validate the candidates. Hardware operation remains unverified.

Artifact: aurora-CP2A-string-window-diagnostic-UNVERIFIED. Temporarily boot the noSB fastboot candidate; do not flash. Allow about five minutes for the accumulated two-second diagnostic markers. Report the last stage, operation, boundary and UI result; a final photo or transcription is sufficient.

The diagnostic renderer can perturb timing or itself fail, especially while a rendering surface is in PAINT_BEGIN. It uses raw GOP fills and does not recurse into StringToWindow. A static display alone does not prove the processor is still executing. Initial auth error and rendering status remain distinct observations.
