<#
.SYNOPSIS
  Simulates a call to the IVR agent as a text chat (Direct Line) so you can test the menu,
  the operating-hours check and the transfer without a phone.

.DESCRIPTION
  Starts a conversation, sends the start event (which plays the greeting and the menu), then
  sends what the caller "says" ("Sales", "Support", or anything else) and prints the replies.

  What you will see:
    - queue OPEN  : "Please hold while I connect you." followed by a handoff.initiate event whose
                    payload contains QueueName (this is what D365 routes on)
    - queue CLOSED: the D365 out-of-operating-hours message, then endOfConversation
  Keypad presses (DTMF) cannot be simulated in text, so type the option name instead.
  Real DTMF and the transfer into D365 need a real call to your phone number.

.PARAMETER EnvironmentId
  The Power Platform environment ID (GUID), not the org URL. Find it in the Power Platform admin center.

.EXAMPLE
  ./Test-IvrConversation.ps1 -EnvironmentId 00000000-0000-0000-0000-000000000000 -Say Sales
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$EnvironmentId,
  [string]$BotSchemaName = 'cr_salesandsupportivr',
  [string]$Say = 'Sales'
)
$ErrorActionPreference = 'Stop'
$hex = $EnvironmentId -replace '-', ''
$apiHost = "$($hex.Substring(0, $hex.Length - 2)).$($hex.Substring($hex.Length - 2)).environment.api.powerplatform.com"
$pp = az account get-access-token --resource https://api.powerplatform.com --query accessToken -o tsv
if (-not $pp) { throw 'Could not get a token. Run: az login' }
$dl = (Invoke-RestMethod -Uri "https://$apiHost/powervirtualagents/botsbyschema/$BotSchemaName/directline/token?api-version=2022-03-01-preview" -Headers @{ Authorization = "Bearer $pp" }).token
$h = @{ Authorization = "Bearer $dl"; 'Content-Type' = 'application/json' }
$cid = (Invoke-RestMethod -Method POST -Uri 'https://directline.botframework.com/v3/directline/conversations' -Headers $h).conversationId
$script:wm = $null

function Read-Replies([int]$Seconds) {
  $until = (Get-Date).AddSeconds($Seconds)
  while ((Get-Date) -lt $until) {
    Start-Sleep -Seconds 2
    $u = "https://directline.botframework.com/v3/directline/conversations/$cid/activities" + $(if ($script:wm) { "?watermark=$($script:wm)" })
    $r = Invoke-RestMethod -Uri $u -Headers $h
    $script:wm = $r.watermark
    foreach ($a in $r.activities) {
      if ($a.from.role -ne 'bot' -and $a.type -eq 'message') { continue }
      $text = "[$($a.type)] $($a.text)"
      if ($a.type -eq 'event') { $text += " $($a.name)"; if ($a.name -eq 'handoff.initiate') { $text += ' QueueName=' + $a.value.QueueName } }
      $text.Trim()
    }
  }
}

function Send($body) {
  Invoke-RestMethod -Method POST -Uri "https://directline.botframework.com/v3/directline/conversations/$cid/activities" -Headers $h -Body ($body | ConvertTo-Json) | Out-Null
}

Write-Host '=== call connects'
Send @{ type = 'event'; name = 'startConversation'; from = @{ id = 'tester' } }
Read-Replies 14
Write-Host "=== caller says: $Say"
Send @{ type = 'message'; from = @{ id = 'tester' }; text = $Say }
Read-Replies 22
