# Aurora authentication status and password-dialog diagnosis — 2026-10-01

## Latest observation
The owner reports that the UI-substage image from commit
`a7114333f7faa43877c081a94aa950b5456a4a3a` ultimately remains at 23, without
a visible password screen or USB device. Video is unavailable due to the school
PC camera. This proves execution reached the branch where GetAuthToken(NULL)
returned a status other than EFI_SUCCESS. It does not prove a password is set,
that ChallengeUserPassword has entered, or that an input loop has been reached.

## Two rows
After initial authentication returns an error, each marker shows:
- Upper row: current execution stage.
- Lower row: class of the original GetAuthToken(NULL) return status.
The lower row is retained through subsequent markers and is NOT a stage number.
The original exact EFI_STATUS is also written to DEBUG output. No new USB log
transport is introduced. Authentication and dialog paths are not bypassed.

| Lower row | Status class |
| --- | --- |
| absent | initial authentication returned EFI_SUCCESS |
| 61 | EFI_NOT_FOUND |
| 62 | EFI_DEVICE_ERROR |
| 63 | EFI_SECURITY_VIOLATION |
| 64 | EFI_OUT_OF_RESOURCES |
| 65 | EFI_ACCESS_DENIED |
| 66 | EFI_UNSUPPORTED |
| 67 | EFI_NOT_READY |
| 68 | other non-success status; DEBUG log needed for exact status |

62 does not by itself prove an RNG failure. AuthWithPW may return DEVICE_ERROR
when token creation fails, which includes RNG or mapping failure; other
GetAuthToken work can also fail. 63 does not by itself prove the user set a
password; further inspection of password-store state is required.

## New execution stages
Existing stages 1–46 retain their earlier meaning.

| Upper row | Reached boundary / following work |
| --- | --- |
| 23 | before ChallengeUserPassword, including marker delay |
| 51 | entered ChallengeUserPassword; before initial HiiGetString |
| 52 | initial empty error string retrieved; more dialog strings follow |
| 53 | dialog title/caption/body strings retrieved; before SwmDialogsPasswordPrompt |
| 54 | password prompt returned; inspect error/cancel/result |
| 71 | entered PasswordDialogInternal; validate args/read GOP |
| 72 | read GOP resolution; calculate dialog bounds and locate OSK |
| 73 | OSK lookup path returned; hide keyboard and icon |
| 74 | hide calls returned; before SetKeyboardSize |
| 75 | SetKeyboardSize returned; SetKeyboardPosition follows |
| 76 | SetKeyboardPosition returned; ShowDockAndCloseButtons follows |
| 77 | OSK setup path passed; before SWM RegisterClient |
| 78 | RegisterClient returned; test status then ActivateWindow |
| 79 | ActivateWindow returned; EnableMousePointer follows |
| 81 | EnableMousePointer returned; InitializeTheme follows |
| 82 | InitializeTheme returned; CreatePasswordDialog follows |
| 83 | CreatePasswordDialog returned; test status |
| 84 | before ProcessDialogInput |
| 87 | entered input processor; access keyboard/pointer event handles |
| 88 | before first canvas Draw in each outer iteration |
| 89 | Draw returned; focus/button processing follows |
| 90 | immediately before first WaitForEvent call |
| 91 | first WaitForEvent call returned |
| 85 | input processor returned; dialog cleanup follows |

90 identifies the call boundary, not proof that the internal WaitForEvent loop
has started: marker drawing/Stall can itself fail. A visible 91 proves the call
returned. Markers overwrite part of the dialog, so this image is for observation,
not normal use. Delays can change races. Each marker delays about two seconds;
allow about three minutes. Record the final upper/lower pair; video is optional.

## Isolation and provenance
Only Aurora DSCs define AURORA_FRONTPAGE_PASSWORD_DIAGNOSTIC. A conditional
FrontPage component library override selects Aurora's diagnostic dialog library.
Other modules and other platforms retain the upstream SwmDialogsLib.
PasswordDialog.c, SwmDialogs.h and strings originate from microsoft/mu_plus
commit `2761c3a83e441f439fb3d90e61972801495b1196`, under BSD-2-Clause-Patent.
Unmodified dialog source files are exact local copies of the pinned upstream
source. EDK2's string-token scan must see the source directly; include wrappers
failed compilation because referenced string tokens were not generated. FrontPage exports the feature-gated
marker to its diagnostic library. Removing the Aurora DEFINE restores upstream
dialog selection; disabling the diagnostic PCD disables all stage marks.

Artifact: `aurora-CP2A-password-status-diagnostic-UNVERIFIED`.
Use temporary fastboot boot; no persistent flashing is needed for this test.
