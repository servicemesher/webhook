#!/bin/sh
docker run -d  \
--restart=always \
--name=githubrobot \
-p 20886:8808 \
-v $(pwd):/webhook \
-e GITHUB_TOKEN="" \
jimmysong/istio-official-translation-webhook:2019-11-14
