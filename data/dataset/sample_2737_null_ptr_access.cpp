#include <iostream>
void handle(int* p){{*p=65;}}
int main(){{int* x=nullptr; handle(x); return 0;}}