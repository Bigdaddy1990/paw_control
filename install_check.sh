#!/bin/bash
# Installation check script for Paw Control

echo "🐕 Paw Control Installation Check"
echo "================================="

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Function to print colored output
print_status() {
    if [ "$1" = "ERROR" ]; then
        echo -e "${RED}❌ $2${NC}"
        ((ERRORS++))
    elif [ "$1" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️ $2${NC}"
    else
        echo "📋 $2"
    fi
}

# Check Python version
echo "🐍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
        print_status "SUCCESS" "Python $PYTHON_VERSION is supported"
    else
        print_status "ERROR" "Python $PYTHON_VERSION is not supported. Minimum: Python 3.11"
    fi
else
    print_status "ERROR" "Python 3 not found"
fi

# Check required files
echo -e "\n📁 Checking required files..."
REQUIRED_FILES=(
    "custom_components/paw_control/__init__.py"
    "custom_components/paw_control/manifest.json"
    "custom_components/paw_control/const.py"
    "README.md"
    "CHANGELOG.md"
    "pyproject.toml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "SUCCESS" "$file exists"
    else
        print_status "ERROR" "$file is missing"
    fi
done

# Check manifest.json validity
echo -e "\n📋 Checking manifest.json..."
if [ -f "custom_components/paw_control/manifest.json" ]; then
    if python3 -m json.tool custom_components/paw_control/manifest.json > /dev/null 2>&1; then
        print_status "SUCCESS" "manifest.json is valid JSON"
        
        # Check required fields
        DOMAIN=$(python3 -c "import json; print(json.load(open('custom_components/paw_control/manifest.json')).get('domain', ''))" 2>/dev/null)
        VERSION=$(python3 -c "import json; print(json.load(open('custom_components/paw_control/manifest.json')).get('version', ''))" 2>/dev/null)
        
        if [ "$DOMAIN" = "paw_control" ]; then
            print_status "SUCCESS" "Domain is correct: $DOMAIN"
        else
            print_status "ERROR" "Domain is incorrect: $DOMAIN (should be: paw_control)"
        fi
        
        if [ -n "$VERSION" ]; then
            print_status "SUCCESS" "Version is set: $VERSION"
        else
            print_status "ERROR" "Version is missing"
        fi
    else
        print_status "ERROR" "manifest.json is invalid JSON"
    fi
fi

# Check Python syntax
echo -e "\n🐍 Checking Python syntax..."
for py_file in custom_components/paw_control/*.py; do
    if [ -f "$py_file" ]; then
        if python3 -m py_compile "$py_file" 2>/dev/null; then
            print_status "SUCCESS" "$(basename $py_file) syntax is valid"
        else
            print_status "ERROR" "$(basename $py_file) has syntax errors"
        fi
    fi
done

# Check dependencies
echo -e "\n📦 Checking dependencies..."
if [ -f "requirements.txt" ]; then
    print_status "SUCCESS" "requirements.txt found"
    
    # Try to install dependencies (dry run)
    if pip3 install --dry-run -r requirements.txt > /dev/null 2>&1; then
        print_status "SUCCESS" "All dependencies are available"
    else
        print_status "WARNING" "Some dependencies might not be available"
    fi
else
    print_status "WARNING" "requirements.txt not found"
fi

# Check HACS compatibility
echo -e "\n🏪 Checking HACS compatibility..."
if [ -f "hacs.json" ]; then
    print_status "SUCCESS" "hacs.json found"
    
    if python3 -m json.tool hacs.json > /dev/null 2>&1; then
        print_status "SUCCESS" "hacs.json is valid JSON"
    else
        print_status "ERROR" "hacs.json is invalid JSON"
    fi
else
    print_status "WARNING" "hacs.json not found (optional for HACS)"
fi

# Summary
echo -e "\n📊 Summary"
echo "=========="
if [ $ERRORS -eq 0 ]; then
    print_status "SUCCESS" "Installation check passed! Ready for installation."
    echo -e "\n🚀 Next steps:"
    echo "1. Copy the custom_components/paw_control folder to your Home Assistant config/custom_components/ directory"
    echo "2. Restart Home Assistant"
    echo "3. Go to Settings > Devices & Services > Add Integration"
    echo "4. Search for 'Paw Control' and follow the setup wizard"
else
    print_status "ERROR" "Installation check failed with $ERRORS errors"
    echo -e "\n🔧 Please fix the errors above before installing."
    exit 1
fi

exit 0
