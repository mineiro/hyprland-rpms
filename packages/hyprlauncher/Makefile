SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources

.PHONY: srpm

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	spectool -g -C "$(SOURCEDIR)" "$(SPEC)"
	@if ls "$(CURDIR)"/patches/*.patch >/dev/null 2>&1; then \
		cp -f "$(CURDIR)"/patches/*.patch "$(SOURCEDIR)"/; \
	fi
	@if ls "$(CURDIR)"/patches/*.diff >/dev/null 2>&1; then \
		cp -f "$(CURDIR)"/patches/*.diff "$(SOURCEDIR)"/; \
	fi
	rpmbuild -bs \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(CURDIR)" \
		--define "_builddir $(CURDIR)" \
		--define "_srcrpmdir $(OUTDIR)" \
		--define "_rpmdir $(CURDIR)" \
		--define "_buildrootdir $(CURDIR)/.build" \
		"$(SPEC)"
