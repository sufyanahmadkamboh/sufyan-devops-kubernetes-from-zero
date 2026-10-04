# LinkedIn package

| File | Use |
|---|---|
| `post.md` | Post text, written for a beginner audience |
| `carousel/carousel.pdf` | **Recommended:** upload as a *Document* post. LinkedIn shows it as a swipeable carousel |
| `carousel/slide-01.png` … `slide-11.png` | The same slides as images (1080×1350), for a multi-image post |
| `carousel/slides.html` | Source of the slides. Edit it and re-render each slide with a headless browser (`slides.html?s=N`) |
| `carousel/qr-repo.svg`, `qr-portfolio.svg` | The QR codes used on the last slide |
| `project-image.png` | Single overview image (1200×627) |
| `project-summary.md` | Short technical summary |
| `hashtags.txt` | Hashtags |

## The slides (visual first: one picture per idea, short captions)

| # | Visual | Message |
|---|---|---|
| 1 | "The usual tutorial" vs. four tiles: kubeadm, Minikube, MicroK8s, EKS | What it is, and the pain |
| 2 | 4 panels: copy-paste installs, NotReady panic, hidden cloud costs, no failure practice | Why first installs go wrong |
| 3 | A road with four vehicles: car from parts, simulator, scooter, taxi | The idea: four ways to "drive" Kubernetes |
| 4 | "Use it when" / "skip it when" panels | When to use it |
| 5 | A winding path through levels 1–10 | How a learner uses it (the roadmap) |
| 6 | Control plane and node components, and where each method puts them | Architecture |
| 7 | lesson.md → mdrun.py → fresh VMs, output written back; CI jobs; the EKS run | How it works |
| 8 | Cluster lifetime bar (14.5 / test / 11 min), cost, inventory, 35 s, five real error messages | Measured results (lab) |
| 9 | Number tiles: 13 / 4 / 8 / 5 / 15 / 12, video, PDF, glossary | Study material |
| 10 | Terminal staircase: clone, multipass launch, prepare-node.sh, kubeadm init, Flannel, join | Run it yourself |
| 11 | QR codes to the repository and the portfolio, and a question | Links |

## How to post

1. Start a post, choose **Add a document**, and upload `carousel/carousel.pdf`.
2. Give it a title, for example *"Kubernetes From Zero: install it 4 ways, break it, fix it"*.
3. Paste the text from `post.md`.
4. Optional: post `project-image.png` as a single image instead, or upload the 11 PNGs as a multi-image post.
5. Reply to comments about install problems with the matching lab in `troubleshooting/`.
