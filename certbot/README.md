# Let's Encrypt (Production SSL)

For production, replace the self-signed cert with a real one from Let's Encrypt.

## Steps

1. Point your domain DNS to the server IP.

2. Run the initial certificate request:
```bash
docker run --rm \
  -v ./certbot/certs:/etc/letsencrypt \
  -v ./certbot/webroot:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --email you@example.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com
```

3. Mount the cert into the nginx container via docker-compose:
```yaml
loadbalancer:
  volumes:
    - ./certbot/certs/live/yourdomain.com/fullchain.pem:/etc/nginx/ssl/server.crt:ro
    - ./certbot/certs/live/yourdomain.com/privkey.pem:/etc/nginx/ssl/server.key:ro
```

4. Update nginx.conf `server_name` to your domain:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

5. Auto-renew (add to crontab):
```bash
0 3 * * * docker run --rm \
  -v ./certbot/certs:/etc/letsencrypt \
  -v ./certbot/webroot:/var/www/certbot \
  certbot/certbot renew --quiet && \
  docker compose exec loadbalancer nginx -s reload
```
