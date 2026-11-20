#!/usr/bin/env bash
# Usage on VPS (Ubuntu): sudo bash deploy/deploy-hostinger.sh yourdomain.com
set -e
DOMAIN="$1"; [ -z "$DOMAIN" ] && { echo "Usage: $0 yourdomain.com"; exit 1; }
[ -f backend/.env ] || { echo "Create backend/.env first (copy backend/.env.example)"; exit 1; }
apt-get update -y
command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh
apt-get install -y nginx certbot python3-certbot-nginx
export PUBLIC_URL="https://$DOMAIN"
docker compose -f docker-compose.prod.yml up -d --build
sed "s/yourdomain.com/$DOMAIN/g" deploy/hostinger-nginx-host.conf > /etc/nginx/sites-available/pizza-king
ln -sf /etc/nginx/sites-available/pizza-king /etc/nginx/sites-enabled/pizza-king
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN" --redirect || echo "SSL later: certbot --nginx -d $DOMAIN"
echo "Live: https://$DOMAIN   (add https://$DOMAIN to CORS_ORIGINS in backend/.env)"
