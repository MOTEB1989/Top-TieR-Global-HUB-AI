# Top-TieR-Global-HUB-AI
Veritas Nexus v2 — منصة OSINT مفتوحة المصدر للتجارب التعليمية: تجمع البيانات من مصادر متعددة، تخزنها في Neo4j، توفر REST API (FastAPI)، وكيل ذكي (LangChain Agent)، وواجهة بصرية (Cytoscape.js).

## Auto-Merge Policy

This repository supports automated merging of pull requests to streamline the development workflow while maintaining code quality and security standards.

### 🔄 How Auto-Merge Works

Pull requests can be automatically merged when they meet all the required conditions. The auto-merge system checks for proper authorization, code quality, and repository health before proceeding.

### 🏷️ Required Labels

To enable auto-merge, add one of these labels to your PR:
- `auto-merge` - Standard auto-merge
- `ready-to-merge` - Alternative trigger label  
- `automerge` - Shorthand version

### 🔐 Authorization Requirements

Auto-merge is restricted to:
- **Repository Owner**: `MOTEB1989`
- **Repository Collaborators**: Users with write access
- **Trusted Contributors**: As defined in the workflow configuration

### 📋 Conditions for Auto-Merge

All of the following conditions must be met:

#### ✅ Required Conditions:
1. **CI Checks**: All continuous integration checks must pass
2. **No Conflicts**: PR must be mergeable without conflicts
3. **No Change Requests**: No pending change requests from reviewers
4. **Draft Status**: PR must not be in draft mode
5. **Proper Labels**: Must have an auto-merge trigger label
6. **Authorized Author**: Author must be in the authorized list

#### 🔀 Merge Methods

You can specify the merge method using additional labels:
- `squash-merge` or `squash` - Squash and merge (combines all commits)
- `rebase-merge` or `rebase` - Rebase and merge (clean linear history)  
- **Default**: Standard merge commit (preserves commit history)

### 🤖 Auto-Merge Process

1. **Trigger**: Auto-merge activates on PR events (open, label, review, etc.)
2. **Validation**: System checks all required conditions
3. **Execution**: If conditions are met, auto-merge is enabled
4. **Notification**: A comment is added to the PR with status details
5. **Merge**: GitHub automatically merges when ready

### ⚠️ Important Notes

- Auto-merge only activates for **non-draft** pull requests
- The system prioritizes safety - any failing condition blocks the merge
- Manual intervention may be required if auto-merge fails
- Repository maintainers can override auto-merge settings if needed

### 🔧 Troubleshooting Auto-Merge

If your PR doesn't auto-merge, check:
- [ ] PR has the correct label (`auto-merge`, `ready-to-merge`, or `automerge`)
- [ ] You are authorized (owner or collaborator)
- [ ] All CI checks are passing (green checkmarks)
- [ ] No merge conflicts exist
- [ ] No reviewers have requested changes
- [ ] PR is not in draft mode

For assistance, contact the repository maintainers or check the workflow logs in the Actions tab.
