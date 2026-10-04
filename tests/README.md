# tests · how the lessons are tested

Every command in the lessons is executed. Nothing in this repository was "written from memory": the outputs under each
command are what the command printed when the lesson was run.

## The runner: mdrun.py

`tests/mdrun.py` reads Markdown files and runs their ```bash blocks in order. An HTML comment just above a block (it
does not show on GitHub) tells the runner where and how to run it:

| Annotation | Meaning |
|---|---|
| `on=k8s-cp` | run inside that VM (`multipass exec k8s-cp -- bash -e`), as the `ubuntu` user |
| `on=k8s-cp+k8s-worker` | run on each of those VMs |
| *(no `on=`)* | run on the host (your computer / the CI runner) |
| `contains=TEXT` / `absent=TEXT` | the output must / must not contain TEXT (can repeat) |
| `fail` | the command is expected to fail (non-zero exit) |
| `retry=N` | repeat the check up to N times, 2 s apart (for things that become ready over time) |
| `timeout=S` | give up after S seconds (default 600) |
| `output`, `output=head:N`, `output=tail:N` | with `--update`, write the real output into the ```text block below |
| `skip` | never run (interactive commands, or commands for another operating system) |
| `aws` | runs only with `MDRUN_AWS=1` (creates billable AWS resources) |
| `<!-- test-run[ on=VM]: command -->` | a hidden step that is run but not shown in the lesson |

```text
python3 tests/mdrun.py [--update] [--record DIR] [--stop-on-failure] FILE.md [FILE.md ...]
```

`--record DIR` saves every command with its output, exit code and duration as numbered files (the video's terminals
are built from these). Before anything is written, the output is sanitised: your home and repository paths, your user
name, IAM user names, e-mail addresses and 12-digit AWS account IDs are masked.

## In CI: real VMs on GitHub-hosted runners

[.github/workflows/test.yaml](../.github/workflows/test.yaml) has these jobs:

| Job | What it runs |
|---|---|
| Static checks | relative links in every Markdown file, ShellCheck on the scripts, `eks/cluster.yaml` safety assertions (region, version, tags, private nodes) |
| Run lessons (kubeadm) | the kubeadm lesson, troubleshooting 01–07, lab 01, kubeadm cleanup, on 2–3 Ubuntu 24.04 VMs |
| Run lessons (minikube) | the Minikube lesson, troubleshooting 08, lab 02, examples/nginx, Minikube cleanup (Docker driver) |
| Run lessons (microk8s) | the MicroK8s lesson, lab 03, MicroK8s cleanup, on one Ubuntu 24.04 VM |
| Install commands (Windows, macOS) | the `winget` / `brew` install commands from the lessons, then `--version` of each tool |

GitHub's Linux runners support nested virtualisation (KVM). The workflow installs **LXD** and puts
[shims/multipass](shims/multipass) on the PATH: a small script that translates the `multipass` commands used in the
lessons (`launch`, `exec`, `info`, `list`, `stop`, `start`, `delete`, `purge`) to LXD virtual machines. The lessons
therefore run unchanged in CI and on your computer.

Each run uploads the recordings and a patch with the real outputs as an artifact (`run-kubeadm`, `run-minikube`,
`run-microk8s`).

## The EKS lesson

The EKS blocks are marked `aws`: they create billable resources and are not run in CI. They were run from a laptop
against a real AWS account (region `eu-central-1`):

```text
MDRUN_AWS=1 MDRUN_ONLY=aws python3 tests/mdrun.py --update eks/README.md
MDRUN_AWS=1 MDRUN_ONLY=aws python3 tests/mdrun.py --update eks/cleanup.md
```

followed by `eks/scripts/verify-cleanup.sh` and a comparison of `eks/scripts/inventory.sh` with the inventory taken
before the run.

## Link checker

```text
python3 tests/check_links.py
```

checks every relative link (files and `#anchors`) in every Markdown file.
