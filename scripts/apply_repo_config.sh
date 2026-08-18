#!/usr/bin/env bash
# 一键应用仓库配置(labels + rulesets)。由仓库维护者在有权限的账号下运行。
# 用法: bash scripts/apply_repo_config.sh [OWNER/REPO]
# 默认 OWNER/REPO = Alastair-Jiang/cognitive-os
#
# 依赖: gh CLI 已登录, 且有仓库 write 权限(labels)与 admin 权限(rulesets)。
# 幂等: 可重复运行; 已存在的 label 会更新, 已存在的 ruleset 会全量替换。

set -euo pipefail

REPO="${1:-Alastair-Jiang/cognitive-os}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABELS_FILE="$SCRIPT_DIR/../.github/labels.json"
RULESET_FILE="$SCRIPT_DIR/../.github/rulesets/protect-default-branch.json"

echo "==> 目标仓库: $REPO"
gh api "repos/$REPO" -q '.full_name' >/dev/null || { echo "无法访问仓库, 检查权限与仓库名"; exit 1; }

# ---------- Labels ----------
echo "==> 应用 labels"
if [ -f "$LABELS_FILE" ]; then
  jq -c 'to_entries[] | {name: .key} + .value' "$LABELS_FILE" | while read -r l; do
    name=$(echo "$l" | jq -r .name)
    color=$(echo "$l" | jq -r .color)
    desc=$(echo "$l" | jq -r .description)
    enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$name")
    if gh api "repos/$REPO/labels/$enc" >/dev/null 2>&1; then
      gh api -X PATCH "repos/$REPO/labels/$enc" -f name="$name" -f color="$color" -f description="$desc" --silent
      echo "  label updated: $name"
    else
      gh api -X POST "repos/$REPO/labels" -f name="$name" -f color="$color" -f description="$desc" --silent
      echo "  label created: $name"
    fi
  done
else
  echo "  跳过: 未找到 $LABELS_FILE"
fi

# ---------- Rulesets ----------
if [ -f "$RULESET_FILE" ]; then
  echo "==> 应用 ruleset (protect-default-branch)"
  DEFAULT_BRANCH=$(gh api "repos/$REPO" -q .default_branch)
  BODY=$(python3 - "$RULESET_FILE" "$DEFAULT_BRANCH" <<'PY'
import json, sys
ruleset_path, branch = sys.argv[1], sys.argv[2]
data = json.load(open(ruleset_path, encoding="utf-8"))
data["conditions"]["ref_name"]["include"] = [f"refs/heads/{branch}"]
print(json.dumps(data))
PY
)
  # 幂等: 同名校验
  EXISTING_ID=$(gh api "repos/$REPO/rulesets" -q '.[] | select(.name == "protect-default-branch") | .id' 2>/dev/null || true)
  if [ -n "$EXISTING_ID" ]; then
    echo "$BODY" | gh api -X PUT "repos/$REPO/rulesets/$EXISTING_ID" --input - -q '.name' 2>/dev/null \
      && echo "  ruleset updated: protect-default-branch" \
      || echo "  !! ruleset 更新失败(可能缺 admin 权限)— 请手动在 GitHub UI 或提升权限后重试"
  else
    echo "$BODY" | gh api -X POST "repos/$REPO/rulesets" --input - -q '.name' 2>/dev/null \
      && echo "  ruleset created: protect-default-branch" \
      || echo "  !! ruleset 创建失败(可能缺 admin 权限)— 请手动在 GitHub UI 或提升权限后重试"
  fi
else
  echo "  跳过: 未找到 $RULESET_FILE"
fi

echo "==> 完成。验证:"
gh label list --repo "$REPO" --limit 200 | wc -l | xargs echo "  label 数:"
gh api "repos/$REPO/rulesets" -q '.[] | "  ruleset: \(.name) [\(.enforcement)]"' 2>/dev/null || echo "  (查询 rulesets 失败)"