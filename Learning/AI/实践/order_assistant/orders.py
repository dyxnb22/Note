"""订单数据、访问范围与示例规则；由两个入口共用。"""

import json
from pathlib import Path

DEFAULT_DATA = Path(__file__).parent / "data" / "orders.json"
STATUSES = {"pending", "shipped", "cancelled"}


class OrderNotFound(Exception):
    """在当前身份的可见范围内找不到订单。"""


def load_orders(path: Path = DEFAULT_DATA) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("订单文件的根节点必须是列表")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("每条订单必须是对象")
        for key in ("order_id", "tenant_id"):
            value = row.get(key)
            if not isinstance(value, str) or not 1 <= len(value) <= 32:
                raise ValueError(f"{key} 必须是 1 到 32 个字符的字符串")
        if row.get("status") not in STATUSES:
            raise ValueError("订单状态不在示例允许范围内")
        if type(row.get("version")) is not int or row["version"] < 1:
            raise ValueError("订单版本必须是正整数")
        identity = (row["tenant_id"], row["order_id"])
        if identity in seen:
            raise ValueError("同一租户中出现重复订单号")
        seen.add(identity)
    return rows


def lookup_order(rows: list[dict], tenant_id: str, order_id: str) -> dict:
    for row in rows:
        if row["tenant_id"] == tenant_id and row["order_id"] == order_id:
            return {key: row[key] for key in ("order_id", "status", "version")}
    raise OrderNotFound(f"当前可访问范围内找不到订单 {order_id}")


def lookup_policy(status: str) -> dict:
    if status not in STATUSES:
        raise ValueError("未知订单状态")
    return {
        "policy_id": "cancel-v1",
        "status": status,
        "can_request_cancellation": status == "pending",
        "rule": "本例仅允许 pending 状态的订单申请取消。",
    }


def consultation(order: dict, policy: dict) -> dict:
    if order["status"] != policy["status"]:
        raise ValueError("订单状态与规则适用状态不一致")
    return {
        "order_id": order["order_id"],
        "status": order["status"],
        "version": order["version"],
        "policy_id": policy["policy_id"],
        "can_request_cancellation": policy["can_request_cancellation"],
    }
