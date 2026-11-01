#include <iostream>
void validate(int* p){{*p=42;}}
int main(){{int* x=nullptr; validate(x); return 0;}}