# 🖥️ NCD Shield AI — Desktop (Tkinter)

A single-window desktop edition of NCD Shield AI — ideal for **quick testing and
demos**. No Docker, Node.js, database, or browser required. It reuses the project's
real ML model and services (prediction, recommendations, chatbot, PDF report).

## Features
- 14-factor health assessment form with automatic BMI calculation
- 📄 **Scan Medical Report (OCR)** — upload a lab report (PDF/image) to auto-fill
  blood sugar, cholesterol, blood pressure, age, height & weight
- AI risk screening: Low / Moderate / High, with probability bars
- Explainable result (top contributing factors)
- Personalized, prioritized recommendations
- Built-in healthcare chatbot (never diagnoses)
- Export a professional **PDF report**

## Optional: enable the medical report scanner
```bash
pip install -r desktop/requirements.txt
```
For **image** scans you also need the Tesseract OCR engine:
- Windows: <https://github.com/UB-Mannheim/tesseract/wiki>
- macOS: `brew install tesseract`  ·  Linux: `sudo apt install tesseract-ocr`

Text-based **PDFs** work without Tesseract (handled by `pdfplumber`/`pypdf`).
If the extras aren't installed, the rest of the app runs fine — the Scan button
simply explains what's missing.

## Requirements
- **Python 3.10+** (Tkinter ships with Python on Windows & macOS;
  on Linux install it: `sudo apt install python3-tk`)
- The backend Python dependencies (model + PDF libraries)

## Setup & Run

From the **project root**:

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 2. install dependencies
pip install -r backend/requirements.txt

# 3. (optional) train the real ML model — otherwise a built-in
#    heuristic is used automatically so the demo still works
cd ml && python generate_dataset.py && python train.py && cd ..

# 4. launch the desktop app
python desktop/ncd_shield_desktop.py
```

A window titled **“NCD Shield AI — Early NCD Screening (Desktop)”** opens.

## How it works
The app sets `MODEL_DIR` to `ml/models/` and adds `backend/` to the Python path,
then imports the existing services:

| Imported from | Used for |
|---------------|----------|
| `app.ml.predictor` | model loading + explainable prediction (heuristic fallback) |
| `app.services.recommendations` | personalized guidance |
| `app.services.chatbot` | healthcare assistant |
| `app.services.pdf_report` | PDF report generation |

> ⚠️ **Disclaimer:** NCD Shield AI is an early-screening and risk-prediction tool,
> **NOT** a medical diagnosis. Always consult a qualified physician.
