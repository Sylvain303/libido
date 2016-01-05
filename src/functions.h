/*
 * libido functions
 */

#ifndef LIBIDO_INC
#define LIBIDO_INC

int parse_command_line(void);
int load_config(void);
int pass1_parser(void);
int resolve_references(void);
int parse_external_sources(char *filename);
int pass2_parser(void);
int write_buffers(void);

#endif
