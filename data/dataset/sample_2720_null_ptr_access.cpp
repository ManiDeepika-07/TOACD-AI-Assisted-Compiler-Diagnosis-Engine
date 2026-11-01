#include <iostream>
void handle(int* p){{*p=13;}}
int main(){{int* x=nullptr; handle(x); return 0;}}