#include <iostream>
void compute(int* p){{*p=50;}}
int main(){{int* x=nullptr; compute(x); return 0;}}