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
