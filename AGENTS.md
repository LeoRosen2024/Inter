# Inter project workflow

## Source of truth

- Write and edit all source code in `C:\Users\0000\Projects\Inter`.
- Treat the local Git repository as the working copy and GitHub `LeoRosen2024/Inter` branch `main` as the shared source of truth.
- Never edit application code directly on the server.
- Never commit passwords, SSH keys, API tokens, `.env` files, or other secrets.

## Required delivery flow

1. Make changes locally in `C:\Users\0000\Projects\Inter`.
2. Test the changes locally.
3. Review `git status` and the intended diff.
4. Commit and push the verified result directly to GitHub `main` when access permits.
5. If direct push to `main` is unavailable, commit the work on a separate branch and open a Pull Request targeting `main`.
6. Let the active deployment platform publish the exact `main` revision. Cloudflare Pages is the current platform; the prepared VPS workflow remains inactive until a VPS is connected.
7. Verify the deployed public page after publication.

## Deployment architecture

- The project runs in its own Docker Compose project named `inter`.
- The web container is named `inter-web` and serves the static site with Caddy.
- Until a domain is connected, expose the site on server port `8080` by default.
- The server checkout lives at `/opt/inter`.
- Server deployments must use `git pull --ff-only`; deployment must stop if the server checkout has diverged or contains conflicting edits.
- Every deployment rebuilds the image and recreates only this project's containers.

## Verification

- Before push: check the page, navigation, desktop layout, and mobile layout.
- After deployment: require a successful HTTP response from Cloudflare Pages. When VPS deployment is activated, also require a healthy `inter-web` container.
- Report the local commit, GitHub push, deployment result, and public/test URL separately.
