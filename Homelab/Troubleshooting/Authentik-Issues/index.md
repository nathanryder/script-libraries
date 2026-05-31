# Authentik Issues

## Token Exchange Failures (403 Forbidden)

**Symptom:** Service logs show `403 Forbidden` when exchanging the authorization code for a token.

**Common causes:**

1. **Scope mismatch** - the service is requesting scopes that do not match what the Authentik provider exposes, or scopes are comma-separated instead of space-separated.
   
   Correct: `openid email profile`
   Incorrect: `openid,email,profile`

2. **Client secret mismatch** - the secret in the service config does not match the Authentik provider. Regenerate the secret in Authentik (Applications -> Providers -> Edit -> Regenerate) and update the service.

3. **Redirect URI mismatch** - the callback URL sent by the service does not match what is configured in the Authentik provider. Check the exact URL including trailing slashes.

---

## Failed to Obtain Access Token

**Symptom:** Service shows "failed to obtain access token" or similar after successful Authentik login.

**Cause:** The service cannot reach Authentik's token endpoint server-side. This is a DNS resolution issue - the service container cannot resolve `auth.lan.nathanryder.xyz`.

**Fix:** Add DNS to the service's compose file:

```yaml
dns:
  - 192.168.1.4
  - 1.1.1.1
```

---

## Missing Claim Error

**Symptom:** Service or Authentik logs show a missing claim (e.g. `missing claim 'preferred_username'`).

**Cause:** The claim is not being sent by Authentik because the required scope is missing.

- `preferred_username` and `name` come from the `profile` scope
- `email` comes from the `email` scope
- `sub` is always included with `openid`

**Fix:** Add `profile` to the scopes in both the Authentik provider and the service configuration.

---

## Redirect URI Mismatch

**Symptom:** Authentik shows a redirect URI error after login.

**Cause:** The callback URL the service is sending does not match any of the redirect URIs configured in the Authentik provider.

Some services (like Wiki.js) generate UUID-based callback URLs rather than using a standard `/callback` path. To find the actual callback URL, attempt login and check the URL that Authentik is redirected to in the browser's network tab.

**Fix:** Add the exact callback URL to the Authentik provider's redirect URI list.

---

## Proxmox OIDC Login Fails with 401

**Symptom:** Proxmox shows `openid authentication failure` after successful Authentik login.

**Common causes:**

1. **User not created** - Proxmox may not auto-create the user even with Autocreate Users enabled. Check Datacenter -> Permissions -> Users for the Authentik user after a login attempt.

2. **No permissions assigned** - the user exists but has no Proxmox permissions. Go to Datacenter -> Permissions -> Add -> User Permission and assign the Administrator role to the user at path `/`.

3. **DNS resolution** - Proxmox cannot reach `auth.lan.nathanryder.xyz` for token validation. Set Proxmox's DNS to `192.168.1.4` in the network configuration.

4. **Username claim** - Proxmox expects a `username` claim. Set the Username Claim field in the Proxmox realm settings to `username`. In the Authentik provider, include the `profile` scope.

---

## Authentik Worker Not Processing Tasks

**Symptom:** Authentik appears to work but some features (email, scheduled tasks) do not function.

**Fix:** Check the worker container is running and healthy:

```bash
docker ps | grep authentik-worker
docker logs authentik-worker 2>&1 | tail -30
```

If the worker crashed, restart it:

```bash
docker restart authentik-worker
```
