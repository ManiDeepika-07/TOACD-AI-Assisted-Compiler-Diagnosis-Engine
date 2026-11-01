#include <iostream>
void execute(int* p){{*p=68;}}
int main(){{int* x=nullptr; execute(x); return 0;}}