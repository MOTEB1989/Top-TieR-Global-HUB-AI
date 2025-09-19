#!/bin/bash

# Script to help update the PR title and description
# This script provides instructions and automation for updating the current PR

echo "===================================================================================="
echo "                    PR TITLE AND DESCRIPTION UPDATE INSTRUCTIONS                    "
echo "===================================================================================="
echo ""
echo "This script helps you update the current PR with the new title and description."
echo ""

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Check if PR_TITLE.txt and PR_DESCRIPTION.md exist
if [[ -f "PR_TITLE.txt" && -f "PR_DESCRIPTION.md" ]]; then
    echo "✅ PR update files found:"
    echo "   - PR_TITLE.txt ($(wc -c < PR_TITLE.txt) characters)"
    echo "   - PR_DESCRIPTION.md ($(wc -c < PR_DESCRIPTION.md) characters)"
    echo ""
else
    echo "❌ Error: PR update files not found!"
    echo "   Expected: PR_TITLE.txt and PR_DESCRIPTION.md"
    exit 1
fi

echo "------- NEW PR TITLE -------"
cat PR_TITLE.txt
echo ""
echo ""

echo "------- NEW PR DESCRIPTION (first 20 lines) -------"
head -20 PR_DESCRIPTION.md
echo ""
echo "[... see PR_DESCRIPTION.md for full content ...]"
echo ""

echo "===================================================================================="
echo "                              HOW TO UPDATE THE PR                                  "
echo "===================================================================================="
echo ""
echo "Method 1: GitHub Web Interface (Recommended)"
echo "---------------------------------------------"
echo "1. Go to your PR on GitHub"
echo "2. Click the 'Edit' button next to the PR title"
echo "3. Replace the title with content from PR_TITLE.txt:"
echo "   $(cat PR_TITLE.txt)"
echo ""
echo "4. Replace the description with content from PR_DESCRIPTION.md"
echo "5. Click 'Update comment' to save changes"
echo ""

echo "Method 2: GitHub CLI (if available)"
echo "-----------------------------------"
if command -v gh >/dev/null 2>&1; then
    echo "GitHub CLI is available. You can use:"
    echo ""
    echo "# Update PR title"
    echo "gh pr edit --title \"$(cat PR_TITLE.txt)\""
    echo ""
    echo "# Update PR description"
    echo "gh pr edit --body-file PR_DESCRIPTION.md"
    echo ""
    echo "# Or update both at once"
    echo "gh pr edit --title \"$(cat PR_TITLE.txt)\" --body-file PR_DESCRIPTION.md"
    echo ""
else
    echo "GitHub CLI not available. Use Method 1 (Web Interface)."
    echo ""
fi

echo "Method 3: Copy and Paste"
echo "------------------------"
echo "1. Copy title from: cat PR_TITLE.txt"
echo "2. Copy description from: cat PR_DESCRIPTION.md"
echo "3. Paste into GitHub PR interface"
echo ""

echo "===================================================================================="
echo "                                VALIDATION                                          "
echo "===================================================================================="
echo ""
echo "After updating the PR, verify:"
echo "✓ Title accurately reflects the scope of changes"
echo "✓ Description includes all key features and improvements"
echo "✓ Migration notes are clear for users"
echo "✓ Testing instructions are provided"
echo "✓ Reviewer is automatically assigned (@MOTEB1989)"
echo ""

echo "Files available for reference:"
echo "- PR_TITLE.txt: Ready-to-use PR title"
echo "- PR_DESCRIPTION.md: Complete PR description"
echo "- PR_UPDATE_CONTENT.md: Full documentation with additional context"
echo ""

echo "===================================================================================="