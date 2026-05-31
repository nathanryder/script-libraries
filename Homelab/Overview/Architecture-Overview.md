# Architecture Overview

## Physical Setup

A single Proxmox host (`HL-HV01P`) runs three VMs on a home LAN (`192.168.1.0/24`). The router is an eir Sagemcom fibrebox at `192.168.1.254`.

## VMs

| VM | Hostname | IP | Purpose |
|---|---|---|---|
| Core VM | HL-CORE01V | 192.168.1.4 | Infrastructure and networking |
| Services VM | HL-SVC01V | 192.168.1.5 | User-facing applications |
| HAOS VM | - | 192.168.1.6 | Home Assistant OS |

## Core VM

Runs all infrastructure and networking services. Everything on this VM is Docker-based using rootless Docker running as the `dockeruser` user. Services include:

- Traefik - reverse proxy and SSL termination
- AdGuard Home - DNS server and ad blocker
- Authentik - identity provider and SSO
- Portainer - Docker management UI
- Redis - shared cache, used by Authentik and traefik-kop
- Homepage - service dashboard

## Services VM

Runs user-facing applications. Also uses rootless Docker. Services include:

- Actual Budget - budgeting
- Wealthfolio - investment and wealth tracking
- Wiki.js - documentation
- traefik-kop - publishes Docker labels to Redis for Traefik auto-discovery
- Socket Proxy - exposes read-only Docker API for Homepage

## HAOS VM

Runs Home Assistant OS. Not Docker-managed - HAOS manages its own services via its addon supervisor. Key addons include Mosquitto, Zigbee2MQTT, and VS Code Server.

## Traffic Flow

All web traffic enters through Traefik on the Core VM. Traefik handles HTTPS termination and routing. Services on the Core VM are reached via the shared `traefik` Docker network. Services on the Services VM are reached via LAN IP and port.

```
Browser
  -> AdGuard (DNS resolves *.lan.nathanryder.xyz to 192.168.1.4)
  -> Traefik (192.168.1.4:443)
  -> Authentik (forward auth check or OIDC)
  -> Core VM service (via Docker network)
     OR
  -> Services VM service (via 192.168.1.5:PORT)
```

## Auto-Discovery

Traefik auto-discovers Core VM services via the Docker socket and container labels. For Services VM services, traefik-kop runs on the Services VM, reads container labels, and publishes routes to Redis. Traefik reads from Redis via the Redis provider.

Homepage auto-discovers Core VM containers via the local Docker socket, and Services VM containers via a read-only socket proxy running on the Services VM.

## DNS

AdGuard Home runs on the Core VM and serves as the DNS server for the network. A wildcard DNS rewrite maps `*.lan.nathanryder.xyz` to `192.168.1.4` so all internal services resolve locally without internet access.

The Core VM itself uses `1.1.1.1` directly in `/etc/resolv.conf` to avoid a circular dependency. Individual containers that need to resolve internal domains have `dns: 192.168.1.4` set in their compose files.

## Remote Access

Tailscale is installed on both VMs at the host level (not in Docker). Remote access is via Tailscale only - no ports are forwarded on the router and there is no Cloudflare Tunnel currently configured.
