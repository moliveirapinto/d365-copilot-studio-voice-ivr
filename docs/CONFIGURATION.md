# Configuration and customization

## Change the operating hours

Operating hours live in Dynamics 365, not in the agent, so **no agent change is needed**.

1. Copilot Service admin center > **Calendars** > **Operating hours** > **Manage**.
2. Open **Sales Hours** or **Support Hours**, go to **Working Hours**, and edit the recurring event (this event, this and following, or all events).
3. Add **holidays** with **New > Holiday**. The IVR will treat the queue as closed on those days.

The change is used by the very next call.

## Change what callers hear when the queue is closed

The agent reads the voice automated message **`MessageReceivedOutsideOperationHoursAck_PhoneCall`** from Dynamics 365 on every call.

1. Copilot Service admin center: find **Automated messages** (voice channel messages are the ones whose names end in `_PhoneCall`).
2. Edit **MessageReceivedOutsideOperationHoursAck_PhoneCall**.
3. There can be **more than one record with that name**. The agent uses the first one returned, so edit all of them.

The default text is chat-oriented ("An agent will respond when we open"). Consider something like:

> Thank you for calling. Our sales team is available Monday to Friday, 8 AM to 12 PM, and our support team 12 PM to 6 PM Eastern. Please call back during those hours.

### Different message per queue (optional)

The Dynamics 365 message is shared by both queues. To give each queue its own wording, in **Check Hours And Transfer**, inside the **closed** branch, replace the **Set variable** `Topic.OohMessage` with a **Condition** on `Global.QueueName` that sets a different literal text for Sales and Support (keep the Dataverse message as the fallback). The trade-off is that the wording then lives in the agent.

## Rename the queues

The queue names appear in two places:

| Where | What to change |
|---|---|
| **Main Menu** topic, the two branches | `Global.QueueName` literal values `Sales` and `Support` |
| **Dynamics 365** | Queue names, the routing rule conditions (`QueueName` equals ...), and the rule actions |

Easiest: run `Install-D365Setup.ps1` with `-SalesQueueName` / `-SupportQueueName` on a fresh setup, then edit the two literals in Main Menu and publish.

## Change the menu wording or the options

Edit **Main Menu**. Question node:

- **Message**: the spoken prompt.
- **Options for user**: option names (spoken) and the **DTMF key** for each.
- Add an option with **New option**, then add a matching branch in the **Condition** node and make sure a queue with that name exists.

For a third queue, also add a rule in the **Route to Queue** ruleset for the new `QueueName` value and create the queue and its hours.

## Change the voice

Copilot Studio > the agent > **Settings** > **Voice** (or the voice settings of the agent): pick another voice, speed or SSML style. The default voice can use a different speaking style than you want, so listen to a test call.

## Use another language

Add the language in the agent, translate the messages in Conversation Start, Main Menu, Check Hours And Transfer and the voice topics, and set the Dynamics 365 automated message text for that language. See Microsoft's multilingual voice guidance for workstreams.

## Production hardening checklist

- Use a **service account** for the Dataverse connection and give it only the privileges it needs (read queues, read automated messages, run the operating-hours action).
- Put the solution through your normal ALM (managed solution in test and production).
- Add monitoring: Copilot Studio **Analytics**, and the Dynamics 365 Contact Center real-time reports.
- Decide what **fail-open** means for you: today, if the queue cannot be found the call is transferred. If you prefer it to end with a message instead, change the first **Set variable** in Check Hours And Transfer to `Topic.QueueClosed = true` and handle the not-found case before the closed branch.
- Test holidays, time zone changes, and the last minute before closing.
