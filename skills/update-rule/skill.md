# Update an installed rule in its origin repo

Send changes you made to an installed rule back to the repo it was authored in, as a
GitHub pull request or GitLab merge request.

Never write to the origin repo before the user approves the diff (step 5).
Never read, print or log `.env` or any token value.

## Where things live

- Installed file: `<agent dir>/rules/<id>.md` (extension varies by agent, e.g. `.mdc`)
- Origin repo directory: `rules/<id>/`, holding `rule.md` and `metadata.yaml`.

## Checklist

### 1. Identify the rule
- [ ] Take the id from the installed path (the directory name or file stem).
- [ ] If the user did not name one, ask which installed rule to publish.

### 2. Resolve the target repo
- [ ] Read `origin` and `version` from the installed file's frontmatter.
- [ ] No `origin` -> stop and tell the user the rule has no recorded origin. Do not guess a repo.
- [ ] `origin` is not a full `https://` URL (e.g. `org/repo`) -> stop and ask the user for the full URL.
- [ ] Parse the URL into `host` and `repo_path` (`org/repo`, or `group/sub/repo` on GitLab).
- [ ] Provider: `github.com` -> GitHub. Any other host -> GitLab with `gitlab_url=https://<host>`.
- [ ] Check that `GITHUB_ACCESS_TOKEN` (GitHub) or `GITLAB_ACCESS_TOKEN` (GitLab) is set. Never print its value.
      See [.env.example](assets/.env.example).

### 3. Fetch upstream
- [ ] Read `rules/<id>/rule.md` and `rules/<id>/metadata.yaml` from the origin repo's default branch.
- [ ] Upstream directory missing -> stop and report it. Do not create a new rule upstream.

### 4. Reverse-render and diff
- [ ] Strip the installed file's frontmatter (the leading `---` ... `---` block and the blank line after it).
      What remains is the new body.
- [ ] Compare it with the upstream body. No difference -> stop: nothing to publish.
- [ ] In upstream `metadata.yaml`, change only `version` (ask the user: patch / minor / major) and
      `description` if the installed one differs. Leave every other field untouched; the installed file
      does not carry them.
- [ ] Installed `version` behind upstream `version` -> warn that upstream moved on and offer to
      re-install first instead of publishing a conflicting change.

### 5. Get approval
- [ ] Show the user: target repo URL, provider, branch name, new version, and the diff of every file.
- [ ] Wait for an explicit yes. No approval -> stop without writing anything.

### 6. Publish
Branch: `update/rule-<id>-<new-version>`. Commit message and PR/MR title: `feat(<id>): <short summary>`.
Description: what changed and why.

- [ ] Branch already exists -> reuse it; open a PR/MR only if none is open for it.
- [ ] Never commit to the default branch.

Run a temporary script with the libraries fetched on demand (no project dependency added),
letting uv load the environment so you never read `.env`:

```bash
uv run --env-file .env --with python-github-plus --with python-gitlab-plus python script.py
```

GitHub:

```python
from python_github_plus import GitHubClient

client = GitHubClient(repo_full_name=repo_path)  # token from GITHUB_ACCESS_TOKEN
repo = client.github.get_repo(repo_path)
default_branch = repo.default_branch
client.branch.create(branch_name=branch, from_branch=default_branch)
for path, content in files.items():  # {"rules/<id>/rule.md": ..., "rules/<id>/metadata.yaml": ...}
    current = repo.get_contents(path, ref=branch)
    repo.update_file(path, commit_message, content, current.sha, branch=branch)
pr = repo.create_pull(base=default_branch, head=branch, title=title, body=description)
print(pr.html_url)
```

GitLab:

```python
from python_gitlab_plus import GitLabClient

client = GitLabClient(gitlab_url=f"https://{host}", project_id=repo_path)  # token from GITLAB_ACCESS_TOKEN
default_branch = client.project.get_info().default_branch
client.branch.create(branch_name=branch, from_branch=default_branch)
for path, content in files.items():
    client.file.update(file_path=path, branch=branch, content=content, commit_message=commit_message)
mr = client.merge_request.create(title=title, from_branch=branch, target=default_branch, description=description)
print(mr.web_url)
```

Delete the temporary script when done.

### 7. Report
- [ ] Give the user the PR/MR URL, the new version and the target repo.
- [ ] Remind them the installed copy keeps its old `version` until they re-install after merge.

## Failure handling
- Authentication error -> tell the user which env var to set; do not try other credentials.
- Permission denied on push -> stop and report it. Do not redirect the change to another repo.
- Never force-push or delete branches you did not create.
