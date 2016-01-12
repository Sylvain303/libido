LEXER=../src/lexer

check:
	$(BATS) lexer.bats

gen-token: $(LEXER)
	$(LEXER) < ../examples/libido/shell_lib.bash > bash_parsed.token

$(LEXER):
	$(MAKE) -C ../src lexer
