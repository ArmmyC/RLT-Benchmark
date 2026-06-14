from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "reports" / "presentation"
PDF_PATH = PRESENTATION / "RTL_LLM_Benchmark_Report_June_2026.pdf"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2E74B5")
LIGHT_BLUE = colors.HexColor("#E8F0F8")
LIGHT_GRAY = colors.HexColor("#F2F4F7")
MID_GRAY = colors.HexColor("#667085")
GOLD = colors.HexColor("#9A6700")
RED = colors.HexColor("#A61B1B")
WHITE = colors.white


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(0.8 * inch, 10.63 * inch, "SILICONCRAFT  |  RTL LLM BENCHMARK")
    canvas.setStrokeColor(colors.HexColor("#D8DEE8"))
    canvas.line(0.8 * inch, 10.52 * inch, 7.7 * inch, 10.52 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(0.8 * inch, 0.42 * inch, "Public benchmark briefing  |  June 2026")
    canvas.drawRightString(7.7 * inch, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="Kicker", parent=s["Normal"], fontName="Helvetica-Bold", fontSize=9, textColor=BLUE, spaceAfter=4))
    s.add(ParagraphStyle(name="ReportTitle", parent=s["Title"], fontName="Helvetica-Bold", fontSize=24, leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=5))
    s.add(ParagraphStyle(name="Subtitle2", parent=s["Normal"], fontName="Helvetica", fontSize=12, leading=15, textColor=MID_GRAY, spaceAfter=16))
    s.add(ParagraphStyle(name="H1x", parent=s["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=BLUE, spaceBefore=12, spaceAfter=7, keepWithNext=True))
    s.add(ParagraphStyle(name="H2x", parent=s["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=BLUE, spaceBefore=9, spaceAfter=5, keepWithNext=True))
    s.add(ParagraphStyle(name="Bodyx", parent=s["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#202124"), spaceAfter=6))
    s.add(ParagraphStyle(name="Smallx", parent=s["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10, textColor=MID_GRAY, spaceAfter=4))
    s.add(ParagraphStyle(name="Captionx", parent=s["BodyText"], fontName="Helvetica-Oblique", fontSize=7.5, leading=9, textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=6))
    s.add(ParagraphStyle(name="Calloutx", parent=s["BodyText"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#202124")))
    s.add(ParagraphStyle(name="TableHeader", parent=s["BodyText"], fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=WHITE, alignment=TA_CENTER))
    s.add(ParagraphStyle(name="TableBody", parent=s["BodyText"], fontName="Helvetica", fontSize=7.4, leading=9, textColor=colors.HexColor("#202124")))
    s.add(ParagraphStyle(name="TableCenter", parent=s["TableBody"], alignment=TA_CENTER))
    return s


S = styles()


def P(text, style="Bodyx"):
    return Paragraph(text, S[style])


def bullets(items, numbered=False):
    return ListFlowable(
        [ListItem(P(item), leftIndent=10) for item in items],
        bulletType="1" if numbered else "bullet",
        start="1",
        leftIndent=17,
        bulletFontName="Helvetica",
        bulletFontSize=8,
        spaceAfter=5,
    )


def callout(label, text, fill=LIGHT_BLUE, label_color=NAVY):
    content = P(f'<font color="{label_color.hexval()}"><b>{label}</b></font>&nbsp;&nbsp;{text}', "Calloutx")
    t = Table([[content]], colWidths=[6.65 * inch], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D8DEE8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def data_table(headers, rows, widths, centered=()):
    data = [[P(str(h), "TableHeader") for h in headers]]
    for row in rows:
        data.append([P(str(value), "TableCenter" if idx in centered else "TableBody") for idx, value in enumerate(row)])
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1, hAlign="CENTER")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C2CF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for idx in range(1, len(data)):
        if idx % 2 == 0:
            commands.append(("BACKGROUND", (0, idx), (-1, idx), LIGHT_GRAY))
    t.setStyle(TableStyle(commands))
    return KeepTogether([t, Spacer(1, 7)])


def build():
    PRESENTATION.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=0.8 * inch,
        leftMargin=0.8 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title="Evaluating Large Language Models for RTL Generation",
        author="SiliconCraft RTL Benchmarking Project",
        subject="Public RTL benchmark comparison",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=header_footer))
    story = []

    story += [Spacer(1, 28), P("TECHNICAL BENCHMARK REPORT", "Kicker"), P("Evaluating Large Language Models for RTL Generation", "ReportTitle"), P("A reproducible comparison across VerilogEval v2, RTLLM 2.0, ProtocolLLM, and RTL-OPT", "Subtitle2")]
    for label, value in [
        ("Prepared by", "SiliconCraft RTL Benchmarking Project"),
        ("Report date", "14 June 2026"),
        ("Models evaluated", "Five public LLM baselines"),
        ("Compute", "Lanta GPU cluster, OpenAI-compatible vLLM endpoints"),
        ("Status", "Completed baseline comparison"),
    ]:
        story.append(P(f"<b>{label}:</b> {value}"))
    story += [Spacer(1, 7), callout("Bottom line", "Qwen3.6 27B is the strongest overall model for functional RTL generation. DeepSeek-Coder-V2-Lite-Instruct leads the RTL-OPT equivalence test, showing the best behavior-preservation rate, but it rarely produces a smaller equivalent circuit."), P("Executive Summary", "H1x"), P("We built a reusable benchmark harness that can swap models through an OpenAI-compatible API while keeping prompts, sampling settings, extraction logic, and evaluation tools consistent. Five models were evaluated under matched conditions.")]
    story.append(bullets([
        "Qwen3.6 27B achieved the best VerilogEval v2 functional pass@1 (61.54%) and pass@5 task recovery (77.56%).",
        "Qwen3.6 27B and Qwen3.6 35B-A3B tied for the best RTLLM 2.0 functional result (60.00%).",
        "DeepSeek Coder achieved the best RTL-OPT equivalence pass rate (72.50%), ahead of Qwen3.6 27B (62.50%).",
        "Qwen2.5 Coder produced the strongest VerilogEval syntax rate, but that did not translate into functional correctness.",
        "ProtocolLLM results are lint-only and must not be interpreted as protocol functional correctness.",
    ]))
    story += [P("Recommendation", "H2x"), P("Use Qwen3.6 27B as the current default baseline for general RTL generation. Keep DeepSeek Coder as a complementary candidate for optimization workflows where behavior preservation is the first gate. Do not select a model based on syntax or lint scores alone."), PageBreak()]

    story += [P("1. What Was Evaluated", "H1x"), P("The benchmark suite covers three distinct questions. These measurements are deliberately reported separately because they do not prove the same capability."), data_table(["Benchmark", "Question answered", "Trusted metric", "Scale"], [
        ["VerilogEval v2", "Can the model generate functionally correct RTL from a specification?", "Icarus simulation pass@1 / pass@5", "156 tasks"],
        ["RTLLM 2.0", "Can the model solve a second public RTL generation task set?", "Icarus functional pass@1", "50 tasks"],
        ["ProtocolLLM", "Does generated protocol RTL parse and lint?", "Verilator lint pass only", "9 public tasks"],
        ["RTL-OPT", "Can the model rewrite RTL while preserving behavior?", "Yosys equivalence pass", "40 tasks"],
    ], [1.1, 2.75, 1.75, 1.05]), P("Models", "H2x"), bullets(["Qwen3.6 27B", "Qwen3.6 35B-A3B", "Qwen3 Coder", "Qwen2.5 Coder", "DeepSeek Coder"]), P("Controlled Settings", "H2x"), P("All comparisons use the same benchmark version, task set, neutral prompt template, extraction logic, timeout policy, and simulator/evaluation flow. Sampling settings were matched by benchmark condition."), data_table(["Condition", "Samples/task", "Temperature", "Top-p", "Max tokens"], [
        ["VerilogEval pass@1", "1", "0.2", "0.95", "2,048"],
        ["VerilogEval pass@5", "5", "0.6", "0.95", "2,048"],
        ["RTLLM / ProtocolLLM / RTL-OPT", "1", "0.2", "0.95", "4,096"],
    ], [2.45, 1.0, 1.0, 0.9, 1.15], centered=(1, 2, 3, 4)), callout("Interpretation rule", "A lint pass is not a functional pass. A synthesis pass is not proof of behavior preservation. For RTL-OPT, only equivalence-passing outputs provide trustworthy optimization evidence.", colors.HexColor("#FFF4E5"), GOLD), PageBreak()]

    story += [P("2. Functional RTL Generation", "H1x"), P("Functional simulation is the primary evidence for normal RTL generation. Higher values are better."), Image(str(PRESENTATION / "verilogeval_chart.png"), width=6.55 * inch, height=2.84 * inch), P("Figure 1. VerilogEval v2 functional pass rates under matched settings.", "Captionx"), data_table(["Model", "VE pass@1", "VE pass@5", "RTLLM pass@1"], [
        ["Qwen3.6 27B", "61.54%", "77.56%", "60.00%"],
        ["Qwen3.6 35B-A3B", "57.05%", "73.08%", "60.00%"],
        ["Qwen3 Coder", "48.08%", "57.05%", "50.00%"],
        ["Qwen2.5 Coder", "44.87%", "53.85%", "54.00%"],
        ["DeepSeek Coder", "48.72%", "56.41%", "52.00%"],
    ], [2.45, 1.35, 1.35, 1.35], centered=(1, 2, 3)), P("What this means", "H2x"), bullets([
        "Qwen3.6 27B is the clearest general-purpose winner across both VerilogEval sampling conditions.",
        "Qwen3.6 35B-A3B is consistently second on VerilogEval and ties the 27B model on RTLLM.",
        "DeepSeek Coder is the best non-Qwen model on VerilogEval pass@1, but Qwen3 Coder slightly overtakes it on pass@5.",
        "The pass@5 gain shows that sampling multiple candidates materially improves task recovery for every model.",
    ]), PageBreak()]

    story += [P("3. Reliability and Failure Patterns", "H1x"), P("A model can produce syntactically valid RTL that is still behaviorally wrong. The benchmark therefore tracks extraction, compilation, and simulation failures separately."), data_table(["Model", "VE syntax pass@1", "VE functional pass@1", "Gap"], [
        ["Qwen3.6 27B", "83.97%", "61.54%", "22.43 pts"],
        ["Qwen3.6 35B-A3B", "75.64%", "57.05%", "18.59 pts"],
        ["Qwen3 Coder", "86.54%", "48.08%", "38.46 pts"],
        ["Qwen2.5 Coder", "88.46%", "44.87%", "43.59 pts"],
        ["DeepSeek Coder", "85.90%", "48.72%", "37.18 pts"],
    ], [2.25, 1.55, 1.55, 1.15], centered=(1, 2, 3)), callout("Key insight", "The coder-specialized models are very good at producing parseable RTL, but their much lower simulation pass rates reveal semantic errors in timing, state transitions, reset behavior, or protocol logic."), P("VerilogEval pass@1 failure counts", "H2x"), data_table(["Model", "Passed", "Simulation", "Compile", "Extraction"], [
        ["Qwen3.6 27B", "96", "35", "17", "8"],
        ["Qwen3.6 35B-A3B", "89", "29", "26", "12"],
        ["Qwen3 Coder", "75", "60", "20", "1"],
        ["Qwen2.5 Coder", "70", "68", "18", "0"],
        ["DeepSeek Coder", "76", "58", "21", "1"],
    ], [2.15, 1.0, 1.2, 1.0, 1.15], centered=(1, 2, 3, 4)), P("The dominant weakness for Qwen3 Coder, Qwen2.5 Coder, and DeepSeek Coder is simulation failure rather than extraction failure. Improving prompt packaging alone is unlikely to close this gap; the models need stronger functional reasoning or an explicitly separate repair loop."), PageBreak()]

    story += [P("4. Protocol Lint and RTL Optimization", "H1x"), P("ProtocolLLM public lint", "H2x"), data_table(["Qwen3.6 27B", "Qwen3.6 35B-A3B", "Qwen3 Coder", "Qwen2.5 Coder", "DeepSeek Coder"], [["77.78%", "22.22%", "77.78%", "66.67%", "66.67%"]], [1.33] * 5, centered=(0, 1, 2, 3, 4)), callout("Important limitation", "ProtocolLLM public results are lint-only. They show whether output is structurally acceptable to Verilator, not whether the generated protocol implementation behaves correctly.", colors.HexColor("#FDECEC"), RED), P("RTL-OPT equivalence", "H2x"), Image(str(PRESENTATION / "rtlopt_chart.png"), width=6.55 * inch, height=2.84 * inch), P("Figure 2. Fraction of RTL-OPT tasks that synthesized and remained equivalent to the original design.", "Captionx"), data_table(["Model", "Equiv. pass", "Reduced cells", "Avg. cell ratio"], [
        ["Qwen3.6 27B", "25 / 40", "9 / 25", "0.9124"],
        ["Qwen3.6 35B-A3B", "19 / 40", "6 / 19", "0.9003"],
        ["Qwen3 Coder", "19 / 40", "4 / 19", "0.9472"],
        ["Qwen2.5 Coder", "19 / 40", "8 / 19", "0.8709"],
        ["DeepSeek Coder", "29 / 40", "3 / 29", "0.9739"],
    ], [2.25, 1.25, 1.35, 1.65], centered=(1, 2, 3)), P("Interpretation", "H2x"), bullets([
        "DeepSeek Coder preserves behavior most often, passing equivalence on 29 of 40 tasks.",
        "Qwen2.5 Coder has the best average cell ratio among equivalent outputs, but it reaches equivalence on only 19 tasks.",
        "Qwen3.6 27B offers the strongest balance: second-best equivalence coverage and the largest number of equivalence-passing reductions.",
        "A lower cell ratio is only meaningful after equivalence passes; non-equivalent or synthesis-failing outputs are excluded from optimization claims.",
    ]), PageBreak()]

    story += [P("5. Model Selection Guide", "H1x"), data_table(["Use case", "Recommended model", "Why", "Caution"], [
        ["General RTL generation", "Qwen3.6 27B", "Best functional pass@1 and pass@5", "Still fails roughly 38% of pass@1 tasks"],
        ["Alternative high-performing baseline", "Qwen3.6 35B-A3B", "Second on VerilogEval; ties RTLLM lead", "Lower syntax and extraction reliability"],
        ["Behavior-preserving RTL rewrite", "DeepSeek Coder", "Best equivalence coverage", "Few equivalent outputs reduce cells"],
        ["Optimization candidate generation", "Qwen3.6 27B / Qwen2.5 Coder", "More valid cell reductions / best ratio", "Use equivalence as a hard gate"],
        ["Syntax-first prototyping", "Qwen2.5 Coder", "Best VerilogEval syntax rate", "Syntax does not imply correct behavior"],
    ], [1.4, 1.4, 2.1, 1.75]), P("Recommended next experiments", "H2x"), bullets([
        "Analyze simulation failures by semantic category: reset, cycle alignment, FSM transitions, width/sign errors, and handshake logic.",
        "Add a separately reported repair-loop condition that feeds compiler or simulation errors back to the model.",
        "Run ProtocolLLM with functional testbenches before making protocol-correctness claims.",
        "Evaluate optimization quality with technology-mapped area, timing, and power after equivalence passes.",
        "Repeat selected runs across seeds to quantify variance and confidence intervals.",
    ], numbered=True), P("Operational achievement", "H2x"), P("The project now has a reusable, model-swappable benchmark workflow. Each run preserves raw responses, extracted RTL, logs, error logs, machine-readable results, summaries, and a per-run report in timestamped folders on Lanta. Committed manifests point to the authoritative output locations without placing large generated artifacts in Git."), PageBreak()]

    story += [P("Appendix A. Exact Model IDs", "H1x"), data_table(["Report label", "Internal model ID"], [
        ["Qwen3.6 27B", "qwen36-27b"],
        ["Qwen3.6 35B-A3B", "qwen36-35b-a3b"],
        ["Qwen3 Coder", "qwen3-coder-30b-a3b-instruct"],
        ["Qwen2.5 Coder", "qwen25-coder-32b"],
        ["DeepSeek Coder", "deepseek-coder-v2-lite-instruct"],
    ], [2.25, 4.4]), P("Appendix B. Scope and Limitations", "H1x"), bullets([
        "Results apply to the tested public benchmark versions, prompts, sampling settings, endpoints, and evaluator toolchain.",
        "No prompt engineering or automated repair loop is included in the baseline condition.",
        "Pass@5 measures whether at least one of five samples solves a task; it is not the same as single-sample reliability.",
        "ProtocolLLM public evaluation is lint-only in the current harness.",
        "RTL-OPT generic cell counts are an early proxy, not final PPA evidence from a technology-mapped flow.",
        "One DeepSeek VerilogEval pass@5 attempt was incomplete and excluded; one ProtocolLLM attempt failed due to endpoint timeout and was rerun successfully.",
    ]), P("Appendix C. Reproducibility", "H1x"), P("The benchmark repository records model presets, deterministic benchmark configuration, timestamped output paths, failure categories, and comparison reports. Raw output folders remain on Lanta; Git tracks the configs, summary reports, and output manifests.")]

    doc.build(story)
    print(PDF_PATH)


if __name__ == "__main__":
    build()
