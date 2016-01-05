
libido: lex.yy.c functions.o functions.h
	gcc functions.o libido.c -o libido 

lexer: lex.yy.c
	gcc -o lexer lex.yy.c -lfl

lex.yy.c: lexer.l
	flex lexer.l
