# Networking

## Overview

The homelab runs on a home LAN (`192.168.1.0/24`) behind an eir Sagemcom fibrebox router at `192.168.1.254`.

All VMs have static IPs configured via cloud-init (Core VM, Services VM) or via the HAOS network configuration interface (HAOS VM).

## DNS

AdGuard Home runs on the Core VM at `192.168.1.4:53` and serves as the DNS server for the network. It handles:

- Ad blocking via blocklists
- Local DNS rewrites for `*.lan.nathanryder.xyz`
- Upstream DNS forwarding to Cloudflare (`1.1.1.1`)

The Core VM itself does not use AdGuard for DNS - it uses `1.1.1.1` directly via a locked `/etc/resolv.conf` file. This avoids a circular dependency where AdGuard going down would take out the Core VM's ability to pull Docker images or reach the internet.

Individual Docker containers that need to resolve internal domains have `dns: 192.168.1.4` configured in their compose files.

## Reverse Proxy

All web traffic goes through Traefik on the Core VM at `192.168.1.4:443`. Traefik terminates TLS and routes requests to the appropriate backend service.

## Remote Access

Tailscale provides encrypted remote access. It is installed at the host level on both the Core VM and Services VM (not in Docker). Remote devices need the Tailscale app installed and must be logged into the same Tailscale account.

No ports are forwarded on the router. There is no public IP exposure.

## Sections

- IP Reference - all IP addresses in use
- Domain Reference - all internal domains
- DNS Configuration - AdGuard setup and rewrites
- Tailscale - setup and device list
