/** @file
  Font-independent 5x7 diagnostic text. No HII, console, SWM or heap dependency.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/
#ifndef AURORA_DIAGNOSTIC_TEXT_H
#define AURORA_DIAGNOSTIC_TEXT_H

STATIC CONST UINT8 mAuroraLetterGlyphs[26][7] = {
  {14,17,17,31,17,17,17},
  {30,17,17,30,17,17,30},
  {14,17,16,16,16,17,14},
  {30,17,17,17,17,17,30},
  {31,16,16,30,16,16,31},
  {31,16,16,30,16,16,16},
  {14,17,16,23,17,17,15},
  {17,17,17,31,17,17,17},
  {14,4,4,4,4,4,14},
  {7,2,2,2,18,18,12},
  {17,18,20,24,20,18,17},
  {16,16,16,16,16,16,31},
  {17,27,21,21,17,17,17},
  {17,25,21,19,17,17,17},
  {14,17,17,17,17,17,14},
  {30,17,17,30,16,16,16},
  {14,17,17,17,21,18,13},
  {30,17,17,30,20,18,17},
  {15,16,16,14,1,1,30},
  {31,4,4,4,4,4,4},
  {17,17,17,17,17,17,14},
  {17,17,17,17,17,10,4},
  {17,17,17,21,21,21,10},
  {17,17,10,4,10,17,17},
  {17,17,10,4,4,4,4},
  {31,1,2,4,8,16,31}
};
STATIC CONST UINT8 mAuroraDigitGlyphs[10][7] = {
  {14,17,19,21,25,17,14}, {4,12,4,4,4,4,14},
  {14,17,1,2,4,8,31}, {30,1,1,14,1,1,30},
  {2,6,10,18,31,2,2}, {31,16,16,30,1,1,30},
  {14,16,16,30,17,17,14}, {31,1,2,4,8,8,8},
  {14,17,17,14,17,17,14}, {14,17,17,15,1,1,14}
};

typedef struct {
  UINTN Stage;
  CONST CHAR8 *Operation;
  CONST CHAR8 *Boundary;
} AURORA_STAGE_TEXT;

STATIC CONST AURORA_STAGE_TEXT mAuroraStageText[] = {
  {1, "FRONTPAGE", "ENTERED"},
  {2, "CONNECT ALL", "BEFORE CALL"},
  {3, "CONNECT ALL", "RETURNED"},
  {4, "CONSOLE MODE", "RETURNED"},
  {5, "CLEAR SCREEN", "BEFORE CALL"},
  {6, "CLEAR SCREEN", "RETURNED"},
  {7, "UI TOOLKIT", "RETURNED"},
  {8, "HII INIT", "RETURNED"},
  {9, "FRONTPAGE UI", "RETURNED"},
  {10, "FRONTPAGE", "EXIT"},
  {11, "UI INIT", "ENTERED"},
  {12, "ALERTS", "BEFORE CALL"},
  {13, "ALERTS", "RETURNED"},
  {14, "TOP MENU", "BEFORE CALL"},
  {15, "TOP MENU", "RETURNED"},
  {16, "TITLEBAR", "RETURNED"},
  {17, "MASTER FRAME", "RETURNED"},
  {18, "CREATE EVENT", "RETURNED"},
  {19, "POINTER PCD", "RETURNED"},
  {21, "GET AUTH TOKEN", "BEFORE CALL"},
  {22, "GET AUTH TOKEN", "RETURNED"},
  {23, "PASSWORD PROMPT", "BEFORE CALL"},
  {24, "PASSWORD PROMPT", "RETURNED"},
  {25, "AUTH BRANCH", "COMPLETED"},
  {26, "MENU LISTBOX", "BEFORE CALL"},
  {27, "MENU LISTBOX", "RETURNED"},
  {31, "ALERT VARIABLE", "BEFORE READ"},
  {32, "ALERT VARIABLE", "READ RETURNED"},
  {33, "WARNING DIALOG", "BEFORE CALL"},
  {34, "WARNING DIALOG", "RETURNED"},
  {41, "AUTH PROTOCOL", "BEFORE LOOKUP"},
  {42, "AUTH PROTOCOL", "LOOKUP RETURNED"},
  {43, "AUTH WITH PW", "BEFORE CALL"},
  {44, "AUTH WITH PW", "RETURNED"},
  {45, "TOKEN INSTALL", "BEFORE SETUP"},
  {46, "TOKEN INSTALL", "RETURNED"},
  {51, "PASSWORD PROMPT", "ENTERED"},
  {52, "ERROR STRING", "LOOKUP RETURNED"},
  {53, "PASSWORD DIALOG", "BEFORE CALL"},
  {54, "PASSWORD DIALOG", "RETURNED"},
  {71, "DIALOG INTERNAL", "ENTERED"},
  {72, "GOP RESOLUTION", "READ"},
  {73, "OSK LOOKUP", "RETURNED"},
  {74, "KEYBOARD SIZE", "BEFORE CALL"},
  {75, "KEYBOARD SIZE", "RETURNED"},
  {76, "KEYBOARD POSITION", "RETURNED"},
  {77, "REGISTER WINDOW", "BEFORE CALL"},
  {78, "REGISTER WINDOW", "RETURNED"},
  {79, "ACTIVATE WINDOW", "RETURNED"},
  {81, "THEME INIT", "BEFORE CALL"},
  {82, "CREATE DIALOG", "BEFORE CALL"},
  {83, "CREATE DIALOG", "RETURNED"},
  {84, "INPUT PROCESSOR", "BEFORE CALL"},
  {85, "INPUT PROCESSOR", "RETURNED"},
  {87, "INPUT PROCESSOR", "ENTERED"},
  {88, "CANVAS DRAW", "BEFORE CALL"},
  {89, "CANVAS DRAW", "RETURNED"},
  {90, "WAIT FOR INPUT", "BEFORE CALL"},
  {91, "WAIT FOR INPUT", "RETURNED"},
  {100, "CREATE DIALOG", "ENTERED"},
  {101, "CREATE CONTROLS", "BEFORE CALL"},
  {110, "NEW CANVAS", "BEFORE CALL"},
  {111, "NEW CANVAS", "RETURNED"},
  {112, "CAPTION FONT", "BEFORE LOOKUP"},
  {113, "CAPTION FONT", "LOOKUP RETURNED"},
  {114, "CAPTION LABEL", "BEFORE CALL"},
  {115, "CAPTION LABEL", "RETURNED"},
  {116, "CAPTION BOUNDS", "RETURNED"},
  {118, "BODY LABEL", "BEFORE CALL"},
  {119, "BODY LABEL", "RETURNED"},
  {120, "BODY BOUNDS", "RETURNED"},
  {121, "PASSWORD EDITBOX", "BEFORE CALL"},
  {122, "PASSWORD EDITBOX", "RETURNED"},
  {123, "EDITBOX SETUP", "COMPLETED"},
  {124, "ERROR LABEL", "BEFORE CALL"},
  {125, "ERROR LABEL", "RETURNED"},
  {126, "BUTTON TEXT SIZE", "BEFORE CALL"},
  {127, "BUTTON TEXT SIZE", "RETURNED"},
  {128, "BUTTON FIT CHECK", "BEFORE CHECK"},
  {129, "OK BUTTON", "BEFORE CALL"},
  {130, "OK BUTTON", "RETURNED"},
  {131, "CANCEL BUTTON", "BEFORE CALL"},
  {132, "CANCEL BUTTON", "RETURNED"},
  {135, "ADD CANCEL", "BEFORE CALL"},
  {136, "ADD CANCEL", "RETURNED"},
  {137, "SET DEFAULT", "BEFORE CALL"},
  {138, "SET DEFAULT", "RETURNED"},
  {139, "SET HIGHLIGHT", "BEFORE CALL"},
  {140, "SET HIGHLIGHT", "RETURNED"},
  {133, "OUTPUT CANVAS", "ASSIGNED"},
  {134, "CREATE CONTROLS", "RETURNED"},
  {141, "DRAW FRAME", "BEFORE CALL"},
  {142, "DRAW FRAME", "RETURNED"},
  {151, "DRAW FRAME", "ENTERED"},
  {152, "FRAME FILL", "BEFORE CALLS"},
  {153, "FRAME FILL", "RETURNED"},
  {154, "BACKGROUND FILL", "RETURNED"},
  {155, "TITLE BUFFER", "ALLOCATED"},
  {156, "TITLE TEXT SIZE", "BEFORE CALL"},
  {157, "TITLE TEXT SIZE", "RETURNED"},
  {158, "TITLE STRING DRAW", "BEFORE CALL"},
  {159, "TITLE STRING DRAW", "RETURNED"},
  {171, "DEFAULT SEARCH", "BEFORE SEARCH"},
  {172, "DEFAULT SEARCH", "COMPLETED"},
  {173, "DEFAULT SEARCH", "NOT FOUND"},
  {174, "BUTTON STATE", "BEFORE CALL"},
  {175, "BUTTON STATE", "RETURNED"},
  {176, "BUTTON DRAW", "BEFORE CALL"},
  {177, "BUTTON DRAW", "RETURNED"},
  {178, "SET DEFAULT", "BEFORE RETURN"},
  {181, "BUTTON DRAW", "ENTERED"},
  {182, "RENDER BUTTON", "BEFORE CALL"},
  {183, "RENDER BUTTON", "RETURNED"},
  {184, "BUTTON DRAW", "BEFORE RETURN"},
  {201, "RENDER BUTTON", "ENTERED"},
  {202, "FONT INFO", "BEFORE CALL"},
  {203, "FONT INFO", "RETURNED"},
  {204, "IMAGE BUFFER", "BEFORE ALLOC"},
  {205, "IMAGE BUFFER", "ALLOC RETURNED"},
  {206, "GOP AND BOUNDS", "BEFORE READ"},
  {207, "GOP AND BOUNDS", "READ COMPLETED"},
  {208, "BUTTON BORDER", "BEFORE CALL"},
  {209, "BUTTON BORDER", "RETURNED"},
  {210, "BUTTON FILL", "BEFORE CALL"},
  {211, "BUTTON FILL", "RETURNED"},
  {212, "FOCUS OUTLINE", "BEFORE CHECK"},
  {213, "FOCUS OUTLINE", "CHECK COMPLETED"},
  {214, "BUTTON TEXT", "BEFORE CALL"},
  {215, "BUTTON TEXT", "RETURNED"},
  {216, "RENDER CLEANUP", "BEFORE FREE"},
  {217, "RENDER BUTTON", "BEFORE RETURN"}
};

STATIC
CONST UINT8 *
AuroraDiagnosticGlyph (
  IN CHAR8 Character
  )
{
  STATIC CONST UINT8 Blank[7] = {0,0,0,0,0,0,0};
  STATIC CONST UINT8 Underline[7] = {0,0,0,0,0,0,31};
  STATIC CONST UINT8 Question[7] = {14,17,1,2,4,0,4};
  if ((Character >= 'A') && (Character <= 'Z')) {
    return mAuroraLetterGlyphs[Character - 'A'];
  }
  if ((Character >= 'a') && (Character <= 'z')) {
    return mAuroraLetterGlyphs[Character - 'a'];
  }
  if ((Character >= '0') && (Character <= '9')) {
    return mAuroraDigitGlyphs[Character - '0'];
  }
  if (Character == ' ') {
    return Blank;
  }
  if (Character == '_') {
    return Underline;
  }
  return Question;
}

STATIC
VOID
AuroraDiagnosticTextLine (
  IN EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop,
  IN CONST CHAR8 *Text,
  IN UINTN CenterX,
  IN UINTN Y,
  IN UINTN MaxWidth,
  IN UINTN PreferredScale
  )
{
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL Ink = {255,255,255,0};
  CONST UINT8 *Glyph;
  UINTN Length;
  UINTN Scale;
  UINTN X;
  UINTN Index;
  UINTN Row;
  UINTN Col;

  Length = AsciiStrLen (Text);
  if ((Length == 0) || (Length > 64) || (PreferredScale == 0)) {
    return;
  }
  Scale = MIN (PreferredScale, MaxWidth / (Length * 6 - 1));
  if (Scale == 0) {
    return;
  }
  X = CenterX - ((Length * 6 - 1) * Scale) / 2;
  for (Index = 0; Index < Length; Index++) {
    Glyph = AuroraDiagnosticGlyph (Text[Index]);
    for (Row = 0; Row < 7; Row++) {
      for (Col = 0; Col < 5; Col++) {
        if ((Glyph[Row] & (1U << (4 - Col))) != 0) {
          Gop->Blt (Gop, &Ink, EfiBltVideoFill, 0, 0,
                    X + (Index * 6 + Col) * Scale, Y + Row * Scale,
                    Scale, Scale, 0);
        }
      }
    }
  }
}

STATIC
CONST CHAR8 *
AuroraDiagnosticStatusName (
  IN EFI_STATUS Status
  )
{
  switch (Status) {
    case EFI_SUCCESS:            return "EFI_SUCCESS";
    case EFI_NOT_FOUND:          return "EFI_NOT_FOUND";
    case EFI_DEVICE_ERROR:       return "EFI_DEVICE_ERROR";
    case EFI_SECURITY_VIOLATION: return "EFI_SECURITY_VIOLATION";
    case EFI_OUT_OF_RESOURCES:   return "EFI_OUT_OF_RESOURCES";
    case EFI_ACCESS_DENIED:      return "EFI_ACCESS_DENIED";
    case EFI_UNSUPPORTED:        return "EFI_UNSUPPORTED";
    case EFI_NOT_READY:          return "EFI_NOT_READY";
    default:                    return "OTHER STATUS";
  }
}
#endif
