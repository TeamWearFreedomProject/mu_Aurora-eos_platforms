"""Execute the actual generated HII buffer block with allocation failures."""
import ast
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BufferDiagnosticTests(unittest.TestCase):
    def test_generated_buffer_code_handles_failure_and_normal_fills(self):
        compiler = shutil.which("cc")
        self.assertIsNotNone(compiler, "A C compiler is required for this safety check")
        module = ast.parse((ROOT / "tools/patch_aurora_canvas_diagnostic.py").read_text())
        node = next(n for n in module.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == "HII_REPLACEMENT")
        replacement = ast.literal_eval(node.value)
        start = replacement.index("        UINT32  Bkgnd = Background.Blue")
        end = replacement.index("\n      }\n\n      AURORA_HII_STAGE (317);", start)
        block = replacement[start:end]
        source = r"""
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
typedef size_t UINTN;
typedef uint32_t UINT32;
typedef int BOOLEAN;
typedef int EFI_STATUS;
typedef struct { uint8_t Blue, Green, Red, Reserved; } EFI_GRAPHICS_OUTPUT_BLT_PIXEL;
typedef struct { UINTN LineWidth, LineHeight; } ROW;
#define TRUE 1
#define FALSE 0
#define MAX_UINTN SIZE_MAX
#define EFI_SUCCESS 0
#define EFI_OUT_OF_RESOURCES 9
#define EFI_BAD_BUFFER_SIZE 4
static int fail_alloc, calls, fills, attempted, results;
static UINTN allocated_bytes, seen_w, seen_h, seen_bytes, seen_address;
static UINTN stages[32], stage_count;
static EFI_STATUS seen_result;
static void trace_buffer(UINTN w, UINTN h, UINTN b, UINTN p, BOOLEAN a) {
  seen_w=w; seen_h=h; seen_bytes=b; seen_address=p; attempted=a;
}
static void trace_result(const char *name, EFI_STATUS status) {
  (void)name; results++; seen_result=status;
}
static void trace_stage(UINTN stage) {
  assert(stage_count < 32); stages[stage_count++]=stage;
}
static struct {
  void (*Buffer)(UINTN,UINTN,UINTN,UINTN,BOOLEAN);
  void (*Result)(const char *,EFI_STATUS);
} Trace = {trace_buffer, trace_result};
#define AURORA_HII_STAGE(n) trace_stage(n)
static void *AllocatePool(UINTN bytes) {
  calls++; allocated_bytes=bytes;
  assert(bytes <= 1024*1024);
  return fail_alloc ? NULL : calloc(1, bytes);
}
static void SetMem32(void *buffer, UINTN bytes, UINT32 value) {
  assert(buffer != NULL); assert(bytes == allocated_bytes);
  assert(bytes % 4 == 0); assert((uintptr_t)buffer % 4 == 0);
  fills++;
  for(UINTN i=0;i<bytes/4;i++) ((UINT32 *)buffer)[i]=value;
}
static EFI_STATUS run(UINTN width, UINTN height, int fail) {
  calls=fills=attempted=results=0; stage_count=0;
  seen_w=seen_h=seen_bytes=seen_address=allocated_bytes=0; fail_alloc=fail;
  ROW RowInfo[1]={{width,height}};
  UINTN RowIndex=0, BaseLine=2;
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL Background={0x11,0x22,0x33,0};
  EFI_GRAPHICS_OUTPUT_BLT_PIXEL *BltBuffer=NULL, *BufferPtr=NULL;
  EFI_STATUS Status=EFI_SUCCESS;
  UINT32 PreInitBkgnd;
  __typeof__(Trace) *AuroraTrace=&Trace;
""" + block + r"""
Exit:
  if(BltBuffer != NULL) {
    assert(BufferPtr == BltBuffer + BaseLine * width);
    for(UINTN i=0;i<allocated_bytes/4;i++) assert(((UINT32 *)BltBuffer)[i]==0x00332211);
    free(BltBuffer);
  }
  return Status;
}
int main(void) {
  assert(run(12,19,1)==EFI_OUT_OF_RESOURCES);
  assert(calls==1 && fills==0 && attempted && seen_address==0);
  assert(seen_bytes==12*19*4 && seen_result==EFI_OUT_OF_RESOURCES);
  assert(stages[stage_count-1]==339);
  assert(run(SIZE_MAX,2,0)==EFI_BAD_BUFFER_SIZE);
  assert(calls==0 && fills==0 && !attempted && seen_bytes==0);
  assert(stages[stage_count-1]==340 && seen_w==SIZE_MAX && seen_h==2);
  assert(run(12,0,0)==EFI_BAD_BUFFER_SIZE);
  assert(calls==0 && fills==0 && !attempted);
  assert(run(12,19,0)==EFI_SUCCESS);
  assert(calls==1 && fills==3 && attempted && seen_address!=0);
  assert(seen_bytes==12*19*4 && seen_result==EFI_SUCCESS && results==1);
  const UINTN expected[]={315,316,330,331,332,333,334,335,336,337,338};
  assert(stage_count==sizeof(expected)/sizeof(expected[0]));
  for(UINTN i=0;i<stage_count;i++) assert(stages[i]==expected[i]);
  puts("PASS: NULL guard, size overflow, zero height and all three normal fills");
  return 0;
}
"""
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "buffer_test.c"
            exe = Path(directory) / "buffer_test"
            src.write_text(source)
            subprocess.run([compiler, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", str(src), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            # Keep address/UB checks; leak scanning needs /proc access unavailable
            # in some managed hosts. The harness frees its only allocation.
            result = subprocess.run([str(exe)], capture_output=True, text=True,
                                    env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS:", result.stdout)


if __name__ == "__main__":
    unittest.main()
