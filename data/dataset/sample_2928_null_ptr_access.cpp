#include <iostream>
void execute(int* p){{*p=56;}}
int main(){{int* x=nullptr; execute(x); return 0;}}