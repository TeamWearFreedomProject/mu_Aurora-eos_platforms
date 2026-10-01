# Aurora FrontPage text diagnostic — 2026-10-01

## Observation and scope

The owner reports that the previous controls diagnostic remains at upper 132, lower 62 (yellow). Stage 132 is drawn after CancelButton creation but before its null check and canvas registration. Lower 62 classified the initial GetAuthToken(NULL) return as EFI_DEVICE_ERROR. This does not establish that a password was configured, which auth sub-operation failed, or which subsequent UI call fails.

This version renders small hand-defined 5x7 ASCII glyphs directly through GOP fills. It does not depend on HII fonts, the console, the window manager, heap allocation, USB, or ADB. It is an on-screen diagnostic, not an interactive shell.

## Screen rows

1. AURORA DIAGNOSTIC
2. STAGE and the last boundary number
3. Operation name
4. Boundary: BEFORE CALL, RETURNED, or another named observation
5. AUTH RESULT
6. Initial authentication EFI status name, or NOT RUN
7. Initial authentication raw 64-bit status in hexadecimal
8. UI and the last tracked UI operation name
9. Last tracked UI return status name, or NOT RUN
10. Last tracked UI raw status in hexadecimal

AUTH RESULT retains the first GetAuthToken(NULL) result; UI tracks only the three calls listed below. EFI_DEVICE_ERROR on AARCH64 is 8000000000000007. An unlisted status is labelled OTHER STATUS with its exact raw value. No return value exists to display when a call has not returned.

## Additional call boundaries after 132

| Stage | Operation | Boundary |
| --- | --- | --- |
| 135 | ADD CANCEL | Before DialogCanvas->AddControl |
| 136 | ADD CANCEL | Returned; UI status captured |
| 137 | SET DEFAULT | Before DialogCanvas->SetDefaultControl |
| 138 | SET DEFAULT | Returned; UI status captured |
| 139 | SET HIGHLIGHT | Before DialogCanvas->SetHighlight |
| 140 | SET HIGHLIGHT | Returned; UI status captured |
| 133 | OUTPUT CANVAS | Output pointer assigned |
| 134 | CREATE CONTROLS | Outer caller observes return |

All existing markers remain; numeric ordering does not imply execution ordering.

The pinned mu_plus Canvas.c (2761c3a83e441f439fb3d90e61972801495b1196) shows that SetDefaultControl and SetHighlight can call a child control's Draw before the outer dialog frame is drawn. AddControl links a new canvas node and queries child bounds. The split observes these paths without choosing a root cause. The captured return values do not change the original Status variable or error-handling flow.

## How to observe

Download the successful Actions run's artifact named aurora-CP2A-text-diagnostic-UNVERIFIED. Use the noSB fastboot candidate for a temporary fastboot boot. Allow about four minutes because each reached marker deliberately delays two seconds. Report the last stage, operation, boundary, AUTH result and UI result. A final written transcription is sufficient.

Do not flash these diagnostic candidates. Firmware layout, inherited initialization and hardware operation remain unverified.

The renderer is best effort. It requires usable GOP and may itself fail or perturb timing. A BEFORE CALL display precedes both the marker delay and the following call; it does not prove that call was entered. A static display does not prove the CPU is still executing. SUCCESS on a tracked UI call does not establish that the entire interface works. USB absence alone is not a localized USB fault.

## Validation

GitHub Actions compiles the firmware, builds the inherited-address BootShim, assembles the CP2A candidates and runs existing structural checks. Successful CI does not establish watch-side compatibility. New text and call-boundary behavior requires the next hardware observation.
