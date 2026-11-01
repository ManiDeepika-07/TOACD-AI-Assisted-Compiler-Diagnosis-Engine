#include <iostream>
void execute(int* p){{*p=50;}}
int main(){{int* x=nullptr; execute(x); return 0;}}