# Aurora password-control construction diagnosis — 2026-10-01

## Latest observation
The owner reports upper 82 / lower 62 (yellow) on the password-status diagnostic
from commit `a80965272bbbcf419225ae86d96073f95c9cb408`. This confirms initial
GetAuthToken(NULL) returned EFI_DEVICE_ERROR and InitializeTheme returned.
There was no report of 83 or an actual password dialog. Input waiting has not
been demonstrated. 62 alone does not prove RNG failure or password state.

## Design
Retain all earlier execution stages and the lower authentication-status row.
Add call-boundary markers inside CreatePasswordDialog, CreateDialogControls
and DrawDialogFrame. Upper stage renderer now supports 1–999 so new upper
numbers are three digits; the lower status remains two digits.
No geometry repair, authentication bypass or password-state mutation is added.
Markers change timing and overwrite part of the dialog. Use this image only
for observation. Allow about four minutes and report the final upper/lower
numbers; video is optional.

## New upper-stage map

| Upper | Boundary reached / following work |
| --- | --- |
| 82 | theme initialized; before CreatePasswordDialog |
| 100 | entered CreatePasswordDialog; calculate canvas rectangle |
| 101 | before CreateDialogControls |
| 110 | controls locals initialized; before new_Canvas |
| 111 | new_Canvas returned; test null then caption coordinates |
| 112 | before caption font-height lookup |
| 113 | caption font-height lookup returned; finish font metadata |
| 114 | before caption new_Label |
| 115 | caption label creation returned |
| 116 | caption AddControl/GetControlBounds returned; body geometry/font |
| 118 | before body new_Label |
| 119 | body label creation returned |
| 120 | body AddControl/GetControlBounds returned; editbox geometry/font |
| 121 | prompt-password branch: before current-password new_EditBox |
| 122 | current-password editbox creation returned |
| 123 | editbox branch completed; error label geometry/font |
| 124 | before error-text new_Label |
| 125 | error label creation returned |
| 126 | before button text GetTextStringBitmapSize |
| 127 | button text measurement returned; test status then calculate dimensions |
| 128 | button dimensions calculated; oversize ASSERT check |
| 129 | before OK new_Button |
| 130 | OK button creation returned |
| 131 | before Cancel new_Button |
| 132 | Cancel button creation returned |
| 133 | default control/highlight set and output canvas assigned |
| 134 | CreateDialogControls returned; test status |
| 141 | before DrawDialogFrame |
| 151 | DrawDialogFrame locals initialized; compute frame rectangles |
| 152 | before four frame BltWindow calls |
| 153 | all four frame fills returned; background BltWindow follows |
| 154 | background fill returned; allocate title image buffer |
| 155 | title buffer allocation returned; test null then font metadata |
| 156 | before title text GetTextStringBitmapSize |
| 157 | title measurement returned; test status |
| 158 | before title StringToWindow |
| 159 | title StringToWindow returned |
| 142 | DrawDialogFrame returned |
| 83 | CreatePasswordDialog returned |

Earlier stages 87–91 still bracket input processing and first WaitForEvent.

## Interpretation limits
A last visible number proves only the displayed boundary was reached.
It does not alone prove the next call has entered or the CPU is alive.
The marker itself, its delay, interrupts, or loss of later drawing can still
explain a missing subsequent marker.

The source contains unsigned geometry differences for labels/title alignment
and large theme-scaled padding. This is a small-screen compatibility candidate,
not a demonstrated underflow in the owner's watch. We preserve the original
formulas in this diagnostic so evidence can localize the operation first.

Artifact: `aurora-CP2A-password-controls-diagnostic-UNVERIFIED`.
Use temporary fastboot boot; persistent flashing is not required.
