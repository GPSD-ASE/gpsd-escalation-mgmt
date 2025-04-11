NAMESPACE = gpsd
DEPLOYMENT = gpsd-escalation-mgmt
SERVICE_NAME = $(DEPLOYMENT)
IMAGE_NAME = $(NAMESPACE)/$(DEPLOYMENT)
CHART_DIRECTORY = helm
REMOTE_CHART_REPOSITORY = gpsd-ase.github.io
VERSION := $(shell grep "version:" helm/Chart.yaml | head -1 | sed 's/version: //')

# Docker commands
.PHONY: docker build-image push-image run-image clean-image
docker: build-image push-image

build-image:
	@echo "Building Docker image $(IMAGE_NAME):v$(VERSION)..."
	docker build -f Dockerfile -t $(IMAGE_NAME):v$(VERSION) --platform linux/amd64 .

push-image:
	@echo "Pushing Docker image $(IMAGE_NAME):v$(VERSION)..."
	docker push $(IMAGE_NAME):v$(VERSION)

run-image:
	@echo "Running Docker image $(IMAGE_NAME):v$(VERSION)..."
	docker network create gpsd-network || true
	docker run -d --name mock-vault --network gpsd-network -p 8200:8200 hashicorp/vault:latest server -dev -dev-root-token-id=root
	docker run -p 7134:7134 --network gpsd-network -e VAULT_ADDR=http://mock-vault:8200 -e VAULT_TOKEN=root $(IMAGE_NAME):v$(VERSION)

clean: clean-container clean-network clean-image 

clean-image:
	@echo "Cleaning dangling Docker images..."
	docker rmi $(docker images --filter "dangling=true" -q) -f

clean-network:
	@echo "Cleaning Docker network..."
	docker network rm gpsd-network

clean-container:
	@echo "Cleaning Docker container..."
	docker rm -f mock-vault $(DEPLOYMENT)

compose-up:
	docker-compose up -d --build

compose-down:
	docker-compose down

compose-logs:
	docker-compose logs -f

compose-restart:
	docker-compose down && docker-compose up -d

compose-rebuild:
	docker-compose down && docker-compose up -d --build

# Test commands
.PHONY: test test-coverage test-verbose

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ -v --cov=app --cov-report=html:coverage/
	@echo "Coverage report generated at coverage/ dir."

test-verbose:
	pytest -vs

test-package:
	@echo "Running tests for package: $(PKG)"
	pytest tests/$(PKG) -v

test-clean:
	rm -rf coverage/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Linting commands
.PHONY: lint-black lint-isort
lint: lint-black lint-isort
lint-black:
	pip install black
	@echo "Checking with black..."
	black --check ./ middleware/ routes/ services/
lint-fix:
	@echo "Running black..."
	black ./ middleware/ routes/ services/
lint-isort:
	pip install isort
	@echo "Running isort..."
	isort --check-only ./ middleware/ routes/ services/

# Kubernetes commands
.PHONY: helm helm-uninstall helm-clean
develop: helm-uninstall build-image push-image helm

helm:
	@echo "Upgrading/Installing $(DEPLOYMENT) Helm chart..."
	helm upgrade --install $(DEPLOYMENT) ./helm --set image.tag=v$(VERSION) --namespace $(NAMESPACE)

helm-lint:
	@echo "Linting Helm chart..."
	helm lint ./$(CHART_DIRECTORY)
	helm template ./$(CHART_DIRECTORY) --set image.tag=v$(VERSION) --namespace $(NAMESPACE) > /dev/null

helm-uninstall:
	@echo "Uninstalling $(DEPLOYMENT) from Kubernetes..."
	helm uninstall demo -n $(NAMESPACE) || true

helm-clean:
	@echo "Cleaning up all resources in the $(NAMESPACE) namespace..."
	kubectl delete all --all -n $(NAMESPACE) || true
	kubectl delete namespace $(NAMESPACE) || true
	sleep 2

# Release and versioning
.PHONY: release bump-version update-changelog
release: update-changelog bump-version build-push

update-changelog:
	@echo "Updating changelog..."
	./scripts/update-changelog.sh

bump-version:
	@echo "Bumping version..."
	./scripts/bump-version.sh

build-push:
	@echo "Building and pushing Docker image $(IMAGE_NAME):v$(VERSION)..."
	docker build -t $(IMAGE_NAME):v$(VERSION) -t $(IMAGE_NAME):latest .
	docker push $(IMAGE_NAME):v$(VERSION)
	docker push $(IMAGE_NAME):latest

# GitHub Pages and Helm chart publishing
.PHONY: gh-pages-publish helm-repo-update

gh-pages-publish:
	@echo "Publishing Helm chart for $(SERVICE_NAME) to GitHub Pages..."
	rm -rf /tmp/$(NAMESPACE)/*
	mkdir -p /tmp/$(NAMESPACE)/
	helm package ./$(CHART_DIRECTORY) -d /tmp/$(NAMESPACE)/
	helm repo index /tmp/$(NAMESPACE)/ --url https://$(REMOTE_CHART_REPOSITORY)/$(SERVICE_NAME)/ --merge /tmp/$(NAMESPACE)/index.yaml
	git checkout gh-pages || git checkout -b gh-pages
	cp /tmp/$(NAMESPACE)/* .
	ls .
	git status
	git add .
	git commit -m "chore: update Helm chart to v$(VERSION)"
	git push origin gh-pages
	git checkout main

helm-repo-update:
	@echo "Adding and updating Helm repo for $(SERVICE_NAME)..."
	helm repo add $(SERVICE_NAME) https://$(REMOTE_CHART_REPOSITORY)/$(SERVICE_NAME)/
	helm repo update
	helm repo list

refresh:
	git fetch && git pull origin main --rebase