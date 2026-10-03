# Pixel Watch 2 HII font diagnostic — 2026-10-03

## Latest hardware observation

The owner temporarily booted the preceding StringToWindow diagnostic and photographed **STAGE 273 / FONT STRING IMAGE / BEFORE CALL**. The display also showed **UI PAINT BEGIN / EFI_SUCCESS / 0000000000000000**, while **AUTH RESULT / EFI_DEVICE_ERROR / 8000000000000007** remained the initial authentication result.

Thus the rendering engine's PAINT_BEGIN call returned success; no return from HII StringToImage (stage 274) has been observed. The screenshot does not establish that the HII call was entered after the diagnostic's two-second delay, nor does it locate the problem within that call.

## New HII boundaries

The pinned `MU_BASECORE/MdeModulePkg/Universal/HiiDatabaseDxe/Font.c` implementation supplies `HiiStringToImage`. A diagnostic callback observes the following operations without skipping the original logic:

| Stage | Operation | Boundary |
| --- | --- | --- |
| 301 | HII STRING IMAGE | ENTERED |
| 302 | HII INPUT | CHECKED |
| 303 | GLYPH ARRAYS | BEFORE ALLOC |
| 304 | GLYPH ARRAYS | ALLOC RETURNED |
| 305 | FONT LOOKUP | BEFORE CALL |
| 306 | FONT LOOKUP | RETURNED |
| 307 | TEXT PREP | BEFORE CALL |
| 308 | TEXT PREP | LINEBREAK DONE |
| 309 | GLYPH FETCH | BEFORE LOOP |
| 310 | GLYPH FETCH | LOOP DONE |
| 311 | ROW LAYOUT | BEFORE ALLOC |
| 312 | ROW LAYOUT | ROWINFO READY |
| 313 | ROW LAYOUT | BEFORE FORMAT |
| 314 | ROW LAYOUT | FORMAT DONE |
| 315 | HII BUFFER | BEFORE ALLOC |
| 316 | HII BUFFER | ALLOC RETURNED |
| 317 | HII GLYPHS | BEFORE DRAW |
| 318 | HII GLYPHS | DRAW RETURNED |
| 319 | HII GOP BLT | BEFORE CALL |
| 320 | HII GOP BLT | RETURNED |
| 321 | HII CLEANUP | BEFORE FREE |
| 322 | HII STRING IMAGE | BEFORE RETURN |

301 marks entry, 302 completed input validation, 303–304 glyph-array allocation, 305–306 font lookup, 307–308 text normalization, 309–310 glyph-buffer fetch, 311–314 row allocation and formatting, 315–316 direct-screen buffer allocation, 317–318 glyph drawing, 319–320 the actual GOP Blt, and 321–322 cleanup/return. The UI row captures the GOP Blt result and the HII return status when available.

Some markers lie within conditional or repeated rendering work, so a stage can be skipped or visited again. A missing later stage proves only that its boundary has not been displayed. Successful allocation or a returned font lookup does not prove correct geometry. The raw initial authentication status is retained separately.

## Implementation and limitations

The same private diagnostic protocol used by the prior StringToWindow build is located by the HII database driver only while FrontPage has armed it for the button text call. The HII code checks the protocol revision and callback pointers before using them. It draws markers through the existing font-independent GOP text renderer, avoiding recursive HII StringToImage calls. Earlier UI text operations remain untraced.

The build script requires the pinned mu_plus commit `2761c3a83e441f439fb3d90e61972801495b1196` and the pinned mu_basecore commit `a18a672778fc28b2cf99642ca2571d3fdfef3ed3`. It checks source anchors before writing its temporary changes to submodule checkouts. The checked-in source and original license notices remain intact.

The diagnostic itself performs additional GOP drawing and two-second delays. The result can change timing, especially within PAINT_BEGIN. A stable marker is not proof that the CPU remains active. The code has not been verified on hardware yet.

## Next observation

The GitHub Actions artifact `aurora-CP2A-hii-font-diagnostic-UNVERIFIED` contains an experimental noSB CP2A fastboot candidate. Temporarily boot it and report the last stage, operation, boundary, and UI result. Do not flash the candidate. The build and structural checks do not verify hardware safety.
