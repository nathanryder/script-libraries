# 7. Portainer Setup

Portainer provides a web UI for managing Docker containers on both VMs. The Core VM runs the full Portainer CE instance. The Services VM runs the Portainer Edge Agent which connects back to the Core VM.

## Core VM - Portainer CE

### Compose File

Location: `docker/portainer/docker-compose.yml`


Notes:
- `--http-enabled` enables plain HTTP on port 9000 internally since Traefik handles HTTPS externally
- Port 8000 stays exposed for edge agent communication - Traefik does not proxy this
- Docker socket path uses the rootless Docker socket at `/run/user/1000/docker.sock`
- DNS entries are needed so Portainer can resolve `auth.lan.nathanryder.xyz` for OIDC

### OIDC Configuration

Portainer is configured to use Authentik as an OAuth provider. Go to Settings -> Authentication -> OAuth in the Portainer UI and configure.

Enable Automatic User Provisioning so Authentik users are created in Portainer on first login.

Keep local admin credentials saved as a fallback in case Authentik goes down.

## Services VM - Edge Agent

### Getting the Edge Agent Command

In Portainer on the Core VM, go to Environments -> Add Environment -> Edge Agent. Portainer generates a `docker run` command with a unique `EDGE_ID` and `EDGE_KEY`. Convert this to a compose file.

### Compose File

Location: `docker/portainer-agent/docker-compose.yml` (on Services VM)

The `EDGE_KEY` contains Portainer credentials - store it in Portainer's environment variables, not in the git repo.

## Git Deployment

All stacks are deployed from the git repo via Portainer's git integration. When creating a stack:

1. Choose Repository as the source
2. Set the repository URL
3. Set the compose file path (e.g. `docker/portainer/docker-compose.yml`)
4. Add environment variables in the Environment Variables section

Portainer stores environment variables securely and injects them at deploy time.

## Notes

- When Portainer redeploys its own stack it restarts itself mid-operation and may show an error even though the deployment succeeded
- If Portainer's database is lost (e.g. container deleted), stacks show as unmanaged - recreate them from the git repo to take ownership again
- The edge agent tunnel error in logs is a background connectivity check and does not affect functionality
