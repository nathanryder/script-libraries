# 6. Traefik Setup

Traefik is the reverse proxy and SSL termination point for all services. It runs on the Core VM and handles routing, HTTPS, and automatic certificate management via Let's Encrypt.

## Prerequisites

- Rootless Docker running on Core VM
- AdGuard running with DNS rewrite for `*.lan.nathanryder.xyz`
- Cloudflare API token with Edit Zone DNS permissions for `nathanryder.xyz`
- `traefik` Docker network created

## Create Docker Network

```bash
docker network create traefik
```

This only needs to be done once. All services that Traefik proxies on the Core VM must join this network.

## Compose File

Location: `docker/traefik/docker-compose.yml`

Static config is passed via CLI arguments in the `command:` section rather than a `traefik.yml` file. This avoids bind mount issues with Portainer git deployments. Dynamic config is inlined using Docker's `configs:` block.

## Environment Variables

Set in Portainer for the Traefik stack:

```
CF_DNS_API_TOKEN=your_cloudflare_token
ACME_EMAIL=your@email.com
DOMAIN=lan.nathanryder.xyz
TRAEFIK_DASHBOARD_AUTH=username:$$2y$$10$$hashedpassword
```

Note: `$` signs in the dashboard auth hash must be doubled (`$$`) when set as Docker Compose environment variables.

## Cloudflare Setup

Before deploying Traefik:

1. Create an API token in Cloudflare with `Edit zone DNS` permission scoped to `nathanryder.xyz`
2. Add a wildcard DNS A record: `*.lan.nathanryder.xyz -> 192.168.1.4` (this is for the Let's Encrypt DNS challenge, not for actual routing)

## Dynamic Config

Dynamic configuration is provided via Docker's `configs:` block in the compose file. This includes:

- `traefik-dashboard.yml` - dashboard route and auth middleware
- `authentik-middleware.yml` - forward auth middleware definition
- `common.yml` - reusable transports and middlewares (skip-verify, forwarded-proto)
- Per-service configs for non-Docker services (Proxmox, Home Assistant)

## Providers

Traefik uses three providers:

**Docker provider** - auto-discovers containers on the Core VM that have `traefik.enable=true` labels and are on the `traefik` network.

**File provider** - watches `/etc/traefik/dynamic/` for YAML files. Used for the dashboard route and services that cannot use Docker labels.

**Redis provider** - reads routes published by traefik-kop from the Services VM. This enables auto-discovery of Services VM containers via their Docker labels.

## Adding a New Core VM Service

Add these labels to the service's compose file:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.SERVICENAME.rule=Host(`SERVICENAME.${DOMAIN}`)"
  - "traefik.http.routers.SERVICENAME.entrypoints=websecure"
  - "traefik.http.routers.SERVICENAME.tls.certresolver=letsencrypt"
  - "traefik.http.services.SERVICENAME.loadbalancer.server.port=PORT"
```

And add the service to the `traefik` network:

```yaml
networks:
  traefik:
    external: true
```

## Adding a New Services VM Service

Add Traefik labels to the container's compose file on the Services VM. traefik-kop will publish them to Redis automatically. Make sure `ports:` is defined so Traefik can reach the container via LAN IP.

## Notes

- Certificates are stored in the `traefik_certs` named volume at `/certs/acme.json`
- Traefik auto-renews certificates before expiry
