# Test file to verify CODEOWNERS functionality

This file is used to test that MOTEB1989 gets automatically requested as a reviewer when changes are made to the repository.

## Expected behavior
When a PR is opened that includes this file, MOTEB1989 should be automatically requested as a reviewer due to:
1. The CODEOWNERS file pattern `* @MOTEB1989` 
2. The specific pattern `*.md @MOTEB1989`
3. The GitHub workflow auto-assign-reviewer.yml as a backup

## Testing
This file can be modified in future test PRs to verify the automation is working correctly.