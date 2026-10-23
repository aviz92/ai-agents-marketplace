# Update an installed command in its origin repo

Send changes you made to an installed command back to the repo it was authored in, as a
GitHub pull request or GitLab merge request.

Never write to the origin repo before the user approves the diff (step 5).
Never read, print or log `.env` or any token value.

## Where things live

- Installed file: `<agent dir>/commands/<id>.md`
- Origin repo directory: `commands/<id>/`, holding `command.md` and `metadata.yaml`.

## Checklist

### 1. Identify the command
- [ ] Take the id from the installed path (the directory name or file stem).
- [ ] If the user did not name one, ask which installed command to publish.

### 2. Resolve the target repo
- [ ] Read `origin` and `version` from the installed file's frontmatter.
- [ ] No `origin` -> stop and tell the user the command has no recorded origin. Do not guess a repo.
- [ ] `origin` is not a full `https://` URL (e.g. `org/repo`) -> stop and ask the user for the full URL.
- [ ] Parse the URL into `host` and `repo_path` (`org/repo`, or `group/sub/repo` on GitLab).
- [ ] Provider: `github.com` -> GitHub. Any other host -> GitLab with `gitlab_url=https://<host>`.
- [ ] Choose the auth method. Never print a token value.
      - `GITHUB_ACCESS_TOKEN` (GitHub) or `GITLAB_ACCESS_TOKEN` (GitLab) is set -> **library mode**.
        See [.env.example](assets/.env.example).
      - Token not set -> **CLI mode**: GitHub needs `gh auth status` to succeed;
        GitLab needs `glab auth status --hostname <host>` to succeed.
      - Neither works -> stop and tell the user to set the token in `.env` or run `gh auth login` / `glab auth login`.

### 3. Fetch upstream
- [ ] Read `commands/<id>/command.md` and `commands/<id>/metadata.yaml` from the origin repo's default branch.
- [ ] Upstream directory missing -> stop and report it. Do not create a new command upstream.

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
Branch: `update/command-<id>-<new-version>`. Commit message and PR/MR title: `feat(<id>): <short summary>`.
Description: what changed and why.

- [ ] Branch already exists -> reuse it; open a PR/MR only if none is open for it.
- [ ] Never commit to the default branch.

**Library mode.** Run a temporary script with the libraries fetched on demand (no project dependency added),
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
for path, content in files.items():  # {"commands/<id>/command.md": ..., "commands/<id>/metadata.yaml": ...}
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

**CLI mode.** Same flow with `gh` / `glab`, which use their own stored login. Write file contents to
temporary files first; delete them afterwards.

GitHub:

```bash
default=$(gh repo view "$repo_path" --json defaultBranchRef -q .defaultBranchRef.name)
base_sha=$(gh api "repos/$repo_path/git/ref/heads/$default" -q .object.sha)
gh api "repos/$repo_path/git/refs" -f ref="refs/heads/$branch" -f sha="$base_sha"
# per file: <path> is the origin path, <local_file> holds the new content
sha=$(gh api "repos/$repo_path/contents/<path>?ref=$branch" -q .sha)
gh api -X PUT "repos/$repo_path/contents/<path>" -f message="$commit_message" \
  -f content="$(base64 < <local_file> | tr -d '\n')" -f sha="$sha" -f branch="$branch"
gh pr create --repo "$repo_path" --base "$default" --head "$branch" --title "$title" --body "$description"
```

GitLab (one commit creates the branch and updates every file):

```bash
enc=$(printf '%s' "$repo_path" | sed 's#/#%2F#g')
default=$(glab api --hostname "$host" "projects/$enc" | jq -r .default_branch)
# commit.json: {"branch": "<branch>", "start_branch": "<default>", "commit_message": "...",
#               "actions": [{"action": "update", "file_path": "<path>", "content": "<new content>"}]}
glab api --hostname "$host" -X POST "projects/$enc/repository/commits" --input commit.json
glab mr create --repo "$host/$repo_path" --source-branch "$branch" --target-branch "$default" \
  --title "$title" --description "$description" --yes
```

Use `"action": "create"` for files that do not exist upstream yet.

Delete temporary scripts and files when done.

### 7. Report
- [ ] Give the user the PR/MR URL, the new version and the target repo.
- [ ] Remind them the installed copy keeps its old `version` until they re-install after merge.

## Failure handling
- Authentication error -> tell the user to set the token env var or log in with `gh` / `glab`; do not try other credentials.
- Permission denied on push -> stop and report it. Do not redirect the change to another repo.
- Never force-push or delete branches you did not create.
