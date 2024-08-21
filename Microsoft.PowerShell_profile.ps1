oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\strykrr_theme.omp.json" | Invoke-Expression
Import-Module -Name Terminal-Icons
if ($host.Name -eq 'ConsoleHost')
{
    Import-Module PSReadLine
}   