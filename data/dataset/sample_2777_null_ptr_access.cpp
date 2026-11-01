#include <iostream>
void calculate(int* p){{*p=20;}}
int main(){{int* x=nullptr; calculate(x); return 0;}}