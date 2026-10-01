# Aurora UI substage diagnosis — 2026-10-01

## Observation
The owner reports that the numbered FrontPage image from commit
`0ca877f4acc64f7d78683c05e8234f61f5727ede` reached a green/teal 8 and stayed there,
with no USB device recognized. The downloaded image SHA256 matched the build.
Previously both this image and the older blue-hold image were refused by temporary
fastboot boot with Load Error. Stock boot_b and dtbo were subsequently flashed
successfully, and the numbered image was later accepted. The exact cause of the
transient refusal is unknown; successful flash is not proof of temporary-boot
compatibility. A full stock OS boot was not reported.

## Diagnostic design
Keep normal warning, authentication and rendering behavior. Add opt-in GOP
markers to identify call entry/return boundaries. No authentication is bypassed
and no USB function is added. The existing feature PCD still gates all markers.
The marker renderer now supports 1–99; colors repeat every ten markers.
Each marker still delays about two seconds. Record video from before boot and
allow at least 120 seconds. These delays alter timing and can hide/expose races.

## Numbers after 8
The execution sequence branches and numbers are not monotonically increasing.

| Number | Reached point / next work |
| --- | --- |
| 8 | HII/string initialization returned; marker delay then UI call |
| 11 | Entered InitializeFrontPageUI; calculate dimensions |
| 12 | Before NotifyUserOfAlerts |
| 31 | Before reading Secure Boot violation variable |
| 32 | Variable read returned; test violation flag |
| 33 | Violation branch: before blocking warning dialog |
| 34 | Warning dialog returned; variable cleanup follows |
| 13 | NotifyUserOfAlerts returned |
| 14 | Before CreateTopMenu |
| 21 | Before GetAuthToken(NULL) |
| 41 | Before authentication protocol lookup |
| 42 | Protocol lookup returned; error returns to caller |
| 43 | Before authentication protocol AuthWithPW |
| 44 | AuthWithPW returned; test result/token |
| 45 | Before token-interface allocation and protocol install |
| 46 | Protocol install returned |
| 22 | GetAuthToken returned |
| 23 | Authentication failed: before ChallengeUserPassword |
| 24 | Password challenge returned |
| 25 | Authentication branch completed; construct menu data and check optional menus |
| 26 | Before new_ListBox |
| 27 | new_ListBox returned; cleanup follows |
| 15 | CreateTopMenu returned; check null then RenderTitlebar |
| 16 | RenderTitlebar returned; RenderMasterFrame follows |
| 17 | RenderMasterFrame returned; CreateEventEx follows |
| 18 | CreateEventEx returned; test status and PcdSet64S |
| 19 | PcdSet64S returned; return UI initialization |
| 9 | UI initialization returned successfully; form display follows |
| 10 | FrontPage exit, including error return |
| Plain red | Diagnostic BDS hook returned from FrontPage/option setup |

A last visible number identifies the last observed boundary, not a proven exact
fault. A marker can itself fail to draw or its Stall can fail to complete.
Unchanged framebuffer contents do not prove CPU liveness. If 33 or 23 remains,
a blocking dialog is a strong candidate, but a marker immediately around the
underlying dialog input loop is needed to prove that it reached WaitForEvent.
If 8 remains without 11, do not blame UI internals yet.

Artifacts: `aurora-CP2A-frontpage-ui-stages-diagnostic-UNVERIFIED`.
Use only temporary fastboot boot for the requested comparison.
