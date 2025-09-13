# CodeQL Security Analysis Setup

This document explains the CodeQL security analysis setup for the Top-TieR-Global-HUB-AI repository.

## Overview

CodeQL is a semantic code analysis engine that helps find security vulnerabilities and coding errors in your Python code. This repository has been configured with a comprehensive CodeQL workflow specifically tailored for Python-based OSINT applications.

## Configuration Files

### 1. Workflow File: `.github/workflows/codeql.yml`

This file defines the GitHub Actions workflow that runs CodeQL analysis. Key features:

- **Language**: Python (specifically configured for this repository)
- **Triggers**: 
  - Push to main/master branches
  - Pull requests to main/master branches
  - Weekly scheduled runs (Mondays at 6 AM UTC)
  - Manual workflow dispatch
- **Permissions**: Configured for security events and code scanning

### 2. Configuration File: `.github/codeql/codeql-config.yml`

This file customizes the CodeQL analysis:

- **Query Suites**: security-extended and security-and-quality
- **Language Filters**: Excludes JavaScript/TypeScript queries that were causing failures
- **Path Filters**: Excludes documentation, build artifacts, and cache files
- **Custom Filters**: Reduces noise from unused imports and similar issues

## Fixing Common CodeQL Issues

### Issue 1: JavaScript Query Failures (e.g., XssThroughDom.ql)

**Problem**: JavaScript-specific queries failing on Python code
**Solution**: Added language-specific filters in `codeql-config.yml`:

```yaml
query-filters:
  - exclude:
      tags: javascript
  - exclude:
      tags: typescript
```

### Issue 2: Query Constraints Failing

**Problem**: Queries failing due to missing dependencies or build issues
**Solution**: Enhanced workflow with:

- Explicit Python setup
- Dependency installation from requirements.txt
- Common package pre-installation (requests, fastapi, uvicorn, pydantic)
- `setup-python-dependencies: true` flag

### Issue 3: Path Inclusion Issues

**Problem**: CodeQL analyzing irrelevant files causing failures
**Solution**: Comprehensive path exclusions:

```yaml
paths-ignore:
  - "**/*.md"
  - "**/*.yml"
  - "**/docs/**"
  - "**/__pycache__/**"
  - "**/build/**"
```

## Enabling Code Scanning

To enable code scanning alerts in the repository:

1. Go to **Repository Settings** → **Security & Analysis**
2. Enable **Code Scanning Alerts**
3. The workflow will automatically start uploading results

## Manual Workflow Trigger

To manually run CodeQL analysis:

1. Go to **Actions** tab in GitHub
2. Select **CodeQL Security Analysis** workflow
3. Click **Run workflow**
4. Choose the branch and click **Run workflow**

## Monitoring Results

CodeQL results are available in:

- **Security** tab → **Code scanning alerts**
- **Actions** tab → Individual workflow runs
- **Pull Request** checks (for PR-triggered runs)

## Security Query Categories

The configuration includes:

- **Security Extended**: Comprehensive security vulnerability detection
- **Security and Quality**: Additional code quality and security checks
- **Python-specific**: Tailored for Python/FastAPI applications
- **OSINT-focused**: Customized for OSINT platform security concerns

## Troubleshooting

### Workflow Fails with "No Code Found"

1. Check that Python files exist in the repository
2. Verify `paths` configuration in `codeql-config.yml`
3. Ensure Python files are not excluded by `paths-ignore`

### JavaScript/TypeScript Query Errors

1. Verify language filters are in place
2. Check that only Python language is specified in the workflow matrix
3. Review query-filters configuration

### Dependency Installation Failures

1. Check `requirements.txt` exists and is valid
2. Verify Python version compatibility
3. Review dependency installation step in workflow

### High Memory Usage

1. Reduce the scope of analysis with more specific path filters
2. Consider excluding test files if not needed for security analysis
3. Adjust timeout settings if needed

## Best Practices

1. **Regular Updates**: Keep CodeQL actions updated to latest versions
2. **Review Alerts**: Regularly check and address security findings
3. **Custom Queries**: Add domain-specific security queries for OSINT applications
4. **False Positives**: Use query filters to exclude irrelevant findings
5. **Documentation**: Keep this documentation updated with configuration changes

## Support

For issues with CodeQL configuration:

1. Check GitHub Actions logs for detailed error messages
2. Review CodeQL documentation: https://codeql.github.com/docs/
3. Open an issue in the repository with the `security` label
4. Contact repository maintainers for assistance

## Version History

- v1.0 - Initial CodeQL setup with Python support
- v1.1 - Enhanced configuration with language filters and error handling
- v1.2 - Added comprehensive documentation and troubleshooting guide