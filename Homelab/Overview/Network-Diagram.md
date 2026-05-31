# Network Diagram

## Physical Network

```
Internet
  |
Router (192.168.1.254)
  |
LAN (192.168.1.0/24)
  |
  +-- Proxmox Host HL-HV01P
  |     +-- Core VM HL-CORE01V (192.168.1.4)
  |     +-- Services VM (192.168.1.5)
  |     +-- HAOS VM (192.168.1.6)
  |
  +-- Other LAN devices
```

## Traffic Flow

```
External device (Tailscale)
  |
  v
Tailscale network (100.x.x.x)
  |
  v
Core VM (192.168.1.4)
  |
  v
Traefik (:443)
  |
  +-- Core VM services (Docker network)
  |     +-- AdGuard (172.20.0.x:80)
  |     +-- Portainer (172.20.0.x:9000)
  |     +-- Authentik (172.20.0.x:9000)
  |     +-- Homepage (172.20.0.x:3000)
  |
  +-- Services VM services (LAN)
        +-- Actual Budget (192.168.1.5:5006)
        +-- Wealthfolio (192.168.1.5:8088)
        +-- Wiki.js (192.168.1.5:3000)
```

## Docker Networks (Core VM)

```
traefik network (172.20.0.0/16)
  +-- traefik
  +-- adguard
  +-- portainer
  +-- authentik-server
  +-- authentik-worker
  +-- authentik-postgresql
  +-- redis
  +-- homepage
```

## DNS Flow

```
Device DNS query
  |
  v
AdGuard (192.168.1.4:53)
  |
  +-- *.lan.nathanryder.xyz -> 192.168.1.4 (local rewrite)
  |
  +-- Everything else -> 1.1.1.1 (upstream)
```

## Port Reference

See the Port Reference page for a full list of ports in use.
