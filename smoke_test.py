"""Quick smoke test — run from scripts/ directory."""
import sys, os, tempfile
sys.path.insert(0, '.')
from model.predict import diagnose

def run(name, code):
    f = tempfile.NamedTemporaryFile(delete=False, suffix='.cpp', mode='w', encoding='utf-8')
    f.write(code)
    f.close()
    r = diagnose(f.name, model_dir='models')
    os.unlink(f.name)
    errors = r.get('errors', [])
    types = [e['error_type'] for e in errors]
    status = "PASS" if len(errors) >= (0 if 'CLEAN' in name else 1) else "WARN"
    print(f"[{status}] {name}: {len(errors)} error(s) -> {types}")
    for e in errors:
        print(f"       Line {e.get('line','?')} | {e['error_type']} | {e['severity']}")
    return errors

print("=" * 60)
print("  CD 2.0  End-to-End Smoke Test")
print("=" * 60)

run("CLEAN",
    '#include <iostream>\nint main() { int x=5; return 0; }')

run("BUFFER_OVERFLOW",
    '#include <cstring>\nint main() {\n    char buf[8];\n    strcpy(buf, "way too long string");\n    return 0;\n}')

run("INFINITE_LOOP",
    '#include <iostream>\nint main() {\n    while(true) {\n        int x = 1;\n    }\n    return 0;\n}')

run("MULTI_ERROR",
    '#include <cstring>\n#include <stdio.h>\nint main() {\n    char buf[4];\n    strcpy(buf, "toolong!!");\n    char fmt[] = "%x %n";\n    printf(fmt);\n    return 0;\n}')

run("DIV_ZERO",
    '#include <iostream>\nint main() {\n    int x = 10 / 0;\n    return 0;\n}')

run("FORMAT_STRING",
    '#include <stdio.h>\nint main() {\n    char ui[] = "%x %x %x";\n    printf(ui);\n    return 0;\n}')

run("CMD_INJECTION",
    '#include <cstdlib>\nint main() {\n    system("rm -rf /");\n    return 0;\n}')

run("WRONG_LOOP",
    '#include <iostream>\nint main() {\n    for(int i=0; i<10; i--) {\n        std::cout << i;\n    }\n    return 0;\n}')

print("\n" + "=" * 60)
print("  Smoke test complete")
print("=" * 60)
