#include <iostream>
void execute(int* p){{*p=47;}}
int main(){{int* x=nullptr; execute(x); return 0;}}