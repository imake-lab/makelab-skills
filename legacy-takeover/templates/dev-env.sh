#!/usr/bin/env bash
# <项目名> 本地环境脚本：一个脚本管安装和启停。
# 由 legacy-takeover 生成。只读方式下未实测，第一次使用前先看一遍内容。
#
# 用法（在项目根目录执行）：
#   bash make-skill-legacy-takeover-output/scripts/dev-env.sh install   # 装中间件并初始化（建库、推配置）
#   bash make-skill-legacy-takeover-output/scripts/dev-env.sh start     # 按依赖顺序串行启动，等就绪再返回
#   bash make-skill-legacy-takeover-output/scripts/dev-env.sh stop      # 逆序停止
#   bash make-skill-legacy-takeover-output/scripts/dev-env.sh status    # 每个中间件的运行状态和端口监听
set -euo pipefail

# 依赖顺序：被依赖的在前（数据库在应用之前，注册中心在依赖它的服务之前）
SERVICES=("<mysql>" "<redis>" "<nacos>")

wait_port() {  # wait_port <名字> <端口> [超时秒数]
  local name=$1 port=$2 timeout=${3:-60} i
  for ((i = 0; i < timeout; i++)); do
    if (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null; then echo "  $name 就绪（:$port）"; return 0; fi
    sleep 1
  done
  echo "  $name 在 ${timeout}s 内没有就绪（:$port）" >&2
  return 1
}

install() {
  # 每个中间件三步：装、初始化、验证。
  # 用 brew（macOS）或 apt（Linux）。需要 sudo 的命令不要藏在这里静默执行，单独列出并提示。
  # 下载不了的依赖，写清下载链接和放在哪。
  :
}

start() {
  # 混合场景：brew services / systemd / 手动 jar，各自用对应的方式启动。
  # 每个服务 wait_port 通过以后，才启动下一个。
  :
}

stop() {
  :
}

status() {
  # 打印每个中间件：是否在运行、端口是否在监听。
  :
}

case "${1:-}" in
  install|start|stop|status) "$1" ;;
  *) echo "用法：$0 install|start|stop|status" >&2; exit 2 ;;
esac
