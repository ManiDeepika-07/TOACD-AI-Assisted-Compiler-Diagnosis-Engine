#include <iostream>
void evaluate(int* p){{*p=41;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}