LEXER=../src/lexer
BATS=./bats/bin/bats

check:
	./run_test.sh
	$(BATS) lexer.bats

gen-token: $(LEXER)
	$(LEXER) < ../examples/libido/shell_lib.bash > bash_parsed.token

show-token-diff: $(LEXER)
	$(BATS) lexer.bats | grep -- ' [+-]'

$(LEXER):
	$(MAKE) -C ../src lexer
