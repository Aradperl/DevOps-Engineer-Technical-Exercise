# AI prompts

I used Cursor to plan, draft, and debug. I read the diff before each commit, committed on `main` myself, and ran the checks on this machine. The prompts below are the instructions I gave, cut down to the ask. When a check failed, I pasted the result and asked for the cause before accepting a change.

## Plan

Read the candidate instructions. Do not write code yet. Propose a tool choice and the order of work for a local cluster, Python, and this existing public repository. Stay on `main`. No pull request. Wait for me to approve the plan.

## Part 0

Draft the plan into the README and list the prompts in `ai-prompts.md`. Stop there so I can read it.

The plan is fine. Add `app/server.py` and a non-root Dockerfile. Python standard library only. `GET /` is HTML with the message, version, and hostname. `GET /healthz` returns 200. The process listens on 8080 as uid 65532. Explain each file in a few sentences. I will build `web:local` and curl it myself.

## Part 1

Plan the Terraform only. I want a kind cluster named `exercise`, 1 control-plane and 2 workers, ingress-nginx, and Argo CD, and `terraform destroy` must remove them. Tell me how I will know the apply worked. Do not apply it.

`brew install terraform` failed. Homebrew says there is no formula by that name. Tell me the current way to install Terraform, then the commands to run from `terraform/`. I will apply and run the node checks.

`terraform init` changed `terraform/.terraform.lock.hcl` by two `h1` lines. Explain that diff. I will commit only that file.

## Part 2

The cluster is up. Plan the GitOps manifests before writing them. I want 2 replicas, probes on `/healthz`, requests and limits, `maxUnavailable: 0`, `maxSurge: 1`, and an Ingress for `web.local`. The first image can be `web:local` loaded into kind. Explain where the Argo CD Application should live so it is not synced into the wrong namespace.

Write those files. I will read them, commit, push, load the image, and apply the Application. Give me the checks, including the browser.

The page is open at `http://web.local`. Record that in the README. I will commit it.

## Part 3

Part 2 is on `main`. Draft a GitHub Actions workflow. On push to `main`, build the image, push `ghcr.io/aradperl/devops-engineer-technical-exercise:<full sha>`, and commit that tag into `deploy/web/deployment.yaml`. Skip pushes from `github-actions[bot]`. Do not run kubectl. The package has to be public. Do not change the message in this commit. I will push and watch Actions.

The first run is red. The build log shows the image digest, then the public-package step returns HTTP 404. Explain that failure. Do not replace the workflow until I agree with the cause.

The retry is green and the tag is committed, but the new pod is `ImagePullBackOff`. The old pods are still Ready. Read the pod event and the image manifest, and tell me the platform mismatch. I will decide the fix.

Build `linux/arm64` and turn provenance off. I checked: the nodes are arm64 and the published manifest was amd64 plus an attestation.

The corrected image is running. I will change `MESSAGE` and run a curl loop during the rollout. Give me the loop. I will push and watch it.

The loop printed `000fail` on every line. The browser still shows the page. `/etc/hosts` has `web.local`, and curl to `127.0.0.1` with `Host: web.local` returns 200. Explain the failure. Do not call it an app error.

## Bonus

Parts 0 to 3 are done and the cluster is up. Add the bonus, and tell me what I still have to apply or click.

I want an HPA for `web`, minimum 2 and maximum 5, synced by the existing Application. metrics-server has to come from Argo CD, because `kubectl top` says the metrics API is missing. Prometheus and Grafana also come from Argo CD. Pin the chart versions. Leave Alertmanager out. Grafana should use the ingress we already have.

In the README, write what would change on EKS. Do not build an EKS cluster.

The push was rejected because Actions had committed an image tag. Rebase my commit onto that tag and push. Do not force-push.

## This write-up

Read the README and `ai-prompts.md`. Rewrite the README as a report for the reviewer: what is finished, what is missing, one decision and why, and one place the AI was wrong and how I noticed. Rewrite the prompt log so it shows how I planned, what I checked myself, and where I sent a failure back. Keep both files accurate to the repo.
