#ifndef _STRING_H
#define _STRING_H
typedef unsigned long size_t;
void* memset(void* s, int c, size_t n);
char* strcpy(char* dest, const char* src);
char* strncpy(char* dest, const char* src, size_t n);
char* strcat(char* dest, const char* src);
#endif
