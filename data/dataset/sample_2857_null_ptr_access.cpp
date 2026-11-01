#include <iostream>
void compute(int* p){{*p=11;}}
int main(){{int* x=nullptr; compute(x); return 0;}}