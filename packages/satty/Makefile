SHELL := /bin/bash

SPEC ?= $(firstword $(wildcard *.spec))
OUTDIR ?= $(CURDIR)/../../dist/srpm
SOURCEDIR ?= $(CURDIR)/sources

.PHONY: srpm

srpm:
	@test -n "$(SPEC)" || { echo "No .spec file found"; exit 1; }
	@mkdir -p "$(OUTDIR)" "$(SOURCEDIR)"
	spectool -g -C "$(SOURCEDIR)" "$(SPEC)"
	@if grep -q '%cargo_prep' "$(SPEC)" && rpmspec -P "$(SPEC)" | grep -q '^Source1:'; then \
		vendor_name="$$(rpmspec -P "$(SPEC)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		src0_name="$$(rpmspec -P "$(SPEC)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		tmpdir="$$(mktemp -d)"; \
		srcdir=""; \
		trap 'rm -rf "$$tmpdir"' EXIT; \
		tar -xf "$(SOURCEDIR)/$$src0_name" -C "$$tmpdir"; \
		srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
		[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
		( cd "$$srcdir" && cargo vendor --locked vendor >/dev/null ); \
		tar -cJf "$(SOURCEDIR)/$$vendor_name" -C "$$srcdir" vendor; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	rpmbuild -bs \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(CURDIR)" \
		--define "_builddir $(CURDIR)" \
		--define "_srcrpmdir $(OUTDIR)" \
		--define "_rpmdir $(CURDIR)" \
		--define "_buildrootdir $(CURDIR)/.build" \
		"$(SPEC)"
