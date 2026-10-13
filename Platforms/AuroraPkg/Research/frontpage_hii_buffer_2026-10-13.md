# Aurora HII buffer diagnostic — 2026-10-13

Owner and hardware tester: **Kyogo**. Analysis and implementation assistance: ChatGPT/Codex.

## Hardware evidence

Kyogo reports the live OS build as **CP2A.260603.001.S1**.
The current fastboot observations are bootloader **eos-5.28-15165501** and active slot **a**.
The supplied photograph shows:

```text
AURORA DIAGNOSTIC
STAGE 316
HII BUFFER
ALLOC RETURNED
AUTH RESULT
EFI_DEVICE_ERROR
8000000000000007
UI PAINT BEGIN
EFI_SUCCESS
0000000000000000
```

Stage 316 is after AllocatePool in the direct-to-screen branch of HiiStringToImage.
It proves that allocation returned, but does not prove a non-NULL pointer.
The displayed EFI_SUCCESS is the earlier PAINT_BEGIN result. The authentication
EFI_DEVICE_ERROR is a separate result. A still photograph alone does not measure
how long the stage remains visible.

## Source finding and diagnostic change

The pinned mu_basecore source checks BltBuffer for NULL **after** its first
SetMem32. If allocation fails, that ordering can attempt to write to NULL.
Allocation failure has **not** been measured on the watch and is not yet the
confirmed cause of the observed last stage.

The temporary build patch now:

- Records row width, row height, requested bytes and the returned pointer.
- Rejects zero-height or overflowing byte counts before allocation.
- Checks NULL before any buffer fill and returns EFI_OUT_OF_RESOURCES on failure.
- Preserves all three upstream SetMem32 fills and traces each before/after.
- Keeps detected allocation/size failure stages readable for about 30 seconds,
  then follows normal HII cleanup and returns the error.

The private diagnostic protocol is revision 2. Its appended Buffer callback and
revision check are shared by FrontPage, SWM and HII in the same build. This is a
volatile diagnostic bridge, not a persistent setting or a public protocol.

## Reading the panel

| Field | Meaning |
| --- | --- |
| ALLOC NOT RUN | Dimensions recorded; allocation has not yet been attempted |
| ALLOC OK | AllocatePool returned non-NULL; subsequent memory writes remain unverified |
| ALLOC NULL | AllocatePool returned NULL |
| W / H | Requested row dimensions, decimal |
| B | Requested byte count, hexadecimal |
| P | Returned pointer, hexadecimal |

From stage 315 through HII cleanup, these fields replace the earlier auth/UI
summary on the panel. The earlier results remain available before stage 315 and
in DEBUG output. The panel renderer uses direct GOP pixel fills, independently
of the HII string renderer under investigation.

| Stage | Boundary |
| --- | --- |
| 315 | Before allocation, with requested dimensions and bytes |
| 316 | Allocation returned, with pointer and allocation classification |
| 330 | NULL check passed |
| 331 / 332 | Before / after first SetMem32 |
| 333 / 334 | Before / after second SetMem32 |
| 335 / 336 | Before / after third SetMem32 |
| 337 / 338 | Before / after calculating the buffer origin |
| 339 | Allocation failed; no SetMem32 executed |
| 340 | Zero-height or overflowing byte count rejected; no allocation attempted |
| 317–322 | Existing glyph drawing, GOP blit, cleanup and return markers |

Markers include pixel drawing and delays; a BEFORE marker does not prove the
following operation was entered. ALLOC OK does not prove the memory map or CPU
access behavior is correct.

## Validation and remaining evidence

The host test extracts the **actual generated C buffer block**, compiles it with
address/undefined-behavior sanitizers and executes null-allocation, multiplication
overflow, zero-height and successful-allocation cases. It checks that failure
does not fill memory, and success runs the three fills with the expected size and
color. The patch also matches and reapplies idempotently to the pinned HII/SWM
sources.

GitHub Actions builds and packages the UEFI candidate. Host tests and compilation
cannot validate watch memory access or diagnose the stopping condition by
themselves. The new buffer panel is **not yet hardware-tested**.

Artifact: `aurora-CP2A-hii-buffer-diagnostic-UNVERIFIED`.
Use the nosb candidate with temporary `fastboot boot`; do not flash it.

## Upstream attribution

- [Microsoft mu_basecore Font.c at the pinned revision](https://github.com/microsoft/mu_basecore/blob/a18a672778fc28b2cf99642ca2571d3fdfef3ed3/MdeModulePkg/Universal/HiiDatabaseDxe/Font.c)
- [Microsoft mu_plus at the pinned revision](https://github.com/microsoft/mu_plus/tree/2761c3a83e441f439fb3d90e61972801495b1196)
- [Project credits](../../../../CREDITS.md)

Original copyright/license notices are retained. The upstream projects do not
guarantee this experimental Watch 2 port.
