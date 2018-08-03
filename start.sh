#!/bin/sh
docker run -d  \
--restart=always \
--name=githubrobot \
-p 20886:80 \
-v $(pwd):/webhook \
-e GITHUB_TOKEN="" \
webhook:local
