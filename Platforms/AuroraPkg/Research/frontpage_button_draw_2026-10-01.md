# Button-draw diagnostic — 2026-10-01

## Latest observation

The owner's photo shows stage 176, BUTTON DRAW / BEFORE CALL. UI ADD CANCEL remains EFI_SUCCESS (0000000000000000), while the retained initial authentication result is EFI_DEVICE_ERROR (8000000000000007). This establishes that the default-control search passed and child SetControlState returned. Stage 177 (child Draw returned) is not observed. It does not establish the root cause or prove the call was entered after the marker's own drawing and delay.

## New stages

| Stage | Operation | Boundary |
| --- | --- | --- |
| 181 | BUTTON DRAW | ENTERED |
| 182 | RENDER BUTTON | BEFORE CALL |
| 183 | RENDER BUTTON | RETURNED |
| 184 | BUTTON DRAW | BEFORE RETURN |
| 201 | RENDER BUTTON | ENTERED |
| 202 | FONT INFO | BEFORE CALL |
| 203 | FONT INFO | RETURNED |
| 204 | IMAGE BUFFER | BEFORE ALLOC |
| 205 | IMAGE BUFFER | ALLOC RETURNED |
| 206 | GOP AND BOUNDS | BEFORE READ |
| 207 | GOP AND BOUNDS | READ COMPLETED |
| 208 | BUTTON BORDER | BEFORE CALL |
| 209 | BUTTON BORDER | RETURNED |
| 210 | BUTTON FILL | BEFORE CALL |
| 211 | BUTTON FILL | RETURNED |
| 212 | FOCUS OUTLINE | BEFORE CHECK |
| 213 | FOCUS OUTLINE | CHECK COMPLETED |
| 214 | BUTTON TEXT | BEFORE CALL |
| 215 | BUTTON TEXT | RETURNED |
| 216 | RENDER CLEANUP | BEFORE FREE |
| 217 | RENDER BUTTON | BEFORE RETURN |

In the first SetDefaultControl draw, DrawHighlight is FALSE and pInputState is NULL. Button Draw's no-input path calls RenderButton. Its original rendering order is color selection, font-info preparation, image-output allocation, GOP/geometry reads, outer border, inner fill, optional focus outline, text, cleanup. No operation is skipped.

BUTTON FILL and BUTTON TEXT now capture the actual EFI_STATUS returned by BltWindow and StringToWindow in the UI row. They do not change the RenderButton Status variable or error flow. This upstream routine normally ignores these two returns and may return EFI_SUCCESS despite a failed draw; do not interpret an outer SUCCESS as proof of successful drawing. A setup allocation error is separately recorded as RENDER SETUP. If a call never returns, UI remains the most recently captured result.

## Implementation

The pinned build-time toolkit patch now transforms Canvas.c and Button.c. Canvas exports stage/result bridge functions whose callbacks start NULL in each statically linked library instance. Diagnostic FrontPage alone registers its stage renderer and UI-result recorder. Other modules do not register callbacks.

All source anchors in both files are validated before either file is written. Repeated identical application is permitted; an incompatible upstream revision or source edit is rejected. Original source notices remain intact. Source pin: microsoft/mu_plus 2761c3a83e441f439fb3d90e61972801495b1196.

The Button Draw entry marker precedes its original bounds-pointer assignment, allowing invalid object pointers to be distinguished from later RenderButton work. The pointer is initially NULL and assigned before its original uses.

## Validation and observation

Local checks cover exact transformations, unchanged surrounding source, idempotence, and rejection of source drift before partial application. GitHub Actions compiles both firmware variants and structurally validates candidate images. Watch-side operation remains unverified.

Artifact: aurora-CP2A-button-draw-diagnostic-UNVERIFIED. Temporarily fastboot boot the noSB candidate; do not flash. Allow around five minutes for the accumulated two-second stage delays, then report the last stage, operation, boundary and UI result. A photo or text transcription suffices.

Diagnostics remain best effort and perturb timing and visible content. A static BEFORE marker alone does not prove continued CPU execution or entry into the next call. Any persistent new boundary also includes the diagnostic renderer/delay as a possible stopping point. The original authentication error remains a separate observation.
