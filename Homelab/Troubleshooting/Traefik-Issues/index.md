# Traefik Issues

## Redis Provider Errors

**Symptom:** Traefik logs show `the WatchTree channel is closed` or `EOF` errors for the Redis provider.

**Cause:** The connection between Traefik and Redis dropped temporarily. Traefik reconnects automatically.

**Impact:** During the reconnection window, Services VM routes may be temporarily unavailable. Routes are restored once the connection is re-established and Traefik re-reads the keys.

**Fix:** Usually self-resolving. If persistent, check Redis is healthy:

```bash
docker ps | grep redis
docker logs redis 2>&1 | tail -20
```

And check both containers are on the `traefik` network:

```bash
docker network inspect traefik | grep -E "redis|traefik"
```

---

## Service Not Appearing in Dashboard

**Symptom:** A newly deployed service does not appear in the Traefik dashboard despite labels being correct.

**For Core VM services:**
- Check the container is on the `traefik` Docker network
- Check `traefik.enable=true` label is present
- Check Traefik logs for any label parsing errors

**For Services VM services:**
- Check traefik-kop published the route: `docker exec redis redis-cli keys "*servicename*"`
- Check the route values are correct: `docker exec redis redis-cli get "traefik/http/routers/servicename/rule"`
- Redis routes may take a few seconds to appear in the Traefik dashboard after publication

Restarting Traefik forces a re-read of all Redis keys if routes are not appearing:

```bash
docker restart traefik
```

---

## Certificate Issues

**Symptom:** Browser shows certificate error or Traefik logs show ACME errors.

**Common causes:**

1. **Cloudflare API token invalid** - check the token has `Edit zone DNS` permission for `nathanryder.xyz`. Regenerate if needed and update the Portainer environment variable.

2. **Rate limit hit** - Let's Encrypt limits failed validation attempts to 5 per hour and 50 certificates per registered domain per week. Wait before retrying.

3. **acme.json permissions** - the file must be readable/writable by Traefik. Check the `traefik_certs` volume is intact.

4. **DNS propagation** - the Cloudflare TXT record for the DNS challenge may not have propagated yet. Traefik uses `1.1.1.1` and `8.8.8.8` as resolvers for the challenge - check the TXT record is visible on those resolvers.

---

## 502 Bad Gateway

**Symptom:** Traefik returns 502 Bad Gateway for a service.

**Cause:** Traefik cannot reach the backend service.

**Checklist:**

1. Is the container running? `docker ps | grep servicename`
2. Is it on the right network (for Core VM services)? `docker network inspect traefik | grep servicename`
3. Is the port correct in the labels?
4. For Services VM services - is the port exposed? `docker ps | grep servicename` (check PORTS column)
5. Can Traefik reach the backend? For Services VM: `curl -v http://192.168.1.5:PORT`

---

## Dashboard 404

**Symptom:** `https://traefik.lan.nathanryder.xyz` returns 404.

**Cause:** The dashboard route requires the `/dashboard/` path with a trailing slash. Accessing without it returns 404.

**Fix:** Access via `https://traefik.lan.nathanryder.xyz/dashboard/`. The redirect middleware in the dashboard dynamic config should handle redirecting the root path automatically. If the redirect is not working, check the dynamic config is loaded correctly:

```bash
docker exec traefik ls /etc/traefik/dynamic/
docker exec traefik cat /etc/traefik/dynamic/traefik-dashboard.yml
```
