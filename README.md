# ResumeIQ — AI-free Resume & ATS Analyzer

ResumeIQ is a polished, privacy-minded resume review workspace built with Streamlit. It helps users review resume structure, compare a resume with a target job description, spot skill keywords, and download an improvement report.

> **Important:** ResumeIQ uses transparent heuristics and a built-in skills dictionary. Its score is an estimate, not an official ATS score or a prediction of hiring outcomes.

## Features

- Upload a text-based PDF resume or paste resume text.
- Estimate resume readiness using visible section, contact, skill, length, and bullet-format checks.
- Paste a job description to compare detected skills.
- Review missing keywords without encouraging dishonest keyword stuffing.
- Explore section audits and interactive Plotly charts.
- Download a Markdown review report.
- Responsive dark interface, glass-like panels, reduced-motion support, and keyboard-friendly native controls.
- No API key required. Uploaded content is processed in the app session and is not stored in a database by this project.

## Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create an app from this repository.
4. Choose `main` as the branch and `app.py` as the main file.
5. Deploy. No secrets or API keys are required.

## How the score works

The readiness score is a simple heuristic based on resume section detection, contact patterns, recognized skills, broad word-count range, and bullet-like formatting. Job matching is a separate skill overlap view based on a built-in dictionary.

The tool does not perform optical character recognition on scanned PDFs. If the PDF has no selectable text, paste the resume text instead. It is not affiliated with any ATS provider.

## Privacy note

This application does not intentionally write resume content to a database or file. Hosting providers may process standard app telemetry/logs, and any public deployment should be used thoughtfully with sensitive personal information.

## License

MIT
