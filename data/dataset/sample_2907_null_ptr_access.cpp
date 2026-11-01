#include <iostream>
void evaluate(int* p){{*p=89;}}
int main(){{int* x=nullptr; evaluate(x); return 0;}}