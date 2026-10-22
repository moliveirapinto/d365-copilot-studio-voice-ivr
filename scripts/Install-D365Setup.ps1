<#
.SYNOPSIS
  Creates the Dynamics 365 Contact Center side of the Sales and Support Voice IVR:
  operating hours, Sales and Support voice queues, a 1-call capacity profile, a voice
  workstream, the QueueName context variable, the route-to-queue rules, and attaches the
  Copilot Studio agent to the workstream.

.DESCRIPTION
  Uses only built-in Dataverse actions (msdyn_CreateOperatingHours, msdyn_ManageQueue,
  msdyn_ManageWorkstream, msdyn_ManageRoutingRule). The routing rule conditions are written
  directly into the ruleset definition because the built-in action does not support them.
  Safe to re-run: existing items (matched by name) are reused.

  It does NOT attach a phone number. Do that in Copilot Service admin center:
  Workstreams > your workstream > Channels > Voice > add your phone number.

.PREREQUISITES
  - Azure CLI signed in to the tenant:  az login
  - System Administrator (or Omnichannel admin) in the target environment
  - The solution SalesSupportVoiceIVR is imported and the agent is PUBLISHED

.EXAMPLE
  ./Install-D365Setup.ps1 -EnvironmentUrl https://contoso.crm.dynamics.com -TimeZoneCode 35
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$EnvironmentUrl,
  [string]$BotName = 'Sales and Support IVR',
  [string]$WorkstreamName = 'Voice IVR Workstream',
  [string]$SalesQueueName = 'Sales',
  [string]$SupportQueueName = 'Support',
  [int]$TimeZoneCode = 35,                  # 35 = Eastern Time (US & Canada). See docs/INSTALL.md
  [string]$SalesStart = '08:00',
  [string]$SalesEnd = '12:00',
  [string]$SupportStart = '12:00',
  [string]$SupportEnd = '18:00',
  [string]$DaysOfWeek = 'MO,TU,WE,TH,FR',   # RRULE-style two-letter days
  [string]$CapacityProfileName = 'Voice IVR inbound'
)

$ErrorActionPreference = 'Stop'
$EnvironmentUrl = $EnvironmentUrl.TrimEnd('/')
$api = "$EnvironmentUrl/api/data/v9.2"

function Get-Headers {
  $tok = az account get-access-token --resource $EnvironmentUrl --query accessToken -o tsv
  if (-not $tok) { throw 'Could not get a token. Run: az login' }
  @{ Authorization = "Bearer $tok"; Accept = 'application/json'; 'OData-Version' = '4.0'; 'OData-MaxVersion' = '4.0'; 'Content-Type' = 'application/json; charset=utf-8' }
}
function Invoke-Dv([string]$Method, [string]$Path, $Body = $null) {
  $req = @{ Method = $Method; Uri = "$api/$Path"; Headers = (Get-Headers) }
  if ($null -ne $Body) { $req.Body = [Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 20)) }
  try { Invoke-RestMethod @req }
  catch { throw "[$Method $Path] $($_.Exception.Message) :: $($_.ErrorDetails.Message)" }
}
function Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }

# ---------------------------------------------------------------- operating hours
function Ensure-OperatingHours([string]$Name, [string]$Start, [string]$End) {
  $f = [uri]::EscapeDataString("msdyn_name eq '$Name'")
  $ex = (Invoke-Dv GET "msdyn_operatinghours?`$select=msdyn_operatinghourid&`$filter=$f").value
  if ($ex) { Write-Host "    operating hours '$Name' exists"; return $ex[0].msdyn_operatinghourid }
  $r = Invoke-Dv POST 'msdyn_CreateOperatingHours' @{
    OperatingHoursName = $Name; TimeZoneCode = $TimeZoneCode; WorkStart = $Start; WorkEnd = $End
    StartDate = (Get-Date).ToString('yyyy-MM-dd'); DaysOfWeek = $DaysOfWeek }
  Write-Host "    created operating hours '$Name'"
  $r.OperatingHourId
}

# ---------------------------------------------------------------- queues
$queueContractXml = @'
<contract version="1">
  <entity logical-name="msdyn_ocliveworkitem" key="msdyn_ocliveworkitem" />
  <entity logical-name="msdyn_ocliveworkitemcharacteristic" key="msdyn_ocliveworkitemcharacteristic" is-collection="true" />
  <complex key="liveworkitemcontext" />
  <entity logical-name="msdyn_ocliveworkitemcapacityprofile" key="msdyn_ocliveworkitemcapacityprofile" is-collection="true" />
  <entity logical-name="msdyn_ocliveworkitemmatchingcriteria" key="msdyn_ocliveworkitemmatchingcriteria" is-collection="true" />
</contract>
'@
function Ensure-Queue([string]$Name, [string]$HoursId) {
  $f = [uri]::EscapeDataString("name eq '$Name'")
  $ex = (Invoke-Dv GET "queues?`$select=queueid,_msdyn_assignmentinputcontractid_value&`$filter=$f").value
  $hasContract = $false
  if ($ex) { $qid = $ex[0].queueid; $hasContract = [bool]$ex[0]._msdyn_assignmentinputcontractid_value; Write-Host "    queue '$Name' exists" }
  else {
    $r = Invoke-Dv POST 'msdyn_ManageQueue' @{ OperationType = 'Create'; QueueName = $Name; QueueType = 'Voice'; QueueViewType = 'Public'; AssignmentStrategy = 'HighestCapacity' }
    $qid = ($r.Result | ConvertFrom-Json).queueId; Write-Host "    created queue '$Name'"
  }
  Invoke-Dv POST 'msdyn_ManageQueue' @{ OperationType = 'SetOperatingHours'; QueueId = $qid; OperatingHoursId = $HoursId } | Out-Null
  # Match what the admin center creates for a voice queue: assignment contract, priority 1, private view
  if (-not $hasContract) {
    $un = 'new_' + ([guid]::NewGuid().ToString().Replace('-', '_'))
    Invoke-Dv POST 'msdyn_decisioncontracts' @{ msdyn_name = $un; msdyn_uniquename = $un; msdyn_contractdefinition = $queueContractXml } | Out-Null
    $cid = (Invoke-Dv GET "msdyn_decisioncontracts?`$select=msdyn_decisioncontractid&`$filter=msdyn_uniquename eq '$un'").value[0].msdyn_decisioncontractid
    Invoke-Dv PATCH "queues($qid)" @{ 'msdyn_routingcontractid@odata.bind' = "/msdyn_decisioncontracts($cid)"; msdyn_priority = 1; queueviewtype = 1 } | Out-Null
  }
  $qid
}

Step "Operating hours"
$salesHours = Ensure-OperatingHours "$SalesQueueName Hours ($SalesStart-$SalesEnd)" $SalesStart $SalesEnd
$supportHours = Ensure-OperatingHours "$SupportQueueName Hours ($SupportStart-$SupportEnd)" $SupportStart $SupportEnd

Step "Queues"
$salesQueueId = Ensure-Queue $SalesQueueName $salesHours
$supportQueueId = Ensure-Queue $SupportQueueName $supportHours

# ---------------------------------------------------------------- capacity profile
Step "Capacity profile '$CapacityProfileName' (voice requires exactly 1 work item)"
$f = [uri]::EscapeDataString("msdyn_name eq '$CapacityProfileName'")
if (-not (Invoke-Dv GET "msdyn_capacityprofiles?`$select=msdyn_capacityprofileid&`$filter=$f").value) {
  Invoke-Dv POST 'msdyn_capacityprofiles' @{ msdyn_name = $CapacityProfileName; msdyn_uniquename = 'new_' + ($CapacityProfileName -replace '\W', '_').ToLower(); msdyn_defaultmaxunits = 1; msdyn_blockassignment = $true; msdyn_resetduration = 192350000 } | Out-Null
  Write-Host '    created'
} else { Write-Host '    exists' }

# ---------------------------------------------------------------- workstream
Step "Workstream '$WorkstreamName'"
$f = [uri]::EscapeDataString("msdyn_name eq '$WorkstreamName'")
$ws = (Invoke-Dv GET "msdyn_liveworkstreams?`$select=msdyn_liveworkstreamid&`$filter=$f").value
if (-not $ws) {
  Invoke-Dv POST 'msdyn_ManageWorkstream' @{ OperationType = 'Create'; WorkstreamName = $WorkstreamName; ChannelType = 'Voice'; WorkDistributionMode = 'Push'; QueueName = $SupportQueueName } | Out-Null
  $ws = (Invoke-Dv GET "msdyn_liveworkstreams?`$select=msdyn_liveworkstreamid&`$filter=$f").value
  Write-Host '    created'
} else { Write-Host '    exists' }
$wsId = $ws[0].msdyn_liveworkstreamid
Invoke-Dv POST 'msdyn_ManageWorkstream' @{ OperationType = 'SetCapacityProfile'; WorkstreamName = $WorkstreamName; CapacityProfileName = $CapacityProfileName; CapacityFormat = 'Profile'; CapacityWrapUpValueInMinutes = '1'; AllowedPresences = 'Available,Busy' } | Out-Null
Write-Host '    capacity profile applied'

# ---------------------------------------------------------------- context variable
Step "Context variable 'QueueName'"
$cv = (Invoke-Dv GET "msdyn_ocliveworkstreamcontextvariables?`$select=msdyn_name&`$filter=_msdyn_liveworkstreamid_value eq $wsId and msdyn_name eq 'QueueName'").value
if (-not $cv) {
  Invoke-Dv POST 'msdyn_ocliveworkstreamcontextvariables' @{ msdyn_name = 'QueueName'; msdyn_displayname = 'QueueName'; msdyn_datatype = 192350000; 'msdyn_liveworkstreamid@odata.bind' = "/msdyn_liveworkstreams($wsId)" } | Out-Null
  Write-Host '    created (waiting for it to propagate to the routing contract)'; Start-Sleep -Seconds 20
} else { Write-Host '    exists' }

# ---------------------------------------------------------------- routing rules
Step "Route-to-queue rules"
$rulesetName = 'Route to Queue'
$existing = $null
try { $existing = (Invoke-Dv POST 'msdyn_ManageRoutingRule' @{ Operation = 'ListRules'; WorkstreamName = $WorkstreamName; RulesetName = $rulesetName }).msdyn_results | ConvertFrom-Json } catch { }
if ($null -eq $existing) {
  Invoke-Dv POST 'msdyn_ManageRoutingRule' @{ Operation = 'CreateRouteToQueueRuleset'; WorkstreamName = $WorkstreamName; RulesetName = $rulesetName; HitPolicy = 'first' } | Out-Null
  $existing = @()
}
foreach ($pair in @(@($SalesQueueName, 1), @($SupportQueueName, 2))) {
  if (-not ($existing | Where-Object { $_.Name -eq "Route to $($pair[0])" })) {
    Invoke-Dv POST 'msdyn_ManageRoutingRule' @{ Operation = 'AddRule'; WorkstreamName = $WorkstreamName; RulesetName = $rulesetName; RuleName = "Route to $($pair[0])"; QueueName = $pair[0]; Priority = "$($pair[1])" } | Out-Null
  }
}
$rules = (Invoke-Dv POST 'msdyn_ManageRoutingRule' @{ Operation = 'ListRules'; WorkstreamName = $WorkstreamName; RulesetName = $rulesetName }).msdyn_results | ConvertFrom-Json
$ruleXml = foreach ($r in $rules) {
  $qName = if ($r.Name -eq "Route to $SalesQueueName") { $SalesQueueName } else { $SupportQueueName }
@"
    <rule id="$($r.Id)" name="$($r.Name)">
      <logical operator="AND">
        <logical operator="AND">
          <condition operator="==">
            <lhs type="attribute">liveworkitemcontext.QueueName</lhs>
            <rhs type="staticvalue">$qName</rhs>
          </condition>
        </logical>
      </logical>
      <action>
        <setattribute>
          <lhs type="attribute">assign_to.queue</lhs>
          <rhs type="staticvalue">$($r.Action.queueId)</rhs>
        </setattribute>
      </action>
    </rule>
"@
}
$definition = "<decision hit-policy=`"first`" version=`"1`">`n  <rules>`n$($ruleXml -join "`n")`n  </rules>`n</decision>"
$rs = (Invoke-Dv GET "msdyn_decisionrulesets?`$select=msdyn_decisionrulesetid,msdyn_name,_msdyn_inputcontractid_value&`$filter=msdyn_name eq '$rulesetName'&`$orderby=createdon desc").value
$wsContract = (Invoke-Dv GET "msdyn_liveworkstreams($wsId)?`$select=_msdyn_routingcontractid_value")._msdyn_routingcontractid_value
$target = $rs | Where-Object { $_._msdyn_inputcontractid_value -eq $wsContract } | Select-Object -First 1
if (-not $target) { throw "Could not find the '$rulesetName' ruleset for this workstream." }
Invoke-Dv PATCH "msdyn_decisionrulesets($($target.msdyn_decisionrulesetid))" @{ msdyn_rulesetdefinition = $definition } | Out-Null
Write-Host "    rules: QueueName=$SalesQueueName -> $SalesQueueName queue, QueueName=$SupportQueueName -> $SupportQueueName queue"

# ---------------------------------------------------------------- attach the agent
Step "Attach agent '$BotName' to the workstream"
try {
  $r = Invoke-Dv POST 'msdyn_ManageWorkstream' @{ OperationType = 'AddBot'; WorkstreamName = $WorkstreamName; BotName = $BotName }
  Write-Host "    $($r.Result)"
} catch {
  Write-Warning "Could not add the agent automatically: $_"
  Write-Warning 'Make sure the agent is published in Copilot Studio, then add it in the admin center: Workstreams > your workstream > Copilot agent.'
}

Step "Validate"
(Invoke-Dv POST 'msdyn_ManageWorkstream' @{ OperationType = 'Validate'; WorkstreamName = $WorkstreamName }).Result

Write-Host "`nDone. Remaining manual step: add your phone number to the Voice channel of '$WorkstreamName'." -ForegroundColor Green
