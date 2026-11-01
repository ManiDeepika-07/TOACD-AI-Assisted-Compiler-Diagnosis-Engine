#include <iostream>
void execute(int* p){{*p=21;}}
int main(){{int* x=nullptr; execute(x); return 0;}}