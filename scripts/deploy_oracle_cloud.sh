#!/usr/bin/env bash
# ==============================================================================
# Holy Bible - Oracle Cloud VM One-Click Automated Deployment Script
# Hosts the FastAPI application under the '/bible' subpath behind Nginx
# ==============================================================================
set -euo pipefail

APP_DIR="/opt/holybible"
REPO_URL="https://github.com/Elroi-thecreator/bibleweb.git"
SERVICE_NAME="holybible"
APP_USER="www-data"
URL_PREFIX="/bible"

echo "======================================================================"
echo " 🕊️ Holy Bible - Oracle Cloud VM Deployment (Subpath: ${URL_PREFIX})"
echo "======================================================================"

if [[ $EUID -ne 0 ]]; then
   echo "[-] Error: This script must be run as root (or with sudo)."
   exit 1
fi

# 1. Detect Linux Distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID=$ID
else
    OS_ID="unknown"
fi

echo "[+] Detected operating system: $OS_ID"

# 2. Install Required System Packages
echo "[+] Installing system packages and dependencies..."
if [[ "$OS_ID" == "ubuntu" || "$OS_ID" == "debian" ]]; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y python3 python3-venv python3-pip git nginx \
        libharfbuzz-dev libfreetype6-dev iptables-persistent netfilter-persistent
elif [[ "$OS_ID" == "ol" || "$OS_ID" == "rhel" || "$OS_ID" == "centos" ]]; then
    dnf install -y python3 python3-pip git nginx harfbuzz-devel freetype-devel firewalld
    APP_USER="nginx"
else
    echo "[!] Warning: Unrecognized OS, attempting apt-get..."
    apt-get update -y && apt-get install -y python3 python3-venv python3-pip git nginx || true
fi

# 3. Clone or Update Application Repository
if [ ! -d "$APP_DIR" ]; then
    echo "[+] Cloning repository into $APP_DIR..."
    git clone "$REPO_URL" "$APP_DIR"
else
    echo "[+] Repository already exists at $APP_DIR. Pulling latest updates..."
    cd "$APP_DIR"
    git fetch origin
    git checkout main || true
    git pull origin main || true
fi

cd "$APP_DIR"

# 4. Set Up Python Virtual Environment & Install Dependencies
echo "[+] Configuring Python virtual environment..."
if [ ! -d "$APP_DIR/.venv" ]; then
    python3 -m venv "$APP_DIR/.venv"
fi

"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 5. Fix Directory Permissions for SQLite and Audio Cache
echo "[+] Configuring permissions for $APP_USER..."
mkdir -p "$APP_DIR/data" "$APP_DIR/.audio_cache"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod -R 775 "$APP_DIR/data" "$APP_DIR/.audio_cache"

# 6. Install Systemd Service Unit
echo "[+] Configuring systemd service: /etc/systemd/system/${SERVICE_NAME}.service..."
cat <<EOF > "/etc/systemd/system/${SERVICE_NAME}.service"
[Unit]
Description=Holy Bible Production Web Server (FastAPI + Embedded SQLite)
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PYTHONPATH=${APP_DIR}"
Environment="URL_PREFIX=${URL_PREFIX}"
Environment="HOST=127.0.0.1"
Environment="PORT=8000"
Environment="WEB_CONCURRENCY=2"
Environment="PAGE_CACHE_SIZE=512"
Environment="AUDIO_CACHE_SIZE=500"
ExecStart=${APP_DIR}/.venv/bin/python scripts/run_server.py --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

# 7. Configure Nginx Reverse Proxy for /bible
echo "[+] Configuring Nginx reverse proxy under ${URL_PREFIX}..."
NGINX_CONF_SNIPPET="
location = ${URL_PREFIX} {
    return 301 ${URL_PREFIX}/;
}

location ${URL_PREFIX}/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \"upgrade\";
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Forwarded-Prefix ${URL_PREFIX};
    proxy_buffering off;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
    client_max_body_size 25M;
}
"

# If a default server block exists in sites-available or conf.d:
if [ -f /etc/nginx/sites-available/default ]; then
    if ! grep -q "location ${URL_PREFIX}/" /etc/nginx/sites-available/default; then
        # Insert the location block right before the last closing brace of the default server
        sed -i '/^}$/i '"$NGINX_CONF_SNIPPET" /etc/nginx/sites-available/default
    fi
else
    cat <<EOF > /etc/nginx/conf.d/holybible.conf
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    ${NGINX_CONF_SNIPPET}
}
EOF
fi

nginx -t
systemctl enable nginx
systemctl reload nginx || systemctl restart nginx

# 8. Configure Host OS Firewall Rules (Oracle Cloud In-Guest Firewall)
echo "[+] Configuring Oracle VM in-guest firewall..."
if [[ "$OS_ID" == "ubuntu" || "$OS_ID" == "debian" ]]; then
    # In Ubuntu on Oracle Cloud, iptables drops port 80/443 by default
    iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
    iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
    netfilter-persistent save || true
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp || true
        ufw allow 443/tcp || true
    fi
elif [[ "$OS_ID" == "ol" || "$OS_ID" == "rhel" ]]; then
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=http || true
        firewall-cmd --permanent --add-service=https || true
        firewall-cmd --reload || true
    fi
fi

echo "======================================================================"
echo " ✅ DEPLOYMENT COMPLETE! Holy Bible is now active under ${URL_PREFIX}"
echo "======================================================================"
echo " Local Test:  curl -I http://127.0.0.1:8000${URL_PREFIX}/"
echo " Web Access:  http://<YOUR_ORACLE_VM_PUBLIC_IP>${URL_PREFIX}/"
echo ""
echo " ⚠️  CRITICAL ORACLE CLOUD INVARIANT (OCI Web Console Security List):"
echo " Oracle Cloud blocks port 80 and 443 at the Virtual Cloud Network (VCN)"
echo " boundary by default. In the OCI Console:"
echo "   1. Navigate to: Networking > Virtual Cloud Networks > Your VCN"
echo "   2. Click: Security Lists > Default Security List"
echo "   3. Click: 'Add Ingress Rules'"
echo "   4. Source CIDR: 0.0.0.0/0"
echo "   5. IP Protocol: TCP"
echo "   6. Destination Port Range: 80, 443"
echo "======================================================================"
