#!/usr/bin/env python3
"""
人工智能行业动态周报 — PDF 渲染器
严格复刻参考PDF版式，从JSON数据生成专业排版的PDF周报。
"""
import json
import os
import urllib.request
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

# ============================================================
# 字体注册
# ============================================================
FONT_SEARCH_PATHS = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
]


def _find_font(paths: list[str]) -> str:
    for p in paths:
        if os.path.exists(p):
            return p
    raise RuntimeError(
        "无法找到中文字体文件，请安装 fonts-wqy-microhei 或 fonts-wqy-zenhei"
    )


_font_path = _find_font(FONT_SEARCH_PATHS)
pdfmetrics.registerFont(TTFont("CN", _font_path))
pdfmetrics.registerFont(TTFont("CNB", _font_path))

FONT = "CN"
FONTB = "CNB"

# ============================================================
# 颜色定义（严格匹配参考PDF）
# ============================================================
C_BLUE = colors.HexColor("#2c6e9e")
C_RED = colors.HexColor("#c0392b")
C_TEXT = colors.HexColor("#333333")
C_GRAY = colors.HexColor("#888888")
C_LGRAY = colors.HexColor("#cccccc")
C_BG_GRAY = colors.HexColor("#f5f5f5")
C_WHITE = colors.white
C_TH_BG = colors.HexColor("#2c6e9e")
C_ROW_ALT = colors.HexColor("#f9f9f9")

PAGE_W, PAGE_H = A4
MARGIN_LR = 20 * mm
MARGIN_TB = 15 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_LR

# ============================================================
# 样式定义
# ============================================================
s_title = ParagraphStyle(
    "Title", fontName=FONTB, fontSize=24, leading=34,
    alignment=TA_CENTER, textColor=C_BLUE,
)
s_subtitle = ParagraphStyle(
    "Subtitle", fontName=FONT, fontSize=10, leading=16,
    alignment=TA_CENTER, textColor=C_GRAY, spaceAfter=8 * mm,
)
s_editor_label = ParagraphStyle(
    "EditorLabel", fontName=FONTB, fontSize=10.5,
    leading=16, textColor=C_TEXT, spaceBefore=2 * mm,
)
s_editor_body = ParagraphStyle(
    "EditorBody", fontName=FONT, fontSize=10, leading=17,
    alignment=TA_JUSTIFY, textColor=C_TEXT, firstLineIndent=20,
)
s_data_title = ParagraphStyle(
    "DataTitle", fontName=FONTB, fontSize=13, leading=20,
    textColor=C_BLUE, spaceBefore=6 * mm, spaceAfter=3 * mm,
)
s_art_title = ParagraphStyle(
    "ArtTitle", fontName=FONTB, fontSize=13, leading=20,
    textColor=C_BLUE, spaceBefore=5 * mm, spaceAfter=2 * mm,
)
s_source = ParagraphStyle(
    "Source", fontName=FONT, fontSize=8.5, leading=13,
    textColor=C_GRAY, spaceAfter=3 * mm,
)
s_body = ParagraphStyle(
    "Body", fontName=FONT, fontSize=10, leading=17,
    alignment=TA_JUSTIFY, textColor=C_TEXT,
    firstLineIndent=20, spaceAfter=2 * mm,
)
s_tags = ParagraphStyle(
    "Tags", fontName=FONT, fontSize=8.5, leading=13,
    textColor=C_BLUE, spaceBefore=2 * mm, spaceAfter=1 * mm,
)
s_insight_label = ParagraphStyle(
    "InsightLabel", fontName=FONTB, fontSize=10,
    leading=16, textColor=C_TEXT, spaceBefore=1 * mm,
)
s_insight_body = ParagraphStyle(
    "InsightBody", fontName=FONT, fontSize=9.5, leading=16,
    alignment=TA_JUSTIFY, textColor=C_TEXT,
    firstLineIndent=19, spaceAfter=1 * mm,
)
s_caption = ParagraphStyle(
    "Caption", fontName=FONT, fontSize=8.5, leading=13,
    textColor=C_GRAY, alignment=TA_CENTER,
    spaceBefore=1 * mm, spaceAfter=3 * mm,
)
s_weekly_body = ParagraphStyle(
    "WeeklyBody", fontName=FONT, fontSize=10, leading=17,
    alignment=TA_JUSTIFY, textColor=C_TEXT,
    firstLineIndent=20, spaceAfter=3 * mm,
)
s_disclaimer = ParagraphStyle(
    "Disclaimer", fontName=FONT, fontSize=8, leading=13,
    alignment=TA_CENTER, textColor=C_GRAY,
)


# ============================================================
# 辅助函数
# ============================================================
def _download_image(url: str, max_w: float = CONTENT_W * 0.85,
                    max_h: float = 65 * mm):
    """下载远程图片并返回 ReportLab Image 对象。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        img_data = BytesIO(resp.read())
        img = Image(img_data)
        w, h = img.drawWidth, img.drawHeight
        if w > max_w:
            ratio = max_w / w
            w, h = max_w, h * ratio
        if h > max_h:
            ratio = max_h / h
            w, h = w * ratio, max_h
        img.drawWidth = w
        img.drawHeight = h
        img.hAlign = "CENTER"
        return img
    except Exception as exc:
        print(f"  [WARN] 图片下载失败: {exc}")
        return None


def _make_section_banner(title: str):
    """红色板块标题条（■ 标题）。"""
    clean = title
    for prefix in ("一、", "二、", "三、", "四、", "五、", "六、"):
        clean = clean.replace(prefix, "")
    p = Paragraph(
        f'<font color="white"><b>\u25a0 {clean}</b></font>',
        ParagraphStyle(
            "Banner", fontName=FONTB, fontSize=13, leading=20,
            textColor=C_WHITE, alignment=TA_LEFT,
        ),
    )
    t = Table([[p]], colWidths=[CONTENT_W], rowHeights=[10 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_RED),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _make_insight_block(text: str):
    """电力行业启示区块（蓝色左竖线 + 浅灰背景）。"""
    label = Paragraph("<b>\u258c 电力行业启示</b>", s_insight_label)
    body = Paragraph(f"    {text}", s_insight_body)
    inner = Table([[label], [body]], colWidths=[CONTENT_W - 12 * mm])
    inner.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 1 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    outer = Table([[inner]], colWidths=[CONTENT_W - 4 * mm])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_BG_GRAY),
        ("LINEBEFORESTYLE", (0, 0), (0, -1), "SOLID"),
        ("LINEBEFOREWIDTH", (0, 0), (0, -1), 3),
        ("LINEBEFORECOLOR", (0, 0), (0, -1), C_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    return outer


def _make_data_table(highlights: list[dict]):
    """关键数据表格（4列：指标、数值、变化、来源）。"""
    header = ["指标", "数值", "变化", "来源"]
    h_sty = ParagraphStyle(
        "TH", fontName=FONTB, fontSize=9.5, leading=14,
        textColor=C_WHITE, alignment=TA_CENTER,
    )
    d_sty = ParagraphStyle(
        "TD", fontName=FONT, fontSize=9, leading=14,
        textColor=C_TEXT, alignment=TA_CENTER,
    )
    d_sty_b = ParagraphStyle(
        "TDB", fontName=FONTB, fontSize=9.5, leading=14,
        textColor=C_TEXT, alignment=TA_CENTER,
    )
    rows = [[Paragraph(h, h_sty) for h in header]]
    for hl in highlights:
        rows.append([
            Paragraph(hl.get("indicator", ""), d_sty),
            Paragraph(f'<b>{hl.get("metric", "")}</b>', d_sty_b),
            Paragraph(hl.get("change", ""), d_sty),
            Paragraph(hl.get("source", ""), d_sty),
        ])
    col_ws = [CONTENT_W * r for r in (0.28, 0.22, 0.28, 0.22)]
    t = Table(rows, colWidths=col_ws)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), C_TH_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_LGRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), C_ROW_ALT))
    t.setStyle(TableStyle(cmds))
    return t


# ============================================================
# 页眉页脚
# ============================================================
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont(FONT, 8)
    canvas.setFillColor(C_GRAY)
    canvas.drawString(MARGIN_LR, h - MARGIN_TB + 2 * mm, "人工智能行业动态周报")
    canvas.drawRightString(w - MARGIN_LR, h - MARGIN_TB + 2 * mm, doc._report_period)
    canvas.setStrokeColor(C_LGRAY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_LR, h - MARGIN_TB, w - MARGIN_LR, h - MARGIN_TB)
    canvas.line(MARGIN_LR, MARGIN_TB, w - MARGIN_LR, MARGIN_TB)
    canvas.setFont(FONT, 7)
    canvas.drawCentredString(w / 2, MARGIN_TB - 4 * mm,
                             f"— 第 {doc.page} 页 —")
    canvas.drawRightString(w - MARGIN_LR, MARGIN_TB - 4 * mm,
                           "内部参考  请勿外传")
    canvas.restoreState()


def _first_page_footer(canvas, doc):
    canvas.saveState()
    w, _ = A4
    canvas.setFont(FONT, 7)
    canvas.setFillColor(C_GRAY)
    canvas.drawCentredString(w / 2, MARGIN_TB - 4 * mm,
                             f"— 第 {doc.page} 页 —")
    canvas.restoreState()


# ============================================================
# 主构建函数
# ============================================================
def build_pdf(json_path: str, output_path: str) -> str:
    """从 JSON 数据文件生成 PDF 周报，返回输出文件路径。"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=MARGIN_TB + 3 * mm,
        bottomMargin=MARGIN_TB + 3 * mm,
        leftMargin=MARGIN_LR,
        rightMargin=MARGIN_LR,
    )
    doc._report_period = data.get("report_period", "")
    story: list = []

    # ---- 封面页 ----
    story.append(Spacer(1, 20 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=C_LGRAY,
                            spaceAfter=15 * mm))
    story.append(Paragraph(data["report_title"], s_title))
    story.append(Paragraph(
        f"报告周期：{data['report_period']}  编制日期：{data['report_date']}",
        s_subtitle,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C_LGRAY,
                            spaceBefore=2 * mm, spaceAfter=8 * mm))

    # 编者按
    ed_label = Paragraph("<b>【编者按】</b>", s_editor_label)
    ed_body = Paragraph(data["editor_note"], s_editor_body)
    ed_tbl = Table([[ed_label], [ed_body]], colWidths=[CONTENT_W - 8 * mm])
    ed_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, C_LGRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
    ]))
    story.append(ed_tbl)
    story.append(Spacer(1, 6 * mm))

    # 关键数据
    story.append(Paragraph("<b>本周关键数据</b>", s_data_title))
    story.append(_make_data_table(data.get("data_highlights", [])))
    story.append(PageBreak())

    # ---- 正文各板块 ----
    for section in data["sections"]:
        story.append(Spacer(1, 6 * mm))
        story.append(_make_section_banner(section["section_title"]))
        story.append(Spacer(1, 4 * mm))

        for idx, art in enumerate(section["articles"]):
            story.append(Paragraph(f"<b>{art['title']}</b>", s_art_title))
            story.append(Paragraph(
                f"来源：{art['source']}  日期：{art['date']}", s_source,
            ))

            if art.get("image_url"):
                print(f"  下载图片: {art['title'][:30]}...")
                img = _download_image(art["image_url"])
                if img:
                    story.append(img)
                    if art.get("image_caption"):
                        story.append(Paragraph(
                            f"\u25b2 {art['image_caption']}", s_caption,
                        ))

            story.append(Paragraph(art["summary"], s_body))

            if art.get("tags"):
                story.append(Paragraph(
                    "  ".join(f"#{t}" for t in art["tags"]), s_tags,
                ))

            story.append(Spacer(1, 2 * mm))
            story.append(_make_insight_block(art["analysis"]))
            story.append(Spacer(1, 3 * mm))

            if idx < len(section["articles"]) - 1:
                story.append(Spacer(1, 2 * mm))
                story.append(HRFlowable(
                    width="60%", thickness=0.5, color=C_LGRAY,
                    spaceBefore=1 * mm, spaceAfter=1 * mm,
                ))

    # ---- 周度洞察 ----
    insight = data.get("weekly_insight", {})
    if insight:
        story.append(Spacer(1, 6 * mm))
        p = Paragraph(
            '<font color="white"><b>\u25a0 周度洞察</b></font>',
            ParagraphStyle(
                "BannerInsight", fontName=FONTB, fontSize=13, leading=20,
                textColor=C_WHITE, alignment=TA_LEFT,
            ),
        )
        t = Table([[p]], colWidths=[CONTENT_W], rowHeights=[10 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_RED),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))
        for para in insight.get("content", "").split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, s_weekly_body))

    # ---- 免责声明 ----
    story.append(Spacer(1, 15 * mm))
    story.append(HRFlowable(width="60%", thickness=0.5, color=C_LGRAY,
                            spaceAfter=4 * mm))
    story.append(Paragraph("仅供内部参考，不代表公司官方立场", s_disclaimer))

    doc.build(story, onFirstPage=_first_page_footer, onLaterPages=_header_footer)
    print(f"\n✅ PDF生成成功: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    json_in = sys.argv[1] if len(sys.argv) > 1 else "data/weekly_report.json"
    pdf_out = sys.argv[2] if len(sys.argv) > 2 else "output/AI行业动态周报.pdf"
    build_pdf(json_in, pdf_out)
