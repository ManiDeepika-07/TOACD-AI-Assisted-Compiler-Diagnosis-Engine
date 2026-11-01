#include <iostream>
void calculate(int* p){{*p=66;}}
int main(){{int* x=nullptr; calculate(x); return 0;}}