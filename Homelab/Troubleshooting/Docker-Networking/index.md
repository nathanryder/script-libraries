# Docker Networking Issues

## Rootless Docker Limitations

Rootless Docker has several networking limitations compared to root Docker:

**Host network mode does not work as expected.** The container gets its own user network namespace rather than sharing the true host network namespace. Containers in host mode cannot see host interfaces like `192.168.1.4`. They only see loopback and their own container network interfaces.

**macvlan and ipvlan are not supported.** These modes require kernel capabilities (`CAP_NET_ADMIN`, `CAP_SYS_ADMIN`) that rootless Docker does not have. Attempts to create macvlan or ipvlan networks fail with permission errors.

**Workaround for host mode:** Use bridge networking with explicit port mappings instead. Rootlesskit handles the port forwarding transparently.

---

## Port Binding Issues

**Symptom:** Container starts but ports are not accessible, or `ss -tlnp` shows no listener on the expected port.

**Common causes:**

1. **Unprivileged port restriction** - ports below 1024 cannot be bound by non-root processes by default. Check:
   ```bash
   cat /proc/sys/net/ipv4/ip_unprivileged_port_start
   ```
   If it shows `1024`, apply the fix:
   ```bash
   sudo sysctl -w net.ipv4.ip_unprivileged_port_start=53
   ```

2. **network_mode: host with ports:** - port mappings are silently ignored in host network mode. Remove the `ports:` section when using host mode, or switch to bridge mode.

3. **Portainer creating a default network** - when deploying via Portainer, it may create a stack-scoped network (e.g. `adguard_network`) that interferes with port bindings. Add `network_mode: bridge` to force the default bridge network, or define explicit networks.

---

## Cross-VM Routing

**Symptom:** Traefik returns 502 Bad Gateway for Services VM services.

**Cause:** Traefik cannot reach the container on the Services VM.

**Checklist:**

1. Check the container has `ports:` defined in its compose file - Services VM containers must expose ports on the host for Traefik to reach them.

2. Check what URL traefik-kop registered:
   ```bash
   docker exec redis redis-cli get "traefik/http/services/servicename/loadBalancer/servers/0/url"
   ```
   Should show `http://192.168.1.5:PORT`.

3. Test the connection from Core VM directly:
   ```bash
   curl -v http://192.168.1.5:PORT
   ```

4. Check traefik-kop logs for the service:
   ```bash
   docker logs traefik-kop 2>&1 | grep -i servicename
   ```

5. Check the `BIND_IP` environment variable in traefik-kop is set to the Services VM's LAN IP (`192.168.1.5`).

---

## Docker Socket Path

**Symptom:** Portainer, Homepage, or traefik-kop cannot connect to Docker.

**Cause:** The Docker socket path is different in rootless mode.

The rootless Docker socket is at `/run/user/UID/docker.sock` where UID is the user ID of the dockeruser. Verify:

```bash
echo $DOCKER_HOST
ls /run/user/$(id -u)/docker.sock
```

All compose files referencing the Docker socket must use this path, not `/var/run/docker.sock`.

---

## Container on Wrong Network

**Symptom:** Traefik cannot route to a Core VM container even though labels are correct.

**Cause:** The container is not on the `traefik` Docker network.

**Fix:** Add the network to the container's compose file:

```yaml
networks:
  traefik:
    external: true
```

And add the container to the network:

```yaml
services:
  myservice:
    networks:
      - traefik
```

Verify the container is on the network:
```bash
docker network inspect traefik | grep -A 3 "myservice"
```
