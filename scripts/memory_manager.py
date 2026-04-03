#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆管理器 - 管理 .memory 文件夹
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

MEMORY_DIR = ".memory"
FILES = {
    "project_context": "project-context.json",
    "terminology": "terminology.json",
    "generation_history": "generation-history.json",
    "user_preferences": "user-preferences.json",
    "ambiguity_decisions": "ambiguity-decisions.json"
}


def init_memory(project_path: str, template_dir: str = "templates",
                requirements_dir: str = "requirements"):
    """初始化 .memory 文件夹"""
    memory_path = Path(project_path) / MEMORY_DIR
    memory_path.mkdir(exist_ok=True)

    # 初始化 project-context.json
    context = {
        "project_name": Path(project_path).name,
        "initialized_at": datetime.now().isoformat(),
        "template_dir": template_dir,
        "requirements_dir": requirements_dir,
        "output_dir": "./test-docs"
    }

    with open(memory_path / FILES["project_context"], 'w', encoding='utf-8') as f:
        json.dump(context, f, ensure_ascii=False, indent=2)

    # 初始化其他文件
    defaults = {
        "terminology": {"domain_terms": {}, "module_abbreviations": {}},
        "generation_history": {"generations": []},
        "user_preferences": {
            "last_output_formats": ["excel", "traceability"],
            "default_output_dir": "./test-docs",
            "show_samples_in_preview": True,
            "auto_confirm_parsing": False,
            "ambiguity_handling": "ask",
            "priority_distribution": {
                "p0_min": 10,
                "p0_max": 15,
                "warn_on_imbalance": True
            },
            "updated_at": None
        },
        "ambiguity_decisions": {"decisions": []}
    }

    for key, default_value in defaults.items():
        file_path = memory_path / FILES[key]
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_value, f, ensure_ascii=False, indent=2)

    print(f"已初始化记忆: {memory_path}")
    return str(memory_path)


def read_memory(project_path: str, memory_type: str) -> dict:
    """读取记忆文件"""
    file_path = Path(project_path) / MEMORY_DIR / FILES.get(memory_type, "")
    if not file_path.exists():
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_memory(project_path: str, memory_type: str, data: dict, merge: bool = True):
    """更新记忆文件"""
    file_path = Path(project_path) / MEMORY_DIR / FILES.get(memory_type, "")

    if merge and file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

        # 深度合并
        def deep_merge(base, updates):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        data = deep_merge(existing, data)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已更新: {file_path}")


def add_generation_record(project_path: str, record: dict):
    """添加生成记录"""
    history = read_memory(project_path, "generation_history")
    if "generations" not in history:
        history["generations"] = []

    record["date"] = datetime.now().isoformat()
    history["generations"].append(record)

    update_memory(project_path, "generation_history", history, merge=False)


def clear_memory(project_path: str):
    """清除所有记忆"""
    import shutil
    memory_path = Path(project_path) / MEMORY_DIR
    if memory_path.exists():
        shutil.rmtree(memory_path)
        print(f"已清除记忆: {memory_path}")
    else:
        print("记忆不存在")


def get_preferences(project_path: str) -> dict:
    """获取用户偏好设置"""
    return read_memory(project_path, "user_preferences")


def set_preference(project_path: str, key: str, value):
    """设置单个偏好项"""
    prefs = get_preferences(project_path)
    prefs[key] = value
    prefs["updated_at"] = datetime.now().isoformat()
    update_memory(project_path, "user_preferences", prefs, merge=False)


def save_output_formats(project_path: str, formats: list):
    """保存上次使用的输出格式"""
    set_preference(project_path, "last_output_formats", formats)


def add_ambiguity_decision(project_path: str, decision: dict):
    """添加歧义处理决策记录"""
    data = read_memory(project_path, "ambiguity_decisions")
    if "decisions" not in data:
        data["decisions"] = []

    decision["date"] = datetime.now().isoformat()
    data["decisions"].append(decision)

    update_memory(project_path, "ambiguity_decisions", data, merge=False)
    print(f"已记录歧义决策: {decision.get('context', 'unknown')}")


def find_similar_ambiguity(project_path: str, ambiguity_type: str, context: str) -> dict:
    """查找类似的历史歧义决策"""
    data = read_memory(project_path, "ambiguity_decisions")
    decisions = data.get("decisions", [])

    for decision in reversed(decisions):  # 从最新的开始查找
        if decision.get("type") == ambiguity_type:
            # 简单的上下文匹配（可以优化为更智能的匹配）
            if context.lower() in decision.get("context", "").lower():
                return decision
    return None


def main():
    parser = argparse.ArgumentParser(description='管理 .memory 记忆文件夹')
    parser.add_argument('--action', required=True,
                       choices=['init', 'read', 'update', 'clear', 'add-record',
                                'get-prefs', 'set-pref',
                                'add-ambiguity', 'find-ambiguity'],
                       help='操作类型')
    parser.add_argument('--project', default='.', help='项目路径')
    parser.add_argument('--type', help='记忆类型')
    parser.add_argument('--data', help='JSON 格式数据')
    parser.add_argument('--key', help='偏好设置键名')
    parser.add_argument('--value', help='偏好设置值')
    parser.add_argument('--context', help='歧义上下文')
    parser.add_argument('--template-dir', default='templates', help='模板目录')
    parser.add_argument('--requirements-dir', default='requirements', help='需求目录')
    args = parser.parse_args()

    try:
        if args.action == 'init':
            init_memory(args.project, args.template_dir, args.requirements_dir)

        elif args.action == 'read':
            if not args.type:
                print("错误：需要指定 --type", file=sys.stderr)
                sys.exit(1)
            data = read_memory(args.project, args.type)
            print(json.dumps(data, ensure_ascii=False, indent=2))

        elif args.action == 'update':
            if not args.type or not args.data:
                print("错误：需要指定 --type 和 --data", file=sys.stderr)
                sys.exit(1)
            update_memory(args.project, args.type, json.loads(args.data))

        elif args.action == 'clear':
            clear_memory(args.project)

        elif args.action == 'add-record':
            if not args.data:
                print("错误：需要指定 --data", file=sys.stderr)
                sys.exit(1)
            add_generation_record(args.project, json.loads(args.data))

        elif args.action == 'get-prefs':
            prefs = get_preferences(args.project)
            print(json.dumps(prefs, ensure_ascii=False, indent=2))

        elif args.action == 'set-pref':
            if not args.key or not args.value:
                print("错误：需要指定 --key 和 --value", file=sys.stderr)
                sys.exit(1)
            # 尝试解析 JSON，否则作为字符串
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            set_preference(args.project, args.key, value)
            print(f"已设置 {args.key} = {value}")

        elif args.action == 'add-ambiguity':
            if not args.data:
                print("错误：需要指定 --data", file=sys.stderr)
                sys.exit(1)
            add_ambiguity_decision(args.project, json.loads(args.data))

        elif args.action == 'find-ambiguity':
            if not args.type or not args.context:
                print("错误：需要指定 --type 和 --context", file=sys.stderr)
                sys.exit(1)
            result = find_similar_ambiguity(args.project, args.type, args.context)
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("未找到类似决策")

    except Exception as e:
        print(f"操作失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
