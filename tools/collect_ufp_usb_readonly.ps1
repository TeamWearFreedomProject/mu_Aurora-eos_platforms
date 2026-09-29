# Read-only Windows PnP collector for the observed Aurora UFP-like USB mode.
# Does not send commands to the device and does not modify drivers.
$ErrorActionPreference = 'Stop'

$devices = Get-PnpDevice -PresentOnly | Where-Object {
    $_.InstanceId -like 'USB\VID_045E&PID_066B\*'
}

if (-not $devices) {
    Write-Host 'No present USB VID_045E&PID_066B device found.'
    exit 1
}

foreach ($d in $devices) {
    Write-Host '=== Aurora/UFP-like USB device ==='
    [pscustomobject]@{
        Status       = $d.Status
        Class        = $d.Class
        FriendlyName = $d.FriendlyName
        InstanceId   = ($d.InstanceId -replace '(USB\\VID_045E&PID_066B\\).*','$1<redacted>')
    } | Format-List

    $props = Get-PnpDeviceProperty -InstanceId $d.InstanceId | Where-Object {
        $_.KeyName -match 'HardwareIds|CompatibleIds|BusReportedDeviceDesc|LocationInfo|Service|Driver'
    }

    $props | Select-Object KeyName,@{
        Name='Data'
        Expression={
            $v=$_.Data
            if ($v -is [System.Array]) { ($v -join '; ') } else { $v }
        }
    } | Format-Table -AutoSize
}
