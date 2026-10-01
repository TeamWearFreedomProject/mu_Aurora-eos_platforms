/** @file
  Private, transient bridge for Aurora StringToWindow diagnostics.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/
#ifndef AURORA_STRING_DIAGNOSTIC_PROTOCOL_H
#define AURORA_STRING_DIAGNOSTIC_PROTOCOL_H
#define AURORA_STRING_DIAGNOSTIC_REVISION 1
STATIC EFI_GUID mAuroraStringDiagnosticGuid = {
  0x9e7b77f3, 0xb8c4, 0x4d79, {0xa5,0x15,0x83,0x5c,0x24,0x30,0x7c,0x62}
};
typedef struct {
  UINT64 Revision;
  BOOLEAN (*IsArmed)(VOID);
  VOID (*Stage)(IN UINTN Stage);
  VOID (*Result)(IN CONST CHAR8 *Operation, IN EFI_STATUS Status);
} AURORA_STRING_DIAGNOSTIC_PROTOCOL;
#endif
