#!/usr/bin/env bash
# 把 make-skill-legacy-takeover-output/apply/ 下的文件放到项目里的固定位置。
# 由用户确认内容后手动运行；目标位置已有同名文件时跳过并列出，绝不覆盖。
#
# 用法（在项目根目录执行）：
#   bash make-skill-legacy-takeover-output/apply/apply.sh            # 实际复制
#   bash make-skill-legacy-takeover-output/apply/apply.sh --dry-run  # 只看会做什么
set -euo pipefail

APPLY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$APPLY_DIR/../.." && pwd)"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

copied=(); skipped=()
while IFS= read -r -d '' src; do
  rel="${src#"$APPLY_DIR"/}"
  [[ "$rel" == "apply.sh" ]] && continue
  dest="$PROJECT_ROOT/$rel"
  if [[ -e "$dest" ]]; then
    skipped+=("$rel")
    continue
  fi
  if [[ $DRY_RUN -eq 0 ]]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
  fi
  copied+=("$rel")
done < <(find "$APPLY_DIR" -type f -print0 | sort -z)

[[ $DRY_RUN -eq 1 ]] && echo "（--dry-run：没有实际复制）"
echo "放到项目里的文件（${#copied[@]}）："
for f in "${copied[@]}"; do echo "  + $f"; done
echo "已存在、跳过的文件（${#skipped[@]}）："
for f in "${skipped[@]}"; do echo "  = $f   （请对照 apply/$f 手动合并，合并建议见 README.md 第五节）"; done
if [[ ${#copied[@]} -gt 0 && $DRY_RUN -eq 0 ]]; then
  echo
  echo "如果放了 .claude/skills/ 下的技能，请完全退出 Claude Code 再重新启动，技能才会生效。"
fi
