#!/usr/bin/env python3
"""
人工智能行业动态周报 — 主入口
串联 JSON验证 → PDF生成 流程。

用法:
  python main.py data/weekly_report.json                # 从JSON生成PDF
  python main.py data/weekly_report.json -o output/     # 指定输出目录
"""
import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_renderer import build_pdf
from validator import validate_report


def main():
    parser = argparse.ArgumentParser(description="AI行业动态周报 PDF 生成器")
    parser.add_argument(
        "json_file", type=str,
        help="周报 JSON 数据文件路径",
    )
    parser.add_argument(
        "-o", "--output-dir", type=str, default="output",
        help="PDF 输出目录（默认: output）",
    )
    args = parser.parse_args()

    json_path = args.json_file
    if not os.path.exists(json_path):
        print(f"❌ JSON 文件不存在: {json_path}")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")

    # ---- Step 1: JSON 验证 ----
    print("=" * 60)
    print("🔍 Step 1/2: JSON 验证")
    print("=" * 60)
    if not validate_report(json_path):
        print("❌ JSON 验证未通过，请检查数据文件")
        sys.exit(1)

    # ---- Step 2: PDF 生成 ----
    print("\n" + "=" * 60)
    print("📄 Step 2/2: PDF 生成")
    print("=" * 60)
    pdf_path = os.path.join(output_dir, f"AI行业动态周报_{date_str}.pdf")
    try:
        build_pdf(json_path, pdf_path)
    except Exception as exc:
        print(f"❌ PDF 生成失败: {exc}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"🎉 周报生成完毕！")
    print(f"   JSON: {json_path}")
    print(f"   PDF:  {pdf_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
