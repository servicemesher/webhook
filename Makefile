REPO := jimmysong/isito-official-translation-webhook
TAG := 2019-11-14

.PHONY: build push

.PHONY: build
build:
	docker build -t $(REPO):$(TAG) .

.PHONY: push
clean:
	docker push $(REPO):$(TAG)
