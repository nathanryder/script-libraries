# 3. Tailscale Setup

Tailscale is installed directly on the VM hosts, not in Docker. This means the entire VM is on the Tailscale network and all containers benefit from it automatically.

## Installation

Run on each VM:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

The second command prints a URL - open it in a browser, log into your Tailscale account and authorise the machine. Once done it appears in the Tailscale admin console at https://login.tailscale.com/admin/machines and gets a `100.x.x.x` IP.

## Verify

```bash
tailscale ip
ping 100.x.x.x  # ping the other VM's Tailscale IP
```

## Admin Console Configuration

After both VMs are connected, do the following in the Tailscale admin console at https://login.tailscale.com/admin:

**Disable key expiry** - for each VM, click the three dots next to the machine and select Disable key expiry. Without this the VM drops off the Tailscale network after 90 days.

**Disable MagicDNS** - go to the DNS tab and turn off MagicDNS. This prevents Tailscale from overwriting `/etc/resolv.conf` and conflicting with AdGuard.

## Prevent DNS Overwriting

Tell Tailscale not to manage DNS:

```bash
sudo tailscale up --accept-dns=false
```

## Firewall

If ufw is active on the VM:

```bash
sudo ufw allow in on tailscale0
sudo ufw reload
```

Check if ufw is active first:

```bash
sudo ufw status
```

## Notes

- Tailscale is installed on both Core VM and Services VM
- Personal devices (laptop, phone) need the Tailscale app installed and logged into the same account for remote access
- The Tailscale admin console global nameserver should be set to the Core VM's Tailscale IP so internal domains resolve when away from home
