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

The image build runs on the desktop, where Docker is installed:

```bash
docker build -t web:local .
docker run --rm -d --name web-part0 -p 8080:8080 web:local
curl -fsS http://127.0.0.1:8080/
curl -fsS -D- http://127.0.0.1:8080/healthz
docker exec web-part0 id
docker rm -f web-part0
```

`id` should show uid 65532.

Part 1 was applied on 26 Oct 2026 from `terraform/`. `terraform apply` added the kind cluster, ingress-nginx, and Argo CD. The checks below passed: three Ready nodes (1 control-plane, 2 workers), the control-plane labeled `ingress-ready=true`, the ingress-nginx controller Running, `curl http://127.0.0.1/` returning nginx's 404, and `argocd-server`, `argocd-repo-server`, and `argocd-application-controller` Running. The cluster is still up. Terraform on this Mac is `brew install hashicorp/tap/terraform`, because `brew install terraform` no longer exists. Chart versions pinned in Terraform:

- ingress-nginx `4.15.1`
- argo-cd `10.11.6`
- provider `tehcyx/kind` `0.13.0`
- provider `hashicorp/helm` `2.17.0`

From `terraform/`:

```bash
terraform init
terraform validate
terraform apply
```

Then:

```bash
kubectl --kubeconfig=kubeconfig get nodes
kubectl --kubeconfig=kubeconfig get nodes -l node-role.kubernetes.io/control-plane --no-headers
kubectl --kubeconfig=kubeconfig get nodes -l '!node-role.kubernetes.io/control-plane' --no-headers
kubectl --kubeconfig=kubeconfig get nodes -l ingress-ready=true --no-headers
kubectl --kubeconfig=kubeconfig get pods -n ingress-nginx
curl -sI http://127.0.0.1/
kubectl --kubeconfig=kubeconfig get pods -n argocd
terraform plan -destroy
```

Pass looks like this: `terraform validate` and `terraform apply` exit 0. Three nodes are Ready, one of them is the control-plane, two are workers, and the control-plane has `ingress-ready=true`. The ingress-nginx controller is Running. `curl` reaches nginx. A 404 is a pass, because the app Ingress is Part 2. `argocd-server`, `argocd-repo-server`, and `argocd-application-controller` are Running. `terraform plan -destroy` lists the cluster and both Helm releases. Do not apply that destroy plan. Leave the cluster up.

Helm uses the cluster's API address and certificates. kubectl uses `terraform/kubeconfig`. That file, `.terraform/`, and `*.tfstate*` stay uncommitted.

Part 2 manifests are in the repo and have not been synced yet. Argo CD reads GitHub, so this commit has to be pushed before the Application can sync.

- `deploy/web/deployment.yaml`: 2 replicas, probes on `/healthz`, requests and limits, rolling update `maxUnavailable: 0` and `maxSurge: 1`. Image `web:local` with `imagePullPolicy: Never`. The process runs as uid 65532. `HOSTNAME` is left unset so Kubernetes sets it to the pod name.
- `deploy/web/service.yaml`: ClusterIP, port 80 to container port 8080.
- `deploy/web/ingress.yaml`: class `nginx`, host `web.local`.
- `deploy/application.yaml`: applied once into the `argocd` namespace. It syncs `deploy/web` from `main`. It stays outside `deploy/web` so Argo CD does not copy that Application into `default`.

After the push, from the repo root:

```bash
docker build -t web:local .
kind load docker-image web:local --name exercise
kubectl --kubeconfig=terraform/kubeconfig apply -f deploy/application.yaml
kubectl --kubeconfig=terraform/kubeconfig get applications -n argocd
kubectl --kubeconfig=terraform/kubeconfig get pods,svc,ingress
grep -q 'web.local' /etc/hosts || echo '127.0.0.1 web.local' | sudo tee -a /etc/hosts
curl -fsS http://web.local/
```

A pass is Application `web` Synced and Healthy, two Running pods, and `curl` printing the HTML page. Open `http://web.local` in a browser too. A refresh can show either pod name. Leave the cluster up.
