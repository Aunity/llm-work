---
name: workstyle-task
description: Maintain and resume evidence-backed task state when Workstyle is selected or a user asks to continue a Workstyle task. Supports multi-step implementation, investigation, and scientific work across CLI tools and sessions.
---

# Workstyle task

Use a project-local task record to carry decisions and verified progress across
sessions. The selected working directory is the project; global skill files are
instructions, not the place to save project results.

## Start or recover

Read project instructions and inspect the current working state. For a new
multi-step task, create `.workstyle/tasks/<UTC-time>-<short-name>.md` using
[the task record](references/task-record.md). State the requested outcome,
authorized scope, acceptance evidence and consequential unknowns. Resolve routine
implementation details yourself; ask for missing information only when it changes
the result or for authority that has not already been granted.

When resuming, use the task named by the user. Otherwise inspect incomplete records
in this project's `.workstyle/tasks/`. Resume a unique match; if several plausible
tasks remain, show their names and ask which one to continue. Reconcile the record
and artifacts against current files and git state. A task record does not grant
new authority for external mutations.

## Advance through evidence

Translate important unknowns into source checks or small discriminating experiments.
For debugging, establish a reproduction, record a causal hypothesis, and test it
before layering further fixes. Change the approach when the evidence contradicts it.

Update the record after a milestone, changed decision, verified result or actual
blocker. Link to logs and outputs. Continue authorized work through the remaining
acceptance items; keep documents and chat aligned.

Use relevant existing skills and project commands. For complex multi-file changes
or consequential scientific results, request a read-only reviewer subagent when
the selected profile authorizes it and the host supports it. Supply requirements
and raw artifacts, not a desired verdict. Verify findings before integrating fixes.

## Verify and hand off

Choose checks that test the requested behavior and important failure cases. A bug
fix needs evidence about the original symptom. Browser work needs a rendered flow
when available. Scientific work may need units, invariants, reference values,
data-split integrity and uncertainty checks relevant to the method. Successful
execution or an output file alone does not establish these properties.

Compare each acceptance item with actual outputs before claiming completion.
Record the command, result, artifact path and meaningful limits. State what was
not checked, and preserve the acceptance criteria when a check fails. A supported
negative finding can be a valid outcome of exploration.

Use `complete` only when the requested deliverables and verification are done.
For unfinished work record the next action and use `in_progress`, `blocked` or
`paused` as appropriate; use paused only at the user's request. These are task
record states, not calls to a host's goal API.

End with a screen-readable result, evidence, limitations and next action if needed.
Saving a document does not replace explaining its important content in chat.
