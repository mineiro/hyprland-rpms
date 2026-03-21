SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources
REPO_ROOT := $(abspath $(CURDIR)/../..)

.PHONY: srpm

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	spectool -g -C "$(SOURCEDIR)" "$(SPEC)"
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
