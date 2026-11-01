#include <iostream>
void evaluate(int* p){{*p=64;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}