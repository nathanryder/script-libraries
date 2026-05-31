# Adding a New Service

This runbook covers adding a new self-hosted service to the homelab. The steps differ depending on which VM the service runs on.

## Core VM Service

Services on the Core VM can use Docker label auto-discovery.

### 1. Create the compose file

Location: `docker/service-name/docker-compose.yml`

```yaml
services:
  service-name:
    image: image/name:version
    container_name: service-name
    pull_policy: always
    restart: unless-stopped
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.service-name.rule=Host(`service-name.${DOMAIN}`)"
      - "traefik.http.routers.service-name.entrypoints=websecure"
      - "traefik.http.routers.service-name.tls.certresolver=letsencrypt"
      - "traefik.http.services.service-name.loadbalancer.server.port=PORT"
      - "homepage.group=Core VM"
      - "homepage.name=Service Name"
      - "homepage.icon=service-name.png"
      - "homepage.href=https://service-name.${DOMAIN}"
      - "homepage.description=What it does"
    volumes:
      - service_data:/data

volumes:
  service_data:

networks:
  traefik:
    external: true
```

### 2. Add to Authentik (if protected)

**For forward auth:**
- Applications -> Providers -> Create -> Proxy Provider
- Mode: Forward auth (single application)
- External host: `https://service-name.lan.nathanryder.xyz`
- Authorization flow: Implicit
- Create Application, add to Outpost
- Add middleware label: `"traefik.http.routers.service-name.middlewares=authentik-forward-auth@file"`

**For native OIDC:**
- Applications -> Providers -> Create -> OAuth2/OpenID Provider
- Redirect URI: service-specific callback URL
- Note Client ID and Secret
- Configure the service with the discovery URL

### 3. Deploy via Portainer

- Stacks -> Add Stack -> Repository
- Set compose file path
- Add environment variables
- Deploy

### 4. Verify

- Check Traefik dashboard shows the new router
- Access `https://service-name.lan.nathanryder.xyz`
- Verify Authentik auth works if applicable
- Check Homepage shows the service tile

---

## Services VM Service

Services on the Services VM cannot use Docker label auto-discovery directly - traefik-kop handles publishing labels to Redis.

### 1. Create the compose file on Services VM

```yaml
services:
  service-name:
    image: image/name:version
    container_name: service-name
    pull_policy: always
    restart: unless-stopped
    ports:
      - "PORT:PORT"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.service-name.rule=Host(`service-name.${DOMAIN}`)"
      - "traefik.http.routers.service-name.entrypoints=websecure"
      - "traefik.http.routers.service-name.tls.certresolver=letsencrypt"
      - "traefik.http.services.service-name.loadbalancer.server.port=PORT"
      - "homepage.group=Services VM"
      - "homepage.name=Service Name"
      - "homepage.icon=service-name.png"
      - "homepage.href=https://service-name.${DOMAIN}"
      - "homepage.description=What it does"
      - "homepage.docker=services-vm"
    dns:
      - 192.168.1.4
      - 1.1.1.1
```

Note: `ports:` is required for Services VM services so Traefik on the Core VM can reach them via LAN IP.

### 2. Set DOMAIN environment variable in Portainer

The `${DOMAIN}` in labels is substituted by Docker Compose. Make sure `DOMAIN=lan.nathanryder.xyz` is set in the stack's environment variables in Portainer.

### 3. Verify traefik-kop published the route

```bash
docker exec redis redis-cli keys "*service-name*"
docker exec redis redis-cli get "traefik/http/services/service-name/loadBalancer/servers/0/url"
```

The URL should show `http://192.168.1.5:PORT`.

### 4. Add to Authentik

Same as Core VM service above.

### 5. Verify

It may take a few seconds after traefik-kop publishes the route for Traefik to pick it up from Redis.

---

## Non-Docker Services (Proxmox, HAOS)

Services not running in Docker need a file provider config in Traefik.

Add a new config to the Traefik compose `configs:` block:

```yaml
configs:
  service-name:
    content: |
      http:
        routers:
          service-name:
            rule: "Host(`service-name.${DOMAIN}`)"
            entryPoints:
              - websecure
            tls:
              certResolver: letsencrypt
            service: service-name
        services:
          service-name:
            loadBalancer:
              servers:
                - url: "http://192.168.1.x:PORT"
```

And mount it:

```yaml
services:
  traefik:
    configs:
      - source: service-name
        target: /etc/traefik/dynamic/service-name.yml
```

For HTTPS backends with self-signed certs, add the `skip-verify` serversTransport and `forwarded-proto` middleware (defined in `common.yml`).
