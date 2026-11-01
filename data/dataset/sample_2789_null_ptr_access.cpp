#include <iostream>
void process(int* p){{*p=87;}}
int main(){{int* x=nullptr; process(x); return 0;}}