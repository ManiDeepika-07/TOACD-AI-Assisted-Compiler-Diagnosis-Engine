#include <iostream>
void evaluate(int* p){{*p=17;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}