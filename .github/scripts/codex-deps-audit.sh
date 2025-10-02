#!/bin/bash
set -euo pipefail

echo "🔧 CodeX Dependencies & Security Audit Started"
REPORT="### 📦 CodeX Dependencies & Security Audit Report\n"

# Python
if [ -f requirements.txt ]; then
  REPORT+="\n🐍 Python (requirements.txt):\n"
  while read -r line; do
    if [ -n "$line" ]; then
      REPORT+="- $line\n"
    fi
  done < requirements.txt

  # Security audit (pip-audit)
  if command -v pip-audit &> /dev/null; then
    AUDIT=$(pip-audit -r requirements.txt --format json || true)
    if [ -n "$AUDIT" ]; then
      REPORT+="\n🔐 Python Security Issues:\n\`\`\`json\n$AUDIT\n\`\`\`\n"
    else
      REPORT+="\n✅ No Python security issues found.\n"
    fi
  fi
fi

# NodeJS
if [ -f package.json ]; then
  REPORT+="\n🟢 NodeJS (package.json):\n"
  if command -v jq &> /dev/null; then
    NODE_DEPS=$(jq -r '.dependencies | to_entries[] | "- \(.key)@\(.value)"' package.json 2>/dev/null || true)
    DEV_DEPS=$(jq -r '.devDependencies | to_entries[] | "- \(.key)@\(.value)"' package.json 2>/dev/null || true)
    if [ -n "$NODE_DEPS" ]; then
      REPORT+="$NODE_DEPS\n"
    fi
    if [ -n "$DEV_DEPS" ]; then
      REPORT+="$DEV_DEPS\n"
    fi
  fi

  # Security audit (npm audit)
  if command -v npm &> /dev/null; then
    npm install --package-lock-only >/dev/null 2>&1 || true
    AUDIT=$(npm audit --json || true)
    if [ -n "$AUDIT" ]; then
      REPORT+="\n🔐 NodeJS Security Issues:\n\`\`\`json\n$AUDIT\n\`\`\`\n"
    else
      REPORT+="\n✅ No NodeJS security issues found.\n"
    fi
  fi
fi

# Java (Maven)
if [ -f pom.xml ]; then
  REPORT+="\n☕ Java (Maven - pom.xml):\n"
  JAVA_DEPS=$(grep -oPm1 "(?<=<artifactId>)[^<]+" pom.xml | sed 's/^/- /' | head -n 20 || true)
  if [ -n "$JAVA_DEPS" ]; then
    REPORT+="$JAVA_DEPS\n"
  fi
fi

# Go
if [ -f go.mod ]; then
  REPORT+="\n🐹 Go (go.mod):\n"
  GO_DEPS=$(grep "require" go.mod | sed 's/^/- /' || true)
  if [ -n "$GO_DEPS" ]; then
    REPORT+="$GO_DEPS\n"
  fi
  # Security: govulncheck
  if command -v govulncheck &> /dev/null; then
    AUDIT=$(govulncheck ./... || true)
    if [ -n "$AUDIT" ]; then
      REPORT+="\n🔐 Go Security Issues:\n\`\`\`\n$AUDIT\n\`\`\`\n"
    fi
  fi
fi

# Rust
if [ -f Cargo.toml ]; then
  REPORT+="\n🦀 Rust (Cargo.toml):\n"
  RUST_DEPS=$(grep "^\s*[^#]" Cargo.toml | head -n 20 | sed 's/^/- /' || true)
  if [ -n "$RUST_DEPS" ]; then
    REPORT+="$RUST_DEPS\n"
  fi
  if command -v cargo-audit &> /dev/null; then
    AUDIT=$(cargo audit || true)
    if [ -n "$AUDIT" ]; then
      REPORT+="\n🔐 Rust Security Issues:\n\`\`\`\n$AUDIT\n\`\`\`\n"
    fi
  fi
fi

# Ruby
if [ -f Gemfile ]; then
  REPORT+="\n💎 Ruby (Gemfile):\n"
  RUBY_DEPS=$(grep "gem" Gemfile | sed 's/^/- /' || true)
  if [ -n "$RUBY_DEPS" ]; then
    REPORT+="$RUBY_DEPS\n"
  fi
fi

# Output
echo -e "$REPORT"

# PR Comment if inside GitHub Actions
if [ -n "${GITHUB_TOKEN-}" ] && [ -f "$GITHUB_EVENT_PATH" ]; then
  PR=$(jq -r .pull_request.number "$GITHUB_EVENT_PATH")
  if [ "$PR" != "null" ]; then
    echo "📩 Posting dependencies + audit report to PR #$PR ..."
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
         -X POST \
         -d "{\"body\": \"$REPORT\"}" \
         "https://api.github.com/repos/$GITHUB_REPOSITORY/issues/$PR/comments"
  fi
fi
