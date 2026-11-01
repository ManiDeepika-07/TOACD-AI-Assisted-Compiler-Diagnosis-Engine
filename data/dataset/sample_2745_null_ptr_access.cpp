#include <iostream>
void execute(int* p){{*p=46;}}
int main(){{int* x=nullptr; execute(x); return 0;}}