# Adding a Service to Authentik

## Forward Auth (Proxy Provider)

Use this for services without native OIDC support.

### 1. Create Provider

Applications -> Providers -> Create -> Proxy Provider

| Field | Value |
|---|---|
| Name | Service name |
| Authorization flow | default-provider-authorization-implicit-consent |
| Mode | Forward auth (single application) |
| External host | https://servicename.lan.nathanryder.xyz |

### 2. Create Application

Applications -> Applications -> Create (or use the wizard)

| Field | Value |
|---|---|
| Name | Service name |
| Slug | servicename |
| Provider | Select the provider created above |

### 3. Add to Outpost

Applications -> Outposts -> Edit the embedded outpost -> Add the application to the list

### 4. Add Middleware Label

Add to the service's Traefik labels:

```yaml
- "traefik.http.routers.servicename.middlewares=authentik-forward-auth@file"
```

---

## Native OIDC (OAuth2/OpenID Provider)

Use this for services that support OIDC natively (Portainer, Actual Budget, Proxmox, Wiki.js etc).

### 1. Create Provider

Applications -> Providers -> Create -> OAuth2/OpenID Provider

| Field | Value |
|---|---|
| Name | Service name |
| Authorization flow | default-provider-authorization-implicit-consent |
| Client type | Confidential |
| Redirect URIs | Service-specific callback URL |
| Signing Key | authentik Self-signed Certificate |
| Scopes | openid email profile |

Note the Client ID and Client Secret - you will need these to configure the service.

The redirect URI format varies by service - check the service's documentation or look at the URL Authentik redirects to during a failed login attempt.

### 2. Create Application

Same as forward auth above.

### 3. Configure the Service

Use the discovery URL to auto-populate endpoints where supported:

```
https://auth.lan.nathanryder.xyz/application/o/APPSLUG/.well-known/openid-configuration
```

Where APPSLUG matches the slug set in step 2.

### 4. Add DNS if Needed

Services that make server-side token requests need to resolve `auth.lan.nathanryder.xyz`. Add to the compose file:

```yaml
dns:
  - 192.168.1.4
  - 1.1.1.1
```

---

## Restricting Access by Group

To restrict an application to specific users:

Applications -> Applications -> select the application -> Policy/Group/User Bindings -> Create

Bind a group (e.g. admins) directly. Only users in that group will be able to access the application.

---

## Common Issues

**403 Forbidden on token exchange** - usually a scope mismatch. Check that scopes in the service config (space-separated) match what the Authentik provider exposes. Commas instead of spaces is a common mistake.

**Failed to obtain access token** - the service cannot reach Authentik's token endpoint. Check DNS resolution from inside the container. Add `dns: 192.168.1.4` to the compose file.

**Redirect URI mismatch** - the callback URL the service is sending does not match what is configured in the Authentik provider. Check the exact URL including trailing slashes.

**Missing claim error** - the service is expecting a claim that Authentik is not sending. Check that the `profile` scope is included, as `preferred_username` and `name` come from the profile scope.
