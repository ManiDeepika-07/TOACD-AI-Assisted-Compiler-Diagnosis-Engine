#include <iostream>
void validate(int* p){{*p=24;}}
int main(){{int* x=nullptr; validate(x); return 0;}}