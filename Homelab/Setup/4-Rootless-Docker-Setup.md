# 4. Rootless Docker Setup

Docker runs in rootless mode on both VMs. This means the Docker daemon runs as an unprivileged user rather than root, reducing the blast radius of any container escape or compromise.

## Create the Docker User

```bash
sudo adduser dockeruser
sudo usermod -aG sudo dockeruser
```

## Install Dependencies

```bash
sudo apt install -y uidmap dbus-user-session
```

## Install Docker (System Binaries)

Install Docker CE to get the binaries, then immediately disable the system daemon:

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl disable --now docker
sudo systemctl disable --now containerd
```

The binaries need to be present for rootless Docker to work, but the system-level daemon should not run.

## Install Rootless Docker

Switch to the dockeruser and run the setup tool:

```bash
su - dockeruser
dockerd-rootless-setuptool.sh install
```

If you see "systemd was not detected", make sure you SSH in as dockeruser directly rather than using `su`. User systemd sessions only fully initialise on a proper login session.

## Enable on Boot

```bash
systemctl --user enable docker
systemctl --user start docker
sudo loginctl enable-linger dockeruser
```

## Configure PATH

Add to `~/.bashrc`:

```bash
export PATH=/usr/bin:$PATH
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
```

Then reload:

```bash
source ~/.bashrc
```

## Allow Privileged Ports

Rootless Docker cannot bind to ports below 1024 by default. AdGuard needs port 53, so allow it:

```bash
echo "net.ipv4.ip_unprivileged_port_start=53" | sudo tee /etc/sysctl.d/99-unprivileged-ports.conf
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=53
```

## Docker Socket Path

The rootless Docker socket is at `/run/user/1000/docker.sock` where `1000` is the UID of dockeruser. Verify with:

```bash
id -u dockeruser
echo $DOCKER_HOST
```

All compose files that need the Docker socket must reference this path rather than `/var/run/docker.sock`.

## Known Issues

Host network mode (`network_mode: host`) does not work correctly in rootless Docker. The container does not share the true host network namespace - it gets its own user namespace instead. This affects AdGuard's ability to see real client IPs.
