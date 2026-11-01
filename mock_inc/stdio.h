#ifndef _STDIO_H
#define _STDIO_H
typedef unsigned long size_t;
typedef struct FILE FILE;
int printf(const char* format, ...);
int snprintf(char* s, size_t n, const char* format, ...);
int sprintf(char* s, const char* format, ...);
char* gets(char* s);
FILE* fopen(const char* filename, const char* mode);
int fclose(FILE* stream);
#endif
