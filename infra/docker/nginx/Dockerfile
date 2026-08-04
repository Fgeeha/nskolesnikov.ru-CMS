# syntax=docker/dockerfile:1
FROM nginx:1.27-alpine

# The official image renders /etc/nginx/templates/*.template with envsubst at
# start-up. The filter keeps Nginx's own $variables untouched.
ENV NGINX_ENVSUBST_FILTER="NGINX_" \
    NGINX_SERVER_NAME="_"

COPY infra/nginx/default.conf.template /etc/nginx/templates/default.conf.template

RUN rm -f /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --spider http://127.0.0.1/nginx-health || exit 1
