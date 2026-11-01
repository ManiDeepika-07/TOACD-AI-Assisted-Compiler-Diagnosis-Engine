#include <iostream>
struct Node{{int val;Node* next;}};
int main(){{Node* n=nullptr; std::cout<<n->val; return 0;}}