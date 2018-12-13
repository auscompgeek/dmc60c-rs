ifndef DMC60C_REPO
$(error DMC60C_REPO is not set (path to dmc60c-frc-api))
endif

all: dmc60c-sys/src/mid.rs dmc60c-sys/lib/libdmc60c.so src/lib.rs
	cargo check

clean:
	rm -f dmc60c-sys/src/mid.rs src/lib.rs

dmc60c-sys/src/mid.rs: $(DMC60C_REPO)/include/digilent/dmc60/DMC60C_C.h
	# TODO: write a rust script instead of calling bindgen and renaming enum variants with sed
	bindgen --whitelist-function 'c_.*' --rustified-enum '*' $^ | sed 's@^/// \\enum \w* @/// @; s/^    DMC_\(\w*\) =/    \1 =/' > $@

dmc60c-sys/lib/libdmc60c.so: $(DMC60C_REPO)/dmc60c-config-utility-release/libdmc60c.so
	@mkdir -p dmc60c-sys/lib
	cp $^ $@

src/lib.rs: gen/hooks.py gen/gen_mod.rs.j2 $(DMC60C_REPO)/include/digilent/dmc60/DMC60C.h
	@mkdir -p src
	h2w --hooks $^ -o $@
	cargo fmt
