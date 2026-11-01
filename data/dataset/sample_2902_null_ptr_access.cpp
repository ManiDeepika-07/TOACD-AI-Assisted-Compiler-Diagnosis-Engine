#include <iostream>
void transform(int* p){{*p=35;}}
int main(){{int* x=nullptr; transform(x); return 0;}}