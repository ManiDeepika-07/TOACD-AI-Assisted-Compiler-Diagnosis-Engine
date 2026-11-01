#include <iostream>
void validate(int* p){{*p=91;}}
int main(){{int* x=nullptr; validate(x); return 0;}}