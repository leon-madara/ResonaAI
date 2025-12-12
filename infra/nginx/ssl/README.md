# SSL Certificate Setup with Let's Encrypt

This directory is for SSL certificates. In production, use Let's Encrypt (free) to obtain certificates.

## Setup Instructions

### Option 1: Using Certbot (Recommended)

1. Install certbot:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. Obtain certificate:
```bash
sudo certbot certonly --standalone -d mentalhealth.ke -d www.mentalhealth.ke
```

3. Certificates will be stored in:
   - `/etc/letsencrypt/live/mentalhealth.ke/fullchain.pem`
   - `/etc/letsencrypt/live/mentalhealth.ke/privkey.pem`

4. Update nginx.conf to point to these certificates

5. Set up auto-renewal:
```bash
sudo certbot renew --dry-run
```

### Option 2: Using Docker Certbot

1. Run certbot in a container:
```bash
docker run -it --rm \
  -v certbot-certs:/etc/letsencrypt \
  -v certbot-www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d mentalhealth.ke
```

2. Mount certificates in docker-compose:
```yaml
volumes:
  - /etc/letsencrypt/live/mentalhealth.ke/fullchain.pem:/etc/nginx/ssl/fullchain.pem
  - /etc/letsencrypt/live/mentalhealth.ke/privkey.pem:/etc/nginx/ssl/privkey.pem
```

### Option 3: AWS Certificate Manager (ACM)

If using AWS, use ACM for free SSL certificates:

1. Request certificate in AWS Console
2. Validate domain ownership
3. Use with Application Load Balancer (ALB)
4. ALB handles SSL termination automatically

## Development

For local development, SSL is not required. The nginx.conf is configured to work without SSL in development mode.

