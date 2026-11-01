#include <iostream>
void handle(int* p){{*p=18;}}
int main(){{int* x=nullptr; handle(x); return 0;}}