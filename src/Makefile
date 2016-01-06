CCFLAS=-g
CC=gcc ${CCFLAS}

all: bash_parser

bash_parser: lex.yy.o bash_parser.tab.c
	${CC} -o bash_parser bash_parser.tab.c lex.yy.o -lfl

bash_parser.tab.c: bash_parser.y
	bison -d bash_parser.y

libido: lex.yy.c functions.o functions.h
	${CC} functions.o libido.c -o libido 

lexer: lex.yy.c
	${CC} -o lexer lex.yy.c -lfl

lex.yy.o: lex.yy.c bash_parser.tab.c
	${CC} -c lex.yy.c

lex.yy.c: lexer.l
	flex lexer.l

calc: calc.tab.c
	${CC} -o calc calc.tab.c -lm

calc.tab.c: calc.y
	bison calc.y

# pkg-config will find cflags for glib, see /usr/lib/x86_64-linux-gnu/pkgconfig/glib-2.0.pc
glib_ex1: glib_ex1.c
	${CC} -o glib_ex1 glib_ex1.c  \
		$$(pkg-config --cflags --libs glib-2.0)
hcreate_r: hcreate_r.c
	${CC} -o hcreate_r hcreate_r.c

clean:
	rm -f lex.yy.c *.o lexer libio glib_ex1 hcreate_r *.tab.[ohc]
