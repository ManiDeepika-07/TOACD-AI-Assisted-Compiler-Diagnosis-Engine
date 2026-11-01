#include <iostream>
void process(int* p){{*p=69;}}
int main(){{int* x=nullptr; process(x); return 0;}}