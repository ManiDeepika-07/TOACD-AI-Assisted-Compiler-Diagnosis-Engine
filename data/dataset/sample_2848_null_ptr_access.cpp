#include <iostream>
void handle(int* p){{*p=47;}}
int main(){{int* x=nullptr; handle(x); return 0;}}