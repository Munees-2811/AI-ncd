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

# --- Theme ------------------------------------------------------------------
BRAND = "#0d9488"
BRAND_DARK = "#0f766e"
BG = "#f1f5f9"
CARD = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"
RISK_COLORS = {"Low Risk": "#16a34a", "Moderate Risk": "#d97706", "High Risk": "#dc2626"}

DISEASE_OPTIONS = ["None", "Diabetes", "Hypertension", "Heart Disease", "Kidney Disease"]


class NCDShieldApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("NCD Shield AI — Early NCD Screening (Desktop)")
        self.geometry("960x720")
        self.minsize(820, 640)
        self.configure(bg=BG)

        self.last_prediction: dict | None = None
        self.last_inputs: dict | None = None

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
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)], foreground=[("selected", BRAND)])
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("H1.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 16, "bold"))
        style.configure("Brand.TButton", font=("Segoe UI", 11, "bold"),
                        foreground="white", background=BRAND, borderwidth=0, padding=10)
        style.map("Brand.TButton", background=[("active", BRAND_DARK)])
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", padding=4)
        style.configure("TCombobox", padding=4)

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=BRAND, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🛡  NCD Shield AI", bg=BRAND, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        model_name = predictor.metadata.get("best_model", "heuristic")
        status = f"Model: {model_name}" + ("" if predictor.is_model_loaded else " (fallback)")
        tk.Label(header, text=status, bg=BRAND, fg="#ccfbf1",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

    def _build_tabs(self) -> None:
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=14, pady=12)
        self._build_assessment_tab()
        self._build_result_tab()
        self._build_chatbot_tab()
        self._build_about_tab()

    # ---- Assessment tab ----------------------------------------------------
    def _build_assessment_tab(self) -> None:
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Assessment  ")
        card = ttk.Frame(tab, style="Card.TFrame", padding=24)
        card.pack(fill="both", expand=True, padx=8, pady=8)

        ttk.Label(card, text="Health Assessment", style="H1.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(card, text="Enter your details for an AI-powered NCD risk screening. "
                  "BMI is calculated automatically.", style="Muted.TLabel").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(2, 16))

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
        # Live BMI recalculation.
        self.vars["height_cm"].trace_add("write", lambda *_: self._update_bmi())
        self.vars["weight_kg"].trace_add("write", lambda *_: self._update_bmi())

        r = 2
        self._entry(card, "Age", "age", r, 0)
        self._combo(card, "Gender", "gender", ["male", "female"], r, 2)
        r += 1
        self._entry(card, "Height (cm)", "height_cm", r, 0)
        self._entry(card, "Weight (kg)", "weight_kg", r, 2)
        r += 1
        self._entry(card, "BMI (auto)", "bmi", r, 0, readonly=True)
        self._entry(card, "Systolic BP (mmHg)", "systolic_bp", r, 2)
        r += 1
        self._entry(card, "Blood Sugar (mg/dL)", "blood_sugar", r, 0)
        self._entry(card, "Cholesterol (mg/dL)", "cholesterol", r, 2)
        r += 1
        self._spin(card, "Exercise (days/week)", "exercise_freq", 0, 7, r, 0)
        self._entry(card, "Sleep (hours)", "sleep_hours", r, 2)
        r += 1
        self._combo(card, "Stress Level", "stress_level", ["low", "moderate", "high"], r, 0)
        self._combo(card, "Existing Condition", "existing", DISEASE_OPTIONS, r, 2)
        r += 1
        checks = ttk.Frame(card, style="Card.TFrame")
        checks.grid(row=r, column=0, columnspan=4, sticky="w", pady=(12, 0))
        ttk.Checkbutton(checks, text="Smoking", variable=self.vars["smoking"]).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(checks, text="Alcohol", variable=self.vars["alcohol"]).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(checks, text="Family History", variable=self.vars["family_history"]).pack(side="left")
        r += 1
        btns = ttk.Frame(card, style="Card.TFrame")
        btns.grid(row=r, column=0, columnspan=4, sticky="ew", pady=(20, 0))
        ttk.Button(btns, text="📄  Scan Medical Report (OCR)",
                   command=self._scan_report).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(btns, text="⚡  Run AI Assessment", style="Brand.TButton",
                   command=self._run_assessment).pack(side="left", expand=True, fill="x")
        for c in range(4):
            card.columnconfigure(c, weight=1)

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
                # Integers for whole-number fields, keep as-is otherwise.
                self.vars[field].set(str(int(value)) if value == int(value) else str(value))
        self._update_bmi()

        summary = "\n".join(f"  • {f.replace('_', ' ').title()}: {v:g}"
                            for f, v in values.items())
        messagebox.showinfo("Report scanned",
                            f"Auto-filled {len(values)} field(s):\n{summary}\n\n"
                            "Please review the values before running the assessment.")

    def _entry(self, parent, label, key, row, col, readonly=False):
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(
            row=row, column=col, sticky="w", padx=(0, 8), pady=6)
        e = ttk.Entry(parent, textvariable=self.vars[key])
        if readonly:
            e.configure(state="readonly")
        e.grid(row=row, column=col + 1, sticky="ew", padx=(0, 24), pady=6)

    def _combo(self, parent, label, key, values, row, col):
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(
            row=row, column=col, sticky="w", padx=(0, 8), pady=6)
        c = ttk.Combobox(parent, textvariable=self.vars[key], values=values, state="readonly")
        c.grid(row=row, column=col + 1, sticky="ew", padx=(0, 24), pady=6)

    def _spin(self, parent, label, key, lo, hi, row, col):
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(
            row=row, column=col, sticky="w", padx=(0, 8), pady=6)
        s = ttk.Spinbox(parent, from_=lo, to=hi, textvariable=self.vars[key])
        s.grid(row=row, column=col + 1, sticky="ew", padx=(0, 24), pady=6)

    def _update_bmi(self) -> None:
        try:
            h = float(self.vars["height_cm"].get()) / 100
            w = float(self.vars["weight_kg"].get())
            if h > 0:
                self.vars["bmi"].set(f"{round(w / (h * h), 1)}")
        except (ValueError, ZeroDivisionError):
            pass

    def _collect_inputs(self) -> dict:
        """Validate and assemble the model input payload."""
        try:
            data = {
                "age": int(float(self.vars["age"].get())),
                "gender": self.vars["gender"].get(),
                "height_cm": float(self.vars["height_cm"].get()),
                "weight_kg": float(self.vars["weight_kg"].get()),
                "systolic_bp": int(float(self.vars["systolic_bp"].get())),
                "blood_sugar": int(float(self.vars["blood_sugar"].get())),
                "cholesterol": int(float(self.vars["cholesterol"].get())),
                "smoking": bool(self.vars["smoking"].get()),
                "alcohol": bool(self.vars["alcohol"].get()),
                "exercise_freq": int(float(self.vars["exercise_freq"].get())),
                "sleep_hours": float(self.vars["sleep_hours"].get()),
                "stress_level": self.vars["stress_level"].get(),
                "family_history": bool(self.vars["family_history"].get()),
            }
        except ValueError:
            raise ValueError("Please enter valid numbers in all numeric fields.")

        if not (1 <= data["age"] <= 120):
            raise ValueError("Age must be between 1 and 120.")
        if data["height_cm"] <= 0 or data["weight_kg"] <= 0:
            raise ValueError("Height and weight must be positive.")

        data["bmi"] = round(data["weight_kg"] / ((data["height_cm"] / 100) ** 2), 1)
        existing = self.vars["existing"].get()
        data["existing_diseases"] = [] if existing == "None" else [existing]
        return data

    def _run_assessment(self) -> None:
        try:
            data = self._collect_inputs()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        result = predictor.predict(data)
        recommendations = generate_recommendations(data, result["risk_class"])
        result["recommendations"] = recommendations

        self.last_inputs = data
        self.last_prediction = result
        self._render_result(data, result)
        self.nb.select(1)  # jump to Results tab

    # ---- Result tab --------------------------------------------------------
    def _build_result_tab(self) -> None:
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Results  ")
        self.result_card = ttk.Frame(tab, style="Card.TFrame", padding=24)
        self.result_card.pack(fill="both", expand=True, padx=8, pady=8)
        self._result_placeholder = ttk.Label(
            self.result_card, style="Muted.TLabel",
            text="Run an assessment to see your results here.")
        self._result_placeholder.pack(pady=40)

    def _render_result(self, data: dict, result: dict) -> None:
        for w in self.result_card.winfo_children():
            w.destroy()

        risk = result["risk_level"]
        color = RISK_COLORS.get(risk, TEXT)

        top = ttk.Frame(self.result_card, style="Card.TFrame")
        top.pack(fill="x")
        tk.Label(top, text=f"{result['risk_score']}%", bg=CARD, fg=color,
                 font=("Segoe UI", 40, "bold")).pack(side="left")
        meta = ttk.Frame(top, style="Card.TFrame")
        meta.pack(side="left", padx=20)
        tk.Label(meta, text=risk, bg=CARD, fg=color,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(meta, text=f"Health Score: {result['health_score']} / 100      BMI: {data['bmi']}",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Button(top, text="⬇  Save PDF Report", style="Brand.TButton",
                   command=self._save_pdf).pack(side="right")

        # Probability bars
        prob_frame = ttk.Frame(self.result_card, style="Card.TFrame")
        prob_frame.pack(fill="x", pady=(18, 8))
        ttk.Label(prob_frame, text="Risk probabilities", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        for label, key, c in [("Low", "low", "#16a34a"),
                              ("Moderate", "moderate", "#d97706"),
                              ("High", "high", "#dc2626")]:
            row = ttk.Frame(prob_frame, style="Card.TFrame")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=10, anchor="w", bg=CARD, fg=TEXT).pack(side="left")
            pct = result["probabilities"].get(key, 0) * 100
            bar = tk.Frame(row, bg="#e2e8f0", height=16, width=400)
            bar.pack(side="left", fill="x", expand=True, padx=8)
            bar.pack_propagate(False)
            fill = tk.Frame(bar, bg=c, height=16)
            fill.place(relwidth=min(1.0, pct / 100), relheight=1)
            tk.Label(row, text=f"{pct:.0f}%", width=5, bg=CARD, fg=MUTED).pack(side="left")

        # Explanation
        exp_frame = ttk.Frame(self.result_card, style="Card.TFrame")
        exp_frame.pack(fill="x", pady=(12, 8))
        ttk.Label(exp_frame, text="Why this result? (top factors)", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        for e in result["explanation"][:5]:
            arrow = {"increases": "↑", "decreases": "↓"}.get(e["contribution"], "•")
            ecol = {"increases": "#dc2626", "decreases": "#16a34a"}.get(e["contribution"], MUTED)
            row = ttk.Frame(exp_frame, style="Card.TFrame")
            row.pack(fill="x")
            tk.Label(row, text=f"{arrow}  {e['label']}", bg=CARD, fg=ecol,
                     font=("Segoe UI", 10)).pack(side="left")

        # Recommendations (scrollable)
        ttk.Label(self.result_card, text="Personalized recommendations", style="Card.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 6))
        tree = ttk.Treeview(self.result_card, columns=("priority", "detail"),
                            show="tree headings", height=7)
        tree.heading("#0", text="Recommendation")
        tree.heading("priority", text="Priority")
        tree.heading("detail", text="Detail")
        tree.column("#0", width=200)
        tree.column("priority", width=80, anchor="center")
        tree.column("detail", width=420)
        for r in result["recommendations"]:
            tree.insert("", "end", text=r["title"],
                        values=(r["priority"].upper(), r["detail"]))
        tree.pack(fill="both", expand=True)

        tk.Label(self.result_card, text="⚠ " + result.get("disclaimer", DISCLAIMER),
                 bg=CARD, fg=MUTED, font=("Segoe UI", 8), wraplength=860,
                 justify="left").pack(anchor="w", pady=(10, 0))

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

    # ---- Chatbot tab -------------------------------------------------------
    def _build_chatbot_tab(self) -> None:
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Health Assistant  ")
        card = ttk.Frame(tab, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True, padx=8, pady=8)

        self.chat_log = tk.Text(card, wrap="word", height=20, bg="#f8fafc",
                                relief="flat", font=("Segoe UI", 10), state="disabled")
        self.chat_log.pack(fill="both", expand=True)
        self.chat_log.tag_configure("bot", foreground=BRAND_DARK, font=("Segoe UI", 10, "bold"))
        self.chat_log.tag_configure("user", foreground=TEXT, font=("Segoe UI", 10, "bold"))
        self.chat_log.tag_configure("msg", foreground=TEXT, font=("Segoe UI", 10))

        entry_row = ttk.Frame(card, style="Card.TFrame")
        entry_row.pack(fill="x", pady=(10, 0))
        self.chat_var = tk.StringVar()
        entry = ttk.Entry(entry_row, textvariable=self.chat_var)
        entry.pack(side="left", fill="x", expand=True)
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
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  About  ")
        card = ttk.Frame(tab, style="Card.TFrame", padding=28)
        card.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(card, text="About NCD Shield AI", style="H1.TLabel").pack(anchor="w")
        about = (
            "NCD Shield AI is an early-screening and risk-prediction tool for Non-Communicable "
            "Diseases: Diabetes, Hypertension, Heart Disease, and Chronic Kidney Disease.\n\n"
            "It estimates your risk from everyday lifestyle and health data using a machine-"
            "learning model, explains which factors drive your result, and offers personalized, "
            "prioritized recommendations — which you can export as a PDF report for your doctor.\n\n"
            "This desktop edition reuses the same ML model and logic as the full web platform, "
            "packaged into a single window for easy testing and demos."
        )
        ttk.Label(card, text=about, style="Card.TLabel", wraplength=860,
                  justify="left").pack(anchor="w", pady=(10, 16))
        tk.Label(card, text="⚠  IMPORTANT: This is NOT a medical diagnosis tool. It is an early "
                 "screening and risk-prediction system. Always consult a qualified physician.",
                 bg="#fef2f2", fg="#b91c1c", font=("Segoe UI", 10, "bold"),
                 wraplength=860, justify="left", padx=14, pady=12).pack(anchor="w", fill="x")


def main() -> None:
    app = NCDShieldApp()
    app.mainloop()


if __name__ == "__main__":
    main()
