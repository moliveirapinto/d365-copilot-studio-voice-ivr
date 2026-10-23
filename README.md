# Sales and Support Voice IVR for Dynamics 365 Contact Center

A ready-to-install **Copilot Studio voice IVR** for **Dynamics 365 Contact Center** that:

- answers a call and offers **"press 1 or say sales"** and **"press 2 or say support"**
- checks the **operating hours of the chosen queue** before it transfers anything
- if the queue is **open**, transfers the call to Dynamics 365 and routes it to the right queue (**Sales** or **Support**)
- if the queue is **closed**, plays the **out-of-operating-hours voice message configured in Dynamics 365**, then **asks if there is anything else it can help with**: "yes" goes back to the menu, "no" says goodbye and ends the call. Nobody is transferred to an empty queue and the call is never dropped right after the message

It uses only built-in pieces: no Power Automate flows, no plugins, no custom APIs, no Azure resources.

![End-to-end call flow](docs/images/01-architecture.png)

## What is in the box

| Part | What it is | Where |
|---|---|---|
| **Copilot Studio agent** `Sales and Support IVR` | The IVR: menu, hours check, transfer. Packaged as a Dataverse solution that contains **only the agent** (no Dynamics 365 items). | [`agent-only-solution/`](agent-only-solution) (and in the [Release](../../releases)) |
| **D365 setup script** | Creates operating hours, the Sales and Support queues, a voice workstream, the routing rules, and attaches the agent. | [`scripts/Install-D365Setup.ps1`](scripts/Install-D365Setup.ps1) |
| **Test script** | Simulates a call as a text chat so you can test without a phone. | [`scripts/Test-IvrConversation.ps1`](scripts/Test-IvrConversation.ps1) |
| **Topic source** | The agent's topics as readable YAML, for reference and code review. | [`agent-source/`](agent-source) |
| **Documentation** | How every node works, install, manual Dynamics 365 setup, configuration, troubleshooting. | [`docs/`](docs) |

## Three ways to install

The solution package contains **only the Copilot Studio agent**. Everything on the Dynamics 365 side (operating hours, queues, workstream, context variable, routing rules) is separate, so you choose how to create it:

| Option | You do | Best for |
|---|---|---|
| **1. AI assistant does it all** | Paste one prompt ([below](#let-an-ai-assistant-install-it-for-you)) and answer its questions. | Anyone with Claude, Scout or a similar agent. |
| **2. Solution + setup script** | Import the solution, publish, run `Install-D365Setup.ps1` (quick start below). | Admins comfortable with PowerShell. |
| **3. Agent-only solution + build Dynamics 365 by hand** | Import **just the agent** from [`agent-only-solution/`](agent-only-solution), then build the Dynamics 365 side yourself with the click-by-click [manual setup guide](docs/MANUAL-D365-SETUP.md). | Teams that want full control or cannot run scripts. |

Option 3 is the same agent package as the other options. The difference is that **you** create the Dynamics 365 items. The [agent-only README](agent-only-solution/README.md) lists exactly what the agent expects from Dynamics 365 (queue names, operating hours, the `QueueName` context variable, the routing rules).

## Quick start (option 2)

1. **Download** `SalesSupportVoiceIVR_unmanaged.zip` from the [latest Release](../../releases/latest). The solution is **unmanaged**, so you can edit the agent after importing it.
2. **Import** it into your environment (make.powerapps.com > Solutions > Import) and pick a **Microsoft Dataverse** connection when asked.
3. **Publish** the agent in Copilot Studio.
4. **Run** the D365 setup script:
   ```powershell
   az login
   ./scripts/Install-D365Setup.ps1 -EnvironmentUrl https://<yourorg>.crm.dynamics.com -TimeZoneCode 35
   ```
5. **Attach your phone number** to the Voice channel of `Voice IVR Workstream` in Copilot Service admin center.
6. **Add representatives** to the Sales and Support queues.
7. **Call** the number.

Full steps, prerequisites and the time zone table are in [docs/INSTALL.md](docs/INSTALL.md).

---

## Let an AI assistant install it for you

Do you have an AI assistant that can work in a browser and/or run commands (for example **Claude** with computer or browser use, **Claude Code**, **Scout**, or a similar agent)? Then you do not have to follow the steps yourself. Copy the whole prompt below, paste it into the assistant, and answer its questions.

It does the whole install, in the right order:

1. checks your environment (Contact Center with voice, permissions, anything that already exists),
2. downloads and verifies the solution, **imports** it, and connects the Dataverse connection,
3. **publishes** the Copilot Studio agent and checks its Telephony and Omnichannel channels,
4. runs the Dynamics 365 setup: **operating hours, Sales and Support queues, capacity profile, voice workstream, the `QueueName` context variable and the routing rules**, and attaches the agent,
5. guides you to **attach your phone number** (the one step only you can do),
6. adds your **representatives** to the queues,
7. **tests** every path (text simulation, then a real call) and gives you a final report with how to roll back.

**You stay in control:** you sign in yourself (including MFA). The assistant changes only what is listed, asks before anything in a production environment, never changes shared items such as an existing capacity profile, and stops whenever something is not as expected.

> ✅ **Nothing to edit.** Paste the prompt exactly as it is. The assistant starts by **asking you** for what it needs: your Dynamics 365 environment URL, your time zone, the queue hours you want, who runs the Dataverse connection, which users take calls, and whether you already have a phone number. Have those ready. Anything in `<angle brackets>` or written as an example (such as `contoso.crm.dynamics.com`) is filled in by the assistant from your answers. You never type passwords: you sign in yourself in the browser.

````text
You are a Dynamics 365 Contact Center and Copilot Studio installation engineer. Install the community package "Sales and Support Voice IVR" in MY environment, end to end, carefully and safely. Work in this order: check, import, publish, set up Dynamics 365, attach the phone number, add representatives, test.

SOURCE (repository: https://github.com/moliveirapinto/d365-copilot-studio-voice-ivr)
README (context): https://raw.githubusercontent.com/moliveirapinto/d365-copilot-studio-voice-ivr/main/README.md
Guides (same repository, main branch): docs/INSTALL.md, docs/HOW-IT-WORKS.md, docs/MANUAL-D365-SETUP.md, docs/CONFIGURATION.md, docs/TROUBLESHOOTING.md
Files (do NOT unzip the solution):
  A) Solution (unmanaged): https://github.com/moliveirapinto/d365-copilot-studio-voice-ivr/releases/latest/download/SalesSupportVoiceIVR_unmanaged.zip
  B) Setup script:         https://github.com/moliveirapinto/d365-copilot-studio-voice-ivr/releases/latest/download/Install-D365Setup.ps1
  C) Test script:          https://github.com/moliveirapinto/d365-copilot-studio-voice-ivr/releases/latest/download/Test-IvrConversation.ps1
  D) Checksums:            https://github.com/moliveirapinto/d365-copilot-studio-voice-ivr/releases/latest/download/SHA256SUMS.txt
Read the README and the guides first. If they and this prompt disagree, follow the repository and tell me.

WHAT THIS PACKAGE DOES (so you can explain it to me)
- A Copilot Studio voice agent "Sales and Support IVR" answers the call: "press 1 or say sales, press 2 or say support".
- It looks up the chosen queue by name and asks Dynamics 365 (built-in action msdyn_ExpandOperatingHoursForEntityCollection) whether the queue is open now.
- Open: it transfers to Dynamics 365 and passes Global.QueueName; the workstream's "Route to Queue" rules (QueueName equals Sales / Support) put the call in the right queue.
- Closed: it plays the Dynamics 365 voice message MessageReceivedOutsideOperationHoursAck_PhoneCall, then asks "Is there anything else I can help you with?" (Yes replays the menu, No says goodbye and ends). Nobody is transferred.
- The Dynamics 365 side is created by the setup script (B): operating hours (default Mon-Fri, Sales 08:00-12:00, Support 12:00-18:00), voice queues Sales and Support, a capacity profile "Voice IVR inbound" with a limit of exactly 1, the workstream "Voice IVR Workstream", the context variable QueueName, the ruleset "Route to Queue" and its two rules, and it attaches the agent. It does NOT attach a phone number.

HOW TO WORK
- Use the tools you have (browser, shell, Azure CLI "az", PowerShell 7 "pwsh", optionally the Power Platform CLI "pac", file download). If you cannot operate a browser or run commands, switch to GUIDE MODE: give me ONE step at a time with exact click paths (use docs/MANUAL-D365-SETUP.md for the Dynamics 365 part), wait for me to say "done", and check what I report before moving on. If you cannot open URLs, ask me to paste the README and guides and to download the files myself.
- Never guess. If a screen, value or count differs from what this prompt says, STOP and tell me exactly what you see.
- Retry a failed action at most twice, then stop and show me the exact error.
- I sign in myself, including MFA. Never ask me to paste passwords, tokens or secrets in this chat, and never store any.
- Change only what this prompt lists. Never delete anything. Never edit or reuse an existing item that is not named here (other workstreams, other queues, shared capacity profiles). Never touch a different environment than the one I give you.
- After each step give a one-line status: OK / WARNING / FAILED.

STEP 0 - QUESTIONS (ask all in one message, then wait)
1. Which environment: sandbox, developer, or production? Give me its URL (for example https://contoso.crm.dynamics.com, ending at ".dynamics.com" with no path, used exactly as I give it) and its name in Power Apps. If production, warn me and continue only after I answer "yes, production". A sandbox is recommended for a first try.
2. Time zone for the operating hours. The queue's own time zone decides whether it is open, never the caller's, so ask me where each team works. Default Eastern Time (US and Canada), code 35, for both queues. If Sales and Support are in different time zones, use -SalesTimeZoneCode and -SupportTimeZoneCode. Common codes: 4 Pacific, 10 Mountain, 20 Central, 35 Eastern, 85 GMT London. If mine is not listed, look it up in the environment (table timezonedefinitions) and confirm it with me. If I need separate queues per country, tell me this package ships one Sales and one Support queue and point me to docs/CONFIGURATION.md "Time zones, countries and holidays"; do not improvise changes to the agent without my approval.
3. Operating hours: keep the defaults (Mon-Fri; Sales 08:00-12:00; Support 12:00-18:00) or give me different days and times (24-hour HH:mm)?
4. Queue names: keep "Sales" and "Support"? (If I change them, the agent's Main Menu topic must be changed too. Warn me and explain before doing it.)
5. Who owns the Dataverse connection the agent uses to look up queues, hours and the closed message? Recommend a service account for production. Tell me this connection runs for every caller.
6. Which users (usernames or emails) must take calls in Sales and in Support?
7. Do I already have a phone number acquired in Dynamics 365 Contact Center (or a bring-your-own-carrier number) that I want on this IVR? If not, tell me I must acquire one first (admin center > Channels > phone numbers) and offer to continue with everything else.
8. Confirm I have: (a) System Administrator in the environment, (b) a Copilot Studio license and permission to publish agents in it, (c) Dynamics 365 Contact Center with the voice channel available, (d) the ability to sign in with the Azure CLI (az login) to this tenant.

STEP 1 - PREFLIGHT (read-only; tell me the results before changing anything)
1. Tools: check "az", "pwsh" (PowerShell 7) and, if I prefer the command line import, "pac". Offer to install what is missing; do not install without my yes.
2. Sign in: "az login" (I complete it). Confirm the signed-in account and tenant with me, and that the environment URL is reachable.
3. Check the environment has Contact Center / Omnichannel: the table "Conversation" (logical name msdyn_ocliveworkitem) exists, and the built-in actions msdyn_ManageWorkstream, msdyn_ManageQueue, msdyn_ManageRoutingRule, msdyn_CreateOperatingHours and msdyn_ExpandOperatingHoursForEntityCollection exist. If not, STOP and tell me Contact Center must be provisioned first.
4. Check what already exists, and tell me before changing anything:
   - solution with unique name SalesSupportVoiceIVR (and its version); agent with schema name cr_salesandsupportivr
   - queues named Sales or Support; a workstream named "Voice IVR Workstream"; operating hours named like "Sales Hours"; a capacity profile "Voice IVR inbound"
   If anything exists, tell me and ask whether to reuse it, leave it, or stop. The setup script reuses items by name and is safe to re-run.
5. Capacity rule: a voice workstream needs a capacity profile with a work item limit of exactly 1. The script creates its own profile "Voice IVR inbound" (limit 1). Never change an existing shared profile such as "Default voice inbound".

STEP 2 - DOWNLOAD AND VERIFY
Download files A, B, C and D into a working folder. Compute the SHA256 of A, B and C and compare with D. If any differs, STOP and tell me.

STEP 3 - IMPORT THE SOLUTION
1. Import A (unmanaged) into my environment: Power Apps (make.powerapps.com) > Solutions > Import solution; or "pac solution import --path <A> --publish-changes" after "pac auth create --environment <URL>". Wait until the import finishes successfully.
2. Connection reference: when asked for "Microsoft Dataverse (Sales and Support IVR)", have me choose or create a Microsoft Dataverse connection owned by the account I named in STEP 0 question 5. If the connection needs my sign-in or consent, I do it.
3. Verify: the agent "Sales and Support IVR" (schema cr_salesandsupportivr) exists, and the connection reference is bound to a connected connection.

STEP 4 - PUBLISH THE AGENT (Copilot Studio)
1. Open https://copilotstudio.microsoft.com, choose the environment, open "Sales and Support IVR". Wait until it has finished provisioning (a minute or two after import).
2. Click Publish and wait for "Published". If publishing fails, read the error, fix only what it says (a missing connection is the usual cause), and publish again.
3. Verify: the agent has the Telephony and Dynamics 365 Contact Center (Omnichannel) channels, and in the topic "Check Hours And Transfer" the three Dataverse nodes show the connection with no red errors.

STEP 5 - DYNAMICS 365 SETUP (run script B)
1. Run, with my answers (add only the parameters that differ from the defaults):
   pwsh -File ./Install-D365Setup.ps1 -EnvironmentUrl <ENV URL> -TimeZoneCode <code> [-SalesTimeZoneCode <code> -SupportTimeZoneCode <code>] [-SalesStart 08:00 -SalesEnd 12:00 -SupportStart 12:00 -SupportEnd 18:00 -DaysOfWeek MO,TU,WE,TH,FR] [-SalesQueueName Sales -SupportQueueName Support]
2. Expect every section to print and the end to say "Valid: Workstream is valid and ready for use." The agent must be published first or the AddBot step prints a warning; if so, publish, wait a minute, and re-run the script (it is safe to re-run).
3. Verify in Copilot Service admin center (read-only): operating hours exist; queues Sales and Support are voice queues with the right hours; the workstream "Voice IVR Workstream" uses profile-based capacity with "Voice IVR inbound", fallback queue Support and the agent attached; the context variable QueueName (Text) is listed under Advanced settings > Context variables; the ruleset "Route to Queue" shows exactly "QueueName equals Sales" and "QueueName equals Support".
4. If the script cannot be run or a part fails, do that part by hand with docs/MANUAL-D365-SETUP.md and tell me what you did.

STEP 6 - PHONE NUMBER (only I can do this part; guide me)
1. Open the workstream "Voice IVR Workstream" and choose Add voice channel, then select my phone number. Do not buy or acquire a number for me.
2. Tell me omnichannel configuration changes can take up to 15 minutes to apply, then wait.
3. If I have no number yet, tell me exactly where to get one (Dynamics 365 Contact Center phone numbers, or bring your own carrier) and finish the other steps.

STEP 7 - REPRESENTATIVES
Add the users I named in STEP 0 question 6 to the queues Sales and Support (admin center > Queues > the queue > Users), and confirm they have a Contact Center / Omnichannel agent license and the Omnichannel agent role. Set nothing else on those users.

STEP 8 - TEST
1. No phone needed: run "pwsh -File ./Test-IvrConversation.ps1 -EnvironmentId <environment GUID> -Say Sales,No" and the same with "Support". Explain what I see: an OPEN queue prints a handoff.initiate event with QueueName=<queue>; a CLOSED queue plays the Dynamics 365 message, asks "Is there anything else I can help you with?", and with Yes replays the menu, with No says goodbye and ends. (Find the environment GUID in the Power Platform admin center.)
2. If both queues are closed right now, the open path cannot be shown. Offer a temporary test: attach an all-day operating-hours schedule to ONE queue, test, then restore its original hours. Do this ONLY after my explicit yes, tell me exactly what you will change, and confirm the restore.
3. Real call (once the number is active): ask me to call, press 1, then 2, say "sales" and "support", press 3 (invalid) and stay silent once. Call once inside and once outside each queue's hours. Confirm: closed hours play the message, then the follow-up question; open hours land in the correct queue in the Customer Service workspace.
4. If a call lands in the wrong queue, check, in this order: the context variable name is exactly QueueName; the rules read exactly "QueueName equals Sales" / "QueueName equals Support"; the call transcript's handoff contains QueueName; the fallback queue is Support. See docs/TROUBLESHOOTING.md.

OPTIONAL - REWORD THE CLOSED MESSAGE (only if I say yes)
The default message says "An agent will respond when we open", which is chat wording. Offer to change the voice automated message MessageReceivedOutsideOperationHoursAck_PhoneCall in Dynamics 365 (there can be two records with that name; change both) to wording I approve, for example: "Thank you for calling. Our sales team is available Monday to Friday, 8 AM to 12 PM, and our support team 12 PM to 6 PM. Please call back during those hours."

STOP AND ASK ME WHENEVER
- a check, count or screen differs from this prompt,
- you are asked to sign in, approve MFA, accept terms or pay for anything,
- the target is production and I have not said "yes, production",
- the next action could affect live calls and I have not said yes,
- something I did not ask for already exists with the same name,
- you would have to do something that is not in this prompt.

FINAL REPORT
Give me a table with every step and its result (OK / WARNING / FAILED), then: (1) anything I still have to do by hand (for example the phone number), (2) exactly what was created (solution, agent, connection reference, operating hours, queues, capacity profile, workstream, context variable, ruleset and rules) and who owns the Dataverse connection, (3) how to roll back: remove the workstream, queues, operating hours, capacity profile and ruleset in the admin center, then delete the solution "Sales and Support Voice IVR" and the agent, (4) links to docs/CONFIGURATION.md and docs/TROUBLESHOOTING.md, (5) a reminder that this is a community sample, not an official Microsoft product, and that a sandbox test comes first.

START with STEP 0.
````

### What this prompt cannot do for you

- It cannot sign in for you, approve MFA, or give consent to the Dataverse connection.
- It cannot acquire a phone number. You need one (or a bring-your-own-carrier number) before calls can reach the IVR.
- It needs a user with System Administrator rights, Contact Center with voice, and a Copilot Studio license; those are set up in Microsoft's admin centers, not by this package.
- If your assistant cannot operate a browser or run commands, it switches to a guided mode and walks you through each click.

## How it works, in one minute

1. The caller dials the number. The voice workstream hands the call to the **IVR agent first**.
2. **Main Menu** asks the question and accepts keypad **1/2** or the spoken words **sales/support**. It stores the choice in `Global.QueueName`.
3. **Check Hours And Transfer** looks up the queue by name, then asks Dynamics 365 (built-in action `msdyn_ExpandOperatingHoursForEntityCollection`) whether that queue has an available slot in the next minute.
4. **Closed**: it reads the voice message `MessageReceivedOutsideOperationHoursAck_PhoneCall` from Dynamics 365 and says it. It then asks **"Is there anything else I can help you with?"** (press 1 or say yes, press 2 or say no). **Yes** replays the menu so the caller can pick the other queue; **No** says goodbye and ends the call.
5. **Open**: it says "Please hold" and runs **Transfer conversation**, which hands the call to Dynamics 365 and passes `QueueName`.
6. In Dynamics 365 the **Route to Queue** ruleset reads `QueueName` and puts the call in the Sales or Support queue.

[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) explains **every node and every Dynamics 365 setting**, with screenshots of each.

## What was tested

| Check | Result |
|---|---|
| Real phone calls with keypad (DTMF) into the IVR, hours check, handoff to Dynamics 365 | Verified in the author's environment |
| Simulated chat: Sales closed -> message played -> "anything else?" -> No -> goodbye and end | Verified |
| Simulated chat: Sales closed -> message -> "anything else?" -> Yes -> menu replayed -> Sales -> message -> No -> end | Verified |
| Simulated chat: Support open -> handoff event with `QueueName=Support` | Verified |
| Invalid answer -> menu replayed | Verified |
| Clean install into a **second** environment (import the unmanaged solution, bind connection, publish, run setup script) | Verified on v1.0.0: import succeeded, agent published, script completed, both paths tested. v1.0.1 changes only the closed-branch topic and was tested in the author's environment. |

## Important info

- **The phone number is not created** by the package. Add yours to the workstream's Voice channel.
- **Operating hours are per queue, but the closed message is shared.** The out-of-hours voice message is a single Dynamics 365 automated message used by both queues. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) to change the wording or to give each queue its own message.
- **Queue names are matched by name.** The agent looks up queues called exactly `Sales` and `Support`. If you rename them, update the agent too (see [Rename the queues](docs/CONFIGURATION.md#rename-the-queues)).
- **The Dataverse connection is the maker's.** Callers are never asked to sign in. The connection owner's account runs the lookups, so use a service account in production.
- **Time zones follow the queue, never the caller.** Each queue's operating hours carry their own time zone and Dynamics 365 evaluates the call against it, so a caller in any country is judged by the queue's local hours. The setup script sets the zone for you (`-TimeZoneCode`, or a different one per queue with `-SalesTimeZoneCode` and `-SupportTimeZoneCode`). Default days are Monday to Friday and holidays live in each operating hours calendar. Several countries usually means one pair of queues per country: see [Time zones, countries and holidays](docs/CONFIGURATION.md#time-zones-countries-and-holidays).
- The agent uses **classic orchestration** with a closed-list menu on purpose: a deterministic menu is faster and more predictable on a phone than a generative one.

## Repository layout

```
.
├── README.md
├── LICENSE
├── agent-only-solution/             The agent solution zips + what it contains and expects (also attached to each Release)
├── scripts/
│   ├── Install-D365Setup.ps1        Dynamics 365 side
│   └── Test-IvrConversation.ps1     Text-chat call simulator
├── agent-source/                    Topics as YAML (reference)
└── docs/
    ├── HOW-IT-WORKS.md              Node-by-node explanation with screenshots
    ├── INSTALL.md
    ├── MANUAL-D365-SETUP.md         Click-by-click Dynamics 365 setup (no script)
    ├── CONFIGURATION.md
    ├── TROUBLESHOOTING.md
    ├── images/
    └── tools/make_diagrams.py       Regenerates the diagrams
```

## License

[MIT](LICENSE). Provided as a sample, without warranty. Test in a non-production environment first.
