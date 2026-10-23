# Agent-only solution

This folder contains **only the Copilot Studio agent**. Use it if you want to import the IVR agent and build the Dynamics 365 side **yourself, by hand**, instead of running the setup script or the AI assistant prompt.

| File | Use |
|---|---|
| `SalesSupportVoiceIVR_unmanaged.zip` | The solution. It is **unmanaged**, so you can open the agent in Copilot Studio and edit any topic. |

The same file is attached to every [Release](../../../releases). All solution packages in this repository are **unmanaged**. Current version: **1.0.1.0**.

## What is inside

- The agent **Sales and Support IVR** (schema name `cr_salesandsupportivr`): the menu, the operating-hours check, the transfer, the closed-queue follow-up question, and the voice system topics.
- **One connection reference**, `Microsoft Dataverse (Sales and Support IVR)`. You choose the Dataverse connection when you import.

## What is NOT inside

Nothing from Dynamics 365 Contact Center. The package has no tables, flows, plugins or settings. You create these yourself (or with the script):

| Not included | Where to create it |
|---|---|
| Operating hours for each queue | [MANUAL-D365-SETUP.md, part 1](../docs/MANUAL-D365-SETUP.md#1-operating-hours-one-per-queue) |
| Voice queues **Sales** and **Support** | [part 2](../docs/MANUAL-D365-SETUP.md#2-queues-sales-and-support) |
| Capacity profile with a limit of 1 | [part 3](../docs/MANUAL-D365-SETUP.md#3-capacity-profile-voice-needs-exactly-one-call) |
| Voice workstream, with this agent attached and your phone number | [part 4](../docs/MANUAL-D365-SETUP.md#4-the-voice-workstream) |
| Context variable `QueueName` | [part 5](../docs/MANUAL-D365-SETUP.md#5-the-context-variable-queuename-verified) |
| Routing rules `QueueName equals Sales / Support` | [part 6](../docs/MANUAL-D365-SETUP.md#6-the-routing-rules-verified-list-editor-wording-may-vary) |

## Steps

1. **Import** the zip: <https://make.powerapps.com> > Solutions > Import solution. When asked for the connection reference, choose (or create) a **Microsoft Dataverse** connection.
2. **Publish** the agent in <https://copilotstudio.microsoft.com> (wait for provisioning to finish first). Publishing provisions the Telephony and Dynamics 365 Contact Center channels.
3. **Build the Dynamics 365 side** with [MANUAL-D365-SETUP.md](../docs/MANUAL-D365-SETUP.md).
4. **Test** with [`Test-IvrConversation.ps1`](../scripts/Test-IvrConversation.ps1) and a real call. See [INSTALL.md](../docs/INSTALL.md#step-6-test).

## What the agent expects from Dynamics 365

The agent works only if your Dynamics 365 setup matches these four things exactly (spelling and capital letters):

| The agent... | ...needs this in Dynamics 365 |
|---|---|
| Looks up queues **by name** | Voice queues named exactly **`Sales`** and **`Support`** |
| Asks whether the queue is open now | Each queue has **operating hours** attached (a queue with none is open 24x7) |
| Sends `Global.QueueName` on the transfer | A workstream **context variable `QueueName`** (Text) |
| Relies on routing after the transfer | Rules **`QueueName equals Sales`** -> queue Sales and **`QueueName equals Support`** -> queue Support |
| Reads the closed-queue message | The voice automated message **`MessageReceivedOutsideOperationHoursAck_PhoneCall`** (exists by default) |

Different queue names? Change the two literals in the **Main Menu** topic. See [Rename the queues](../docs/CONFIGURATION.md#rename-the-queues).

## Checksums (SHA256)

```
6f5da5f80ed4c5f7b19d51beba04d655aee5fea7cef8c288c67646967e81461e  SalesSupportVoiceIVR_unmanaged.zip
```

Want everything done for you instead? Use the setup script or the AI assistant prompt in the [main README](../README.md).
