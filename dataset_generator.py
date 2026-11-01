import os
import random


# ─────────────────────────────────────────────
#  CORRECT / NO-ERROR TEMPLATES
# ─────────────────────────────────────────────
CORRECT_TEMPLATES = [
    """#include <iostream>
int main() {
    int x = %VAL1%;
    int y = %VAL2%;
    int z = x + y;
    std::cout << z << std::endl;
    return 0;
}""",
    """#include <iostream>
void func(int a) {
    if (a > 10) {
        std::cout << "Greater" << std::endl;
    }
}
int main() {
    func(%VAL1%);
    return 0;
}""",
    """#include <iostream>
int main() {
    int arr[5] = {1, 2, 3, 4, 5};
    int index = %VAL1%;
    std::cout << arr[index] << std::endl;
    return 0;
}""",
    """#include <iostream>
int main() {
    int sum = 0;
    for (int i = 0; i < %VAL1%; ++i) {
        sum += i;
    }
    std::cout << sum << std::endl;
    return 0;
}""",
    """#include <iostream>
void print_sum(int a, int b) {
    std::cout << (a + b) << std::endl;
}
int main() {
    int x = %VAL1%;
    int y = %VAL2%;
    print_sum(x, y);
    return 0;
}""",
    """#include <iostream>
class Calculator {
public:
    int add(int a, int b) { return a + b; }
};
int main() {
    Calculator calc;
    std::cout << calc.add(%VAL1%, %VAL2%) << std::endl;
    return 0;
}""",
    """#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int val = %VAL1%;
    std::cout << factorial(val) << std::endl;
    return 0;
}""",
    """#include <iostream>
int main() {
    int* ptr = new int(%VAL1%);
    std::cout << *ptr << std::endl;
    delete ptr;
    return 0;
}""",
    """#include <iostream>
int main() {
    int choice = %VAL1%;
    switch(choice) {
        case 1: std::cout << "One" << std::endl; break;
        default: std::cout << "Default" << std::endl; break;
    }
    return 0;
}"""
]

# ─────────────────────────────────────────────
#  TYPE-MISMATCH TEMPLATES
# ─────────────────────────────────────────────
TYPE_MISMATCH_TEMPLATES = [
    # Assigning string literal to int
    """#include <iostream>
int main() {
    int x = "hello";
    std::cout << x << std::endl;
    return 0;
}""",
    # Float → int truncation with pointer arithmetic
    """#include <iostream>
int main() {
    float f = 3.14f;
    int* p = &f;
    std::cout << *p << std::endl;
    return 0;
}""",
    # Bool used as array index with wrong type
    """#include <iostream>
int main() {
    double d = 9.99;
    int arr[2] = {1, 2};
    int idx = d;
    std::cout << arr[idx] << std::endl;
    return 0;
}""",
    # Return type mismatch
    """#include <iostream>
char* getNum() {
    int num = 42;
    return num;
}
int main() {
    std::cout << getNum() << std::endl;
    return 0;
}""",
    # Passing float to int parameter
    """#include <iostream>
void printInt(int n) { std::cout << n << std::endl; }
int main() {
    float f = 2.718f;
    printInt(f);
    return 0;
}""",
    # Arithmetic between incompatible types
    """#include <iostream>
#include <string>
int main() {
    int x = 5;
    std::string s = "hello";
    int result = x + s;
    std::cout << result << std::endl;
    return 0;
}""",
    # Char* arithmetic mismatch
    """#include <iostream>
int main() {
    char* msg = "world";
    int len = msg;
    std::cout << len << std::endl;
    return 0;
}""",
    # Comparing signed and unsigned
    """#include <iostream>
int main() {
    int a = -1;
    unsigned int b = 10;
    if (a > b) {
        std::cout << "a is greater" << std::endl;
    }
    return 0;
}""",
    # Struct assigned to int
    """#include <iostream>
struct Point { int x, y; };
int main() {
    Point p = {1, 2};
    int val = p;
    std::cout << val << std::endl;
    return 0;
}""",
    # Double to bool implicit conversion
    """#include <iostream>
int main() {
    double d = 0.0001;
    bool flag = d;
    int result = flag + 10;
    std::cout << result << std::endl;
    return 0;
}""",
    # Void function result assigned
    """#include <iostream>
void doNothing() {}
int main() {
    int x = doNothing();
    std::cout << x << std::endl;
    return 0;
}""",
    # Enum to string implicit conversion
    """#include <iostream>
enum Color { RED, GREEN, BLUE };
int main() {
    Color c = RED;
    std::string s = c;
    std::cout << s << std::endl;
    return 0;
}"""
]

# ─────────────────────────────────────────────
#  SECURITY-CRITICAL TEMPLATES
# ─────────────────────────────────────────────
SECURITY_TEMPLATES = [
    # Classic stack buffer overflow
    """#include <cstring>
#include <iostream>
int main() {
    char buf[8];
    strcpy(buf, "This string is way too long for the buffer!");
    std::cout << buf << std::endl;
    return 0;
}""",
    # gets() — unsafe input (CWE-242)
    """#include <stdio.h>
int main() {
    char buf[32];
    gets(buf);
    printf("%s\\n", buf);
    return 0;
}""",
    # Format string vulnerability (CWE-134)
    """#include <stdio.h>
int main() {
    char user_input[64] = "%x %x %x %x";
    printf(user_input);
    return 0;
}""",
    # Command injection via system() (CWE-78)
    """#include <cstdlib>
#include <cstring>
#include <string>
int main() {
    char cmd[128];
    char user_arg[] = "arg; rm -rf /";
    sprintf(cmd, "echo %s", user_arg);
    system(cmd);
    return 0;
}""",
    # Heap buffer overflow
    """#include <cstring>
#include <cstdlib>
int main() {
    char* heap_buf = (char*)malloc(8);
    strcpy(heap_buf, "AAAAAAAAAAAAAAAAAAAAAAAAAAAA");
    free(heap_buf);
    return 0;
}""",
    # Integer overflow leading to under-allocation (CWE-190)
    """#include <cstdlib>
#include <cstring>
int main() {
    unsigned int len = 0xFFFFFFFF;
    char* buf = (char*)malloc(len + 1);
    memset(buf, 'A', len);
    free(buf);
    return 0;
}""",
    # Use after free (CWE-416)
    """#include <iostream>
#include <cstdlib>
int main() {
    int* p = (int*)malloc(sizeof(int));
    *p = 42;
    free(p);
    std::cout << *p << std::endl;
    return 0;
}""",
    # Double free (CWE-415)
    """#include <cstdlib>
int main() {
    int* p = (int*)malloc(sizeof(int));
    free(p);
    free(p);
    return 0;
}""",
    # Path traversal via snprintf (CWE-22)
    """#include <stdio.h>
#include <string.h>
int main() {
    char filename[256];
    char user_input[] = "../../etc/passwd";
    snprintf(filename, sizeof(filename), "/data/%s", user_input);
    FILE* f = fopen(filename, "r");
    if (f) fclose(f);
    return 0;
}""",
    # Null terminator missing → info leak
    """#include <cstring>
#include <cstdlib>
#include <stdio.h>
int main() {
    char buf[8];
    strncpy(buf, "ABCDEFGH", 8);
    printf("%s\\n", buf);
    return 0;
}""",
    # Sensitive data in fixed memory (CWE-312)
    """#include <cstring>
#include <iostream>
int main() {
    char password[32] = "SuperSecret123!";
    std::cout << "Password: " << password << std::endl;
    memset(password, 0, sizeof(password));
    return 0;
}""",
    # Race condition via shared global (CWE-362)
    """#include <iostream>
int shared_counter = 0;
void increment() {
    for (int i = 0; i < 1000; i++) {
        shared_counter++;
    }
}
int main() {
    increment();
    std::cout << shared_counter << std::endl;
    return 0;
}"""
]

# ─────────────────────────────────────────────
#  INFINITE LOOP TEMPLATES  (no exit/break/return)
# ─────────────────────────────────────────────
INFINITE_LOOP_TEMPLATES = [
    # while(true) — no break
    """#include <iostream>
int main() {
    int x = 0;
    while (true) {
        x++;
    }
    return 0;
}""",
    # for with always-true condition
    """#include <iostream>
int main() {
    for (int i = 0; i >= 0; i++) {
        std::cout << i;
    }
    return 0;
}""",
    # Decrementing loop that never reaches condition
    """#include <iostream>
int main() {
    for (int i = 0; i < 10; i--) {
        std::cout << i;
    }
    return 0;
}""",
    # while(1) — no break or return
    """#include <iostream>
int main() {
    int n = 5;
    while (1) {
        n = n * 2;
    }
    return 0;
}""",
    # do-while — always true condition
    """#include <iostream>
int main() {
    int x = 10;
    do {
        x += 1;
    } while (x > 0);
    return 0;
}""",
    # Loop counter never modified
    """#include <iostream>
int main() {
    int i = 0;
    while (i < 10) {
        std::cout << "stuck";
    }
    return 0;
}""",
    # Nested infinite loop — no exits
    """#include <iostream>
int main() {
    while (true) {
        for (int j = 0; j >= 0; j++) {
            std::cout << j;
        }
    }
    return 0;
}""",
    # Recursive infinite call — no base case
    """#include <iostream>
void recurse(int x) {
    recurse(x + 1);
}
int main() {
    recurse(0);
    return 0;
}"""
]

# ─────────────────────────────────────────────
#  LOOP WITH EXIT (no_error / correct)
# ─────────────────────────────────────────────
LOOP_WITH_EXIT_TEMPLATES = [
    """#include <iostream>
int main() {
    int x = 0;
    while (true) {
        x++;
        if (x > 10) break;
    }
    return 0;
}""",
    """#include <iostream>
int main() {
    for (int i = 0; i >= 0; i++) {
        if (i > 100) return 0;
        std::cout << i;
    }
    return 0;
}""",
    """#include <iostream>
#include <cstdlib>
int main() {
    int n = 0;
    while (1) {
        n++;
        if (n >= 50) exit(0);
    }
    return 0;
}""",
    """int main() {
    while(1) {
        break;
    }
    return 0;
}"""
]

# ─────────────────────────────────────────────
#  ERROR TYPE REGISTRY
# ─────────────────────────────────────────────
ERROR_TYPES = {
    "no_error": {
        "val1": "10", "val2": "20",
        "severity": "Low", "category": "N/A", "nature": "N/A",
        "alt_templates": [
            """#include <iostream>\nint main() {\n    int a = 5;\n    int b = 10;\n    return a * b;\n}""",
            """#include <iostream>\nint main() {\n    for (int i = 0; i < 10; i++) {\n        std::cout << i << " ";\n    }\n    return 0;\n}""",
        ] + LOOP_WITH_EXIT_TEMPLATES
    },
    "missing_semicolon": {
        "val1": "10\n    int temp = 5", "val2": "20",
        "severity": "Low", "category": "Compile-time", "nature": "Syntax"
    },
    "missing_brace": {
        "val1": "10", "val2": "20",
        "severity": "Medium", "category": "Compile-time", "nature": "Syntax"
    },
    "undeclared_variable": {
        "val1": "undeclared_var", "val2": "20",
        "severity": "High", "category": "Compile-time", "nature": "Syntax"
    },
    "uninitialized_variable": {
        "val1": "%UNINIT%", "val2": "20",
        "severity": "Medium", "category": "Runtime", "nature": "Logical"
    },
    "assignment_in_condition": {
        "val1": "10", "val2": "20",
        "severity": "Medium", "category": "Runtime", "nature": "Logical"
    },
    "out_of_bounds": {
        "val1": "10", "val2": "20",
        "severity": "High", "category": "Runtime", "nature": "Logical"
    },
    "null_ptr_access": {
        "val1": "%NULL_PTR%", "val2": "20",
        "severity": "High", "category": "Runtime", "nature": "Logical"
    },
    "division_by_zero": {
        "val1": "10", "val2": "0",
        "severity": "High", "category": "Runtime", "nature": "Logical"
    },
    "infinite_loop": {
        "val1": "10", "val2": "20",
        "severity": "High", "category": "Runtime", "nature": "Logical",
        "alt_templates": INFINITE_LOOP_TEMPLATES
    },
    "type_mismatch": {
        "val1": '"string"', "val2": "20",
        "severity": "Medium", "category": "Compile-time", "nature": "Syntax",
        "alt_templates": TYPE_MISMATCH_TEMPLATES
    },
    "buffer_overflow": {
        "val1": "10", "val2": "20",
        "severity": "Critical", "category": "Runtime", "nature": "Security",
        "alt_templates": SECURITY_TEMPLATES[:4]
    },
    "use_after_free": {
        "val1": "10", "val2": "20",
        "severity": "Critical", "category": "Runtime", "nature": "Security",
        "alt_templates": [SECURITY_TEMPLATES[6], SECURITY_TEMPLATES[7]]
    },
    "command_injection": {
        "val1": "10", "val2": "20",
        "severity": "Critical", "category": "Runtime", "nature": "Security",
        "alt_templates": [SECURITY_TEMPLATES[3], SECURITY_TEMPLATES[8]]
    },
    "format_string": {
        "val1": "10", "val2": "20",
        "severity": "Critical", "category": "Runtime", "nature": "Security",
        "alt_templates": [SECURITY_TEMPLATES[2], SECURITY_TEMPLATES[9]]
    },
    "integer_overflow": {
        "val1": "10", "val2": "20",
        "severity": "High", "category": "Runtime", "nature": "Security",
        "alt_templates": [SECURITY_TEMPLATES[5], SECURITY_TEMPLATES[10], SECURITY_TEMPLATES[11]]
    },
}


def _has_loop_exit(code: str) -> bool:
    """Return True if the code contains an explicit loop exit (break / return / exit)."""
    import re
    return bool(re.search(r'\b(break|return|exit)\s*[\(;]', code))


def generate_dataset(num_samples: int = 500):
    os.makedirs("data/dataset", exist_ok=True)
    labels = []

    error_names = list(ERROR_TYPES.keys())

    for i in range(num_samples):
        template = random.choice(CORRECT_TEMPLATES)
        error_name = random.choice(error_names)
        error_info = ERROR_TYPES[error_name]

        # ── Choose base code ────────────────────────────────────────────
        if "alt_templates" in error_info:
            code = random.choice(error_info["alt_templates"])
        else:
            code = template

        # ── Per-error transformations ────────────────────────────────────

        if error_name == "uninitialized_variable":
            if "int x = %VAL1%;" in code:
                code = code.replace("int x = %VAL1%;", "int x;")
            elif "func(%VAL1%);" in code:
                code = code.replace("func(%VAL1%);", "int x; func(x);")
            elif "int index = %VAL1%;" in code:
                code = code.replace("int index = %VAL1%;", "int index; std::cout << index;")
            else:
                code = code.replace("%VAL1%", "var_uninit").replace("int var_uninit", "int var_uninit;")

        if error_name == "null_ptr_access":
            if "%VAL1%" in code:
                code = code.replace("%VAL1%", "*(nullptr)")
            else:
                code = code.replace("return 0;", "int* p=nullptr; *p=10; return 0;", 1)

        if error_name == "missing_brace":
            if "{" in code:
                code = code.replace("{", "", 1)

        if error_name == "assignment_in_condition":
            if "if (" in code:
                code = code.replace(">", "=").replace("<", "=").replace("==", "=")
            elif "for (" in code:
                code = code.replace("< %VAL1%", "= %VAL1%").replace("<%VAL1%", "=%VAL1%")
            else:
                code = code.replace("return 0;", "if(x=10) return 0; return 0;", 1)

        if error_name == "division_by_zero":
            if "+" in code:
                code = code.replace("+", "/", 1)
            else:
                code = code.replace("return 0;", "int z = 10/0; return 0;", 1)

        if error_name == "infinite_loop":
            # Alt templates are already crafted without exits.
            # For code derived from correct templates inject an infinite loop.
            if "alt_templates" not in error_info or code not in error_info["alt_templates"]:
                loop_type = random.choice(["dec", "inc", "while"])
                if loop_type == "dec":
                    if "++i" in code:
                        code = code.replace("++i", "i--")
                    elif "i++" in code:
                        code = code.replace("i++", "i--")
                    elif "j++" in code:
                        code = code.replace("j++", "j--")
                    else:
                        code = code.replace("return 0;", "while(1){} return 0;", 1)
                elif loop_type == "inc":
                    if "< 10" in code:
                        code = code.replace("< 10", "> -1")
                    elif "< 5" in code:
                        code = code.replace("< 5", "> 0")
                    else:
                        code = code.replace("return 0;", "while(1){} return 0;", 1)
                else:
                    code = code.replace("return 0;", "while(1){} return 0;", 1)

            # Safety check — if the injected loop has a break/return/exit,
            # it's not actually an infinite loop; mark as no_error
            if _has_loop_exit(code):
                error_name = "no_error"
                error_info = ERROR_TYPES["no_error"]

        if error_name == "missing_semicolon":
            if ";" in code:
                code = code.replace(";", "", 1)

        if error_name == "type_mismatch" and "alt_templates" not in error_info:
            # Inject a type mismatch into a generic template
            code = code.replace("%VAL1%", '"hello"')

        # ── Replace remaining placeholders ──────────────────────────────
        code = code.replace("%VAL1%", error_info.get("val1", "5"))
        code = code.replace("%VAL2%", error_info.get("val2", "10"))

        # ── Write file ──────────────────────────────────────────────────
        file_name = f"sample_{i}_{error_name}.cpp"
        with open(f"data/dataset/{file_name}", "w") as f:
            f.write(code)

        labels.append({
            "file": file_name,
            "error_type": error_name,
            "severity": error_info["severity"],
            "category": error_info["category"],
            "nature": error_info["nature"]
        })

    import json
    with open("data/dataset/labels.json", "w") as f:
        json.dump(labels, f, indent=2)
    print(f"Generated {num_samples} samples in data/dataset/")


if __name__ == "__main__":
    generate_dataset(5000)
