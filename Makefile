.PHONY: helptext
.PHONY: up
.PHONY: down
.PHONY: Makfile

define helptext

 Commands:

 up          Run tests with docker compose.
 down        Shut down containers.

endef

export helptext

# Help should be first so that make without arguments is the same as help
help:
	@echo "$$helptext"

up:
	@docker compose up --build --detach

down:
	@docker compose down --volumes --remove-orphans
