#include <iostream>
void compute(int* p){{*p=40;}}
int main(){{int* x=nullptr; compute(x); return 0;}}