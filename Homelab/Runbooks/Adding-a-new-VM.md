---
title: Adding A New VM
description: 
published: true
date: 2026-05-31T19:50:31.341Z
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

## Setup Portainer

## Socket Proxy

## Traefik-kop for auto discovery

## Homepage auto discovery