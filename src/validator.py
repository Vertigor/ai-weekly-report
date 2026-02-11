#!/usr/bin/env python3
"""
人工智能行业动态周报 — JSON 数据验证器
检查周报 JSON 文件的结构完整性和内容规范性。
"""
import json
import sys


def validate_report(filepath: str) -> bool:
    """验证周报 JSON 文件，返回是否通过。"""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. 解析 JSON
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"❌ JSON解析失败: {exc}")
        return False
    print("✅ JSON格式合法")

    # 2. 顶层字段
    required_top = [
        "report_title", "report_period", "report_date",
        "target_audience", "editor_note", "sections",
        "weekly_insight", "data_highlights",
    ]
    for field in required_top:
        if field not in data:
            errors.append(f"缺少顶层字段: {field}")
        elif not data[field]:
            errors.append(f"顶层字段为空: {field}")

    # 3. sections
    sections = data.get("sections", [])
    if len(sections) < 2:
        errors.append(f"板块数量不足: {len(sections)} (要求至少2个)")

    total_articles = 0
    article_ids: set = set()

    for i, section in enumerate(sections):
        if "section_title" not in section:
            errors.append(f"第{i+1}个板块缺少 section_title")
        if "articles" not in section:
            errors.append(f"第{i+1}个板块缺少 articles")
            continue

        for article in section.get("articles", []):
            total_articles += 1
            aid = article.get("id")

            for field in ("id", "title", "source", "date", "url",
                          "summary", "analysis", "tags"):
                if field not in article:
                    errors.append(f"文章{aid}缺少字段: {field}")
                elif not article[field]:
                    errors.append(f"文章{aid}字段为空: {field}")

            if aid in article_ids:
                errors.append(f"文章ID重复: {aid}")
            article_ids.add(aid)

            if not article.get("image_url"):
                warnings.append(f"文章{aid}缺少配图URL")
            if not article.get("image_caption"):
                warnings.append(f"文章{aid}缺少图片说明")

            summary_len = len(article.get("summary", ""))
            if summary_len < 100:
                warnings.append(f"文章{aid}摘要过短: {summary_len}字")
            elif summary_len > 500:
                warnings.append(f"文章{aid}摘要过长: {summary_len}字")

            if len(article.get("analysis", "")) < 50:
                warnings.append(f"文章{aid}解读过短")
            if len(article.get("tags", [])) < 2:
                warnings.append(f"文章{aid}标签过少")

            date_str = article.get("date", "")
            if date_str and not (len(date_str) == 10
                                 and date_str[4] == "-"
                                 and date_str[7] == "-"):
                warnings.append(f"文章{aid}日期格式不规范: {date_str}")

    if total_articles < 8:
        errors.append(f"文章总数不足: {total_articles} (要求8-10条)")
    elif total_articles > 12:
        warnings.append(f"文章总数偏多: {total_articles}")

    # 4. weekly_insight
    insight = data.get("weekly_insight", {})
    if not insight.get("title"):
        errors.append("weekly_insight 缺少 title")
    if not insight.get("content"):
        errors.append("weekly_insight 缺少 content")
    elif len(insight["content"]) < 100:
        warnings.append(f"weekly_insight 内容过短: {len(insight['content'])}字")

    # 5. data_highlights
    highlights = data.get("data_highlights", [])
    if len(highlights) < 3:
        warnings.append(f"数据亮点过少: {len(highlights)}个")
    for k, h in enumerate(highlights):
        if "metric" not in h:
            errors.append(f"第{k+1}个数据亮点缺少 metric")

    # 6. 输出
    print(f"\n📊 检查结果汇总:")
    print(f"  板块数: {len(sections)}")
    print(f"  文章总数: {total_articles}")
    print(f"  数据亮点数: {len(highlights)}")
    print(f"  错误数: {len(errors)}")
    print(f"  警告数: {len(warnings)}")

    if errors:
        print(f"\n❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print("\n✅ 所有必需检查项通过！")
        return True
    print("\n❌ 存在错误，需要修复！")
    return False


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/weekly_report.json"
    ok = validate_report(path)
    sys.exit(0 if ok else 1)
