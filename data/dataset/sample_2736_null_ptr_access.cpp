#include <iostream>
void transform(int* p){{*p=24;}}
int main(){{int* x=nullptr; transform(x); return 0;}}