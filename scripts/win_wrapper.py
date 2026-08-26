# -*- coding: utf-8 -*-
"""Windows 适配器：在 Windows 上运行作者的 Unix 风格脚本。

作者脚本顶层 `import resource`（Unix-only），Windows 无此模块。
本 wrapper 注入一个假 resource 模块（仅提供 getrusage 占位），
再 exec 目标脚本，不改动作者任何代码。

用法: python win_wrapper.py <target_script.py> [args...]
"""
import sys
import types

# --- 注入假 resource 模块 ---
fake_resource = types.ModuleType("resource")
fake_resource.RUSAGE_SELF = 0


class _Rusage:
    ru_maxrss = 0


def getrusage(who):
    return _Rusage()


fake_resource.getrusage = getrusage
sys.modules["resource"] = fake_resource

# --- 执行目标脚本 ---
if len(sys.argv) < 2:
    print("usage: win_wrapper.py <target_script.py> [args...]", file=sys.stderr)
    sys.exit(2)

target = sys.argv[1]
sys.argv = [target] + sys.argv[2:]

with open(target, "r", encoding="utf-8") as f:
    code = f.read()

# 关键：让目标脚本里的 __file__ 解析到它自己的路径（而不是 wrapper 的）
g = dict(globals())
g["__file__"] = target
g["__name__"] = "__main__"
exec(compile(code, target, "exec"), g)
