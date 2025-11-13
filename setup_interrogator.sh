#!/bin/zsh
# quick setup script for jamf interrogator on macos, using uv for python environment management

set -e

echo "jamf interrogator setup"
echo "======================="
echo ""

# check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found - installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.zshrc 2>/dev/null || true
fi

echo "setting up python environment..."

# check if we're in a project directory with pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo "found jamfpy project - installing..."
    uv pip install -e .
else
    echo "installing requirements..."
    if [ -f "requirements-interrogator.txt" ]; then
        uv pip install -r requirements-interrogator.txt
    fi
fi

echo ""
echo "creating config file..."

CONFIG_PATH="$HOME/.jamf_interrogator.json"

if [ -f "$CONFIG_PATH" ]; then
    echo "config already exists at $CONFIG_PATH"
    echo "skipping config creation"
else
    cat > "$CONFIG_PATH" << 'EOF'
{
  "fqdn": "https://your-tenant.jamfcloud.com",
  "auth_method": "oauth2",
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here"
}
EOF
    echo "created config at $CONFIG_PATH"
    echo ""
    echo "⚠️  edit this file with your jamf credentials:"
    echo "   vim $CONFIG_PATH"
    echo "   or"
    echo "   open -e $CONFIG_PATH"
fi

echo ""
echo "setup complete!"
echo ""
echo "next steps:"
echo "  1. edit your config file with jamf credentials"
echo "  2. run: python jamf_interrogator.py list policies"
echo ""
echo "for help: python jamf_interrogator.py --help"
