#include <iostream>
void evaluate(int* p){{*p=53;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}