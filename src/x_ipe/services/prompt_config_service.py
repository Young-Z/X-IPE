"""
Prompt Configuration Service for FEATURE-028-A/B.

Provides:
- migrate_prompt_config(): v2.0 → v3.0 migration for copilot-prompt.json
- extract_language_section(): Extract language-specific content from bilingual templates
"""

import copy

from x_ipe.tracing import x_ipe_tracing


# Chinese translations for known prompt IDs
ZH_TRANSLATIONS = {
    "generate-architecture": {
        "label": "生成架构图",
        "command": "基于<current-idea-file>生成分层架构图"
    },
    "idea-reflection": {
        "label": "创意反思",
        "command": "提取<current-idea-file>中的关键点，然后创建一个子代理，使用这些关键点从项目中学习并给出对创意文件的反馈（反馈应当批判性但建设性），然后你使用反馈来改进创意。"
    },
    "generate-mockup": {
        "label": "生成原型",
        "command": "基于<current-idea-file>生成原型设计"
    },
    "free-question": {
        "label": "自由协作",
        "command": "基于<current-idea-file>进行协作，等待我的指示。"
    },
    "evaluate": {
        "label": "评估项目质量",
        "command": "评估项目质量并生成报告"
    },
    "refactor-all": {
        "label": "全面重构",
        "command": "参照代码和<evaluation-file>进行全面重构"
    },
    "refactor-requirements": {
        "label": "对齐需求与功能",
        "command": "更新需求文档以匹配当前功能规范"
    },
    "refactor-features": {
        "label": "对齐功能与代码",
        "command": "更新功能规范以匹配当前代码实现"
    },
    "refactor-tests": {
        "label": "对齐测试与代码",
        "command": "更新测试用例以匹配当前代码实现，参照<evaluation-file>"
    },
    "refactor-tracing-tests": {
        "label": "对齐追踪与测试",
        "command": "更新追踪装饰器和测试以匹配当前功能规范"
    },
    "refactor-code-tests": {
        "label": "重构代码+追踪+测试",
        "command": "重构代码和测试以匹配当前功能规范，参照<evaluation-file>"
    },
}


@x_ipe_tracing(level="INFO")
def migrate_prompt_config(data):
    """Migrate copilot-prompt.json from v2.0 (or v1.0) to v3.0 format.

    Wraps each prompt's top-level label/command into a prompt-details array
    with EN and ZH entries. Idempotent — v3.0 input is returned unchanged.

    Args:
        data: Parsed JSON dict of copilot-prompt.json

    Returns:
        Migrated v3.0 dict (deep copy, input is not mutated)

    Raises:
        TypeError: If data is not a dict
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__}")

    if data.get("version") == "3.0":
        return data

    result = copy.deepcopy(data)

    # Handle v1.0 legacy: flat prompts[] → ideation.prompts[]
    if "prompts" in result and "ideation" not in result:
        result["ideation"] = {"prompts": result.pop("prompts")}

    # Migrate ideation.prompts[]
    if "ideation" in result and "prompts" in result["ideation"]:
        result["ideation"]["prompts"] = [
            _migrate_prompt(p) for p in result["ideation"]["prompts"]
        ]

    # Migrate evaluation.evaluate (singleton)
    if "evaluation" in result and "evaluate" in result["evaluation"]:
        result["evaluation"]["evaluate"] = _migrate_singleton(
            result["evaluation"]["evaluate"]
        )

    # Migrate evaluation.refactoring[]
    if "evaluation" in result and "refactoring" in result["evaluation"]:
        result["evaluation"]["refactoring"] = [
            _migrate_prompt(p) for p in result["evaluation"]["refactoring"]
        ]

    result["version"] = "3.0"
    return result


def _migrate_prompt(prompt):
    """Migrate a single prompt object: wrap label/command into prompt-details."""
    if "prompt-details" in prompt:
        return prompt

    en_entry = {
        "language": "en",
        "label": prompt.pop("label"),
        "command": prompt.pop("command"),
    }
    prompt["prompt-details"] = [en_entry]

    zh = ZH_TRANSLATIONS.get(prompt.get("id", ""))
    if zh:
        prompt["prompt-details"].append({"language": "zh", **zh})

    return prompt


def _migrate_singleton(prompt):
    """Migrate evaluate singleton — adds id if missing, then delegates."""
    if "id" not in prompt:
        prompt["id"] = "evaluate"
    return _migrate_prompt(prompt)


@x_ipe_tracing(level="INFO")
def extract_language_section(template, language):
    """Extract content for a specific language from a bilingual template.

    Templates use ---LANG:xx--- markers to delimit language sections.

    Args:
        template: Full template string with ---LANG:xx--- markers
        language: Target language code ("en" or "zh")

    Returns:
        Extracted content without the marker line.
        If no markers found, returns the full template (backward compat).
    """
    marker = f"---LANG:{language}---"
    lines = template.split("\n")

    collecting = False
    result_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == marker:
            collecting = True
            continue
        elif stripped.startswith("---LANG:") and stripped.endswith("---") and collecting:
            break
        elif collecting:
            result_lines.append(line)

    if not result_lines:
        return template.strip()

    return "\n".join(result_lines).strip()
