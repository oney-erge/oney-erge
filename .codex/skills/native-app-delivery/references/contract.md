# Install and Run Contract

## Public command surface

Use the closest platform-native root entry points supported by the product:

- Windows: `run.bat` for double-click and `run.ps1` for terminals.
- macOS: `run.command` for double-click and `run.sh` for terminals.
- Linux: `run.sh`.

The default action is `run`. Support the following actions when they apply:

- `run`: install or repair missing runtime pieces, start or reuse the app, wait
  for readiness, then open the UI.
- `doctor`: report actionable platform, dependency, configuration, port,
  hardware, and service status without changing state.
- `repair`: rebuild package-owned runtime state while preserving user state.
- `docker`: start the Compose profile, wait for health, then open or print the
  UI URL.
- `stop`: stop only processes or containers managed by the product.
- `logs`: show where logs live or stream the relevant log.

Also preserve `--no-browser` and `--non-interactive` where meaningful.

Use plain names for repository plumbing:

- Shared helper code: `scripts/install-utils.ps1` and
  `scripts/install-utils.sh`.
- Install state and persistent failures: `.setup/install.log`.
- Do not expose the internal skill name in product copy or public READMEs.

## Bootstrap and state

For Python applications, prefer this order:

1. A working pinned `uv` already available.
2. A verified or official pinned standalone uv installer.
3. A second built-in downloader.
4. An existing platform package manager only when the required downloader or
   external application is absent.

Let uv provide the declared Python version. Keep the environment inside the
application or its per-user data directory. Compute a fingerprint from the
runtime lock, project metadata, selected extras, installer version, and relevant
platform profile. Skip synchronization only when both the fingerprint and a
runtime smoke check pass.

Keep package-owned state distinct from user-owned state. Repair may replace an
environment, generated frontend, or downloaded application payload. It must not
delete local configuration, credentials, databases, model caches, inputs,
outputs, run histories, or user workspaces.

## Failure behavior

- Acquire a per-install lock so two launchers cannot modify the same runtime.
- Retry transient downloads and registry operations at most three times with
  increasing delays. Preserve partial downloads only when the downloader can
  resume them safely.
- Verify release archives before extraction and extract to a temporary
  directory before atomic promotion.
- Check disk space before large optional downloads.
- If the configured port contains this product and its health contract passes,
  reuse it. If the port belongs to something else, choose a safe alternate when
  the product supports dynamic ports or stop with an actionable error.
- Write a persistent installer log and show its exact location on failure.
- A browser opener failure does not make a healthy server fail. Print the URL.

## Docker contract

Every runnable application should have a valid Docker path even when native
execution is preferred:

- Multi-stage build when build tooling is not needed at runtime.
- Trusted, versioned base image, pinned by digest for release-critical images.
- Non-root runtime user where the application permits it.
- `.dockerignore`, health check, loopback-only published port, and explicit
  persistent volumes.
- CPU-capable default Compose service. Put NVIDIA access in an overlay or
  profile. Do not imply that CPU and GPU performance are equivalent.
- Secrets come from environment or mounted files, never image layers.
- Publish amd64 and arm64 only when dependencies are actually compatible and
  tested. State architecture limits otherwise.

`docker` action should detect `docker compose`, report when the engine is not
running, start the service, wait for container health, and open or print the UI.
It should not silently install Docker Desktop or GPU drivers.

## Release and verification

Public releases should contain the fully built runtime payload required by an
end user. Attach SHA-256 checksums and build provenance when supported. Keep
source packages, Python distributions, containers, and native installers
clearly labeled.

Minimum acceptance checks:

1. Clean Windows, macOS, and Linux first run for every claimed platform.
2. A second run skips installation and reaches readiness.
3. A dependency input change triggers synchronization.
4. A damaged package-owned environment repairs without losing user state.
5. A simulated transient download failure exercises the fallback path.
6. Readiness precedes browser opening.
7. An unrelated port owner is preserved.
8. A first successful installation can start offline when the product permits.
9. Compose validates, the image builds, and the container becomes healthy.
10. Release artifacts install and run outside the source checkout.

Run `python scripts/audit_install_run.py <repository>` from this skill for the
fast structural gate. It does not replace product-specific readiness checks or
clean-machine testing.
