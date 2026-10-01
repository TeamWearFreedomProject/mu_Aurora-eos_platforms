# Default-control diagnostic — 2026-10-01

## Hardware observations

The supplied photos show stage 118 (BODY LABEL / BEFORE CALL) and later stage 137 (SET DEFAULT / BEFORE CALL). At 137, UI ADD CANCEL reports EFI_SUCCESS (0000000000000000), while the retained initial authentication result is EFI_DEVICE_ERROR (8000000000000007). The earlier photo is not evidence of a persistent stop at 118.

The later photo establishes that the diagnostic drew the boundary before SetDefaultControl and that cancel registration returned successfully. It does not establish which internal step stops. Marker delays and rendering precede the call, and a still image does not prove CPU activity.

## New boundaries

| Stage | Operation | Meaning |
| --- | --- | --- |
| 171 | DEFAULT SEARCH | Before searching the canvas child list |
| 172 | DEFAULT SEARCH | Search completed; success or not-found path follows |
| 173 | DEFAULT SEARCH | Target not found |
| 174 | BUTTON STATE | Before child SetControlState(KEYDEFAULT) |
| 175 | BUTTON STATE | State call returned |
| 176 | BUTTON DRAW | Before child Draw(FALSE, NULL, NULL) |
| 177 | BUTTON DRAW | Draw returned |
| 178 | SET DEFAULT | Before returning from SetDefaultControl |
| 138 | SET DEFAULT | Outer caller captured EFI status |

These boundaries do not replace the existing authentication and UI result rows. UI ADD CANCEL remains the last captured EFI result until SetDefaultControl returns. The new markers observe completion; they do not capture the child Draw's OBJECT_STATE or the SetControlState return value.

If 176 persists without 177, drawing or the boundary's own rendering/delay becomes the next focus. This alone does not identify a failing font or GOP implementation. Search, state and draw are unchanged, including their original ignored return values.

## Implementation

tools/patch_aurora_canvas_diagnostic.py modifies only the pinned mu_plus Canvas.c during Aurora builds. It rejects a different mu_plus commit or different source anchors, and permits an already applied identical patch. build_fd_aurora.sh applies it before both firmware builds.

The patch adds a callback initialized to NULL in each statically linked SimpleUIToolKit library instance. Diagnostic FrontPage alone installs AuroraFrontPageStage at entry under PcdAuroraFrontPageStageDiagnostic. Other modules do not install it, so their SetDefaultControl does not draw these diagnostics. The registration uses the same ordinary C calling convention as AuroraFrontPageStage.

Pinned source: microsoft/mu_plus, 2761c3a83e441f439fb3d90e61972801495b1196, MsGraphicsPkg/Library/SimpleUIToolKit/Canvas.c. The original license notice is preserved. This build patch is temporary instrumentation, not a upstream fix.

## Validation and use

The patch script was checked for Python syntax, exact transformation, unchanged surrounding code, repeat application and rejection of source drift. GitHub Actions must additionally compile both firmware variants and structurally validate candidates. Watch-side operation remains unverified.

Download aurora-CP2A-default-control-diagnostic-UNVERIFIED from the successful Actions run. Temporarily boot the noSB fastboot candidate; do not flash it. Allow around four minutes for intentional two-second markers. Transcribe the final stage, operation, boundary, AUTH RESULT and UI result; video is unnecessary.
