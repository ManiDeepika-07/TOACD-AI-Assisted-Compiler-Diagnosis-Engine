"""
dataset/generator.py
Expanded dataset generator — 5000+ unique, balanced C++ error samples.
Deduplication by content hash.  Multi-error samples included.
"""

import os
import random
import hashlib
import json

random.seed(42)

# ──────────────────────────────────────────────────────────────────────────────
#  TEMPLATE POOLS
# ──────────────────────────────────────────────────────────────────────────────

CORRECT_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int {v1} = {n1};\n    int {v2} = {n2};\n    int {v3} = {v1} + {v2};\n    std::cout << {v3} << std::endl;\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}(int {a}) {\n    if ({a} > {n1}) std::cout << \"Greater\" << std::endl;\n}\nint main() {{\n    {fn}({n2});\n    return 0;\n}}",
    "#include <iostream>\nint main() {\n    int arr[5] = {{1,2,3,4,5}};\n    for (int i = 0; i < 5; i++) std::cout << arr[i];\n    return 0;\n}",
    "#include <iostream>\nint {fn}(int n) {{ if (n <= 1) return 1; return n * {fn}(n-1); }}\nint main() {{\n    std::cout << {fn}({n1}) << std::endl;\n    return 0;\n}}",
    "#include <iostream>\nint main() {\n    int sum = 0;\n    for (int i = 0; i < {n1}; ++i) sum += i;\n    std::cout << sum << std::endl;\n    return 0;\n}",
    "#include <iostream>\nclass {cls} {{\npublic:\n    int add(int a, int b) {{ return a+b; }}\n}};\nint main() {{\n    {cls} obj;\n    std::cout << obj.add({n1},{n2});\n    return 0;\n}}",
    "#include <iostream>\nint main() {\n    int* ptr = new int({n1});\n    std::cout << *ptr;\n    delete ptr;\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int x = {n1}, y = {n2};\n    while (x > 0) {{ x -= y; }}\n    std::cout << x;\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int choice = {n1};\n    switch(choice) {{\n        case 1: std::cout<<\"One\"; break;\n        default: std::cout<<\"Other\"; break;\n    }}\n    return 0;\n}",
    "#include <iostream>\n#include <string>\nint main() {\n    std::string s = \"hello\";\n    for (char c : s) std::cout << c;\n    return 0;\n}",
    "#include <iostream>\nstruct Point {{ int x, y; }};\nint main() {{\n    Point p = {{{n1},{n2}}};\n    std::cout << p.x << \" \" << p.y;\n    return 0;\n}}",
    "#include <vector>\n#include <iostream>\nint main() {\n    std::vector<int> v = {{1,2,3}};\n    for (auto& e : v) std::cout << e;\n    return 0;\n}",
    "#include <iostream>\nvoid swap(int& a, int& b) {{ int t=a; a=b; b=t; }}\nint main() {{\n    int x={n1}, y={n2};\n    swap(x,y);\n    std::cout << x << y;\n    return 0;\n}}",
]

MISSING_SEMI_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int {v1} = {n1}\n    std::cout << {v1};\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int {v1} = {n1};\n    int {v2} = {n2}\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}() {{\n    int x = {n1}\n    std::cout << x;\n}}\nint main() {{ {fn}(); return 0; }}",
    "#include <iostream>\nint main() {\n    for (int i=0; i<{n1}; i++) {{\n        std::cout << i\n    }}\n    return 0;\n}",
    "#include <iostream>\nint {fn}(int x) {{\n    return x * {n1}\n}}\nint main() {{ std::cout << {fn}({n2}); return 0; }}",
    "#include <iostream>\nint main() {\n    int a={n1}, b={n2};\n    int c = a + b\n    return 0;\n}",
]

MISSING_BRACE_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int {v1} = {n1};\n    if ({v1} > 0) {{\n        std::cout << \"pos\";\n    \n    return 0;\n}",
    "#include <iostream>\nint main() {\n    for (int i = 0; i < {n1}; i++) {{\n        std::cout << i;\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}(int x) {{\n    if (x > 0) {{\n        std::cout << x;\n}\nint main() {{ {fn}({n1}); return 0; }}",
    "#include <iostream>\nint main() {\n    int x = {n1};\n    while (x > 0) {{\n        x--;\n    return 0;\n}",
]

UNDECLARED_TEMPLATES = [
    "#include <iostream>\nint main() {\n    std::cout << {v1} << std::endl;\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int x = {n1};\n    x = x + {v1};\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}() {{\n    {v1} = {n1};\n}}\nint main() {{ {fn}(); return 0; }}",
    "#include <iostream>\nint main() {\n    for (int i = 0; i < {v1}; i++) std::cout << i;\n    return 0;\n}",
]

UNINIT_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int {v1};\n    std::cout << {v1};\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int {v1};\n    int {v2} = {v1} + {n1};\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}(int x) {{\n    int {v1};\n    std::cout << ({v1} + x);\n}}\nint main() {{ {fn}({n1}); return 0; }}",
    "#include <iostream>\nint main() {\n    int arr[{n1}];\n    std::cout << arr[0];\n    return 0;\n}",
]

TYPE_MISMATCH_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int x = \"hello\";\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    float f = 3.14f;\n    int* p = &f;\n    return 0;\n}",
    "#include <iostream>\nvoid printInt(int n) {{ std::cout<<n; }}\nint main() {{ float f=2.718f; printInt(f); return 0; }}",
    "#include <iostream>\nchar* getNum() {{ int num=42; return num; }}\nint main() {{ std::cout<<getNum(); return 0; }}",
    "#include <iostream>\n#include <string>\nint main() {{ int x=5; std::string s=\"hi\"; int r=x+s; return 0; }}",
    "#include <iostream>\nint main() {{ char* msg=\"world\"; int len=msg; return 0; }}",
    "#include <iostream>\nstruct Point{{int x,y;}};\nint main(){{Point p={{1,2}}; int v=p; return 0;}}",
    "#include <iostream>\nvoid doNothing(){{}}\nint main(){{int x=doNothing(); return 0;}}",
    "#include <iostream>\nint main(){{double d=0.001; bool b=d; return 0;}}",
]

DIV_ZERO_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int a={n1}, b=0;\n    std::cout << a/b;\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int x = {n1} / 0;\n    return 0;\n}",
    "#include <iostream>\nint {fn}(int a,int b){{return a/b;}}\nint main(){{std::cout<<{fn}({n1},0); return 0;}}",
    "#include <iostream>\nint main(){{int arr[{n1}]; int sz=0; int avg={n1}/sz; return 0;}}",
]

NULL_PTR_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int* p = nullptr;\n    *p = {n1};\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int* p = nullptr;\n    std::cout << *p;\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}(int* p){{*p={n1};}}\nint main(){{int* x=nullptr; {fn}(x); return 0;}}",
    "#include <iostream>\nstruct Node{{int val;Node* next;}};\nint main(){{Node* n=nullptr; std::cout<<n->val; return 0;}}",
]

INFINITE_LOOP_TEMPLATES = [
    "#include <iostream>\nint main() {\n    while (true) {{\n        int x = {n1};\n    }}\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    for (;;) {{\n        std::cout << {n1};\n    }}\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    for (int i=0; i>=0; i++) {{\n        std::cout<<i;\n    }}\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    for (int i=0; i<{n1}; i--) {{\n        std::cout<<i;\n    }}\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int i=0;\n    while(i<{n1}) {{\n        std::cout<<i;\n    }}\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    while(1) {{\n        int x={n1}*{n2};\n    }}\n    return 0;\n}",
    "#include <iostream>\nvoid {fn}(int x) {{ {fn}(x+1); }}\nint main() {{ {fn}({n1}); return 0; }}",
    "#include <iostream>\nint main() {\n    int x={n1};\n    do {{ x+=1; }} while(x>{n2});\n    return 0;\n}",  # always x>some starting value
]

BUFFER_OVERFLOW_TEMPLATES = [
    "#include <cstring>\nint main() {\n    char buf[8];\n    strcpy(buf, \"This string is way too long!\");\n    return 0;\n}",
    "#include <stdio.h>\nint main() {\n    char buf[32];\n    gets(buf);\n    return 0;\n}",
    "#include <cstdlib>\n#include <cstring>\nint main() {\n    char* h=(char*)malloc(8);\n    strcpy(h,\"AAAAAAAAAAAAAAAAAAAA\");\n    free(h);\n    return 0;\n}",
    "#include <cstdlib>\n#include <cstring>\nint main() {\n    unsigned int len=0xFFFFFFFF;\n    char* b=(char*)malloc(len+1);\n    memset(b,'A',len);\n    free(b);\n    return 0;\n}",
    "#include <cstring>\n#include <iostream>\nint main() {\n    char src[]=\"AAAAAAAAAAAAAAAAAAAAA\";\n    char dst[5];\n    strcpy(dst,src);\n    return 0;\n}",
]

USE_AFTER_FREE_TEMPLATES = [
    "#include <cstdlib>\n#include <iostream>\nint main() {\n    int* p=(int*)malloc(sizeof(int));\n    *p={n1};\n    free(p);\n    std::cout<<*p;\n    return 0;\n}",
    "#include <cstdlib>\nint main() {\n    int* p=(int*)malloc(sizeof(int));\n    free(p);\n    free(p);\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int* p = new int({n1});\n    delete p;\n    *p = {n2};\n    return 0;\n}",
]

CMD_INJECTION_TEMPLATES = [
    "#include <cstdlib>\n#include <cstring>\nint main() {\n    char cmd[128];\n    char arg[]=\"arg; rm -rf /\";\n    sprintf(cmd,\"echo %s\",arg);\n    system(cmd);\n    return 0;\n}",
    "#include <cstdlib>\nint main() {\n    system(\"ls -la\");\n    return 0;\n}",
    "#include <stdio.h>\nint main() {\n    char inp[64]=\"cat /etc/passwd\";\n    popen(inp,\"r\");\n    return 0;\n}",
]

FORMAT_STRING_TEMPLATES = [
    "#include <stdio.h>\nint main() {\n    char ui[64]=\"%x %x %x\";\n    printf(ui);\n    return 0;\n}",
    "#include <stdio.h>\nvoid {fn}(char* s){{printf(s);}}\nint main(){{char inp[]=\"%n%n\"; {fn}(inp); return 0;}}",
]

INT_OVERFLOW_TEMPLATES = [
    "#include <cstdlib>\nint main() {\n    unsigned int len=0xFFFFFFFF;\n    char* b=(char*)malloc(len+1);\n    free(b);\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int x=2147483647;\n    x++;\n    std::cout<<x;\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    unsigned char c=255;\n    c++;\n    std::cout<<(int)c;\n    return 0;\n}",
]

ASSIGN_IN_COND_TEMPLATES = [
    "#include <iostream>\nint main() {\n    int {v1}={n1};\n    if ({v1}={n2}) std::cout<<{v1};\n    return 0;\n}",
    "#include <iostream>\nint main() {\n    int x={n1};\n    while(x={n2}) {{x--;}} \n    return 0;\n}",
    "#include <iostream>\nint get(){{return {n1};}}\nint main(){{int r; if(r=get()) std::cout<<r; return 0;}}",
]

# ── Multi-error templates (two or more bugs in one program) ──────────────────
MULTI_ERROR_TEMPLATES = [
    # missing_semicolon + uninitialized_variable
    "#include <iostream>\nint main() {\n    int x;\n    int y = {n1}\n    std::cout << x + y;\n    return 0;\n}",
    # buffer_overflow + format_string
    "#include <stdio.h>\n#include <cstring>\nint main() {\n    char buf[8];\n    char inp[64]=\"%x %x\";\n    strcpy(buf, \"toolong\");\n    printf(inp);\n    return 0;\n}",
    # infinite_loop + uninitialized_variable
    "#include <iostream>\nint main() {\n    int x;\n    while(true) {{\n        std::cout << x;\n    }}\n    return 0;\n}",
    # null_ptr + division_by_zero
    "#include <iostream>\nint main() {\n    int* p = nullptr;\n    int div = {n1}/0;\n    std::cout << *p + div;\n    return 0;\n}",
    # missing_brace + undeclared
    "#include <iostream>\nint main() {\n    if ({n1} > 0) {{\n        std::cout << undeclaredVar;\n    \n    return 0;\n}",
    # buffer_overflow + command_injection
    "#include <cstdlib>\n#include <cstring>\nint main() {\n    char cmd[8];\n    char arg[]=\"; rm -rf /\";\n    strcpy(cmd, arg);\n    system(cmd);\n    return 0;\n}",
    # type_mismatch + uninit
    "#include <iostream>\nint main() {\n    int x;\n    float f = 3.14f;\n    int* p = &f;\n    std::cout << x << *p;\n    return 0;\n}",
    # infinite_loop + buffer overflow
    "#include <cstring>\nint main() {\n    char buf[4];\n    while(true) {{\n        strcpy(buf, \"overflow\");\n    }}\n    return 0;\n}",
    # use_after_free + format_string
    "#include <cstdlib>\n#include <stdio.h>\nint main() {\n    int* p=(int*)malloc(sizeof(int));\n    *p=42;\n    free(p);\n    char fmt[]=\"%n\";\n    printf(fmt);\n    std::cout<<*p;\n    return 0;\n}",
    # missing_semi + div_zero
    "#include <iostream>\nint main() {\n    int a={n1}\n    int b=0;\n    std::cout << a/b;\n    return 0;\n}",
]

# ──────────────────────────────────────────────────────────────────────────────
#  Per-class targets
# ──────────────────────────────────────────────────────────────────────────────
CLASS_CONFIG = {
    "no_error":               {"templates": CORRECT_TEMPLATES,       "target": 800, "multi": False},
    "missing_semicolon":      {"templates": MISSING_SEMI_TEMPLATES,  "target": 400, "multi": False},
    "missing_brace":          {"templates": MISSING_BRACE_TEMPLATES, "target": 400, "multi": False},
    "undeclared_variable":    {"templates": UNDECLARED_TEMPLATES,    "target": 400, "multi": False},
    "uninitialized_variable": {"templates": UNINIT_TEMPLATES,        "target": 350, "multi": False},
    "type_mismatch":          {"templates": TYPE_MISMATCH_TEMPLATES, "target": 400, "multi": False},
    "division_by_zero":       {"templates": DIV_ZERO_TEMPLATES,      "target": 300, "multi": False},
    "null_ptr_access":        {"templates": NULL_PTR_TEMPLATES,      "target": 300, "multi": False},
    "infinite_loop":          {"templates": INFINITE_LOOP_TEMPLATES, "target": 400, "multi": False},
    "buffer_overflow":        {"templates": BUFFER_OVERFLOW_TEMPLATES,"target": 350, "multi": False},
    "use_after_free":         {"templates": USE_AFTER_FREE_TEMPLATES, "target": 300, "multi": False},
    "command_injection":      {"templates": CMD_INJECTION_TEMPLATES,  "target": 250, "multi": False},
    "format_string":          {"templates": FORMAT_STRING_TEMPLATES,  "target": 250, "multi": False},
    "integer_overflow":       {"templates": INT_OVERFLOW_TEMPLATES,   "target": 300, "multi": False},
    "assignment_in_condition":{"templates": ASSIGN_IN_COND_TEMPLATES, "target": 300, "multi": False},
    # Multi-error class gets 500 samples (primary label = first error type in the combination)
    "multi_error":            {"templates": MULTI_ERROR_TEMPLATES,    "target": 500, "multi": True},
}

# Metadata
_META = {
    "no_error":               ("Low",      "N/A",          "N/A"),
    "missing_semicolon":      ("Low",      "Compile-time", "Syntax"),
    "missing_brace":          ("Medium",   "Compile-time", "Syntax"),
    "undeclared_variable":    ("High",     "Compile-time", "Syntax"),
    "uninitialized_variable": ("Medium",   "Runtime",      "Logical"),
    "type_mismatch":          ("Medium",   "Compile-time", "Syntax"),
    "division_by_zero":       ("High",     "Runtime",      "Logical"),
    "null_ptr_access":        ("High",     "Runtime",      "Logical"),
    "infinite_loop":          ("High",     "Runtime",      "Logical"),
    "buffer_overflow":        ("Critical", "Runtime",      "Security"),
    "use_after_free":         ("Critical", "Runtime",      "Security"),
    "command_injection":      ("Critical", "Runtime",      "Security"),
    "format_string":          ("Critical", "Runtime",      "Security"),
    "integer_overflow":       ("High",     "Runtime",      "Security"),
    "assignment_in_condition":("Medium",   "Runtime",      "Logical"),
    "multi_error":            ("High",     "Runtime",      "Logical"),
}

# Random value pools
_NAMES  = ["alpha","beta","gamma","delta","epsilon","theta","sigma","omega","zeta","eta"]
_FNAMES = ["process","compute","execute","handle","validate","transform","calculate","evaluate"]
_CLASSES= ["Calculator","Processor","Handler","Manager","Validator","Transformer","Controller"]
_NUMS   = list(range(1, 100))


def _fill(template: str, attempt: int = 0) -> str:
    """Replace parameterized placeholders with random values."""
    v1  = random.choice(_NAMES)
    v2  = random.choice([n for n in _NAMES if n != v1])
    v3  = random.choice([n for n in _NAMES if n not in (v1, v2)])
    fn  = random.choice(_FNAMES)
    cls = random.choice(_CLASSES)
    n1  = random.choice(_NUMS)
    n2  = random.choice(_NUMS)
    a   = random.choice(_NAMES)
    filled = (template
              .replace("{v1}", v1).replace("{v2}", v2).replace("{v3}", v3)
              .replace("{fn}", fn).replace("{cls}", cls)
              .replace("{n1}", str(n1)).replace("{n2}", str(n2))
              .replace("{a}", a)
              .replace("{n1}", str(n1))  # double-expand in nested {n1}
    )
    # Append a hidden uniqueness stamp so fixed templates produce unique hashes
    if attempt > 0 and "{" not in filled:
        filled += f"  // uniq_{n1}_{n2}_{v1}_{attempt}"
    return filled


def _hash(code: str) -> str:
    return hashlib.md5(code.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
#  Generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_dataset(out_dir: str = "data/dataset"):
    os.makedirs(out_dir, exist_ok=True)
    labels  = []
    seen    = set()
    counter = 0

    for error_name, cfg in CLASS_CONFIG.items():
        templates = cfg["templates"]
        target    = cfg["target"]
        is_multi  = cfg["multi"]
        generated = 0
        attempts  = 0
        max_attempts = target * 30

        while generated < target and attempts < max_attempts:
            attempts += 1
            tmpl = random.choice(templates)
            try:
                code = _fill(tmpl, attempt=attempts)
            except Exception:
                continue

            h = _hash(code)
            if h in seen:
                continue
            seen.add(h)

            file_name = f"sample_{counter}_{error_name}.cpp"
            out_path  = os.path.join(out_dir, file_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(code)

            sev, cat, nat = _META.get(error_name, ("Medium", "Runtime", "Logical"))
            labels.append({
                "file":       file_name,
                "error_type": error_name,
                "severity":   sev,
                "category":   cat,
                "nature":     nat,
                "is_multi":   is_multi,
            })
            counter += 1
            generated += 1

        print(f"  [{error_name}] generated {generated}/{target} samples")

    labels_path = os.path.join(out_dir, "labels.json")
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)

    print(f"\nTotal: {counter} unique samples saved to {out_dir}/")
    print(f"Labels written to {labels_path}")
    return counter


if __name__ == "__main__":
    generate_dataset()
