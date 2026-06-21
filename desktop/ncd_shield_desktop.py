"""
NCD Shield AI — Tkinter Desktop Application
===========================================

A self-contained desktop GUI for early NCD risk screening — perfect for local
testing and demos (no Docker, Node, database, or browser required).

It reuses the project's existing ML model and services:
  • app.ml.predictor          → model loading + explainable prediction
  • app.services.recommendations → personalized guidance
  • app.services.chatbot      → healthcare assistant (never diagnoses)
  • app.services.pdf_report   → professional PDF report

Run from the project root (or this folder):
    python desktop/ncd_shield_desktop.py

If a trained model is not present in ml/models/, the predictor automatically
falls back to a built-in heuristic, so the demo always works. To use the real
ML model, first run:  cd ml && python generate_dataset.py && python train.py
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- Wire up the existing backend logic ------------------------------------
# Make the `app` package importable and point the predictor at ml/models/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MODEL_DIR", os.path.join(ROOT, "ml", "models"))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from app.ml.predictor import DISCLAIMER, predictor  # noqa: E402
from app.services.chatbot import get_reply  # noqa: E402
from app.services.pdf_report import build_report  # noqa: E402
from app.services.recommendations import generate_recommendations  # noqa: E402

# --- Theme (modern healthcare dashboard) ------------------------------------
BG = "#eef1f7"          # app canvas
CARD = "#ffffff"        # card surface
SOFT = "#f5f7fb"        # inset / readonly surface
BORDER = "#e3e8f0"      # hairline
TRACK = "#eaeef5"       # progress track
INK = "#0f172a"         # primary text
MUTED = "#6b7689"       # secondary text
FAINT = "#94a1b5"       # tertiary text
PRIMARY = "#6c5cf0"     # iris accent (matches web)
PRIMARY_DARK = "#5847e6"

# (text color, soft background) per risk band
RISK = {
    "Low": ("#0f9d6b", "#e7f6ef"),
    "Moderate": ("#d9820a", "#fdf2e3"),
    "High": ("#e11d48", "#fdeaee"),
}

DISEASE_OPTIONS = ["None", "Diabetes", "Hypertension", "Heart Disease", "Kidney Disease"]

FONT = "Segoe UI"


def band(score: float) -> str:
    return "Low" if score < 34 else "Moderate" if score < 67 else "High"


def _lerp(x, x0, x1, y0, y1):
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def _glucose_score(bs):
    if bs < 100:
        return _lerp(bs, 70, 100, 0, 28)        # normal
    if bs < 126:
        return _lerp(bs, 100, 126, 34, 56)      # pre-diabetic
    return _lerp(bs, 126, 250, 64, 90)          # diabetic range


def _bp_score(bp):
    if bp < 120:
        return _lerp(bp, 90, 120, 0, 16)        # normal
    if bp < 130:
        return _lerp(bp, 120, 130, 26, 34)      # elevated
    if bp < 140:
        return _lerp(bp, 130, 140, 44, 58)      # stage 1
    return _lerp(bp, 140, 200, 64, 92)          # stage 2


def _chol_score(c):
    if c < 200:
        return _lerp(c, 140, 200, 0, 26)        # desirable
    if c < 240:
        return _lerp(c, 200, 240, 34, 56)       # borderline high
    return _lerp(c, 240, 330, 60, 86)           # high


def compute_disease_risks(d: dict) -> list[dict]:
    """Clinically-inspired per-disease risk estimates (0-100) from the inputs.

    The ML model outputs a single overall NCD risk; these heuristics break that
    down into the four headline diseases — using recognised clinical breakpoints
    for the primary marker plus lifestyle modifiers — so the dashboard can show a
    per-disease view. They are illustrative screening signals, not diagnoses.
    """
    def clamp(x, lo=0.0, hi=100.0):
        return max(lo, min(hi, x))

    bmi, bp, bs, chol = d["bmi"], d["systolic_bp"], d["blood_sugar"], d["cholesterol"]
    age, smoke, fam = d["age"], d["smoking"], d["family_history"]
    ex, stress = d["exercise_freq"], d["stress_level"]
    stress_pts = {"low": 0, "moderate": 4, "high": 8}[stress]
    bmi_pts = 10 if bmi >= 30 else 5 if bmi >= 25 else 0

    diabetes = clamp(
        _glucose_score(bs) * 0.75 + bmi_pts + (8 if fam else 0)
        + (5 if age > 45 else 0) + (4 if ex < 3 else 0)
    )
    hypertension = clamp(
        _bp_score(bp) * 0.8 + (10 if smoke else 0) + stress_pts
        + bmi_pts + (5 if age > 50 else 0)
    )
    heart = clamp(
        _chol_score(chol) * 0.55 + _bp_score(bp) * 0.2 + (14 if smoke else 0)
        + (6 if age > 50 else 0) + (5 if ex < 3 else 0) + (5 if fam else 0)
    )
    kidney = clamp(
        _bp_score(bp) * 0.45 + _glucose_score(bs) * 0.35 + (8 if age > 50 else 0)
        + (8 if fam else 0) + (5 if smoke else 0)
    )

    rows = [
        ("Diabetes", "🩸", diabetes, "Blood sugar · BMI · family history"),
        ("Hypertension", "💗", hypertension, "Blood pressure · age · stress"),
        ("Heart Disease", "❤️", heart, "Cholesterol · BP · smoking"),
        ("Kidney Disease", "🫧", kidney, "Blood pressure · blood sugar · age"),
    ]
    return [
        {"name": n, "icon": ic, "score": round(s, 1), "note": note, "level": band(s)}
        for n, ic, s, note in rows
    ]


class ScrollFrame(tk.Frame):
    """A vertically scrollable container (Tkinter has none built in)."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.interior = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._win, width=e.width))
        for w in (self.canvas, self.interior):
            w.bind("<Enter>", self._bind_wheel)
            w.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _e):
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>", self._on_wheel)
        self.canvas.bind_all("<Button-5>", self._on_wheel)

    def _unbind_wheel(self, _e):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_wheel(self, e):
        delta = 1 if getattr(e, "num", None) == 5 else -1 if getattr(e, "num", None) == 4 else int(-e.delta / 120)
        self.canvas.yview_scroll(delta, "units")


def make_card(parent, bg=CARD):
    """Return (wrapper, inner) — a hairline-bordered card with internal padding."""
    wrap = tk.Frame(parent, bg=parent["bg"])
    card = tk.Frame(wrap, bg=bg, highlightbackground=BORDER, highlightthickness=1, bd=0)
    card.pack(fill="both", expand=True)
    inner = tk.Frame(card, bg=bg)
    inner.pack(fill="both", expand=True, padx=18, pady=16)
    return wrap, inner


def pill(parent, text, level, bg=CARD):
    fg, soft = RISK[level]
    lbl = tk.Label(parent, text=f"  {text}  ", bg=soft, fg=fg,
                   font=(FONT, 9, "bold"), padx=2, pady=2)
    return lbl


def progress_bar(parent, pct, color, bg=CARD, height=9):
    track = tk.Frame(parent, bg=TRACK, height=height)
    track.pack_propagate(False)
    fill = tk.Frame(track, bg=color, height=height)
    fill.place(relwidth=max(0.02, min(1.0, pct / 100)), relheight=1)
    return track


class NCDShieldApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("NCD Shield AI — Early NCD Screening (Desktop)")
        self.geometry("1040x760")
        self.minsize(900, 680)
        self.configure(bg=BG)

        self.last_prediction: dict | None = None
        self.last_inputs: dict | None = None
        self.entries: dict[str, tk.Entry] = {}

        self._init_style()
        self._build_header()
        self._build_tabs()

    # ---- styling -----------------------------------------------------------
    def _init_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(10, 8, 10, 0))
        style.configure("TNotebook.Tab", padding=(20, 11), font=(FONT, 10, "bold"),
                        background=BG, foreground=MUTED, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", PRIMARY)])
        style.configure("Vertical.TScrollbar", background=BORDER, troughcolor=BG,
                        borderwidth=0, arrowsize=12)
        style.configure("TCombobox", padding=6, fieldbackground=CARD, background=CARD)
        style.configure("Brand.TButton", font=(FONT, 11, "bold"), foreground="white",
                        background=PRIMARY, borderwidth=0, padding=11, focuscolor=PRIMARY)
        style.map("Brand.TButton", background=[("active", PRIMARY_DARK)])
        style.configure("Ghost.TButton", font=(FONT, 10, "bold"), foreground=INK,
                        background=SOFT, borderwidth=0, padding=11)
        style.map("Ghost.TButton", background=[("active", BORDER)])

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=CARD, height=70, highlightbackground=BORDER,
                          highlightthickness=1)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=CARD)
        left.pack(side="left", padx=22, pady=12)
        badge = tk.Label(left, text="🛡", bg=PRIMARY, fg="white", font=(FONT, 15),
                         width=2, height=1)
        badge.pack(side="left", padx=(0, 12))
        title_box = tk.Frame(left, bg=CARD)
        title_box.pack(side="left")
        tk.Label(title_box, text="NCD Shield AI", bg=CARD, fg=INK,
                 font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(title_box, text="AI-Powered Early Screening for Non-Communicable Diseases",
                 bg=CARD, fg=MUTED, font=(FONT, 9)).pack(anchor="w")

        model_name = predictor.metadata.get("best_model", "heuristic")
        ok = predictor.is_model_loaded
        chip = tk.Frame(header, bg=CARD)
        chip.pack(side="right", padx=22)
        tk.Label(chip, text="●", bg=CARD, fg=("#0f9d6b" if ok else "#d9820a"),
                 font=(FONT, 11)).pack(side="left")
        tk.Label(chip, text=f" Model: {model_name}" + ("" if ok else " · fallback"),
                 bg=CARD, fg=MUTED, font=(FONT, 9, "bold")).pack(side="left")

    def _build_tabs(self) -> None:
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=16, pady=14)
        self._build_assessment_tab()
        self._build_result_tab()
        self._build_chatbot_tab()
        self._build_about_tab()

    # ---- Assessment tab ----------------------------------------------------
    def _build_assessment_tab(self) -> None:
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Assessment  ")

        self.vars: dict[str, tk.Variable] = {
            "age": tk.StringVar(value="35"),
            "gender": tk.StringVar(value="male"),
            "height_cm": tk.StringVar(value="170"),
            "weight_kg": tk.StringVar(value="70"),
            "bmi": tk.StringVar(value="24.2"),
            "systolic_bp": tk.StringVar(value="120"),
            "blood_sugar": tk.StringVar(value="95"),
            "cholesterol": tk.StringVar(value="180"),
            "exercise_freq": tk.StringVar(value="3"),
            "sleep_hours": tk.StringVar(value="7"),
            "stress_level": tk.StringVar(value="moderate"),
            "smoking": tk.BooleanVar(value=False),
            "alcohol": tk.BooleanVar(value=False),
            "family_history": tk.BooleanVar(value=False),
            "existing": tk.StringVar(value="None"),
        }
        self.vars["height_cm"].trace_add("write", lambda *_: self._update_bmi())
        self.vars["weight_kg"].trace_add("write", lambda *_: self._update_bmi())

        wrap, inner = make_card(tab)
        wrap.pack(fill="both", expand=True, padx=8, pady=8)

        tk.Label(inner, text="Health Assessment", bg=CARD, fg=INK,
                 font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(inner, text="Enter your details for an AI-powered NCD risk screening. "
                 "BMI is calculated automatically.", bg=CARD, fg=MUTED,
                 font=(FONT, 9)).pack(anchor="w", pady=(2, 4))

        # Inline validation banner (hidden until needed).
        self.banner = tk.Label(inner, text="", bg="#fdeaee", fg="#e11d48",
                               font=(FONT, 9, "bold"), anchor="w", padx=12, pady=8,
                               justify="left")

        grid = tk.Frame(inner, bg=CARD)
        grid.pack(fill="x", pady=(14, 0))
        for c in range(3):
            grid.columnconfigure(c, weight=1, uniform="f")

        self._field(grid, "Age", "age", 0, 0)
        self._field(grid, "Gender", "gender", 0, 1, kind="combo", values=["male", "female"])
        self._field(grid, "BMI (auto)", "bmi", 0, 2, readonly=True)
        self._field(grid, "Height (cm)", "height_cm", 1, 0)
        self._field(grid, "Weight (kg)", "weight_kg", 1, 1)
        self._field(grid, "Systolic BP (mmHg)", "systolic_bp", 1, 2)
        self._field(grid, "Blood Sugar (mg/dL)", "blood_sugar", 2, 0)
        self._field(grid, "Cholesterol (mg/dL)", "cholesterol", 2, 1)
        self._field(grid, "Exercise (days/week)", "exercise_freq", 2, 2)
        self._field(grid, "Sleep (hours)", "sleep_hours", 3, 0)
        self._field(grid, "Stress Level", "stress_level", 3, 1, kind="combo",
                    values=["low", "moderate", "high"])
        self._field(grid, "Existing Condition", "existing", 3, 2, kind="combo",
                    values=DISEASE_OPTIONS)

        checks = tk.Frame(inner, bg=SOFT, highlightbackground=BORDER, highlightthickness=1)
        checks.pack(fill="x", pady=(16, 0))
        cinner = tk.Frame(checks, bg=SOFT)
        cinner.pack(anchor="w", padx=14, pady=10)
        for text, key in [("Smoking", "smoking"), ("Alcohol", "alcohol"),
                          ("Family History", "family_history")]:
            tk.Checkbutton(cinner, text=text, variable=self.vars[key], bg=SOFT,
                           activebackground=SOFT, fg=INK, font=(FONT, 10),
                           selectcolor=CARD, anchor="w").pack(side="left", padx=(0, 26))

        actions = tk.Frame(inner, bg=CARD)
        actions.pack(fill="x", pady=(18, 0))
        ttk.Button(actions, text="📄  Scan Medical Report (OCR)", style="Ghost.TButton",
                   command=self._scan_report).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(actions, text="⚡  Run AI Assessment", style="Brand.TButton",
                   command=self._run_assessment).pack(side="left", expand=True, fill="x")

    def _field(self, parent, label, key, row, col, kind="entry", values=None, readonly=False):
        cell = tk.Frame(parent, bg=CARD)
        cell.grid(row=row, column=col, sticky="ew", padx=(0, 16), pady=8)
        tk.Label(cell, text=label.upper(), bg=CARD, fg=FAINT,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 4))
        if kind == "combo":
            cb = ttk.Combobox(cell, textvariable=self.vars[key], values=values,
                              state="readonly", font=(FONT, 10))
            cb.pack(fill="x", ipady=3)
        else:
            e = tk.Entry(cell, textvariable=self.vars[key], font=(FONT, 11), fg=INK,
                         relief="flat", highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=PRIMARY, bg=CARD)
            if readonly:
                e.configure(state="readonly", readonlybackground=SOFT, fg=MUTED)
            e.pack(fill="x", ipady=6)
            self.entries[key] = e

    def _update_bmi(self) -> None:
        try:
            h = float(self.vars["height_cm"].get()) / 100
            w = float(self.vars["weight_kg"].get())
            if h > 0:
                self.vars["bmi"].set(f"{round(w / (h * h), 1)}")
        except (ValueError, ZeroDivisionError):
            pass

    def _show_banner(self, message: str) -> None:
        self.banner.configure(text="⚠  " + message)
        self.banner.pack(fill="x", pady=(10, 0))

    def _clear_validation(self) -> None:
        self.banner.pack_forget()
        for e in self.entries.values():
            e.configure(highlightbackground=BORDER)

    def _collect_inputs(self):
        """Validate fields. Returns (data, None) or (None, (message, bad_key))."""
        specs = [
            ("age", "Age", 1, 120, True),
            ("height_cm", "Height", 50, 250, False),
            ("weight_kg", "Weight", 10, 400, False),
            ("systolic_bp", "Systolic BP", 60, 260, True),
            ("blood_sugar", "Blood Sugar", 40, 600, True),
            ("cholesterol", "Cholesterol", 80, 500, True),
            ("exercise_freq", "Exercise days", 0, 7, True),
            ("sleep_hours", "Sleep hours", 0, 24, False),
        ]
        data: dict = {}
        for key, label, lo, hi, is_int in specs:
            raw = self.vars[key].get().strip()
            try:
                val = float(raw)
            except ValueError:
                return None, (f"Please enter a valid number for {label}.", key)
            if not (lo <= val <= hi):
                return None, (f"{label} must be between {lo} and {hi}.", key)
            data[key] = int(val) if is_int else round(val, 1)

        data["gender"] = self.vars["gender"].get()
        data["stress_level"] = self.vars["stress_level"].get()
        data["smoking"] = bool(self.vars["smoking"].get())
        data["alcohol"] = bool(self.vars["alcohol"].get())
        data["family_history"] = bool(self.vars["family_history"].get())
        data["bmi"] = round(data["weight_kg"] / ((data["height_cm"] / 100) ** 2), 1)
        existing = self.vars["existing"].get()
        data["existing_diseases"] = [] if existing == "None" else [existing]
        return data, None

    def _run_assessment(self) -> None:
        self._clear_validation()
        data, err = self._collect_inputs()
        if err:
            message, bad_key = err
            self._show_banner(message)
            if bad_key in self.entries:
                self.entries[bad_key].configure(highlightbackground="#e11d48")
                self.entries[bad_key].focus_set()
            return

        result = predictor.predict(data)
        result["recommendations"] = generate_recommendations(data, result["risk_class"])
        result["diseases"] = compute_disease_risks(data)

        self.last_inputs = data
        self.last_prediction = result
        self._render_result(data, result)
        self.nb.select(1)

    # ---- Result tab --------------------------------------------------------
    def _build_result_tab(self) -> None:
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Results  ")
        self.result_scroll = ScrollFrame(tab, bg=BG)
        self.result_scroll.pack(fill="both", expand=True)
        self.result_body = self.result_scroll.interior

        ph = tk.Label(self.result_body, bg=BG, fg=MUTED, font=(FONT, 11),
                      text="\n\n   Run an assessment to see your results here.")
        ph.pack(pady=60)

    def _render_result(self, data: dict, result: dict) -> None:
        for w in self.result_body.winfo_children():
            w.destroy()
        body = tk.Frame(self.result_body, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=8)

        self._render_overall_card(body, data, result)
        self._render_disease_section(body, result["diseases"])
        self._render_explanation_card(body, result)
        self._render_recommendations_card(body, result["recommendations"])

        tk.Label(body, text="⚠  " + result.get("disclaimer", DISCLAIMER), bg=BG, fg=FAINT,
                 font=(FONT, 8), wraplength=920, justify="left").pack(anchor="w", pady=(6, 10))

    def _render_overall_card(self, parent, data, result):
        wrap, inner = make_card(parent)
        wrap.pack(fill="x", pady=6)
        level = result["risk_level"].replace(" Risk", "")
        fg, soft = RISK[level]

        top = tk.Frame(inner, bg=CARD)
        top.pack(fill="x")

        score_box = tk.Frame(top, bg=CARD)
        score_box.pack(side="left")
        tk.Label(score_box, text="OVERALL NCD RISK", bg=CARD, fg=FAINT,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(score_box, text=f"{result['risk_score']:g}%", bg=CARD, fg=fg,
                 font=(FONT, 40, "bold")).pack(anchor="w")
        pill(score_box, result["risk_level"], level).pack(anchor="w")

        stats = tk.Frame(top, bg=CARD)
        stats.pack(side="left", padx=34)
        for lab, val in [("Health Score", f"{result['health_score']:g} / 100"),
                         ("BMI", f"{data['bmi']:g}"),
                         ("Risk Class", level)]:
            row = tk.Frame(stats, bg=CARD)
            row.pack(anchor="w", pady=5)
            tk.Label(row, text=lab, bg=CARD, fg=MUTED, font=(FONT, 9),
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD, fg=INK, font=(FONT, 11, "bold")).pack(side="left")

        ttk.Button(top, text="⬇  Save PDF Report", style="Brand.TButton",
                   command=self._save_pdf).pack(side="right")

        # 3-class probability bars
        probs = tk.Frame(inner, bg=CARD)
        probs.pack(fill="x", pady=(16, 0))
        tk.Label(probs, text="RISK PROBABILITY", bg=CARD, fg=FAINT,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(0, 6))
        for label, key, lv in [("Low", "low", "Low"), ("Moderate", "moderate", "Moderate"),
                              ("High", "high", "High")]:
            pct = result["probabilities"].get(key, 0) * 100
            row = tk.Frame(probs, bg=CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=CARD, fg=MUTED, width=10, anchor="w",
                     font=(FONT, 9)).pack(side="left")
            bar_wrap = tk.Frame(row, bg=CARD, height=9)
            bar_wrap.pack(side="left", fill="x", expand=True, padx=8)
            progress_bar(bar_wrap, pct, RISK[lv][0]).pack(fill="x")
            tk.Label(row, text=f"{pct:.0f}%", bg=CARD, fg=INK, width=5, anchor="e",
                     font=(FONT, 9, "bold")).pack(side="left")

    def _render_disease_section(self, parent, diseases):
        tk.Label(parent, text="Disease-wise risk breakdown", bg=BG, fg=INK,
                 font=(FONT, 12, "bold")).pack(anchor="w", pady=(14, 2))
        tk.Label(parent, text="Estimated screening signal for each condition — not a diagnosis.",
                 bg=BG, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(0, 8))

        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="x")
        for c in range(2):
            grid.columnconfigure(c, weight=1, uniform="d")
        for i, dz in enumerate(diseases):
            self._disease_card(grid, dz, i // 2, i % 2)

    def _disease_card(self, parent, dz, row, col):
        fg, soft = RISK[dz["level"]]
        wrap = tk.Frame(parent, bg=BG)
        wrap.grid(row=row, column=col, sticky="ew", padx=6, pady=6)
        card = tk.Frame(wrap, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x")
        tk.Label(head, text=dz["icon"], bg=CARD, font=(FONT, 15)).pack(side="left")
        tk.Label(head, text="  " + dz["name"], bg=CARD, fg=INK,
                 font=(FONT, 11, "bold")).pack(side="left")
        pill(head, dz["level"], dz["level"]).pack(side="right")

        tk.Label(inner, text=f"{dz['score']:g}%", bg=CARD, fg=fg,
                 font=(FONT, 24, "bold")).pack(anchor="w", pady=(8, 2))
        progress_bar(inner, dz["score"], fg).pack(fill="x", pady=(2, 8))
        tk.Label(inner, text=dz["note"], bg=CARD, fg=MUTED, font=(FONT, 8),
                 anchor="w").pack(anchor="w")

    def _render_explanation_card(self, parent, result):
        wrap, inner = make_card(parent)
        wrap.pack(fill="x", pady=6)
        tk.Label(inner, text="Why this result?", bg=CARD, fg=INK,
                 font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(inner, text="Top factors influencing your overall risk.", bg=CARD,
                 fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(0, 8))
        for e in result["explanation"][:5]:
            arrow = {"increases": "▲", "decreases": "▼"}.get(e["contribution"], "•")
            color = {"increases": "#e11d48", "decreases": "#0f9d6b"}.get(e["contribution"], MUTED)
            row = tk.Frame(inner, bg=CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=arrow, bg=CARD, fg=color, font=(FONT, 9),
                     width=2).pack(side="left")
            tk.Label(row, text=e["label"], bg=CARD, fg=INK, font=(FONT, 10),
                     anchor="w").pack(side="left")
            barw = tk.Frame(row, bg=CARD, height=8, width=140)
            barw.pack(side="right")
            barw.pack_propagate(False)
            progress_bar(barw, min(100, e["importance"] * 300), PRIMARY, height=8).pack(fill="x")

    def _render_recommendations_card(self, parent, recs):
        wrap, inner = make_card(parent)
        wrap.pack(fill="x", pady=6)
        tk.Label(inner, text="Personalized recommendations", bg=CARD, fg=INK,
                 font=(FONT, 12, "bold")).pack(anchor="w", pady=(0, 8))
        for r in recs:
            fg, soft = RISK[{"high": "High", "medium": "Moderate", "low": "Low"}[r["priority"]]]
            item = tk.Frame(inner, bg=SOFT, highlightbackground=BORDER, highlightthickness=1)
            item.pack(fill="x", pady=4)
            it = tk.Frame(item, bg=SOFT)
            it.pack(fill="x", padx=12, pady=9)
            head = tk.Frame(it, bg=SOFT)
            head.pack(fill="x")
            tk.Label(head, text=r["title"], bg=SOFT, fg=INK,
                     font=(FONT, 10, "bold")).pack(side="left")
            tk.Label(head, text=f" {r['priority'].upper()} ", bg=soft, fg=fg,
                     font=(FONT, 8, "bold")).pack(side="right")
            tk.Label(it, text=r["detail"], bg=SOFT, fg=MUTED, font=(FONT, 9),
                     wraplength=860, justify="left", anchor="w").pack(anchor="w", pady=(3, 0))

    def _save_pdf(self) -> None:
        if not self.last_prediction or not self.last_inputs:
            messagebox.showwarning("No report", "Run an assessment first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialfile="ncd_shield_report.pdf")
        if not path:
            return
        prediction_dict = {
            "inputs": self.last_inputs,
            "risk_level": self.last_prediction["risk_level"],
            "risk_class": self.last_prediction["risk_class"],
            "risk_score": self.last_prediction["risk_score"],
            "health_score": self.last_prediction["health_score"],
            "bmi": self.last_inputs["bmi"],
            "recommendations": self.last_prediction["recommendations"],
            "disclaimer": self.last_prediction.get("disclaimer", DISCLAIMER),
        }
        try:
            pdf_bytes = build_report(
                {"full_name": "Desktop User", "email": "—"}, prediction_dict)
            with open(path, "wb") as f:
                f.write(pdf_bytes)
            messagebox.showinfo("Saved", f"Report saved to:\n{path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"Could not save report:\n{exc}")

    def _scan_report(self) -> None:
        """Upload a lab report (image/PDF), OCR it, and auto-fill matched fields."""
        from ocr import OCRUnavailable, scan_report

        path = filedialog.askopenfilename(
            title="Select a medical / lab report",
            filetypes=[("Reports", "*.pdf *.png *.jpg *.jpeg *.bmp *.tiff"),
                       ("PDF", "*.pdf"), ("Images", "*.png *.jpg *.jpeg")])
        if not path:
            return
        try:
            values = scan_report(path)
        except OCRUnavailable as exc:
            messagebox.showwarning("Scan unavailable", str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Scan failed", f"Could not read the report:\n{exc}")
            return

        if not values:
            messagebox.showinfo(
                "Nothing detected",
                "No recognisable lab values were found in that report.\n"
                "You can still fill the form manually.")
            return

        for field, value in values.items():
            if field in self.vars:
                self.vars[field].set(str(int(value)) if value == int(value) else str(value))
        self._update_bmi()

        summary = "\n".join(f"  • {f.replace('_', ' ').title()}: {v:g}"
                            for f, v in values.items())
        messagebox.showinfo("Report scanned",
                            f"Auto-filled {len(values)} field(s):\n{summary}\n\n"
                            "Please review the values before running the assessment.")

    # ---- Health Assistant tab ---------------------------------------------
    def _build_chatbot_tab(self) -> None:
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Health Assistant  ")
        wrap, inner = make_card(tab)
        wrap.pack(fill="both", expand=True, padx=8, pady=8)

        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x", pady=(0, 8))
        tk.Label(head, text="●", bg=CARD, fg="#0f9d6b", font=(FONT, 11)).pack(side="left")
        tk.Label(head, text=" Health Assistant", bg=CARD, fg=INK,
                 font=(FONT, 13, "bold")).pack(side="left")
        tk.Label(head, text="  ·  general wellness guidance, never a diagnosis", bg=CARD,
                 fg=MUTED, font=(FONT, 9)).pack(side="left")

        self.chat_log = tk.Text(inner, wrap="word", height=20, bg=SOFT, relief="flat",
                                font=(FONT, 10), state="disabled", padx=14, pady=12,
                                highlightthickness=1, highlightbackground=BORDER)
        self.chat_log.pack(fill="both", expand=True)
        self.chat_log.tag_configure("bot", foreground=PRIMARY_DARK, font=(FONT, 10, "bold"))
        self.chat_log.tag_configure("user", foreground=INK, font=(FONT, 10, "bold"))
        self.chat_log.tag_configure("msg", foreground=INK, font=(FONT, 10))

        entry_row = tk.Frame(inner, bg=CARD)
        entry_row.pack(fill="x", pady=(10, 0))
        self.chat_var = tk.StringVar()
        entry = tk.Entry(entry_row, textvariable=self.chat_var, font=(FONT, 11), relief="flat",
                         highlightthickness=1, highlightbackground=BORDER, highlightcolor=PRIMARY,
                         bg=CARD)
        entry.pack(side="left", fill="x", expand=True, ipady=7)
        entry.bind("<Return>", lambda _e: self._send_chat())
        ttk.Button(entry_row, text="Send", style="Brand.TButton",
                   command=self._send_chat).pack(side="left", padx=(8, 0))

        self._append_chat("Assistant", "Hi! I'm your health assistant. Ask me about lifestyle, "
                          "nutrition, exercise, sleep, stress, or NCD awareness. I never diagnose.", "bot")

    def _append_chat(self, who: str, text: str, tag: str) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", f"{who}: ", tag)
        self.chat_log.insert("end", f"{text}\n\n", "msg")
        self.chat_log.configure(state="disabled")
        self.chat_log.see("end")

    def _send_chat(self) -> None:
        text = self.chat_var.get().strip()
        if not text:
            return
        self._append_chat("You", text, "user")
        self.chat_var.set("")
        reply = get_reply(text)
        self._append_chat("Assistant", reply["reply"], "bot")

    # ---- About tab ---------------------------------------------------------
    def _build_about_tab(self) -> None:
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  About  ")
        wrap, inner = make_card(tab)
        wrap.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(inner, text="About NCD Shield AI", bg=CARD, fg=INK,
                 font=(FONT, 15, "bold")).pack(anchor="w")
        about = (
            "NCD Shield AI is an early-screening and risk-prediction tool for Non-Communicable "
            "Diseases: Diabetes, Hypertension, Heart Disease, and Chronic Kidney Disease.\n\n"
            "It estimates your risk from everyday lifestyle and health data using a machine-"
            "learning model, explains which factors drive your result, and offers personalized, "
            "prioritized recommendations — which you can export as a PDF report for your doctor.\n\n"
            "This desktop edition reuses the same ML model and logic as the full web platform, "
            "packaged into a single window for easy testing and demos."
        )
        tk.Label(inner, text=about, bg=CARD, fg=MUTED, font=(FONT, 10), wraplength=900,
                 justify="left").pack(anchor="w", pady=(10, 16))
        tk.Label(inner, text="⚠  IMPORTANT: This is NOT a medical diagnosis tool. It is an early "
                 "screening and risk-prediction system. Always consult a qualified physician.",
                 bg="#fdeaee", fg="#b4123f", font=(FONT, 10, "bold"), wraplength=900,
                 justify="left", padx=14, pady=12).pack(anchor="w", fill="x")


def main() -> None:
    app = NCDShieldApp()
    app.mainloop()


if __name__ == "__main__":
    main()
