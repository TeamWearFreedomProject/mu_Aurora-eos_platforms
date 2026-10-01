#!/usr/bin/env python3
"""Apply the narrowly scoped Canvas diagnostic hook to pinned mu_plus sources.

The callback is NULL in every library instance except diagnostic FrontPage.
Reject changed upstream code instead of silently patching an incompatible version.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "Common/MU"
PIN = "2761c3a83e441f439fb3d90e61972801495b1196"
TARGET = UPSTREAM / "MsGraphicsPkg/Library/SimpleUIToolKit/Canvas.c"
ORIGINAL = "static\nEFI_STATUS\nSetDefaultControl (\n  IN struct _Canvas  *this,\n  IN VOID            *pControl\n  )\n{\n  EFI_STATUS                Status        = EFI_NOT_FOUND;\n  UIT_CANVAS_CHILD_CONTROL  *pControlList = this->m_pControls;\n  ControlBase               *pControlBase;\n\n  // TODO: Need to check whether there's already a default control?\n\n  // Walk through the list of child controls, looking for the caller-specified control.\n  //\n  while (NULL != pControlList) {\n    // If we found it set it as the default control.\n    //\n    if (pControlList->pControl == pControl) {\n      this->m_pDefaultControl = pControlList;\n      Status                  = EFI_SUCCESS;\n      break;\n    }\n\n    pControlList = pControlList->pNext;\n  }\n\n  if (EFI_ERROR (Status)) {\n    DEBUG ((DEBUG_INFO, \"INFO [SUIT]: Failed to find canvas child control to set as default (%r).\\r\\n\", Status));\n    goto Exit;\n  }\n\n  // Update the control's state so it can signal that it's the default (visual indicator) then draw.\n  //\n  pControlBase = (ControlBase *)this->m_pDefaultControl->pControl;\n\n  pControlBase->SetControlState (\n                  pControlBase,\n                  KEYDEFAULT\n                  );\n\n  pControlBase->Draw (\n                  pControlBase,\n                  FALSE,\n                  NULL,\n                  NULL\n                  );\n\nExit:\n\n  return Status;\n}\n"
REPLACEMENT = "static\nEFI_STATUS\nSetDefaultControl (\n  IN struct _Canvas  *this,\n  IN VOID            *pControl\n  )\n{\n  EFI_STATUS                Status        = EFI_NOT_FOUND;\n  UIT_CANVAS_CHILD_CONTROL  *pControlList = this->m_pControls;\n  ControlBase               *pControlBase;\n\n  AuroraCanvasDiagnosticStage (171);\n\n  // TODO: Need to check whether there's already a default control?\n\n  // Walk through the list of child controls, looking for the caller-specified control.\n  //\n  while (NULL != pControlList) {\n    // If we found it set it as the default control.\n    //\n    if (pControlList->pControl == pControl) {\n      this->m_pDefaultControl = pControlList;\n      Status                  = EFI_SUCCESS;\n      break;\n    }\n\n    pControlList = pControlList->pNext;\n  }\n\n  AuroraCanvasDiagnosticStage (172);\n  if (EFI_ERROR (Status)) {\n    AuroraCanvasDiagnosticStage (173);\n    DEBUG ((DEBUG_INFO, \"INFO [SUIT]: Failed to find canvas child control to set as default (%r).\\r\\n\", Status));\n    goto Exit;\n  }\n\n  // Update the control's state so it can signal that it's the default (visual indicator) then draw.\n  //\n  pControlBase = (ControlBase *)this->m_pDefaultControl->pControl;\n\n  AuroraCanvasDiagnosticStage (174);\n  pControlBase->SetControlState (\n                  pControlBase,\n                  KEYDEFAULT\n                  );\n\n  AuroraCanvasDiagnosticStage (175);\n  AuroraCanvasDiagnosticStage (176);\n  pControlBase->Draw (\n                  pControlBase,\n                  FALSE,\n                  NULL,\n                  NULL\n                  );\n\n  AuroraCanvasDiagnosticStage (177);\n\nExit:\n  AuroraCanvasDiagnosticStage (178);\n\n  return Status;\n}\n"
HELPERS = "// Aurora diagnostic hook: only the FrontPage library instance installs a callback.\ntypedef VOID (*AURORA_CANVAS_DIAGNOSTIC_CALLBACK)(IN UINTN Stage);\nSTATIC AURORA_CANVAS_DIAGNOSTIC_CALLBACK mAuroraCanvasDiagnosticCallback = NULL;\n\nVOID\nAuroraCanvasSetDiagnosticCallback (\n  IN AURORA_CANVAS_DIAGNOSTIC_CALLBACK Callback\n  );\n\nVOID\nAuroraCanvasSetDiagnosticCallback (\n  IN AURORA_CANVAS_DIAGNOSTIC_CALLBACK Callback\n  )\n{\n  mAuroraCanvasDiagnosticCallback = Callback;\n}\n\nSTATIC\nVOID\nAuroraCanvasDiagnosticStage (\n  IN UINTN Stage\n  )\n{\n  if (mAuroraCanvasDiagnosticCallback != NULL) {\n    mAuroraCanvasDiagnosticCallback (Stage);\n  }\n}\n\n"
INCLUDE = '#include "SimpleUIToolKitInternal.h"\n'

def main():
    actual = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != PIN:
        raise SystemExit(f"Canvas diagnostic requires mu_plus {PIN}, found {actual}")
    text = TARGET.read_text(encoding="utf-8")
    if text.count(REPLACEMENT) == 1 and text.count(HELPERS) == 1:
        print("PASS: pinned Canvas diagnostic hook already applied")
        return
    if text.count(ORIGINAL) != 1 or text.count(INCLUDE) != 1 or "AuroraCanvasDiagnosticStage" in text:
        raise SystemExit("Canvas source differs from expected diagnostic anchors")
    updated = text.replace(ORIGINAL, REPLACEMENT, 1).replace(
        INCLUDE, INCLUDE + "\n" + HELPERS, 1
    )
    TARGET.write_text(updated, encoding="utf-8")
    print("PASS: pinned Canvas default-control boundaries 171-178 applied")

if __name__ == "__main__":
    main()
