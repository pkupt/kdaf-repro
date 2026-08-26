# -*- coding: utf-8 -*-
"""KDAF 复现验证：把我们跑出的检索指标 vs 作者存档的 definitive 指标逐字段对比。

用法:
    python compare_metrics.py \
        --ours   <retrieval_metrics.json 我们跑出的> \
        --author <seed_invariant_retrieval_metrics.json 作者存档的>

判定原则：所有可比字段精确相等（浮点误差 < 1e-9）才算 PASS。
每个系统对比 M1(跨公司泄漏)/M2(off-period)/M4(token)/M5(hop)/M6(血缘失败)/M7(重放)/M8(图规模)。
"""
import argparse
import json

ALLOWED_EPS = 1e-9

# 环境相关字段：允许差异（硬件/OS 决定的性能量），不影响"复现成功"判定。
# 行为字段必须精确一致；性能字段差异要报告但不算 FAIL。
ENV_SENSITIVE_SUFFIXES = (
    "graph_build_peak_rss_bytes",   # 内存峰值：Windows 无 resource 模块，我们注入的值为 0
    "retrieval_wall_clock_p50_ms",  # 检索延迟：取决于 CPU，非行为
)


def is_env_sensitive(path: str) -> bool:
    return any(path.endswith(s) for s in ENV_SENSITIVE_SUFFIXES)


def approx(a, b, eps=ALLOWED_EPS):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < eps
    return a == b


def compare_field(path, ours, author, results):
    """递归对比 JSON 字段；按 行为/性能 分类记录差异。"""
    if isinstance(ours, dict) and isinstance(author, dict):
        for k in set(ours) | set(author):
            if k in ours and k in author:
                compare_field(f"{path}.{k}", ours[k], author[k], results)
            elif k in ours:
                results.append(("MISSING-IN-AUTHOR", path + "." + k))
            else:
                results.append(("EXTRA-IN-AUTHOR", path + "." + k))
    elif isinstance(ours, list) and isinstance(author, list):
        if len(ours) != len(author):
            results.append(("LEN-DIFF", f"{path}: {len(ours)} vs {len(author)}"))
        for i, (a, b) in enumerate(zip(ours, author)):
            compare_field(f"{path}[{i}]", a, b, results)
    else:
        if not approx(ours, author):
            if is_env_sensitive(path):
                results.append(("ENV-DIFF", f"{path}: ours={ours!r} author={author!r}"))
            else:
                results.append(("DIFF", f"{path}: ours={ours!r} author={author!r}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", required=True)
    ap.add_argument("--author", required=True)
    args = ap.parse_args()

    ours = json.load(open(args.ours, encoding="utf-8"))
    author = json.load(open(args.author, encoding="utf-8"))

    # 只看检索指标部分（systems 下的 M1-M8）
    o_sys = ours.get("systems", {})
    a_sys = author.get("systems", {})
    diffs = []
    for name in sorted(set(o_sys) | set(a_sys)):
        if name not in o_sys or name not in a_sys:
            diffs.append(("SYSTEM-MISSING", name))
            continue
        compare_field(f"systems.{name}", o_sys[name], a_sys[name], diffs)

    behavior_diff = [d for d in diffs if d[0] in ("DIFF", "SYSTEM-MISSING", "LEN-DIFF", "MISSING-IN-AUTHOR", "EXTRA-IN-AUTHOR")]
    env_diff = [d for d in diffs if d[0] == "ENV-DIFF"]

    if not behavior_diff:
        print("✅ 行为指标全部一致（跨公司泄漏/off-period/血缘/重放/hop/token/图规模）")
        if env_diff:
            print(f"ℹ️  {len(env_diff)} 处环境相关差异（性能量，不影响复现判定）:")
            for _, d in env_diff[:10]:
                print("     ", d)
        print("✅ 判定：复现成功（行为等价）")
        return 0

    print(f"❌ {len(behavior_diff)} 处行为不一致:")
    for _, d in behavior_diff[:30]:
        print("  ", d)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
