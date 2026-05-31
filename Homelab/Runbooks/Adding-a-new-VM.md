---
title: Adding A New VM
description: 
published: true
date: 2026-05-31T19:30:41.005Z
tags: 
editor: markdown
dateCreated: 2026-05-31T19:30:41.005Z
---

## Set hostname
`hostname HL-OBS01V`

## Set static ip

Add the netconfig to /etc/cloud/cloud.cfg.d/10-netcfg.cfg
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