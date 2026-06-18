<p align="center">
  <img src="assets/banner.png" width="100%" />
</p>

<h1 align="center">🧠 TAIF: Multimodal Autism Screening & Developmental Support System</h1>

<p align="center"><b>طِيف · AI-Guided Child Development · Questionnaire · Vision · Speech/Text · PDF Report</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Machine%20Learning-Questionnaire%20Models-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Vision-ResNet50-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Speech-AssemblyAI%20%2B%20Text%20Analysis-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Live%20Demo-Coming%20Soon-lightgrey?style=for-the-badge" />
</p>

<div align="center">
  <table>
    <tr>
      <td align="center" width="850">
        <h2>🌟 Executive Summary</h2>
        <p>
          TAIF is a bilingual Arabic/English Streamlit system for early autism screening support and child development guidance. It combines structured questionnaire models, optional visual assessment, speech-to-text communication analysis, PDF reporting, and developmental support modules in one end-to-end application.
        </p>
      </td>
    </tr>
  </table>
</div>

---

## 📑 Table of Contents

1. [Problem Statement](#problem-statement)
2. [Why Autism Screening Matters](#why-autism-screening-matters)
3. [Dataset Description](#dataset-description)
4. [Project Pipeline](#project-pipeline)
5. [System Architecture](#system-architecture)
6. [Model Performance](#model-performance)
7. [Streamlit App UI Preview](#streamlit-app-ui-preview)
8. [Project Features](#project-features)
9. [How to Run Locally](#how-to-run-locally)
10. [Required Model Files](#required-model-files)
11. [Environment Variables](#environment-variables)
12. [Folder Structure](#folder-structure)
13. [Clinical Disclaimer](#clinical-disclaimer)
14. [Limitations](#limitations)
15. [Contact](#contact)

---

## Problem Statement

Many children with developmental or autism-related indicators may not receive timely screening because of limited access to specialists, long waiting lists, cost barriers, and low awareness.

**TAIF addresses this gap by providing an accessible screening-support interface that helps organize early indicators, generate a structured report, and suggest age-appropriate developmental support.**

> TAIF is a screening-support tool only. It does not diagnose Autism Spectrum Disorder and must not replace certified clinical evaluation.

---

## Why Autism Screening Matters

- Early screening can help families seek professional support sooner.
- Structured questionnaires can organize parent observations.
- Digital tools can support triage in low-resource settings.
- Multimodal inputs such as behavior, image, and speech/text can enrich the screening picture.
- Reports can help communicate observations clearly to specialists.

---

## Dataset Description

| Module | Dataset / Source | Purpose |
|---|---|---|
| Toddler questionnaire | Kaggle: Early Autism Screening Dataset for Toddlers | 12–32 months structured screening model |
| Child questionnaire | Kaggle: Autistic Spectrum Disorder dataset | 3–12 years structured screening model |
| Vision model | Kaggle: Autism image dataset by jobincjohnson | ResNet50 visual assessment |
| Speech module | AssemblyAI transcription + rule-based text analysis | Communication-pattern support indicators |

Dataset links are documented in `docs/DATA_CARD.md`.

---

## Project Pipeline

<p align="center">
  <img src="assets/project_pipeline.png" width="95%" />
</p>

---

## System Architecture

<p align="center">
  <img src="assets/system_architecture.png" width="95%" />
</p>

---

## Model Performance

<p align="center">
  <img src="assets/model_performance_cards.png" width="95%" />
</p>

### Performance Table

| Component | Accuracy | Precision | Recall | F1 Score | Notes |
|---|---:|---:|---:|---:|---|
| Toddler questionnaire model | 96.68% | 96.83% | 96.68% | 96.63% | Evaluated from available toddler model/data split |
| Questionnaire model 3–12 | 98.58% | 98.66% | 98.58% | 98.59% | Extracted from notebook outputs |
| Vision ResNet50 model | 97.14% | 97.83% | 96.43% | 97.12% | Extracted from vision notebook outputs |
| Speech module | — | — | — | — | Speech-to-text + transcript analysis, not an acoustic ML classifier |

### Evaluation Visuals

<details>
<summary><strong>📊 Click to expand model result images</strong></summary>

#### Toddler Questionnaire Confusion Matrix
<p align="center"><img src="assets/model_results/toddler_questionnaire_confusion_matrix.png" width="70%" /></p>

#### Questionnaire 3–12 Confusion Matrix
<p align="center"><img src="assets/model_results/questionnaire_3_12_confusion_matrix.png" width="70%" /></p>

#### Vision Model Confusion Matrices
<p align="center"><img src="assets/model_results/vision_confusion_matrix_test.png" width="70%" /></p>
<p align="center"><img src="assets/model_results/vision_confusion_matrix_validation.png" width="70%" /></p>

#### Performance Comparison
<p align="center"><img src="assets/model_results/model_performance_comparison.png" width="75%" /></p>

</details>

---

## Streamlit App UI Preview

<p align="center">
  <img src="assets/ui_gallery_collage.png" width="95%" />
</p>

<details>
<summary><strong>📸 Click to expand full UI gallery</strong></summary>

### Home / Language Selection
<p align="center"><img src="assets/ui/01_home_language.png" width="85%" /></p>

### Child Information
<p align="center"><img src="assets/ui/02_child_information.png" width="85%" /></p>

### Screening Inputs
<p align="center"><img src="assets/ui/03_screening_inputs_behavioral.png" width="85%" /></p>

### Vision & Speech Inputs
<p align="center"><img src="assets/ui/04_vision_speech_inputs.png" width="85%" /></p>

### Screening Report
<p align="center"><img src="assets/ui/05_screening_report_summary.png" width="85%" /></p>

### Recommendations
<p align="center"><img src="assets/ui/06_report_recommendations.png" width="85%" /></p>

### PDF Report
<p align="center"><img src="assets/ui/07_pdf_report_page1.png" width="85%" /></p>
<p align="center"><img src="assets/ui/08_pdf_report_page2.png" width="85%" /></p>

### Development Support
<p align="center"><img src="assets/ui/09_development_support.png" width="85%" /></p>

### Story Support
<p align="center"><img src="assets/ui/10_story_selection.png" width="85%" /></p>
<p align="center"><img src="assets/ui/11_generated_story.png" width="85%" /></p>
<p align="center"><img src="assets/ui/12_story_questions.png" width="85%" /></p>

</details>

---

## Project Features

<details>
<summary><strong>✨ Click to expand Feature Highlights</strong></summary>

### Core Features

- Arabic / English bilingual Streamlit interface
- Privacy-friendly child code instead of real name
- Age-aware screening flow
- Behavioral questionnaire screening
- Optional image-based visual assessment
- Optional speech upload or manual transcript input
- Fusion scoring across available inputs
- Clean result cards with probability ring
- PDF report generation
- Therapy and development support section
- Therapeutic story generator with follow-up questions

### Technical Features

- Modular pipelines: questionnaire, vision, audio/text, fusion
- Streamlit-based frontend
- ResNet50-based visual model
- AssemblyAI speech-to-text integration
- Transcript-based communication indicator analysis
- ReportLab PDF generation
- Arabic text support in reports
- GitHub-ready documentation and assets

</details>

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/taif-autism-screening-system.git
cd taif-autism-screening-system
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add required model files

Place the model files in the `models/` folder:

```text
models/numeric_model.pkl
models/model.pkl
models/resnet50.h5
```

### 5. Run the app

```bash
python -m streamlit run app/streamlit_app_ar_en_final.py
```

---

## Required Model Files

The repository is prepared to receive the following trained models:

```text
models/numeric_model.pkl
models/model.pkl
models/resnet50.h5
```

If model files are larger than GitHub's normal file limit, use Git LFS:

```bash
git lfs install
git lfs track "*.h5" "*.pkl" "*.keras" "*.joblib"
git add .gitattributes
```

---

## Environment Variables

For speech transcription, set your AssemblyAI key.

PowerShell:

```powershell
$env:ASSEMBLYAI_API_KEY="your_api_key_here"
```

Or create a local `.env` file based on `.env.example`. Never commit the real `.env` file.

---

## Folder Structure

```text
taif-autism-screening-system/
│
├── app/
│   └── streamlit_app_ar_en_final.py
│
├── assets/
│   ├── banner.png
│   ├── project_pipeline.png
│   ├── system_architecture.png
│   ├── model_performance_cards.png
│   ├── ui/
│   └── model_results/
│
├── models/
│   ├── README.md
│   ├── numeric_model.pkl      # add locally
│   ├── model.pkl              # add locally
│   └── resnet50.h5            # add locally
│
├── pipeline/
│   ├── diagnosis_pipeline.py
│   ├── questionnaire_pipeline.py
│   ├── vision_pipeline.py
│   ├── audio_pipeline.py
│   └── fusion_model.py
│
├── modules/
│   ├── transcript_analysis.py
│   ├── recommendation_engine.py
│   ├── embeddings.py
│   ├── medical_notes.py
│   └── rag_engine.py
│
├── treatment/
│   ├── therapy_engine.py
│   ├── story_generator.py
│   └── question_generator.py
│
├── notebooks/
│   ├── questionnaire_3_12_model.ipynb
│   └── vision_resnet50_training.ipynb
│
├── training/
│   ├── train.py
│   ├── predict.py
│   ├── classifier.py
│   ├── preprocessor.py
│   └── data.csv
│
├── docs/
│   ├── DATA_CARD.md
│   ├── MODEL_CARD.md
│   └── ETHICS_CARD.md
│
├── requirements.txt
├── .env.example
├── .gitignore
├── .gitattributes
└── README.md
```

---

## Clinical Disclaimer

⚠️ **TAIF is not a diagnostic medical system.**

It is an educational AI screening-support project designed to organize early indicators and generate supportive reports. Autism Spectrum Disorder diagnosis must be performed by qualified clinicians using validated clinical evaluation, developmental history, behavioral observation, and specialist assessment.

No machine-learning model, screening questionnaire, image model, audio module, or digital report can replace professional medical evaluation.

---

## Limitations

- Questionnaire datasets may be small and highly structured.
- High performance may not generalize to all populations or clinical settings.
- Vision models can be sensitive to lighting, image quality, dataset bias, and model-class mapping.
- Speech module uses transcription and text indicators, not a raw acoustic diagnostic model.
- The tool is intended for demonstration, education, and screening support only.

---

## Contact

**Author:** Mohamed Abdo Aamer  
**Email:** moamedmer68@gmail.com  
**LinkedIn:** www.linkedin.com/in/mohamed-aamer055
