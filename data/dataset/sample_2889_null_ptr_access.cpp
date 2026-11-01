#include <iostream>
void execute(int* p){{*p=10;}}
int main(){{int* x=nullptr; execute(x); return 0;}}