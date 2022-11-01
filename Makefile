include .env
export

.PHONY: all
all: bondy_docker webapp_docker market

.PHONY: bondy_docker
bondy_docker:
	@echo "Removing existing bondy-demo container"
	docker stop bondy-demo || true
	docker rm -fv bondy-demo || true
	docker run \
		-e BONDY_ERL_NODENAME=bondy1@127.0.0.1 \
		-e BONDY_ERL_DISTRIBUTED_COOKIE=bondy \
		--env-file .env \
		-p 18080:18080 \
		-p 18081:18081 \
		-p 18082:18082 \
		-p 18086:18086 \
		-u 0:1000 \
		--name bondy-demo \
		-v "${PWD}/bondy/etc:/bondy/etc" \
		-d leapsight/bondy:1.0.0-beta.64

.PHONY: webapp_docker
webapp_docker:
	@echo "Removing existing bondy-marketplace-webapp container"
	docker stop bondy-marketplace-webapp || true
	docker rm -fv bondy-marketplace-webapp || true
	docker build --load -t bondy-marketplace-webapp ./webapp
	docker run \
		-p 8080:80 \
		--name bondy-marketplace-webapp \
		-d bondy-marketplace-webapp

.PHONY: demo_docker
demo_docker:
	docker compose -f docker-compose.yml up -d --force-recreate

.PHONY: shutdown
shutdown:
	# From local runs
	docker rm -fv bondy-demo
	docker rm -fv bondy-marketplace-webapp
	# From docker compose
	docker compose -f docker-compose.yml rm --stop --force

.PHONY: clear
clear:
	docker compose -f docker-compose.yml down --rmi local --timeout 0
	docker image prune --force

VENV?=venv-market

.PHONY: market
market: ${VENV}
	source venv/${VENV}/bin/activate; \
		python3 market.py

.PHONY: client
client: ${VENV}
	source venv/${VENV}/bin/activate; \
		python3 client.py

BOT_NAME?=Bob
BOT_INCR?=1
BOT_LIMIT?=10
BOT_LAG?=5

.PHONY: bot
bot: ${VENV}
	source venv/${VENV}/bin/activate; \
		python3 bot.py ${BOT_NAME} ${BOT_INCR} ${BOT_LIMIT} ${BOT_LAG}

.PHONY: many_bots
many_bots: ${VENV}
	source venv/${VENV}/bin/activate; \
		python3 bot.py Alice 3 10000 0.3& \
		python3 bot.py Tom 5 10000 0.5& \
		python3 bot.py Mary 7 10000 0.7& \
		python3 bot.py Victor 11 10000 1.1&

PIP_REQS_FILE:=pip_reqs.txt

.PHONY: ${VENV}
${VENV}: venv/${VENV}/touch-file
venv/${VENV}/touch-file: ${PIP_REQS_FILE}
ifeq (,$(shell which python3))
	$(error "No python3 executable found in PATH; install or update PATH")
endif
	[[ -d venv/${VENV} ]] || python3 -m venv venv/${VENV}
	source venv/${VENV}/bin/activate; pip install --upgrade pip
	source venv/${VENV}/bin/activate; pip install -r ${PIP_REQS_FILE}
	touch venv/${VENV}/touch-file
