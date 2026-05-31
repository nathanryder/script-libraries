# Setup

This section documents the chronological order in which the homelab was built. Each page covers the setup steps, decisions made, and issues encountered for that component.

The order matters - some services depend on others being in place first.

## Core Infrastructure Setup

1. Proxmox
2. VM Creation
3. Tailscale
4. Rootless Docker
5. AdGuard
6. Traefik
7. Portainer
8. Redis
9. traefik-kop
10. Authentik

# Services Setup

1. Homepage
2. Wiki.js
3. Actual Budget
4. Wealthfolio
5. Home Assistant

## Why This Order

Tailscale first - provides a secure management channel into the VMs before anything else is configured. If something goes wrong during setup, Tailscale gives a way back in that does not depend on Traefik or AdGuard being healthy.

AdGuard before Traefik - DNS needs to be working before testing Traefik routes. The wildcard DNS rewrite needs to be in place so hostnames resolve correctly when testing.

Traefik before other services - every service goes straight behind Traefik from the start rather than being accessible directly and then reconfigured later.

Portainer early - gives a UI for managing containers for the rest of the setup rather than doing everything via CLI.

Authentik after the core stack - needs Traefik and Redis running first, and it makes more sense to get the basic services working before adding an authentication layer on top.
