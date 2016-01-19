CFLAGS=-g -DYYDEBUG=1
CC=gcc ${CFLAGS}

all: bash_parser

OBJECTS=lex.yy.o bash_keywords.o function_lines.o
bash_parser: bash_parser.tab.c $(OBJECTS)
	${CC} -o bash_parser bash_parser.tab.c $(OBJECTS) -lfl $$(pkg-config --cflags --libs glib-2.0)

# -d generate tab.h for inclusion in lexer.l
# -g graph
# -W warning
bash_parser.tab.c: bash_parser.y
	bison -d -g -W bash_parser.y

bash_parser.tab.h: bash_parser.tab.c
	touch $@

libido: lex.yy.c functions.o functions.h
	${CC} functions.o libido.c -o libido

# build only the lexer, used by unittest too
# for debuging -DDEBUG=1 too
lexer: lex.yy.c bash_parser.tab.h bash_keywords.o
	${CC} -o lexer lex.yy.c -D TEST_LEXER=1 -lfl $$(pkg-config --libs --cflags glib-2.0) bash_keywords.o

lex.yy.o: lex.yy.c bash_parser.tab.h bash_keywords.h bash_keywords.c
	${CC} -DDEBUG=1 -c lex.yy.c $$(pkg-config --cflags glib-2.0)

lex.yy.c: lexer.l
	flex lexer.l

bash_keywords.o: bash_keywords.c bash_keywords.h
	${CC} -c bash_keywords.c

function_lines.o: function_lines.c function_lines.h
	${CC} -c function_lines.c $$(pkg-config --cflags glib-2.0)

# experimentation maybe not commited code
calc: calc.tab.c
	${CC} -o calc calc.tab.c -lm

calc.tab.c: calc.y
	bison calc.y

# pkg-config will find cflags for glib, see /usr/lib/x86_64-linux-gnu/pkgconfig/glib-2.0.pc
glib_ex1: glib_ex1.c
	${CC} -o glib_ex1 glib_ex1.c $$(pkg-config --cflags --libs glib-2.0)

hcreate_r: hcreate_r.c
	${CC} -o hcreate_r hcreate_r.c

clean:
	rm -f lex.yy.c *.o lexer libio glib_ex1 hcreate_r *.tab.[ohc] bash_parser *.dot *.output
