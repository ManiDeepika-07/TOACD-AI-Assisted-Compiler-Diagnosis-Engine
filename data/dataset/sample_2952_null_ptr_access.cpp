#include <iostream>
void execute(int* p){{*p=85;}}
int main(){{int* x=nullptr; execute(x); return 0;}}