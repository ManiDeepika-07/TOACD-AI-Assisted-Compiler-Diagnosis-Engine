#include <iostream>
void transform(int* p){{*p=23;}}
int main(){{int* x=nullptr; transform(x); return 0;}}