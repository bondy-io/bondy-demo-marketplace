.PHONY: all
all: bondy_docker market

.PHONY: bondy_docker
bondy_docker:
	docker ps | grep bondy-demo > /dev/null \
	|| docker run \
		-e BONDY_ERL_NODENAME=bondy1@127.0.0.1 \
		-e BONDY_ERL_DISTRIBUTED_COOKIE=bondy \
		-p 18080:18080 \
		-p 18081:18081 \
		-p 18082:18082 \
		-p 18086:18086 \
		-u 0:1000 \
		--name bondy-demo \
		-v "${PWD}/bondy/etc:/bondy/etc" \
		-d leapsight/bondy:1.0.0-beta.64

.PHONY: shutdown
shutdown:
	docker rm -fv bondy-demo

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
