.PHONY: prepare srpm

# COPR passes `spec` and `outdir` when using SCM + make_srpm.
specfile = $(notdir $(spec))
repo_root = $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

prepare:
	@pkgs="rpm-build rpmdevtools"; \
	if [ -n "$(spec)" ] && grep -q '%cargo_prep' "./$(specfile)" && rpmspec -P "./$(specfile)" | grep -q '^Source1:'; then \
		pkgs="$$pkgs cargo"; \
	fi; \
	if [ -n "$(spec)" ] && grep -Eq '^[[:space:]]*BuildRequires:[[:space:]]+golang([[:space:]]|$$)' "./$(specfile)" && rpmspec -P "./$(specfile)" | grep -q '^Source1:'; then \
		pkgs="$$pkgs golang"; \
	fi; \
	dnf -y install --setopt=install_weak_deps=0 --nodocs $$pkgs

srpm: prepare
	@test -n "$(spec)" || { echo "COPR did not pass 'spec'"; exit 1; }
	@test -n "$(outdir)" || { echo "COPR did not pass 'outdir'"; exit 1; }
	@if [ -x ./prepare-sources.sh ]; then \
		./prepare-sources.sh "./$(specfile)" "$(CURDIR)"; \
	fi
	@if rpmspec -P "./$(specfile)" | awk '/^Source[0-9]*:[[:space:]]*/ { print $$2 }' | grep -Eq '^(https?|ftp)://'; then \
		spectool -g -R "./$(specfile)"; \
	fi
	@if ls ./patches/*.patch >/dev/null 2>&1; then \
		cp -f ./patches/*.patch ./; \
	fi
	@if ls ./patches/*.diff >/dev/null 2>&1; then \
		cp -f ./patches/*.diff ./; \
	fi
	@if grep -q '%cargo_prep' "./$(specfile)" && rpmspec -P "./$(specfile)" | grep -q '^Source1:'; then \
		if ! command -v cargo >/dev/null 2>&1; then \
			echo "cargo is required to generate vendored Rust sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		vendor_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source1:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
		src0_name="$$(rpmspec -P "./$(specfile)" | awk '/^Source0:[[:space:]]*/ { print $$2; exit }' | xargs basename)"; \
			tmpdir="$$(mktemp -d)"; \
			rpm_sourcedir="$$(rpm --eval '%{_sourcedir}' 2>/dev/null || true)"; \
			srcdir=""; \
			src0_path="./$$src0_name"; \
			rust_vendor_patches="$$(awk -F= '/^RUST_VENDOR_PATCHES=/{sub(/^[^=]*=/, ""); print; exit}' ./package.env 2>/dev/null || true)"; \
			source_date_epoch="$$(awk -F= '/^SOURCE_DATE_EPOCH=/{print $$2; exit}' ./package.env 2>/dev/null || true)"; \
			trap 'rm -rf "$$tmpdir"' EXIT; \
			if [ ! -f "$$src0_path" ] && [ -f "./sources/$$src0_name" ]; then \
				src0_path="./sources/$$src0_name"; \
			fi; \
			if [ ! -f "$$src0_path" ] && [ -f "./SOURCES/$$src0_name" ]; then \
				src0_path="./SOURCES/$$src0_name"; \
			fi; \
			if [ ! -f "$$src0_path" ] && [ -n "$$rpm_sourcedir" ] && [ -f "$$rpm_sourcedir/$$src0_name" ]; then \
				src0_path="$$rpm_sourcedir/$$src0_name"; \
			fi; \
			if [ ! -f "$$src0_path" ] && [ -f "$$HOME/rpmbuild/SOURCES/$$src0_name" ]; then \
				src0_path="$$HOME/rpmbuild/SOURCES/$$src0_name"; \
			fi; \
			if [ "$$src0_path" != "./$$src0_name" ]; then \
				cp -f "$$src0_path" "./$$src0_name"; \
				src0_path="./$$src0_name"; \
			fi; \
			[ -f "$$src0_path" ] || { echo "Downloaded Source0 not found for vendoring: $$src0_name"; exit 1; }; \
			if [ -f ./sources.sha256 ]; then \
				expected_sha="$$(awk -v name="$$src0_name" '$$2 == name || $$2 == "*" name { print $$1; exit }' ./sources.sha256)"; \
				[ -n "$$expected_sha" ] || { echo "No checksum recorded for $$src0_name"; exit 1; }; \
				actual_sha="$$(sha256sum "$$src0_path" | awk '{print $$1}')"; \
				[ "$$actual_sha" = "$$expected_sha" ] || { echo "Source0 checksum mismatch for $$src0_name"; exit 1; }; \
			fi; \
			tar -xf "$$src0_path" -C "$$tmpdir"; \
		srcdir="$$(find "$$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"; \
		[ -n "$$srcdir" ] || { echo "Failed to locate extracted source dir for vendoring"; exit 1; }; \
		for vendor_patch in $$rust_vendor_patches; do \
			[ -f "./$$vendor_patch" ] || { echo "Rust vendor patch not found: $$vendor_patch"; exit 1; }; \
			patch -d "$$srcdir" -p1 < "./$$vendor_patch"; \
		done; \
		( cd "$$srcdir" && cargo vendor --locked vendor >/dev/null ); \
		if [ -n "$$source_date_epoch" ]; then \
			tar --sort=name --mtime="@$$source_date_epoch" --owner=0 --group=0 --numeric-owner -cJf "./$$vendor_name" -C "$$srcdir" vendor; \
		else \
			tar -cJf "./$$vendor_name" -C "$$srcdir" vendor; \
		fi; \
		if [ -f ./vendor.sha256 ]; then \
			sha256sum -c ./vendor.sha256; \
		fi; \
		rm -rf "$$tmpdir"; \
		trap - EXIT; \
	fi
	@if grep -Eq '^[[:space:]]*BuildRequires:[[:space:]]+golang([[:space:]]|$$)' "./$(specfile)" && rpmspec -P "./$(specfile)" | grep -q '^Source1:'; then \
		if ! command -v go >/dev/null 2>&1; then \
			echo "golang is required to generate vendored Go sources for ./$(specfile)"; \
			exit 1; \
		fi; \
		vendor_subdir="$$(awk -F= '/^GO_VENDOR_SUBDIR=/{print $$2}' ./package.env 2>/dev/null || true)"; \
		if [ -z "$$vendor_subdir" ]; then \
			vendor_subdir="."; \
		fi; \
		"$(repo_root)/scripts/prepare-go-vendor.sh" "./$(specfile)" "$(CURDIR)" "$$vendor_subdir"; \
	fi
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_specdir $(CURDIR)" \
		--define "_builddir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		--define "_rpmdir $(CURDIR)" \
		--define "_buildrootdir $(CURDIR)/.build" \
		"./$(specfile)"
