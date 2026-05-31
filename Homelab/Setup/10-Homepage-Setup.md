# 10. Homepage Setup

Homepage is the service dashboard running on the Core VM. It auto-discovers services via Docker labels and displays them as tiles with optional live widgets.

## Prerequisites

- Traefik running on Core VM
- Socket proxy running on Services VM (for Services VM container discovery)
- Git repo with `docker/homepage/config/` folder containing config files

## Architecture

Homepage discovers services in two ways:

- **Core VM containers** - via the local Docker socket mounted directly into the Homepage container
- **Services VM containers** - via a read-only socket proxy running on the Services VM, configured in `docker.yaml`

## Compose File

Location: `docker/homepage/docker-compose.yml` (on Core VM)

The compose file uses an init container to clone the git repo and copy config files into the Homepage volume before Homepage starts. This avoids Portainer bind mount issues with git deployments.

## Config Files

Config files live in `docker/homepage/config/` in the git repo. The init container copies them to the Homepage volume on every redeploy.

### docker.yaml

Tells Homepage which Docker instances to watch:

```yaml
my-docker:
  socket: /var/run/docker.sock

services-vm:
  host: 192.168.1.5
  port: 2375
```

Without this file Homepage does not auto-discover any containers even with labels present.

### services.yaml

Used for non-Docker services (Proxmox, Home Assistant) that cannot use labels:

```yaml
- Core VM:
    - Proxmox:
        href: https://proxmox.lan.nathanryder.xyz
        icon: proxmox.png
        description: Hypervisor

- Home:
    - Home Assistant:
        href: https://homeassistant.lan.nathanryder.xyz
        icon: home-assistant.png
        description: Home Automation
```

Note: `${DOMAIN}` does not substitute in Homepage config files - use the full domain name.

## Docker Labels for Auto-Discovery

Add these labels to any Docker container to have it appear in Homepage:

**Core VM containers:**
```yaml
- "homepage.group=Core VM"
- "homepage.name=Service Name"
- "homepage.icon=service-name.png"
- "homepage.href=https://service-name.${DOMAIN}"
- "homepage.description=What it does"
```

**Services VM containers** (add `homepage.docker` to specify the instance):
```yaml
- "homepage.group=Services VM"
- "homepage.name=Service Name"
- "homepage.icon=service-name.png"
- "homepage.href=https://service-name.${DOMAIN}"
- "homepage.description=What it does"
- "homepage.docker=services-vm"
```

Icons are sourced from the walkxcode/dashboard-icons community pack. Browse available icons at https://github.com/walkxcode/dashboard-icons.

## Socket Proxy (Services VM)

Homepage uses a read-only Docker socket proxy on the Services VM to discover Services VM containers. See the Socket Proxy setup page for details.

## Updating Config Files

When config files in the git repo are updated, redeploy the Homepage stack in Portainer. The init container re-clones the repo and copies the updated files before Homepage restarts.
