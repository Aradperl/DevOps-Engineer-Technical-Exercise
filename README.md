# DevOps technical exercise

A small Python web service, built into a container and deployed to a local Kubernetes cluster with Terraform and Argo CD. The repository is [Aradperl/DevOps-Engineer-Technical-Exercise](https://github.com/Aradperl/DevOps-Engineer-Technical-Exercise). Work stayed on `main`. There is no feature branch and no pull request.

The cluster is still running on this machine. `terraform/kubeconfig` is the kubeconfig. That file, `terraform/.terraform/`, and `*.tfstate*` are not in git.

## What I finished

### Part 0 — service and image

`app/server.py` uses only the Python standard library. `GET /` returns HTML with the message, the app version, and the pod name. `GET /healthz` returns `200` and `ok`. Any other path returns `404`. The process listens on port 8080.

`MESSAGE` and `APP_VERSION` come from the environment. The pod name is `HOSTNAME`, which Kubernetes sets to the pod name.

The Dockerfile uses `python:3.12-slim` and runs as uid `65532`. I built `web:local` and checked it on this machine: `/` returned the HTML page, `/healthz` returned `200`, and `id` inside the container showed uid `65532`.

### Part 1 — cluster as code

`terraform/` creates a kind cluster named `exercise` with 1 control-plane and 2 workers, then installs ingress-nginx `4.15.1` and Argo CD `10.11.6`. Host port 80 is mapped to the control-plane, which is labeled `ingress-ready=true`. `terraform apply` created all three. `terraform destroy` would remove them. I did not destroy the cluster.

Checked after apply: three nodes Ready, one control-plane and two workers, ingress-nginx Running, and `curl http://127.0.0.1/` answered by nginx. A 404 there was expected before the app Ingress existed. `argocd-server`, `argocd-repo-server`, and `argocd-application-controller` were Running.

Terraform on this Mac is `brew install hashicorp/tap/terraform`. `brew install terraform` no longer exists in Homebrew core. Providers are pinned in `terraform/versions.tf`: `tehcyx/kind` `0.13.0` and `hashicorp/helm` `2.17.0`.

### Part 2 — GitOps

Argo CD Application `web` syncs `deploy/web` from `main` into the `default` namespace. The Application manifest is `deploy/application.yaml`. It is applied once into the `argocd` namespace and is not inside `deploy/web`, so Argo CD does not copy that Application into `default`.

`deploy/web/deployment.yaml` has 2 replicas, readiness and liveness probes on `/healthz`, CPU and memory requests and limits, and a rolling update of `maxUnavailable: 0` and `maxSurge: 1`. The container runs as uid `65532`. `deploy/web/service.yaml` is a ClusterIP Service on port 80, targeting container port 8080. `deploy/web/ingress.yaml` uses class `nginx` and host `web.local`. `/etc/hosts` has `127.0.0.1 web.local`.

The first sync used the local image loaded into kind. The page opened in the browser at `http://web.local`.

### Part 3 — CI

`.github/workflows/image.yml` runs on every push to `main`, except when the pusher is `github-actions[bot]`. It builds the image, pushes `ghcr.io/aradperl/devops-engineer-technical-exercise:<full sha>`, and commits that tag back into `deploy/web/deployment.yaml`. CI does not run kubectl. Argo CD rolls out the bot commit.

The GHCR package is public, so the kind nodes can pull it. The repository's Actions token was read-only at first, which would have blocked that commit. It is allowed to write now.

The image is built for `linux/arm64`, with provenance and sbom turned off. The first published tag was `linux/amd64` plus an attestation manifest. The nodes rejected it. See the decision below.

I changed `MESSAGE` to `hello during the rollout` and pushed. The browser at `http://web.local` showed that message, version `0.1.0`, and a new pod name. The Deployment image is the tag in `deploy/web/deployment.yaml`. A later push to `main` builds a new tag and Argo CD follows it.

### Bonus

`deploy/web/hpa.yaml` scales `web` from 2 to 5 replicas at 70% CPU. The web Application syncs it with the rest of `deploy/web`.

metrics-server and kube-prometheus-stack are separate Argo CD Applications, `deploy/metrics-server.yaml` and `deploy/monitoring.yaml`, because they are Helm charts. metrics-server chart `3.14.0` is started with `--kubelet-insecure-tls`, which kind needs. kube-prometheus-stack chart `92.14.0` installs Prometheus and Grafana. Alertmanager is off. Grafana is at `http://grafana.local` through the existing ingress. `/etc/hosts` has `127.0.0.1 grafana.local`. The login user is `admin`. The password is the `admin-password` key in the Secret `monitoring-grafana` in the `monitoring` namespace.

I opened Grafana in the browser. Applications `web`, `metrics-server`, and `monitoring` were Synced and Healthy, and the HPA was reporting CPU against the 70% target with 2 replicas.

## What is missing

The required parts and the bonus are done. I did not build an EKS cluster. The EKS section below is the note the exercise asked for, not a second environment.

Alertmanager is disabled. Prometheus on this laptop does not use a persistent volume. Both were left out so the local cluster stayed small enough to run beside the app.

## One decision and why

The workflow builds `linux/arm64` and turns provenance off.

GitHub-hosted runners are amd64. The kind nodes on this Mac are arm64. The first green workflow published an amd64 image wrapped in a manifest list that also contained an attestation. The new pod stayed in `ImagePullBackOff` with `no match for platform in manifest`. The two old pods kept serving because `maxUnavailable` is 0, so the page stayed up while I read the pod event and compared it with `docker buildx imagetools inspect`.

An arm64 image without the attestation manifest is one image the nodes can run. A multi-arch image was unnecessary for this exercise.

## One place the AI was wrong, and how I noticed

The first rollout loop was `curl http://web.local/` with a 2 second limit. Every line was `000fail`.

I noticed because the browser still showed the page, and `/etc/hosts` already had `127.0.0.1 web.local`. A request to `http://127.0.0.1/` with `Host: web.local` returned `200` and the HTML. Curl was spending the whole timeout on the name. macOS treats `.local` as a network discovery name. The loop that reaches the ingress is:

```bash
curl --resolve web.local:80:127.0.0.1 http://web.local/
```

That version returned `200`. The `000fail` lines were the lookup, not failed responses from the app.

## What would change on EKS

The application manifests and the GitHub workflow stay. These pieces change:

- Terraform creates an EKS cluster and a managed node group instead of a kind cluster. `terraform destroy` still removes them. kubectl uses the AWS kubeconfig, not `terraform/kubeconfig`.
- ingress-nginx is a LoadBalancer, or the AWS Load Balancer Controller replaces it. The control-plane host port 80 and the `ingress-ready` label go away.
- The image stays the public GHCR tag, or moves to ECR. There is no `kind load`, and `imagePullPolicy: Never` is not used.
- Prometheus keeps its data on a persistent volume such as gp3.
- metrics-server does not get `--kubelet-insecure-tls`. EKS kubelet certificates are ones the API server trusts.

## Where to look

| Path | What it is |
| --- | --- |
| `app/server.py` | The web process |
| `Dockerfile` | Non-root image, uid 65532 |
| `terraform/` | kind cluster, ingress-nginx, Argo CD |
| `deploy/web/` | Deployment, Service, Ingress, HPA |
| `deploy/application.yaml` | Argo CD app for `deploy/web` |
| `deploy/metrics-server.yaml` | Argo CD app for metrics-server |
| `deploy/monitoring.yaml` | Argo CD app for Prometheus and Grafana |
| `.github/workflows/image.yml` | Build, push, and write the image tag back |
| `ai-prompts.md` | Prompts used for each part |

Pages on this machine: `http://web.local` and `http://grafana.local`. Inspect the cluster with `kubectl --kubeconfig=terraform/kubeconfig`. Leave the cluster up.
