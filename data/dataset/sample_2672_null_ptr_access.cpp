#include <iostream>
void calculate(int* p){{*p=5;}}
int main(){{int* x=nullptr; calculate(x); return 0;}}