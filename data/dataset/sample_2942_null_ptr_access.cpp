#include <iostream>
void validate(int* p){{*p=44;}}
int main(){{int* x=nullptr; validate(x); return 0;}}