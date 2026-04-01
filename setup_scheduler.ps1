$taskName = "Jiddi_ClickUp_Sync_Every_2h"
$projectDir = "C:\Users\Jasurbek\Desktop\Jiddi_clickup"
$pythonExe = "C:\Users\Jasurbek\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$scriptPath = Join-Path $projectDir "sync_excel_to_clickup.py"
$excelPath = Join-Path $projectDir "Jiddi_lead.xlsx"

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`" --source google" -WorkingDirectory $projectDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 2)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Sync Excel leads to ClickUp every 2 hours" -Force | Out-Null
Write-Host "Scheduled task registered: $taskName"
