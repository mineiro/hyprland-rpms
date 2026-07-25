SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources
REPO_ROOT := $(abspath $(CURDIR)/../..)

.PHONY: srpm

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	@if [ -x ./prepare-sources.sh ]; then \
		./prepare-sources.sh "$(SPEC)" "$(SOURCEDIR)"; \
	fi
	@if rpmspec -P "$(SPEC)" | awk '/^Source[0-9]*:[[:space:]]*/ { print $$2 }' | grep -Eq '^(https?|ftp)://'; then \
		spectool -g -C "$(SOURCEDIR)" "$(SPEC)"; \
	fi
	@if [ -d ./patches ]; then \
		find ./patches -maxdepth 1 -type f ! -name '.gitkeep' -exec cp -a {} "$(SOURCEDIR)/" \; ; \
	fi
	@vendor_subdir="$$(awk -F= '/^GO_VENDOR_SUBDIR=/{print $$2}' ./package.env 2>/dev/null || true)"; \
	if [ -n "$$vendor_subdir" ]; then \
		"$(REPO_ROOT)/scripts/prepare-go-vendor.sh" "$(SPEC)" "$(SOURCEDIR)" "$$vendor_subdir"; \
	fi
	rpmbuild -bs \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(CURDIR)" \
		--define "_builddir $(CURDIR)" \
		--define "_srcrpmdir $(OUTDIR)" \
		--define "_rpmdir $(CURDIR)" \
		--define "_buildrootdir $(CURDIR)/.build" \
		"$(SPEC)"
