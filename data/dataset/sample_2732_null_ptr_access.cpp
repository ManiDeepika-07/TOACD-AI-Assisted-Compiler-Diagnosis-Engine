#include <iostream>
void handle(int* p){{*p=6;}}
int main(){{int* x=nullptr; handle(x); return 0;}}