param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $PushArguments
)

& git push @PushArguments
$pushExitCode = $LASTEXITCODE

if ($pushExitCode -ne 0) {
    exit $pushExitCode
}

Write-Host "Push completado correctamente."
