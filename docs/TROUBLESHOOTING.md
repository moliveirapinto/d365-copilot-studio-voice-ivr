# Troubleshooting

## The caller is transferred even though the queue is closed

1. **Check which key was pressed.** In the call transcript (Copilot Studio > Analytics > sessions, or Dataverse `conversationtranscript`) look for the user message and `dtmfMappingKey`. A common cause is simply that the *other* queue was chosen and it is open.
2. Look for a `QueueClosed` trace in the transcript. `QueueClosed = False` means the hours check saw an available slot.
3. Confirm the **queue has operating hours attached** (a queue with no operating hours is open 24x7).
4. Confirm the **time zone** and days of the operating hours record.
5. Run the text simulation (`Test-IvrConversation.ps1`) at the same moment and compare.

## "Voice workstreams require a capacity profile with work item limit set to exactly 1"

You cannot save the **Work distribution** panel because the selected capacity profile has a limit other than 1. Select **Voice IVR inbound** (created by the script), or set the limit of your chosen profile to **1**. Note the shipped **Default voice inbound** profile should be 1; if it was edited in your environment it will fail this check.

## Red text in the Copilot Studio designer

| Message | Cause | Fix |
|---|---|---|
| *Input variable 'Action parameters' is of incorrect type: Record* | Dates or the queue table were passed as text. | Pass real date-times (`Now()`) and a table (`[{...}]`). The packaged agent already does. |
| *Missing required property 'Variable'* on a Condition | The condition is a formula such as `IsBlank(...)` that the designer cannot show as variable / operator / value. | Put the result in a variable first, then test `variable = true`. The packaged agent already does. |
| Connection error on a Dataverse node | The connection reference is not bound after import. | Re-select a Dataverse connection on the node, or fix the connection reference in the solution. Publish again. |

## The agent will not publish, or says "model not trained"

This solution uses classic orchestration. If you changed the agent to use NLU+ and see `AdvanceNluModelNotTrained`, wait for training or switch back to the default recognizer.

## The setup script fails

| Error | Fix |
|---|---|
| `Could not get a token. Run: az login` | Sign in with `az login` to the right tenant. |
| `Failed to create operating hours` | The days must be two-letter codes (`MO,TU,...`), times `HH:mm`, and the date format is handled by the script. Check the time zone code. |
| `PhoneNumber is required` | You tried to create the voice channel setting without a number. The script does not; add the number in the admin center. |
| `Could not add the agent automatically` | The agent is not published or not provisioned yet. Publish it in Copilot Studio, wait a minute, then re-run the script (it is safe to re-run). |
| Routing rules not applied | Wait for the context variable to propagate (about 20 seconds) and re-run. |

## The call is transferred but lands in the wrong queue

- The **context variable** `QueueName` must exist on the workstream (the script creates it).
- The **rule conditions** must compare `liveworkitemcontext.QueueName` to exactly `Sales` / `Support` (case matters).
- The fallback queue is **Support**: an unmatched call goes there.
- The transfer carries the value from `Global.QueueName`. Confirm in the transcript that the **handoff** activity contains `QueueName`.

## Nobody can answer the call

Add representatives to the **Sales** and **Support** queues and set their presence to **Available** or **Busy**. The profile-based capacity is **1** call per representative.

## I hear an unexpected speaking style

The voice style comes from the voice configuration of the agent, not from the topics. Change the voice or the style in the agent's voice settings and place a test call.

## Where to look in the logs

| What | Where |
|---|---|
| Every step of one call (variables, nodes, errors) | Copilot Studio **Analytics** / the Dataverse table `conversationtranscript` |
| Bot session outcomes | Dataverse `msdyn_botsession` |
| The Dynamics 365 conversation | Customer Service workspace > conversation history; table `msdyn_ocliveworkitem` |
