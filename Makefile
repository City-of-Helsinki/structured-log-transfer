.PHONY: helptext
.PHONY: up
.PHONY: down
.PHONY: Makfile

define helptext

 Commands:

 up1/up      Run testing configuation 1 with docker compose.
 up2         Run testing configuation 2 with docker compose.
 down        Shut down containers.

endef

export helptext

# Help should be first so that make without arguments is the same as help
help:
	@echo "$$helptext"

up:
	@docker compose --profile test-1 up --build --detach

up1: up

up2:
	@docker compose --profile test-2 up --build --detach

down:
	@docker compose --profile test-1 --profile test-2 down --volumes --remove-orphans
