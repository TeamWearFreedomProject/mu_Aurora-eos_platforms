<#
Collect only Linux's reserved-memory tree on a normally booted CP3A Watch 2.
Read-only: does not root, flash, reboot, switch slots or dump partitions.
If ADB access is denied, stop rather than bypassing restrictions.
#>
[CmdletBinding()]
param(
    [string] $AdbPath = '.\adb.exe',
    [string] $OutputRoot = '.'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $AdbPath)) {
    throw "adb.exe not found. Run in C:\platform-tools or supply -AdbPath."
}
$device = (& $AdbPath shell getprop ro.product.device).Trim()
if ($LASTEXITCODE -ne 0 -or $device -ne 'aurora') {
    throw 'ADB target is not aurora; no data collected.'
}
$fingerprint = (& $AdbPath shell getprop ro.build.fingerprint).Trim()
$expected = 'google/aurora/aurora:17/CP3A.260905.002.E1/16053217:user/release-keys'
if ($LASTEXITCODE -ne 0 -or $fingerprint -ne $expected) {
    throw 'Firmware is not the exact expected CP3A build; no data collected.'
}
$folder = Join-Path $OutputRoot ('cp3a-aurora-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $folder | Out-Null
@{device = $device; fingerprint = $fingerprint; collection = 'read-only Linux reserved-memory DTFS'} |
    ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $folder 'metadata.json')
$locations = @('/sys/firmware/devicetree/base/reserved-memory', '/proc/device-tree/reserved-memory')
$ok = $false
foreach ($location in $locations) {
    $present = (& $AdbPath shell "if [ -d $location ]; then echo FOUND; fi").Trim()
    if ($present -eq 'FOUND') {
        & $AdbPath pull $location (Join-Path $folder 'reserved-memory')
        if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath (Join-Path $folder 'reserved-memory'))) {
            $ok = $true
            break
        }
    }
}
if (-not $ok) {
    throw 'Could not read DTFS reserved-memory with ordinary ADB. No privilege bypass attempted.'
}
Write-Host ('Snapshot: ' + $folder)
Write-Host 'This is ONLY the running Linux device-tree view, not the full bootloader/secure-world memory map.'
Write-Host 'Never flash or fastboot boot the research .img based on this snapshot alone.'
