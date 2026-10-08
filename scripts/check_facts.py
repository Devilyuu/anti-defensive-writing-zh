#!/usr/bin/env python3
"""比对原稿与改稿的硬信息，只报告，不改写。

用法：
    python check_facts.py 原稿.md 改稿.md
    python check_facts.py 原稿.md 改稿.md --quiet   # 只在有差异时输出

检查对象（按字面比对，多重集）：
    数字与单位、百分比、日期、版本号、URL、引用标记（\\cite{}、[1]、(作者, 年份)）、
    代码块与行内代码、引号内的引文、英文术语与缩写。
另外统计否定、情态、强度、归因四类“语义承载词”的前后数量，供人工核对，不下结论。

查不到什么（请人工回查）：
    数值互换（“修了 3 个 bug、上了 12 个功能”互换后数字仍在）；
    “多数”改成“全部”、相关改成因果、参与改成负责；
    否定反转时数字仍在（“不足 10%”改成“超过 10%”只会报出“不足”少了一个）；
    中文数字只覆盖常见量词组合（三倍、两小时、五十人），不覆盖所有写法。

退出码：发现硬信息缺失或新增时返回 1，否则 0。零依赖，Python 3.8+。
"""
import re
import sys
from collections import Counter

CN_NUM = "零一二两三四五六七八九十百千万亿点"
UNITS = (
    r"(?:%|％|倍|次|人|名|位|个|件|项|篇|页|张|条|段|章|节|年|个月|月|周|天|日|小时|分钟|秒|"
    r"ms|毫秒|元|万元|亿元|万|亿|km|m|cm|mm|kg|g|GB|MB|KB|TB|分|级|届|轮|组|批|家|所|台|套|份|例|字)"
)

PATTERNS = {
    "日期": [
        r"\d{4}\s*年\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?",
        r"\d{1,2}\s*月\s*\d{1,2}\s*日",
        r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b",
        r"\b\d{4}[-/.]\d{1,2}\b",
    ],
    "百分比": [
        r"\d+(?:\.\d+)?\s*[%％]",
        r"百分之[" + CN_NUM + r"]+",
        r"[" + CN_NUM + r"]+成(?![绩本])",
    ],
    "数字": [
        r"(?<![\d.])\d+(?:[.,]\d+)*\s*" + UNITS + r"?(?![\d.])",
        r"(?<![" + CN_NUM + r"])[" + CN_NUM + r"]{1,6}\s*" + UNITS + r"(?![" + CN_NUM + r"])",
    ],
    "版本号": [r"\bv?\d+\.\d+(?:\.\d+)*\b"],
    "URL": [r"https?://[^\s\]\)）>」”\"'\u3000-\u303f\uff00-\uffef\u4e00-\u9fff]+"],
    "引用标记": [
        r"\\cite[a-zA-Z]*\{[^}]*\}",
        r"\[\d{1,3}(?:[-–,]\s*\d{1,3})*\]",
        r"[（(][A-Za-z\u4e00-\u9fff][^（）()]{0,40}?[,，]\s*\d{4}[a-z]?[)）]",
    ],
    "代码块": [r"```[\s\S]*?```", r"`[^`\n]+`"],
    "引文": [r"“[^”]{2,}”", r"「[^」]{2,}」", r"\"[^\"\n]{4,}\""],
    "术语缩写": [r"\b[A-Z][A-Za-z0-9+#\-]{1,}(?:\s[A-Z][A-Za-z0-9+#\-]{1,})*\b"],
}

SEMANTIC = {
    "否定": r"(?:不是|并非|没有|无法|不能|不会|不再|未能|尚未|并不|不|没|无|非|未|否)",
    "情态": r"(?:可能|可以|或许|也许|大概|似乎|应该|应当|必须|需要|计划|正在|已经|将会|将|尚|仍|暂)",
    "强度": r"(?:显著|全面|彻底|大幅|明显|有效|充分|极大|重大|严重|轻微|略|稍)",
    "归因": r"(?:研究表明|据|专家(?:认为|指出)|用户反馈|数据显示|众所周知|普遍认为|有人说|业内)",
}


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def strip_code(text):
    return re.sub(r"```[\s\S]*?```", " ", text)


MASK_FIRST = ("URL", "引用标记", "代码块")


def extract(text):
    found = {}
    masked = text
    for name in MASK_FIRST:
        for r in PATTERNS[name]:
            masked = re.sub(r, " ", masked)
    for name, regs in PATTERNS.items():
        bag = Counter()
        source = text if name in MASK_FIRST else masked
        for r in regs:
            for m in re.finditer(r, source):
                token = re.sub(r"\s+", "", m.group(0))
                bag[token] += 1
        found[name] = bag
    return found


def diff_bags(a, b):
    missing = Counter()
    added = Counter()
    for k in set(a) | set(b):
        d = a[k] - b[k]
        if d > 0:
            missing[k] = d
        elif d < 0:
            added[k] = -d
    return missing, added


def semantic_bags(text):
    body = strip_code(text)
    return {name: Counter(re.findall(r, body)) for name, r in SEMANTIC.items()}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    quiet = "--quiet" in argv
    src, dst = read(argv[1]), read(argv[2])
    a, b = extract(src), extract(dst)
    problems = 0
    lines = []
    for name in PATTERNS:
        missing, added = diff_bags(a[name], b[name])
        if not missing and not added:
            continue
        problems += 1
        lines.append(f"[{name}]")
        for k, n in sorted(missing.items()):
            lines.append(f"  缺失 ×{n}: {k[:80]}")
        for k, n in sorted(added.items()):
            lines.append(f"  新增 ×{n}: {k[:80]}")
    sa, sb = semantic_bags(src), semantic_bags(dst)
    sem_lines = []
    for name in SEMANTIC:
        missing, added = diff_bags(sa[name], sb[name])
        total_a, total_b = sum(sa[name].values()), sum(sb[name].values())
        detail = ""
        if missing or added:
            parts = []
            if missing:
                parts.append("少了 " + "、".join(f"{k}×{n}" for k, n in sorted(missing.items())))
            if added:
                parts.append("多了 " + "、".join(f"{k}×{n}" for k, n in sorted(added.items())))
            detail = "  ← " + "；".join(parts) + "。请逐处核对含义"
        sem_lines.append(f"  {name}: 原稿 {total_a} → 改稿 {total_b}{detail}")
    if problems == 0 and quiet:
        return 0
    print(f"原稿 {len(src)} 字符 → 改稿 {len(dst)} 字符（{len(dst) / max(len(src), 1):.0%}）")
    if problems:
        print("硬信息差异（字面比对；缺失要么是误删，要么是你有意合并，请逐条确认）：")
        print("\n".join(lines))
    else:
        print("硬信息：数字、日期、百分比、URL、引用、代码、引文、术语未见缺失或新增。")
    print("语义承载词（只提示，不判定；词没变也可能对象或范围变了）：")
    print("\n".join(sem_lines))
    print("本脚本查不到：数值互换、多数→全部、相关→因果、参与→负责、否定反转。这些靠回查清单。")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
