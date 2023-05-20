FROM jwilder/nginx-proxy:0.9
COPY static/css/attach_file.css /home/app/web/staticfiles/attach_file.css
COPY vhost.d/default /etc/nginx/vhost.d/default
COPY custom.conf /etc/nginx/conf.d/custom.conf
