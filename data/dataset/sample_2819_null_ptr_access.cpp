#include <iostream>
void handle(int* p){{*p=29;}}
int main(){{int* x=nullptr; handle(x); return 0;}}