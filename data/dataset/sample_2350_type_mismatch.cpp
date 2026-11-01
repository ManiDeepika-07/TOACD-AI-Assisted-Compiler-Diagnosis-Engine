#include <iostream>
char* getNum() {{ int num=42; return num; }}
int main() {{ std::cout<<getNum(); return 0; }}