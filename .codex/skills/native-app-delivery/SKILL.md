---
name: native-app-delivery
description: Standardize native install, run, repair, and Docker delivery for local applications. Use when a repository needs a clean-machine launcher, cross-platform first-run UX, idempotent reruns, Docker support, installer hardening, or public release packaging. Do not force browser or container behavior onto libraries that have no runnable application.
---

# Native App Delivery

Give each runnable repository one recognizable lifecycle while preserving its real
platform, hardware, licensing, and authentication limits.

## Workflow

1. Read the repository instructions and inspect existing launchers, locks,
   health endpoints, process ownership, Docker assets, release workflows, and
   supported platforms before changing anything.
2. Read [references/contract.md](references/contract.md) before designing or
   changing end-user install, run, repair, Docker, or release behavior.
3. Reuse the repository's strongest existing lifecycle logic. Put the shared
   command surface in thin root entry points and keep product-specific work in
   the repository's existing scripts or packaging layer.
4. Make the normal path reach the first useful local state. Large model pulls,
   GPU drivers, Docker Desktop, license acceptance, credentials, and provider
   sign-in remain explicit user decisions.
5. Verify syntax, first-run behavior, idempotent rerun, dependency-change
   repair, readiness, process cleanup, and Docker health in proportion to the
   repository's risk and available platforms.

## Durable Rules

- Prefer a pinned standalone `uv` bootstrap for Python applications so Python
  does not need to be preinstalled. Use frozen runtime locks, not development
  extras, for end users.
- Retry only transient network operations, with bounded backoff. Never retry or
  bypass bad checksums, rejected licenses, invalid credentials, unsupported
  hardware, permission denial, or insufficient disk space.
- Open a browser only after the application health check succeeds. Reuse an
  existing healthy instance. Never kill an unrelated process that merely owns
  the desired port.
- Preserve user configuration, data, models, outputs, and caches during repair
  and update. Track dependency inputs so reruns skip valid environments and
  refresh stale ones.
- Bind local web applications to loopback by default. Containers should run
  non-root when practical, declare health checks, persist state in explicit
  volumes, and separate CPU defaults from optional GPU overlays.
- Do not call source archives, wheels, ZIP folders, or unsigned binaries an
  installer unless the user experience actually installs the application.
- Do not publish, tag, push, create a release, install system software, or
  change credentials unless the current request authorizes it.
