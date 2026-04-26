SHELL := /bin/bash

PACKAGES_DIR := $(CURDIR)/packages
OUTDIR ?= $(CURDIR)/dist/srpm
PACKAGE ?=

.PHONY: help list check-specs check-abi-rebuilds srpm

help:
	@echo "Targets:"
	@echo "  make list"
	@echo "  make check-specs"
	@echo "  make check-abi-rebuilds [ABI_REBUILD_BASE=<ref>] [ABI_REBUILD_HEAD=<ref>]"
	@echo "  make srpm PACKAGE=<package-name> [OUTDIR=dist/srpm]"

list:
	@find "$(PACKAGES_DIR)" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort

check-specs:
	@./scripts/check-specs.sh

check-abi-rebuilds:
	@./scripts/check-abi-rebuilds.sh

srpm:
	@test -n "$(PACKAGE)" || { echo "PACKAGE is required"; exit 1; }
	@$(MAKE) -C "$(PACKAGES_DIR)/$(PACKAGE)" srpm OUTDIR="$(OUTDIR)"
