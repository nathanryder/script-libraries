# DNS Issues

## systemd-resolved Conflict

**Symptom:** AdGuard fails to start with a port binding error, or port 53 is already in use.

**Cause:** Ubuntu 22.04+ runs `systemd-resolved` with a stub listener on port 53 by default.

**Fix:**
```bash
sudo systemctl disable --now systemd-resolved
sudo rm /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
sudo chattr +i /etc/resolv.conf
```

The `chattr +i` prevents other processes from overwriting the file.

---

## Tailscale Overwriting resolv.conf

**Symptom:** After a reboot, `/etc/resolv.conf` points to Tailscale's DNS instead of `1.1.1.1`, causing DNS to fail or loop.

**Fix:**
```bash
sudo tailscale up --accept-dns=false
sudo chattr -i /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
sudo chattr +i /etc/resolv.conf
```

---

## IPv6 Router DNS Interference

**Symptom:** Internal domains do not resolve even though AdGuard is running. `ipconfig /all` on Windows shows an IPv6 address (e.g. `fe80::4615:24ff:fe62:963f`) as the first DNS server.

**Cause:** The router advertises itself as a DNS server via IPv6. Windows queries it first, before reaching AdGuard at `192.168.1.4`.

**Fix:** Set IPv6 DNS to manual on Windows and either leave it blank or set it to `2606:4700:4700::1111` (Cloudflare IPv6). This prevents the router's IPv6 address from being used for DNS.

---

## eir Router DNS Limitation

**Symptom:** Setting `192.168.1.4` as the DNS server in the eir router's WAN DNS settings does not affect LAN clients. LAN DNS settings have no DNS field exposed.

**Cause:** The eir Sagemcom router does not expose a LAN DNS field in its standard UI. The WAN DNS setting only affects the router's own DNS queries, not what is handed out to LAN clients via DHCP.

**Workaround:** Set DNS manually on each device pointing at `192.168.1.4`. The JavaScript console trick (`$.xmo.setValuesTree`) may work but does not reliably survive router reboots.

---

## Container Cannot Resolve Internal Domains

**Symptom:** A Docker container returns an error like `dial tcp: lookup auth.lan.nathanryder.xyz: no such host`.

**Cause:** Docker containers use Docker's internal DNS resolver (`127.0.0.11`) by default, which does not know about AdGuard rewrites.

**Fix:** Add DNS configuration to the container's compose file:

```yaml
dns:
  - 192.168.1.4
  - 1.1.1.1
```

This tells the container to use AdGuard for DNS, which has the local rewrites.

---

## Core VM Cannot Resolve Internal Domains

**Symptom:** Commands run directly on the Core VM cannot resolve `*.lan.nathanryder.xyz`.

**Cause:** The Core VM uses `1.1.1.1` directly to avoid a circular dependency on AdGuard. It intentionally does not use AdGuard for DNS.

**Fix:** This is expected behaviour. For one-off resolution, query AdGuard directly:

```bash
dig servicename.lan.nathanryder.xyz @192.168.1.4
```

For containers on the Core VM that need to resolve internal domains, add the `dns:` section to their compose file.
