# DevOps technical exercise

Small Python web service, deployed to a local Kubernetes cluster the GitOps way.

Build window: Monday 26 Oct 2026, finish the build around 16:45 Asia/Jerusalem. A review follows. Finishing every part is not the goal. The history and being able to explain each file are.

## Tools

Already installed on the build machine. Versions were checked there; this file names the tools and their roles. The repo is [Aradperl/DevOps-Engineer-Technical-Exercise](https://github.com/Aradperl/DevOps-Engineer-Technical-Exercise), public, cloned locally.

| Tool | Role |
| --- | --- |
| Python 3 standard library | The web process. No framework and no pip dependencies. |
| Docker | Build and run the image locally. |
| kind | Local cluster: 1 control-plane and 2 workers. |
| Terraform (`tehcyx/kind`, Helm, Kubernetes providers) | Create the cluster, ingress-nginx, and Argo CD. `terraform destroy` removes them. |
| kubectl | Inspect the cluster. Not used from CI. |
| Helm | Install ingress-nginx and Argo CD from Terraform. |
| ingress-nginx | Ingress controller. Host port 80 on the control-plane. |
| Argo CD | Syncs manifests from this repo. |
| GitHub Actions and GHCR | Part 3. Build on push to `main`, push the image tagged with the commit SHA, update that tag in git. The GHCR package is public. |

Git stays on `main`. Commit and push as each slice lands. No feature branch and no pull request.

## What the app does

`GET /` returns an HTML page, not JSON. The page shows a message, the app version, and the pod name.

- `MESSAGE` and `APP_VERSION` come from environment variables.
- The pod name is `HOSTNAME`, which Kubernetes sets to the pod name.
- `GET /healthz` returns 200.
- The process listens on port 8080 and runs as uid 65532.

Local image tag: `web:local`.

## Steps

### Part 0 — service and image

1. This README, with the plan and the tools above.
2. `ai-prompts.md` for the prompts used to produce each change.
3. `app/server.py` on port 8080.
4. A Dockerfile that runs as non-root. Build it and run it locally. Check `/` and `/healthz`.

### Part 1 — cluster as code

Terraform creates the kind cluster (1 control-plane, 2 workers) and installs ingress-nginx and Argo CD. `terraform apply` brings it up. `terraform destroy` tears it down.

### Part 2 — GitOps

Manifests live in `deploy/`. Argo CD syncs them from `main`.

- Deployment: 2 replicas, readiness and liveness probes on `/healthz`, resource requests and limits, rolling update `maxUnavailable: 0` and `maxSurge: 1`.
- Service and an Ingress for `web.local`.
- The page opens in a browser on this machine.

The first sync can use the local image loaded into kind. The registry tag comes in Part 3.

### Part 3 — CI, if time remains

A workflow on push to `main` builds the image, pushes `ghcr.io/aradperl/devops-engineer-technical-exercise:<full-sha>`, and commits the new tag back to `deploy/`. The workflow skips pushes from `github-actions[bot]` so that commit does not loop. CI does not run `kubectl apply`.

Then change the message, push, and run a curl loop during the rollout. The loop should show no failed responses.

### Bonus — only after Part 3

- HorizontalPodAutoscaler, min 2, max 5.
- Prometheus and Grafana, installed through Argo CD.
- A short note here on what would change to run this on EKS.

If time runs short, drop in this order: bonus, the live curl loop, the CI tag write-back, the workflow itself, and Terraform only if apply is still failing. Keep the image, the service, the Deployment shape, this README, and `ai-prompts.md`.

## Status

Part 0, checked from the agent session on 26 Oct 2026:

- `GET /` returns HTML with the message, version `0.1.0`, and hostname `local-check`.
- `GET /healthz` returns 200 and `ok`.
- Any other path returns 404.

Docker is not installed in that session, so the image is not built there yet. On the desktop, where Docker is installed, run:

```bash
docker build -t web:local .
docker run --rm -d --name web-part0 -p 8080:8080 web:local
curl -fsS http://127.0.0.1:8080/
curl -fsS -D- http://127.0.0.1:8080/healthz
docker exec web-part0 id
docker rm -f web-part0
```

`id` should show uid 65532. Nothing has been deployed. The cluster is not up.
