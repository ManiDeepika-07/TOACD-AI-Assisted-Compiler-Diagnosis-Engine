#include <iostream>
void handle(int* p){{*p=87;}}
int main(){{int* x=nullptr; handle(x); return 0;}}