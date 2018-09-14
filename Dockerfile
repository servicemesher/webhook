FROM alpine
RUN  apk add --update --no-cache python3 && \
  pip3 install github-webhook PyGithub && \
  mkdir /webhook
COPY webhook.py /webhook
#VOLUME [ "/webhook" ]
#CMD "/webhook/webhook.py"
