# 9. traefik-kop Setup

traefik-kop runs on the Services VM and publishes Docker container labels to Redis on the Core VM. Traefik reads from Redis via its Redis provider, giving auto-discovery of Services VM containers without running a second Traefik instance.

## Prerequisites

- Redis running on Core VM on the `traefik` Docker network
- Traefik configured with `--providers.redis.endpoints=redis:6379`
- Services VM has network access to Core VM on port 6379

## Compose File

Location: `docker/traefik-kop/docker-compose.yml` (on Services VM)

## Key Configuration

**REDIS_ADDR** - must use the Core VM's LAN IP, not a hostname. traefik-kop runs on the Services VM where there is no `redis` container to resolve by name.

**BIND_IP** - the IP that traefik-kop registers for discovered services. This must be the Services VM's LAN IP (`192.168.1.5`) so Traefik knows where to route requests. If this is wrong or missing, Traefik will try to route to the wrong IP and return 502.

**DOCKER_HOST / socket path** - must point at the rootless Docker socket. Replace `1000` with the actual UID of dockeruser if different:

```bash
id -u dockeruser
```

## How It Works

traefik-kop watches the Services VM Docker socket for containers with `traefik.enable=true` labels. When it finds one, it publishes the route to Redis using Traefik's key format:

```
traefik/http/routers/servicename/rule
traefik/http/routers/servicename/entryPoints/0
traefik/http/services/servicename/loadBalancer/servers/0/url
```

The URL published uses `BIND_IP` and the port from `traefik.http.services.servicename.loadbalancer.server.port`.

## Verify

Check traefik-kop published a service:

```bash
docker logs traefik-kop 2>&1 | grep -i "publishing"
docker exec redis redis-cli keys "*servicename*"
docker exec redis redis-cli get "traefik/http/services/servicename/loadBalancer/servers/0/url"
```

The URL should show `http://192.168.1.5:PORT`.

## Requirements for Services VM Services

For traefik-kop to route a service correctly, the container must have:

1. `traefik.enable=true` label
2. Standard Traefik routing labels
3. `ports:` defined in the compose file - traefik-kop registers `BIND_IP:PORT` and Traefik connects to the host, not the container directly
4. `DOMAIN` environment variable set in Portainer so `${DOMAIN}` substitutes correctly in labels

## Common Issues

**Connection refused to Redis** - check `REDIS_ADDR` uses the LAN IP not a hostname. Check Redis port 6379 is reachable from the Services VM.

**Routes published but Traefik not picking them up** - Traefik may need a restart after initial Redis provider configuration. Check Traefik logs for Redis provider errors.

**Wrong backend URL** - check `BIND_IP` is set to the Services VM's LAN IP. If missing, traefik-kop may use the container's Docker network IP which Traefik cannot reach.
