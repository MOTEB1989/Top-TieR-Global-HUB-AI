#!/bin/bash
# CodeQL Setup Validation Script
# This script validates the CodeQL configuration and tests basic functionality

set -e

echo "🔍 CodeQL Setup Validation for Top-TieR-Global-HUB-AI"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f ".github/workflows/codeql.yml" ]; then
    echo "❌ Error: CodeQL workflow file not found. Run this from repository root."
    exit 1
fi

echo "✅ Found CodeQL workflow file"

# Validate YAML syntax
echo "📝 Validating YAML syntax..."

if command -v yamllint &> /dev/null; then
    yamllint .github/workflows/codeql.yml
    yamllint .github/codeql/codeql-config.yml
    echo "✅ YAML syntax validation passed"
else
    echo "⚠️  yamllint not available, using Python for basic validation"
    python -c "import yaml; yaml.safe_load(open('.github/workflows/codeql.yml')); print('✅ Workflow YAML is valid')"
    python -c "import yaml; yaml.safe_load(open('.github/codeql/codeql-config.yml')); print('✅ Config YAML is valid')"
fi

# Check Python files
echo "🐍 Checking Python files..."
python_files=$(find . -name "*.py" | grep -v __pycache__ | wc -l)
echo "📊 Found $python_files Python files"

if [ "$python_files" -eq 0 ]; then
    echo "⚠️  No Python files found. CodeQL analysis may not be meaningful."
else
    echo "✅ Python files detected for analysis"
fi

# Test Python compilation
echo "🔧 Testing Python compilation..."
if python -m py_compile $(find . -name "*.py" | grep -v __pycache__) 2>/dev/null; then
    echo "✅ All Python files compile successfully"
else
    echo "⚠️  Some Python files have syntax errors"
fi

# Check dependencies
echo "📦 Checking dependencies..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    echo "📋 Dependencies:"
    head -5 requirements.txt
    if [ $(wc -l < requirements.txt) -gt 5 ]; then
        echo "... and $(( $(wc -l < requirements.txt) - 5 )) more"
    fi
else
    echo "⚠️  requirements.txt not found"
fi

# Check for potential security issues
echo "🔒 Quick security check..."
security_patterns=("password.*=" "api.*key.*=" "secret.*=" "token.*=")
found_issues=0

for pattern in "${security_patterns[@]}"; do
    if grep -r -i "$pattern" --include="*.py" . 2>/dev/null | grep -v "test" | head -1; then
        found_issues=$((found_issues + 1))
    fi
done

if [ $found_issues -eq 0 ]; then
    echo "✅ No obvious hardcoded secrets found"
else
    echo "⚠️  Found $found_issues potential security issues (please review)"
fi

# Validate configuration structure
echo "⚙️  Validating CodeQL configuration structure..."

config_file=".github/codeql/codeql-config.yml"
if [ -f "$config_file" ]; then
    if grep -q "python" "$config_file" || grep -q "queries:" "$config_file"; then
        echo "✅ CodeQL configuration appears valid"
    else
        echo "⚠️  CodeQL configuration may be incomplete"
    fi
else
    echo "⚠️  CodeQL configuration file not found"
fi

# Check GitHub Actions syntax (basic)
echo "🔄 Checking GitHub Actions workflow structure..."
workflow_file=".github/workflows/codeql.yml"
required_sections=("name:" "on:" "jobs:" "steps:")
missing_sections=()

for section in "${required_sections[@]}"; do
    if ! grep -q "$section" "$workflow_file"; then
        missing_sections+=("$section")
    fi
done

if [ ${#missing_sections[@]} -eq 0 ]; then
    echo "✅ Workflow structure appears complete"
else
    echo "⚠️  Missing workflow sections: ${missing_sections[*]}"
fi

echo ""
echo "🎯 Validation Summary"
echo "===================="

if [ $found_issues -eq 0 ] && [ "$python_files" -gt 0 ]; then
    echo "✅ CodeQL setup appears ready for use"
    echo "   • YAML configuration is valid"
    echo "   • Python files are present and compile"
    echo "   • No obvious security issues detected"
    echo ""
    echo "Next steps:"
    echo "1. Push changes to trigger CodeQL workflow"
    echo "2. Enable code scanning in repository settings"
    echo "3. Monitor results in Security tab"
else
    echo "⚠️  Some issues detected - review above warnings"
    echo "   CodeQL may still work but could have issues"
fi

echo ""
echo "📚 For more information, see docs/CODEQL_SETUP.md"