# Reference

## IP Addresses

| Host          | IP            | Hostname    |
| ------------- | ------------- | ----------- |
| Router        | 192.168.1.254 |             |
| Proxmox host  | 192.168.1.3   | HL-HV01P    |
| Core VM       | 192.168.1.4   | HL-CORE01V  |
| Services VM   | 192.168.1.5   | HL-SRV01V   |
| HAOS VM       | 192.168.1.6   |             |
| External Dedi | 192.99.0.159  | SYS-MISC01P |

## Domain Reference

| Service        | URL                                            | VM       | Auth                            |
| -------------- | ---------------------------------------------- | -------- | ------------------------------- |
| Homepage       | https://homepage.lan.nathanryder.xyz           | Core     | None                            |
| Traefik        | https://traefik.lan.nathanryder.xyz/dashboard/ | Core     | Authentik forward auth          |
| AdGuard        | https://adguard.lan.nathanryder.xyz            | Core     | Authentik forward auth          |
| Portainer      | https://portainer.lan.nathanryder.xyz          | Core     | Authentik OIDC                  |
| Authentik      | https://auth.lan.nathanryder.xyz               | Core     |                                 |
| Wiki.js        | https://wiki.lan.nathanryder.xyz               | Services | Authentik OIDC                  |
| Actual Budget  | https://actual-budget.lan.nathanryder.xyz      | Services | Authentik OIDC                  |
| Wealthfolio    | https://wealthfolio.lan.nathanryder.xyz        | Services | Authentik forward auth          |
| Home Assistant | https://homeassistant.lan.nathanryder.xyz      | HAOS     | Authentik OIDC                  |
| Proxmox        | https://proxmox.lan.nathanryder.xyz            | Host     | Authentik OIDC + local fallback |

## Port Reference (Core VM)

| Port | Protocol | Service | Notes |
|---|---|---|---|
| 53 | TCP/UDP | AdGuard | DNS |
| 80 | TCP | Traefik | HTTP, redirects to 443 |
| 443 | TCP | Traefik | HTTPS |
| 8000 | TCP | Portainer | Edge agent communication |
| 8080 | TCP | AdGuard | Web UI (mapped from container port 80) |
| 6379 | TCP | Redis | Not exposed externally, Docker network only |
| 9000 | TCP | Portainer | Internal HTTP (not exposed, Traefik routes to it) |
| 9443 | TCP | Portainer | Internal HTTPS (not used, HTTP enabled instead) |

## Port Reference (Services VM)

| Port | Protocol | Service         | Notes                                |
| ---- | -------- | --------------- | ------------------------------------ |
| 2375 | TCP      | Socket Proxy    | Read-only Docker API for Homepage    |
| 3000 | TCP      | Wiki.js         |                                      |
| 5006 | TCP      | Actual Budget   |                                      |
| 8088 | TCP      | Wealthfolio     |                                      |
| 9001 | TCP      | Portainer Agent | Edge agent (if using standard agent) |

## Direct Access (Bypasses Traefik)

| Service        | URL                      | Notes                             |
| -------------- | ------------------------ | --------------------------------- |
| Proxmox        | https://192.168.1.3:8006 | Always accessible, local auth     |
| AdGuard        | http://192.168.1.4:8080  | Fallback if Traefik is down       |
| Portainer      | http://192.168.1.4:8000  | Edge agent port, also fallback UI |

