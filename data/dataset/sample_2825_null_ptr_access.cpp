#include <iostream>
void execute(int* p){{*p=78;}}
int main(){{int* x=nullptr; execute(x); return 0;}}