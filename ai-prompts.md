# AI prompts

Prompts that produced the changes in this repo, kept with the commits they belong to.

## Plan and this README

Read the candidate instructions PDF and write a 90-minute plan the candidate can execute. Do not implement yet.

Answers that locked the plan:

1. The candidate and the agents work together to implement the solution.
2. GitHub is already logged in.
3. The cluster is local.
4. Python.
5. Docker is downloaded; check whether the other tools are installed.
6. Use the existing repository.
7. The repository is public.

Form a plan for Part 0. The repo exists and the tools are installed.

Add git handling to the plan. The repo is already cloned on the desktop. Consider whether a new branch is needed.

Build the README and wait for approval.

Implement Part 0 as specified: README plan, `ai-prompts.md`, Python service, non-root Dockerfile, local checks. Commit the README and prompt log before the app exists. Two commits on `main`. No pull request.

## Part 1

Form a plan for Part 1 with the implementation and the tests that show the part is done.

Add a copy-paste git command section, and an explanation of what the code change does.

Implement Part 1 as specified. Terraform creates a kind cluster named `exercise` with 1 control-plane and 2 workers, installs ingress-nginx and Argo CD, and can destroy the cluster. Do not commit. The desktop runs apply and the checks.

`brew install terraform` fails because Homebrew core no longer has that formula. Install Terraform from the HashiCorp tap, plus kind and Helm. Run init, validate, and apply from `terraform/`.

Commit only the two `h1` lines `terraform init` added to `terraform/.terraform.lock.hcl`. The candidate commits and pushes that by hand.

## Part 2

Plan Part 2, then implement it after the lockfile commit is on `main`.

Manifests for the app live in `deploy/web`. The Argo CD Application lives in `deploy/application.yaml` and is applied once into the `argocd` namespace. It syncs `deploy/web` from `main`. The first image is `web:local`, loaded into kind. The Ingress host is `web.local`. Update the README status and this file in the same change. The candidate commits and pushes before Argo CD is asked to sync.

Record the Part 2 browser check in the README. The candidate commits and pushes that.

## Part 3

The Part 2 README commit is pushed. Implement Part 3.

A workflow on push to `main` builds the image, pushes `ghcr.io/aradperl/devops-engineer-technical-exercise:<full-sha>`, and commits that tag into `deploy/web/deployment.yaml`. Skip pushes from `github-actions[bot]`. Do not run kubectl. The package has to be public so the kind nodes can pull it. Leave the message change and the curl loop for the push after this workflow is on `main`. Update the README and this file in the same change. The candidate commits and pushes.

The first run pushed the image and then failed. `GITHUB_TOKEN` got HTTP 404 from `/user/packages`, so the tag was not committed. Call `/users/Aradperl/packages/container/devops-engineer-technical-exercise` instead, and retry until the package record exists.

The retry run went green and committed the tag. The kind nodes are arm64 and the published image was linux/amd64 plus an attestation manifest, so the new pod stayed in ImagePullBackOff. Build `linux/arm64` with provenance and sbom turned off. The old pods keep serving because `maxUnavailable` is 0.

The arm64 tag rolled out. Both pods are Ready on that image and the page still shows the old message. Change `MESSAGE` to `hello from the rollout`, push, and curl `http://web.local` through the rollout. A pass is a 200 on every request.

That curl loop printed `000fail`. macOS treats `.local` as a network name, so curl never reached the ingress. The rollout had already finished. Run the loop with `--resolve web.local:80:127.0.0.1` and change `MESSAGE` to `hello during the rollout` while it is printing `200`.

The browser showed that message on pod `web-57bcf54d88-s9w72`. Record the finished parts, the missing bonus, the arm64 image decision, and the `.local` curl failure in the README.
