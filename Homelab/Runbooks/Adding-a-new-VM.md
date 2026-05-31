---
title: Adding A New VM
description: 
published: true
date: 2026-05-31T20:31:22.171Z
tags: 
editor: markdown
dateCreated: 2026-05-31T19:30:41.005Z
---

## Set hostname
`sudo hostnamectl set-hostname HL-OBS01V`

Update /etc/hosts with the new hostname

## Set static ip

Add the netconfig to /etc/netplan/50-cloud-init.yaml
```yaml
network:
  version: 2
  ethernets:
    eth0:
      match:
        macaddress: "MAC_ADDRESS"
      addresses: [STATIC_IP/24]
      gateway4: GATEWAY
      dhcp4: false
      set-name: "eth0"
```

Then apply the configuration: `netplan apply`

## Tailscale configuration

Follow steps in [Tailscale Setup](https://wiki.lan.nathanryder.xyz/en/Homelab/Setup/3-Tailscale-Setup)

## Setup rootless Docker

Follow steps in [Rootless Docker Setup](https://wiki.lan.nathanryder.xyz/en/Homelab/Setup/4-Rootless-Docker-Setup)

## Setup Portainer

Follow steps in [Portainer Setup](https://wiki.lan.nathanryder.xyz/en/Homelab/Setup/7-Portainer-Setup)

## Traefik-kop for auto discovery

Deploy `/docker/traefik-kop/docker-compose.yml` using portainer

Detailed information on traefik-kop setup available on the [Traefik-kop Setup Page](https://wiki.lan.nathanryder.xyz/en/Homelab/Setup/9-traefik-kop-Setup)

## Socket Proxy


## Homepage auto discovery