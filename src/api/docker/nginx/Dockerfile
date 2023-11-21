FROM nginx:latest

COPY nginx.conf.template /etc/nginx/conf.d/nginx.conf.template
COPY proxy_params /etc/nginx

CMD /bin/bash -c "envsubst '\$PROJECT_DIR' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"
