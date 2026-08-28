# Inter deployment

The application is served by Caddy in a dedicated Docker container. The default test address is:

```text
http://SERVER_IP:8080
```

## Server prerequisites

- A Linux server with a public IP address
- SSH access for a non-root deployment user
- Git
- Docker Engine with the Compose plugin
- Firewall access to TCP port `8080` during the pre-domain stage

## One-time server setup

1. Create `/opt/inter` and give the deployment user ownership.
2. Add a read-only GitHub deploy key for `LeoRosen2024/Inter` to the server.
3. Clone the repository into `/opt/inter`.
4. Make `scripts/deploy.sh` executable.
5. Run `docker compose up -d --build` once.

## GitHub Actions secrets

Configure these repository environment secrets for the `production` environment:

- `DEPLOY_HOST`: server IP or hostname
- `DEPLOY_PORT`: SSH port, normally `22`
- `DEPLOY_USER`: non-root deployment user
- `DEPLOY_SSH_KEY`: private SSH key used only by GitHub Actions to connect to the server
- `DEPLOY_KNOWN_HOSTS`: verified SSH host-key line for the server

The matching public key must be present in the deployment user's `~/.ssh/authorized_keys` on the server.

After the first successful manual deployment, set the repository variable
`DEPLOY_ENABLED` to `true`. Until then, pushes remain safe and the deploy job is
skipped instead of failing with missing server credentials.

## Normal workflow

Every push to `main` runs `.github/workflows/deploy.yml`. The server performs a fast-forward-only pull, rebuilds `inter-web`, and verifies `http://127.0.0.1:8080/` before the workflow succeeds.
