# 13. Actual Budget Setup

Actual Budget runs on the Services VM. It supports native OIDC with Authentik but requires users to be pre-created in Actual Budget before OIDC login works.

## Compose File

Location: `docker/actual-budget/docker-compose.yml` (on Services VM)

`ACTUAL_OPENID_ENFORCE=false` keeps password login available as a fallback alongside OIDC.

## Initial Setup

On first access, Actual Budget prompts for a password to create a local admin account. Set a strong password and save it - this is the fallback if Authentik is unavailable.

## Pre-Creating the OIDC User

Actual Budget does not auto-provision users on first OIDC login. The user must exist in Actual Budget before attempting OIDC login or it will fail with a password error.

After the initial password setup:

1. Log in with the local password
2. Go to Server online -> User Directory (or Settings -> Users depending on version)
3. Create a user matching the Authentik username
4. Log out and test OIDC login
