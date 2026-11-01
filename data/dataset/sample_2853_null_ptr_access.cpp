#include <iostream>
void validate(int* p){{*p=78;}}
int main(){{int* x=nullptr; validate(x); return 0;}}