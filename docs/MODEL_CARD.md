# MODEL CARD

## Intended Use
TAIF is an educational AI screening support system for early autism indicators. It is designed to support awareness and triage, not medical diagnosis.

## Model Components

| Component | Method | Output |
|---|---|---|
| Toddler questionnaire | Structured ML classifier | Risk probability |
| 3–12 questionnaire | Structured ML classifier | Risk probability |
| Vision assessment | ResNet50 image classifier | ASD image probability |
| Speech module | AssemblyAI transcript + text indicators | Communication-risk score |

## Performance Summary

| Component | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Toddler questionnaire | 96.68% | 96.83% | 96.68% | 96.63% |
| Questionnaire 3–12 | 98.58% | 98.66% | 98.58% | 98.59% |
| Vision ResNet50 | 97.14% | 97.83% | 96.43% | 97.12% |

## Important Limitation
The speech module is not a trained acoustic classifier. It uses speech-to-text transcription and communication-pattern analysis.
