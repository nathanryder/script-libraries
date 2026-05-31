# 11. Authentik Setup

Authentik is the identity provider handling all authentication across services. It runs on the Core VM alongside a dedicated PostgreSQL database. Redis is shared with the existing Redis instance used by traefik-kop.

## Prerequisites

- Traefik running on Core VM
- Redis running on Core VM on the `traefik` Docker network
- `auth.lan.nathanryder.xyz` DNS rewrite in AdGuard

## Compose File

Location: `docker/authentik/docker-compose.yml`

## Environment Variables

```
PG_DB=authentik
PG_USER=authentik
PG_PASS=strong_random_password
AUTHENTIK_SECRET_KEY=generated_with_openssl_rand_base64_36
DOMAIN=lan.nathanryder.xyz
```

Generate the secret key:

```bash
openssl rand -base64 36
```

## Initial Setup

After deploying, access the setup wizard at:

```
https://auth.lan.nathanryder.xyz/if/flow/initial-setup/
```

Create the admin account. Use an email address as the identifier - it does not need to be real for a local setup.

## Concepts

**Provider** - defines how authentication works (Proxy, OAuth2/OIDC, SAML, LDAP).

**Application** - represents a service being protected. Links to a Provider.

**Outpost** - the running component that handles forward auth requests from Traefik. One embedded outpost serves all Proxy Provider applications.

**Flow** - a step-by-step authentication process (login, logout, enrollment etc).

**Policy** - a rule that evaluates to true or false, used to control access.

## Forward Auth Setup (Per Service)

For services without native OIDC support:

1. In Authentik: Applications -> Providers -> Create -> Proxy Provider
   - Mode: Forward auth (single application)
   - External host: `https://servicename.lan.nathanryder.xyz`
   - Authorization flow: Implicit

2. Create Application linked to the provider

3. Add application to the embedded Outpost (Applications -> Outposts -> Edit)

4. Add middleware label to service compose file:
   ```yaml
   - "traefik.http.routers.SERVICENAME.middlewares=authentik-forward-auth@file"
   ```

## OIDC Setup (Per Service)

For services with native OIDC support:

1. In Authentik: Applications -> Providers -> Create -> OAuth2/OpenID Provider
   - Client type: Confidential
   - Redirect URI: service-specific callback URL
   - Authorization flow: Implicit
   - Scopes: openid email profile

2. Create Application linked to the provider

3. Configure the service with the Client ID, Client Secret, and discovery URL:
   ```
   https://auth.lan.nathanryder.xyz/application/o/APPSLUG/.well-known/openid-configuration
   ```

## Fallback Access

Services with their own auth systems (Proxmox, AdGuard, Portainer, Home Assistant) keep their local credentials as fallback. If Authentik goes down these services can still be accessed directly via IP and port using local credentials.

Do not put Proxmox or AdGuard behind Authentik middleware in Traefik as they are needed for infrastructure recovery.
