FROM caddy:2.10-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html styles.css app.js /srv/

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --spider http://127.0.0.1/ || exit 1
