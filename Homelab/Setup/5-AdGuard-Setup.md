# 5. AdGuard Setup

AdGuard Home runs on the Core VM as a Docker container in bridge networking mode. It serves as the DNS server for the entire network, handling ad blocking and providing local DNS rewrites for internal services.

## Prerequisites

- Rootless Docker running on Core VM
- Port 53 unprivileged access configured (see Rootless Docker Setup)
- systemd-resolved disabled

## Disable systemd-resolved

Ubuntu has a stub DNS listener on port 53 by default that conflicts with AdGuard:

```bash
sudo systemctl disable --now systemd-resolved
sudo rm /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
sudo chattr +i /etc/resolv.conf
```

The `chattr +i` makes the file immutable so Tailscale and cloud-init cannot overwrite it.

## Compose File

Location: `docker/adguard/docker-compose.yml`

## Initial Setup

Port 3000 is only used for the initial setup wizard. Access it at `http://192.168.1.4:3000` after starting the container. During setup, set the web interface port to `80` (which maps to `8080` on the host).

After setup is complete, port 3000 can be removed from the compose file if desired, though it does no harm to leave it.

## Configuration

### Upstream DNS

Set upstream DNS servers to IP addresses only to avoid circular resolution:

```
1.1.1.1
1.0.0.1
```

Use plain IP addresses rather than DoH hostnames. If AdGuard needs to resolve the DoH hostname it would need to use itself for DNS, creating a loop.

### DNS Rewrites

Add a wildcard rewrite under Filters -> DNS Rewrites:

```
Domain:  *.lan.nathanryder.xyz
Answer:  192.168.1.4
```

This means all internal services resolve to the Core VM (where Traefik is) without needing internet access.

### Router DNS

The eir Sagemcom router does not expose a DNS field in its normal UI. Options:

1. Set DNS manually on each device to `192.168.1.4`
2. Use the JavaScript console trick in the router UI (may not survive reboots)
3. Let AdGuard handle DHCP instead of the router

Currently DNS is set manually on devices as the most reliable approach given the eir router's limitations.

## Known Issues

### Real Client IPs

AdGuard runs in bridge networking mode rather than host mode due to rootless Docker limitations. This means DNS queries appear to come from `172.20.0.1` (the Docker gateway) rather than the real client IP. Per-client filtering and statistics are not available as a result.

Host network mode was attempted but does not work correctly in rootless Docker - the container gets its own network namespace rather than sharing the host's, so `192.168.1.4` never appears as a listening interface.

macvlan and ipvlan were also attempted but both require kernel capabilities not available in rootless Docker.
