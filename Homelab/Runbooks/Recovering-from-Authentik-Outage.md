# Recovering from Authentik Outage

If Authentik goes down, services protected by forward auth become inaccessible via their domain. Services with native OIDC also lose SSO login.

## What Still Works

- Proxmox at `192.168.1.3:8006` with `root@pam`
- AdGuard at `192.168.1.4:8080` with local credentials
- Portainer at `192.168.1.4:8000` - note that if Portainer is configured for OIDC only and local auth is disabled, this will not work. Always keep a local admin account in Portainer.
- SSH into Core VM as dockeruser

## Restart Authentik

SSH into Core VM and restart the containers:

```bash
docker restart authentik-server authentik-worker
```

Check logs for errors:

```bash
docker logs authentik-server | tail -50
docker logs authentik-worker | tail -50
```

## Check Dependencies

Authentik depends on PostgreSQL and Redis. Check they are running:

```bash
docker ps | grep -E "authentik|postgresql|redis"
```

If PostgreSQL is down:

```bash
docker restart authentik-postgresql
docker restart authentik-server authentik-worker
```

If Redis is down:

```bash
docker restart redis
docker restart authentik-server authentik-worker
```

## Check Database

If Authentik fails to start with database errors:

```bash
docker exec authentik-postgresql pg_isready -d authentik -U authentik
```

## Access Portainer Without OIDC

If Portainer's OIDC is broken but local auth is still enabled, go to:

```
https://192.168.1.4:8000
```

And use the local admin credentials to log in, then restart Authentik from the Portainer UI.

## Full Recovery from Scratch

If the Authentik stack needs to be redeployed from scratch:

1. Redeploy the Authentik stack from Portainer using the git repo
2. Wait for PostgreSQL to be healthy before Authentik starts
3. Access `https://auth.lan.nathanryder.xyz/if/flow/initial-setup/` if it is a completely fresh install
4. If restoring from backup, restore the `authentik_postgresql` volume first

All Authentik configuration (providers, applications, users, groups) is stored in the PostgreSQL database. If the volume is intact, everything should be restored after redeployment.
