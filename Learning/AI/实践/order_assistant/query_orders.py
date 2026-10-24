"""固定路径：命令行输入 → 订单 → 规则 → 咨询结果。"""

import argparse
import json
import sys
from pathlib import Path

from orders import (
    DEFAULT_DATA, OrderNotFound, consultation, load_orders, lookup_order, lookup_policy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="查询示例订单及其取消申请条件")
    parser.add_argument("order_id", help="示例订单号，如 A、B")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    if not 1 <= len(args.order_id) <= 32:
        parser.error("订单号长度须为 1 到 32")
    try:
        rows = load_orders(args.data)
        # 演示已登录身份；不从订单号或模型参数取得租户。
        order = lookup_order(rows, tenant_id="demo", order_id=args.order_id)
        result = consultation(order, lookup_policy(order["status"]))
    except OrderNotFound as exc:
        result = {"error": "not_found", "message": str(exc)}
        code = 2
    except (OSError, ValueError, TypeError):
        result = {"error": "invalid_data", "message": "无法读取有效的订单数据"}
        code = 1
    else:
        code = 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
