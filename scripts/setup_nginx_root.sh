#!/usr/bin/env bash
set -euo pipefail

# 1. Update /etc/nginx/snippets/holybible.conf
cat << 'EOF' > /etc/nginx/snippets/holybible.conf
# =====================================================================
# Holy Bible Web Application - Nginx Reverse Proxy Configuration
# =====================================================================

# 1. 301 Redirection from legacy /bible subpath to root
location ~ ^/bible/?(.*)$ {
    return 301 /$1;
}

# 2. Main Holy Bible FastAPI Application Proxy
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;

    # WebSocket and EventSource / Chunked Streaming Support (Edge-TTS & Ask Bible AI)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Standard Proxy Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Performance & Streaming Buffering Settings
    proxy_buffering off;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;

    # Client payload size (for audio / verse import if needed)
    client_max_body_size 25M;
}
EOF

# 2. Update /etc/nginx/sites-available/default
cat << 'EOF' > /etc/nginx/sites-available/default
##
# Default server configuration for Holy Bible at root (/)
##
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	server_name _;

	include /etc/nginx/snippets/holybible.conf;
}

server {
	server_name pnrs.is-a.dev;

	include /etc/nginx/snippets/holybible.conf;

	listen [::]:443 ssl ipv6only=on; # managed by Certbot
	listen 443 ssl; # managed by Certbot
	ssl_certificate /etc/letsencrypt/live/pnrs.is-a.dev/fullchain.pem; # managed by Certbot
	ssl_certificate_key /etc/letsencrypt/live/pnrs.is-a.dev/privkey.pem; # managed by Certbot
	include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
	ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
	if ($host = pnrs.is-a.dev) {
		return 301 https://$host$request_uri;
	} # managed by Certbot

	listen 80;
	listen [::]:80;
	server_name pnrs.is-a.dev;
	return 404; # managed by Certbot
}
EOF

echo "[+] Testing Nginx configuration..."
nginx -t

echo "[+] Reloading Nginx service..."
systemctl reload nginx
echo "[+] SUCCESS: Nginx root configuration deployed and reloaded successfully!"
