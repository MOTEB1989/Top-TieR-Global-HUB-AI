# Scripts Overview - Top-TieR-Global-HUB-AI

Comprehensive documentation for all Python and shell scripts in the repository.

## Table of Contents

- [Python Scripts](#python-scripts)
- [Shell Scripts](#shell-scripts)
- [Utility Modules](#utility-modules)
- [Environment Variables](#environment-variables)
- [Common Patterns](#common-patterns)

---

## Python Scripts

### telegram_chatgpt_mode.py

**Purpose**: Advanced Telegram bot acting as ChatGPT interface for the repository.

**Dependencies**:
- python-telegram-bot >= 21.0.0
- openai
- requests
- python-dotenv

**Usage**:
````bash
# Normal mode
python scripts/telegram_chatgpt_mode.py

# Refactored mode (enhanced logging)
python scripts/telegram_chatgpt_mode.py --mode=refactored

# Dry-run mode (initialize without polling)
python scripts/telegram_chatgpt_mode.py --dry-run
````

**Features**:
- `/chat` - Interactive chat with memory per user
- `/repo` - Repository analysis using ARCHITECTURE/SECURITY reports
- `/insights` - Smart summary of project status
- `/file` - File analysis
- `/status` - Bot and repository status
- `/help` - Help message
- `/whoami` - Get Telegram ID for allowlist

**Environment Variables**:
- `TELEGRAM_BOT_TOKEN` (required)
- `TELEGRAM_ALLOWLIST` (optional)
- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (optional, default: gpt-4o-mini)
- `GITHUB_REPO` (optional, for display)

---

### verify_env.py

**Purpose**: Validate environment variables before starting services.

**Dependencies**: None (standard library)

**Usage**:
````bash
# Normal mode
python scripts/verify_env.py

# Strict mode (treats optional vars as required)
python scripts/verify_env.py --strict
````

**Features**:
- Validates required environment variables
- Masks sensitive values in output
- Supports strict mode for optional variables
- Returns exit code 1 on failure

**Validated Variables**:
- Required: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `GITHUB_REPO`
- Optional: `OPENAI_MODEL`, `TELEGRAM_ALLOWLIST`, `OPENAI_BASE_URL`
- Strict Mode: `OPENAI_MODEL` (becomes required)

---

### run_telegram_bot.py

**Purpose**: Full-featured Telegram bot with AI and GitHub support (@LexnexuxBot).

**Dependencies**:
- python-telegram-bot >= 21.0.0
- openai (optional, for AI features)
- requests

**Usage**:
````bash
python scripts/run_telegram_bot.py
````

**Features**:
- `/start` - Welcome message
- `/status` - System status
- `/preflight` - Run comprehensive system check
- `/keys` - Check API keys
- `/secrets` - Check GitHub secrets
- `/ai <question>` - AI chat
- `/help` - Help documentation

**Environment Variables**:
- `TELEGRAM_BOT_TOKEN` (required)
- `TELEGRAM_ALLOWLIST` (optional)
- `OPENAI_API_KEY` (optional, for AI features)
- `GITHUB_TOKEN` (optional, for GitHub features)

---

### test_telegram_bot.py

**Purpose**: Test script for Telegram bot functionality.

**Dependencies**:
- python-telegram-bot >= 21.0.0
- requests

**Usage**:
````bash
python scripts/test_telegram_bot.py
````

**Features**:
- Tests bot token validity
- Tests connection to Telegram API
- Fetches recent updates
- Optionally sends test message if `TELEGRAM_CHAT_ID` is set

---

### check_all_keys.py

**Purpose**: Comprehensive API keys and configuration validator.

**Dependencies**: None (standard library)

**Usage**:
````bash
python scripts/check_all_keys.py
````

**Features**:
- Validates all API keys and secrets
- Categorizes keys (AI/LLM, Telegram, GitHub, Databases, Scripts)
- Identifies placeholder values
- Provides completion percentage
- Suggests fixes for missing/invalid keys

**Checked Variables**:
- AI/LLM: `OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWLIST`, `TELEGRAM_CHAT_ID`
- GitHub: `GITHUB_TOKEN`, `GITHUB_REPO`
- Databases: `DB_URL`, `REDIS_URL`, `NEO4J_URI`, `NEO4J_AUTH`
- Scripts: `ULTRA_PREFLIGHT_PATH`, `FULL_SCAN_SCRIPT`, `LOG_FILE_PATH`

---

### check_github_secrets.py

**Purpose**: Validate GitHub repository secrets.

**Dependencies**:
- requests

**Usage**:
````bash
python scripts/check_github_secrets.py
````

**Features**:
- Validates GitHub token
- Lists repository secrets
- Checks for required secrets
- Analyzes workflow secret usage
- Compares local vs GitHub secrets

**Required Environment**:
- `GITHUB_TOKEN` (required)
- `GITHUB_REPO` (default: MOTEB1989/Top-TieR-Global-HUB-AI)

---

### close_github_items.py

**Purpose**: Utility to close open issues and pull requests in bulk.

**Dependencies**:
- requests

**Usage**:
````bash
# Interactive mode
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI

# Non-interactive with filters
python scripts/close_github_items.py MOTEB1989/Top-TieR-Global-HUB-AI --yes \
  --exclude 123 456 \
  --label-exclude keep important \
  --before 2024-01-01 \
  --dry-run
````

**Features**:
- Close issues and/or pull requests
- Filter by labels, dates, or specific numbers
- Dry-run mode
- Rate limit handling
- Retry logic for transient errors

---

### convert_thread_messages.py

**Purpose**: Convert OpenAI thread messages to conversation format.

**Dependencies**:
- openai

**Usage**:
````bash
python scripts/convert_thread_messages.py
````

**Features**:
- Converts thread messages to conversation
- Handles text and image content
- Uses OpenAI API

---

## Shell Scripts

### ultra_preflight.sh

**Purpose**: Comprehensive preflight check before running services.

**Dependencies**: bash, docker, docker-compose, python3, git

**Usage**:
````bash
./scripts/ultra_preflight.sh
````

**Checks**:
- System information (OS, IP, memory, disk)
- Repository structure
- Docker and Docker Compose
- Configuration files
- Scripts presence and syntax
- Port availability
- Python environment
- Git status
- Network connectivity
- Running containers

---

### check_connections.sh

**Purpose**: Validate docker-compose services, ports, models, and secrets.

**Usage**:
````bash
API_PORT=3000 ./scripts/check_connections.sh
````

**Features**:
- Docker Compose validation
- Port availability checks
- Model/environment scanning
- Secret validation
- Optional Telegram notification

---

### GIT_READY_COMMANDS.sh

**Purpose**: Quick reference for Git commands to create PRs.

**Usage**:
````bash
# Run automated PR creation
bash scripts/GIT_READY_COMMANDS.sh

# Or follow manual commands in the file
````

---

### check_environment.sh

**Purpose**: Environment validation script.

**Usage**:
````bash
./scripts/check_environment.sh
````

---

### collect_context_for_claude.sh

**Purpose**: Collect repository context for AI analysis.

**Usage**:
````bash
./scripts/collect_context_for_claude.sh
````

---

### comprehensive_setup_and_test.sh

**Purpose**: Complete setup and testing script.

**Usage**:
````bash
./scripts/comprehensive_setup_and_test.sh
````

---

### fix_and_create_all.sh

**Purpose**: Fix common issues and create missing components.

**Usage**:
````bash
./scripts/fix_and_create_all.sh
````

---

### force_fix_railway.sh

**Purpose**: Force fix Railway deployment issues.

**Usage**:
````bash
./scripts/force_fix_railway.sh
````

---

### run_everything.sh

**Purpose**: Start all services using Docker Compose.

**Usage**:
````bash
./scripts/run_everything.sh up
./scripts/run_everything.sh down
````

---

### run_everything_railway.sh

**Purpose**: Railway-specific service startup script.

**Usage**:
````bash
./scripts/run_everything_railway.sh
````

---

### setup_check_connections.sh

**Purpose**: Setup script for check_connections functionality.

**Usage**:
````bash
./scripts/setup_check_connections.sh
````

---

### validate_check_connections.sh

**Purpose**: Validate check_connections setup.

**Usage**:
````bash
./scripts/validate_check_connections.sh
````

---

### post_refactor_check.sh

**Purpose**: Post-refactor diagnostic to validate all changes.

**Usage**:
````bash
./scripts/post_refactor_check.sh
````

**Checks**:
- Presence of all refactored scripts
- Script executability
- Python dependencies
- verify_env.py functionality
- telegram_chatgpt_mode.py flags (--dry-run, --mode)
- Documentation files
- railway.json configuration
- Shell script safety flags

---

## Utility Modules

### scripts/lib/common.py

**Purpose**: Shared utility functions for all scripts.

**Functions**:
- `load_env(env_path)` - Load environment from .env file
- `mask_secret(value, key)` - Mask sensitive values for logging
- `ensure_paths(paths)` - Create directories if they don't exist
- `get_repo_name()` - Get repository name from environment
- `setup_logging(level, format_string)` - Setup unified logging
- `validate_required_env_vars(required_vars)` - Validate environment variables

**Usage Example**:
````python
from scripts.lib.common import setup_logging, mask_secret, validate_required_env_vars

# Setup logging
setup_logging()

# Validate environment
if not validate_required_env_vars(['API_KEY', 'TOKEN']):
    sys.exit(1)

# Mask secret for logging
logger.info("Token: %s", mask_secret(token, "API_TOKEN"))
````

---

## Environment Variables

### Required Variables

| Variable | Description | Used By |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot authentication token | telegram_chatgpt_mode.py, run_telegram_bot.py |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | telegram_chatgpt_mode.py, run_telegram_bot.py |
| `GITHUB_REPO` | Repository name (owner/repo format) | Most scripts |

### Optional Variables

| Variable | Description | Default | Used By |
|----------|-------------|---------|---------|
| `OPENAI_MODEL` | OpenAI model to use | gpt-4o-mini | telegram_chatgpt_mode.py |
| `OPENAI_BASE_URL` | OpenAI API base URL | https://api.openai.com/v1 | telegram_chatgpt_mode.py |
| `TELEGRAM_ALLOWLIST` | Comma-separated user IDs | (empty) | All Telegram bots |
| `TELEGRAM_CHAT_ID` | Default chat ID for notifications | (empty) | test_telegram_bot.py |
| `GITHUB_TOKEN` | GitHub personal access token | (empty) | check_github_secrets.py |
| `ULTRA_PREFLIGHT_PATH` | Path to preflight script | scripts/ultra_preflight.sh | telegram_chatgpt_mode.py |
| `FULL_SCAN_SCRIPT` | Path to full scan script | scripts/execute_full_scan.sh | telegram_chatgpt_mode.py |
| `LOG_FILE_PATH` | Path to log file | analysis/ULTRA_REPORT.md | telegram_chatgpt_mode.py |

### Database Variables (Optional)

| Variable | Description |
|----------|-------------|
| `DB_URL` | Database connection URL |
| `REDIS_URL` | Redis connection URL |
| `NEO4J_URI` | Neo4j database URI |
| `NEO4J_AUTH` | Neo4j authentication credentials |

---

## Common Patterns

### Unified Logging

All refactored Python scripts use unified logging:

````python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Use logger instead of print
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
````

### Safe Main Pattern

All scripts use safe_main() wrapper for error handling:

````python
def safe_main():
    """Main function wrapped in safe error handling"""
    try:
        # Main logic here
        return 0
    except Exception as e:
        logger.error("❌ Fatal error: %s", e, exc_info=True)
        return 1

def main():
    """Entry point for the script"""
    sys.exit(safe_main())

if __name__ == "__main__":
    main()
````

### Environment Verification

Scripts verify environment at startup:

````python
from verify_env import check_variables, REQUIRED_NON_EMPTY

missing, empty = check_variables(REQUIRED_NON_EMPTY)
if missing or empty:
    logger.error("Required environment variables missing or empty")
    sys.exit(1)
````

### Shell Script Safety

All shell scripts include safety flags:

````bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Script continues...
````

---

## Best Practices

1. **Always use logging instead of print** in Python scripts
2. **Mask sensitive values** when logging (use `mask_secret()`)
3. **Validate environment** before proceeding with operations
4. **Use safe_main() pattern** for consistent error handling
5. **Include descriptive headers** in shell scripts
6. **Make shell scripts executable**: `chmod +x script.sh`
7. **Test in dry-run mode** before production runs
8. **Check script syntax** before committing: `bash -n script.sh` or `python -m py_compile script.py`

---

## Troubleshooting

### Common Issues

**Issue**: Script fails with "module not found"
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: Shell script fails with "permission denied"
**Solution**: Make executable: `chmod +x scripts/script.sh`

**Issue**: Environment validation fails
**Solution**: Check `.env` file exists and contains required variables

**Issue**: Telegram bot fails to start
**Solution**: Run `python scripts/test_telegram_bot.py` to diagnose

**Issue**: Railway deployment fails
**Solution**: Verify `railway.json` and run `python scripts/verify_env.py --strict`

---

## See Also

- [BOT_VALIDATION.md](BOT_VALIDATION.md) - End-to-end bot testing guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [README.md](README.md) - Main repository documentation

---

*Last Updated: 2025-11-23*
*Repository: MOTEB1989/Top-TieR-Global-HUB-AI*
