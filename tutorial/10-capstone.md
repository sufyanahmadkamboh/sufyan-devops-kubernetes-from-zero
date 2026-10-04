# 10 · Capstone

> Goal: prove, without help, that you understand what you built and can fix it under pressure.
> Time: about 90 minutes. Level 10 of the [roadmap](../README.md#4-the-roadmap).

## Before you start

- For Part A: nothing but a quiet half hour. **No notes, no docs.**
- For Part B: a working kubeadm cluster from [kubeadm/README.md](../kubeadm/README.md) that passes the verification
  checklist. If you already cleaned it up in chapter 09, build it again (the second time takes much less time, and that
  is part of the point) or use [kubeadm/scripts/prepare-node.sh](../kubeadm/scripts/prepare-node.sh) for the
  preparation steps.

Open [capstone/README.md](../capstone/README.md).

## Part A · 15 questions

Answer every question **in writing** before you open its answer. Then mark each one:

| Mark | Meaning | What to do |
|---|---|---|
| ✅ | my answer contains everything in the official one | nothing |
| 🟡 | right idea, missing a piece | re-read the linked lesson section |
| ❌ | wrong or blank | redo the lab or chapter the answer links to, then answer again tomorrow |

Two or more ❌ in the same area (say, networking) tells you which chapter to repeat. That is more useful than a score.

## Part B · The Monday morning cluster

The scenario breaks your kubeadm cluster in **three** ways at once. That is realistic: real incidents rarely have one
neat cause, and one fault often hides another.

Ask a friend to run the setup block for you, or run it yourself and wait a day so you forget the details. Then work
like on-call:

1. **Start where the user starts.** `kubectl get nodes` on the control plane. What does the error tell you about
   *which layer* is broken?
2. **Fix the layer that hides the others first.** You cannot see the nodes while kubectl cannot reach the API server.
3. **Don't stop at "all green".** After the node is `Ready`, run the complete verification checklist from
   [docs/11](../docs/11-cluster-verification.md), including the request to a Pod on the **other** node. One of the three
   faults only shows there.
4. **One change at a time, then verify** with the same command that showed the symptom.

You have seen every one of these faults on its own in chapter 05. The capstone checks whether you can find them when
they come together and nobody tells you what happened.

### The incident note

Finish with a short note, 5–10 lines, as you would post it in a team channel after an incident:

```text
What broke:     ...
Impact:         ...  (what could users/developers not do, and since when)
Detection:      ...  (which command/symptom showed it)
Root causes:    1. ...  2. ...  3. ...
Fix:            ...
Prevention:     ...  (config management, monitoring, a smoke test that includes cross-node traffic, ...)
```

Writing it is part of the exercise. In a job, the note is often the only part of your work that managers and other
teams see.

## Expert commentary

- **Why it matters at work.** Multi-cause incidents are where experience shows. Juniors fix the first thing they find
  and declare victory; seniors verify the whole path end to end before they close the incident.
- **Common mistakes.** Restarting things at random (it can destroy evidence and create new problems); fixing the node
  and never testing cross-node traffic; forgetting to restore the backup of a file you changed.
- **What an interviewer asks.** Scenario questions like this one: "Monday morning, the cluster doesn't work. Walk me
  through what you do." Answer with the method from chapter 05, in order, out loud.

## Checkpoint

You are done when:

- [ ] Part A: at least 12 of 15 ✅, and you re-studied every ❌
- [ ] Part B: all three faults found and fixed, and the full verification checklist passes
- [ ] your incident note is written
- [ ] the cluster is cleaned up afterwards with [kubeadm/cleanup.md](../kubeadm/cleanup.md)

Next: [11 · Knowledge check](11-knowledge-check.md)
