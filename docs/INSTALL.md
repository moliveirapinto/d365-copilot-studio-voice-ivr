# Install

## Prerequisites

| Need | Details |
|---|---|
| **Dynamics 365 Contact Center** (or Customer Service with Omnichannel/voice) | In the target environment, with voice available. |
| **Copilot Studio** | Same environment. You need permission to import solutions and publish agents. |
| **A Dataverse connection** | A Microsoft Dataverse connection owned by the account (preferably a service account) that will run the lookups. |
| **Roles** | System Administrator (or equivalent) in the environment for import and the setup script. |
| **Azure CLI** | Needed only for the PowerShell scripts: <https://aka.ms/installazurecli>, then `az login` with the same tenant. |
| **PowerShell 7** | `pwsh`. The scripts also run in Windows PowerShell 5.1. |
| **A phone number** | Acquired in Dynamics 365 Contact Center (or bring your own carrier). You attach it at the end. |

> Do a trial run in a **sandbox** environment first.

## Step 1: Import the solution

1. Download `SalesSupportVoiceIVR_unmanaged.zip` (to edit the agent) or `SalesSupportVoiceIVR_managed.zip` (to lock it) from the [latest Release](../../../releases/latest).
2. Go to <https://make.powerapps.com>, pick your environment, **Solutions > Import solution**, and upload the zip.
3. When asked for the **connection reference** `Microsoft Dataverse (Sales and Support IVR)`, choose (or create) a **Microsoft Dataverse** connection and finish the import.

The import brings in the agent **Sales and Support IVR** and its connection reference.

<details><summary>Import with the command line instead</summary>

```powershell
# Requires the Power Platform CLI (pac)
pac auth create --environment https://<yourorg>.crm.dynamics.com
pac solution import --path .\SalesSupportVoiceIVR_unmanaged.zip --publish-changes
```
Then set the connection reference in make.powerapps.com > Solutions > Sales and Support Voice IVR > Connection references.
</details>

## Step 2: Publish the agent

1. Open <https://copilotstudio.microsoft.com>, choose the environment, open **Sales and Support IVR**.
2. Wait until the agent finishes provisioning (a minute or two after import).
3. Click **Publish**.

Publishing also provisions the **Telephony** and **Dynamics 365 Contact Center (Omnichannel)** channels the agent needs.

If a topic shows a connection error, open **Check Hours And Transfer** and re-select the Dataverse connection on the three Dataverse nodes.

## Step 3: Create the Dynamics 365 side

```powershell
az login
./scripts/Install-D365Setup.ps1 `
    -EnvironmentUrl https://<yourorg>.crm.dynamics.com `
    -TimeZoneCode 35
```

What it creates is listed in [HOW-IT-WORKS.md, section 7](HOW-IT-WORKS.md#7-the-dynamics-365-side). It is safe to re-run: items that already exist (matched by name) are reused.

> **Prefer to click through it, or can't run scripts?** Follow [MANUAL-D365-SETUP.md](MANUAL-D365-SETUP.md) instead. It covers the operating hours, queues, workstream, the `QueueName` context variable and the routing rules.

### Parameters

| Parameter | Default | Notes |
|---|---|---|
| `-EnvironmentUrl` | (required) | Your org URL. |
| `-TimeZoneCode` | `35` | Dataverse time zone code of the **operating hours**. See table below. |
| `-SalesStart` / `-SalesEnd` | `08:00` / `12:00` | 24-hour `HH:mm`. |
| `-SupportStart` / `-SupportEnd` | `12:00` / `18:00` | |
| `-DaysOfWeek` | `MO,TU,WE,TH,FR` | Two-letter days: `MO,TU,WE,TH,FR,SA,SU`. |
| `-SalesQueueName` / `-SupportQueueName` | `Sales` / `Support` | If you change these, change the agent too ([CONFIGURATION.md](CONFIGURATION.md#rename-the-queues)). |
| `-WorkstreamName` | `Voice IVR Workstream` | |
| `-BotName` | `Sales and Support IVR` | Must match the imported agent's name. |
| `-CapacityProfileName` | `Voice IVR inbound` | Created with a 1-call limit. |

### Time zone codes

| Code | Time zone |
|---|---|
| `4` | Pacific Time (US and Canada) |
| `10` | Mountain Time (US and Canada) |
| `20` | Central Time (US and Canada) |
| `35` | Eastern Time (US and Canada) |
| `85` | GMT, London |

Others: query `timezonedefinitions?$select=timezonecode,userinterfacename` in your environment, or use the one shown in your Dynamics 365 personal settings.

## Step 4: Attach your phone number

1. Open **Copilot Service admin center** (Customer support > **Workstreams**) and open **Voice IVR Workstream**.
2. In the voice channel section, choose **Add voice channel** and select your phone number. (Phone numbers are not part of the package.)
3. Wait up to 15 minutes: omnichannel configuration changes can take a while to apply.

## Step 5: Add representatives

Add the people who should take calls to the **Sales** and **Support** queues (Customer support > Queues > the queue > Users) and make sure they are in a presence of **Available** or **Busy**.

## Step 6: Test

**Without a phone** (text simulation, both paths):

```powershell
./scripts/Test-IvrConversation.ps1 -EnvironmentId <environment GUID> -Say Sales,No
./scripts/Test-IvrConversation.ps1 -EnvironmentId <environment GUID> -Say Support
```

Closed queues play the Dynamics 365 message and then ask "anything else?": answer `Yes` to replay the menu or `No` to hear goodbye and end. Open queues print a `handoff.initiate` event containing `QueueName=...`.

**With a phone**: call the number and try 1, 2, the words *sales* and *support*, an invalid key such as 3, and silence. Call **inside** and **outside** each queue's hours.

> Tip: to test the open path outside business hours, temporarily attach an all-day operating-hours schedule to the queue, then restore it.

## Uninstall

1. Remove the workstream, queues, operating hours, capacity profile and ruleset created by the script (admin center).
2. Delete the **Sales and Support Voice IVR** solution (this removes the agent and the connection reference).
