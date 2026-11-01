#include <iostream>
void compute(int* p){{*p=43;}}
int main(){{int* x=nullptr; compute(x); return 0;}}