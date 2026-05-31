# Security

## Authentication

All services are protected by Authentik. Services either use:

- **Forward auth** - Traefik checks with Authentik before forwarding the request. The service itself has no knowledge of the authentication. Used for services without native OIDC support.
- **Native OIDC** - the service redirects to Authentik for login and receives an identity token. Provides true SSO with no double login.

## Fallback Access

Critical infrastructure services keep local credentials as a fallback in case Authentik goes down:

- **Proxmox** - always accessible via `root@pam` local auth
- **AdGuard** - always accessible via local credentials set during initial setup
- **Portainer** - keep a local admin account alongside OIDC
- **Home Assistant** - local HA accounts remain active alongside OIDC

SSH into the Core VM is the ultimate fallback for managing containers when web interfaces are unavailable.

## SSL/TLS

All services are served over HTTPS. Traefik obtains a wildcard certificate for `*.lan.nathanryder.xyz` from Let's Encrypt using the Cloudflare DNS challenge. No inbound internet access is required for certificate issuance or renewal.

Internal service-to-service communication (Traefik to backend) is plain HTTP except for services that run their own HTTPS (Proxmox, Portainer's internal HTTPS endpoint). For those, the `skip-verify` serversTransport is used to allow Traefik to connect to backends with self-signed certificates.

## Rootless Docker

Docker runs in rootless mode on both VMs. The Docker daemon runs as `dockeruser` rather than root. This means a container escape or compromised container has limited access - it cannot escalate to host root.

Known limitations of rootless Docker in this setup are documented in the Rootless Docker Setup page and the Docker Networking Troubleshooting page.

## Network Isolation

Services on the Core VM that should not be publicly accessible are only on the `traefik` Docker network and have no exposed ports. They are only reachable via Traefik.

Services on the Services VM expose ports on the host for cross-VM communication with Traefik. These ports are reachable from the LAN directly, bypassing Traefik and Authentik. This is an accepted limitation for a home LAN environment.

No ports are forwarded on the router. The only external access is via Tailscale.

## Git Repository

The homelab git repository is used for all Docker compose files and configuration. Secrets are never committed - they are stored in Portainer environment variables instead. `.env` files are gitignored. The repository may be public as it contains no sensitive information.

The wiki branch of the same repository stores Wiki.js content. A deploy key with write access is used for Wiki.js git sync. The private key is stored only in Wiki.js administration settings.
