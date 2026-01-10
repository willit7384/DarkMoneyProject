# ===============================
# Dark Money Project – Windows Setup
# ===============================

Write-Host "Starting Dark Money Project setup..."

# -------------------------------
# Install Chocolatey
# -------------------------------
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Refresh environment
refreshenv

# -------------------------------
# Core Developer Tools
# -------------------------------
choco install -y git
choco install -y nodejs-lts
choco install -y python
choco install -y postgresql
choco install -y vscode

# -------------------------------
# Optional but Strongly Recommended
# -------------------------------
choco install -y pgadmin4
choco install -y docker-desktop
choco install -y openssh

# -------------------------------
# VS Code Extensions
# -------------------------------
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next

# -------------------------------
# Verify installs
# -------------------------------
python --version
node --version
npm --version
git --version
psql --version

Write-Host "Setup complete. Restart PowerShell before continuing."
