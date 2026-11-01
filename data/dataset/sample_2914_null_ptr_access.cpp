#include <iostream>
void evaluate(int* p){{*p=11;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}