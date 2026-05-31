# 15. Home Assistant Setup

Home Assistant runs on a dedicated HAOS VM. It is not Docker-managed - HAOS handles its own services via the addon supervisor. Traefik proxies to it via a file provider config. Authentication uses the hass-oidc-auth custom integration via HACS.

## VM Network Configuration

HAOS has a known bug where the IPv4 gateway disappears when DNS settings are changed in the UI, causing network update failures. Configure the network via the HA CLI instead.

From the Home Assistant terminal (SSH addon or web terminal):

```bash
ha network update enp6s18 \
  --ipv4-method static \
  --ipv4-address 192.168.1.6/24 \
  --ipv4-gateway 192.168.1.254 \
  --ipv4-nameserver 192.168.1.4 \
  --ipv6-method disabled
```

Verify the config applied:

```bash
ha network info
```

The output should show `192.168.1.4` as the nameserver and no IPv6 gateway. IPv6 is disabled to avoid the router's IPv6 link-local address interfering with DNS resolution (same issue as on Windows clients).

## Trusted Proxies

Home Assistant rejects requests from untrusted proxies by default. Add the Core VM IP to the trusted proxies list.

Using the VS Code Server addon, edit `/config/configuration.yaml`:

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.4
```

Restart Home Assistant after saving.

Without this, all requests through Traefik return a 400 Bad Request.

## Installing HACS

HACS (Home Assistant Community Store) is required to install the hass-oidc-auth integration.

From the Home Assistant terminal:

```bash
wget -O - https://get.hacs.xyz | bash -
```

Restart Home Assistant after installation. Then go to Settings -> Devices & Services -> Add Integration and search for HACS to complete setup. A GitHub account is required for HACS authentication.

## Installing hass-oidc-auth

After HACS is installed:

1. Go to HACS -> Integrations -> Explore & Download
2. Search for `OpenID Connect`
3. Install `hass-oidc-auth` by christiaangoossens
4. Restart Home Assistant

## Authentik OIDC Setup

Create an OAuth2/OIDC Provider in Authentik:

- Name: Home Assistant
- Client type: **Public** (required for mobile app compatibility - public clients use PKCE instead of a client secret, which is more secure for mobile apps)
- Redirect URI: `https://homeassistant.lan.nathanryder.xyz/auth/oidc/callback`
- Authorization flow: Implicit
- Scopes: openid email profile

Note the Client ID (no secret for public clients).

Create the Application. No Outpost needed for native OIDC.

## Configuring hass-oidc-auth

Add to `/config/configuration.yaml` via VS Code Server:

```yaml
auth_oidc:
  client_id: YOUR_CLIENT_ID_FROM_AUTHENTIK
  discovery_url: https://auth.lan.nathanryder.xyz/application/o/homeassistant/.well-known/openid-configuration
  features:
    automatic_user_linking: true
```

The application slug in the discovery URL must match exactly what was set when creating the Authentik application. If the application slug is `homeassistant` (no hyphen), the URL uses `homeassistant`. If it is `home-assistant`, use `home-assistant`.

Restart Home Assistant after saving.
