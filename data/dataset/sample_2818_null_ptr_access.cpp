#include <iostream>
void validate(int* p){{*p=67;}}
int main(){{int* x=nullptr; validate(x); return 0;}}