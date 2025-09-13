# CodeQL Security Analysis

This repository includes comprehensive CodeQL security analysis configured specifically for Python-based OSINT applications.

## Quick Start

To validate the CodeQL setup:

```bash
./scripts/validate_codeql.sh
```

## Configuration

- **Workflow**: `.github/workflows/codeql.yml` - Main GitHub Actions workflow
- **Config**: `.github/codeql/codeql-config.yml` - Custom analysis configuration
- **Docs**: `docs/CODEQL_SETUP.md` - Detailed setup and troubleshooting guide

## Features

✅ **Python-focused Analysis** - Configured specifically for Python/FastAPI code
✅ **Security Queries** - Includes security-extended and security-and-quality query suites
✅ **Language Filtering** - Prevents JavaScript/TypeScript query failures on Python code
✅ **Path Optimization** - Excludes docs, build artifacts, and cache files
✅ **Automated Triggers** - Runs on push, PR, and weekly schedule
✅ **Manual Triggers** - Can be run on-demand via GitHub Actions

## Monitoring

CodeQL results are available in the **Security** tab under **Code scanning alerts**. The workflow automatically uploads findings to GitHub's security dashboard.

## Common Issues Fixed

- ❌ JavaScript XSS queries failing on Python code → ✅ Language-specific filtering
- ❌ Query constraint failures → ✅ Proper dependency setup and build configuration
- ❌ Path inclusion issues → ✅ Comprehensive path filters
- ❌ Missing code scanning → ✅ Proper permissions and upload configuration

For detailed troubleshooting, see [docs/CODEQL_SETUP.md](docs/CODEQL_SETUP.md).