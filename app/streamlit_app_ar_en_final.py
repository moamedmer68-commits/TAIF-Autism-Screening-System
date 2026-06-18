"""
TAIF Autism Screening System
Bilingual Streamlit interface: Arabic / English.

This reviewed version localizes the interface and also prevents hidden model
errors from appearing to the parent as a false 0% screening result.
"""

import base64
import html
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = Path(BASE_DIR) / "assets"
LOGO_PATH = ASSETS_DIR / "taif_logo.jpg"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.diagnosis_pipeline import diagnose
from treatment.question_generator import generate_questions
from treatment.story_generator import generate_story
from treatment.therapy_engine import therapy_plan

# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="TAIF - Autism Screening System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Language helpers
# -----------------------------------------------------------------------------

LANG_NAMES = {"en": "English", "ar": "العربية"}
YES_NO = {"Yes": {"en": "Yes", "ar": "نعم"}, "No": {"en": "No", "ar": "لا"}}
GENDERS = {"Female": {"en": "Female", "ar": "أنثى"}, "Male": {"en": "Male", "ar": "ذكر"}}
RISK_LABELS = {
    "Low Risk": {"en": "Low Risk", "ar": "مؤشر منخفض"},
    "Moderate Risk": {"en": "Moderate Risk", "ar": "مؤشر متوسط"},
    "High Risk": {"en": "High Risk", "ar": "مؤشر مرتفع"},
}

T = {
    "app_title": {"en": "🧠 TAIF Autism Screening System", "ar": "🧠 نظام طيف للفحص الأولي للتوحد"},
    "app_subtitle": {"en": "Early screening and developmental support for children", "ar": "فحص أولي ودعم نمائي للأطفال"},
    "medical_disclaimer_title": {"en": "Medical Disclaimer", "ar": "تنبيه طبي"},
    "medical_disclaimer": {
        "en": "This tool provides an initial screening indicator only. It is not a substitute for a professional medical diagnosis. Always consult a certified specialist.",
        "ar": "هذه الأداة تقدم مؤشر فحص أولي فقط، ولا تُعد تشخيصًا طبيًا نهائيًا. يجب دائمًا الرجوع إلى أخصائي معتمد.",
    },
    "choose_language": {"en": "Choose Language", "ar": "اختر اللغة"},
    "current_language": {"en": "Current language", "ar": "اللغة الحالية"},
    "sidebar_caption": {"en": "Early screening and developmental support", "ar": "فحص أولي ودعم نمائي"},
    "start_new_case": {"en": "🏠 Start New Case", "ar": "🏠 بدء حالة جديدة"},
    "previous_cases": {"en": "📁 Previous Cases", "ar": "📁 الحالات السابقة"},
    "back_current_case": {"en": "↩ Back to Current Case", "ar": "↩ الرجوع للحالة الحالية"},
    "case_id": {"en": "Case ID", "ar": "رقم الحالة"},

    "progress_1": {"en": "1. Child Information", "ar": "١. بيانات الطفل"},
    "progress_2": {"en": "2. Screening Inputs", "ar": "٢. بيانات الفحص"},
    "progress_3": {"en": "3. Screening Report", "ar": "٣. تقرير الفحص"},
    "progress_4": {"en": "4. Development Support", "ar": "٤. الدعم النمائي"},

    "child_information": {"en": "👤 Child Information", "ar": "👤 بيانات الطفل"},
    "child_information_caption": {"en": "Enter general information and confirm guardian consent before starting the screening.", "ar": "أدخل البيانات العامة ووافق على إقرار ولي الأمر قبل بدء الفحص."},
    "patient_code": {"en": "Patient Code / Child Code", "ar": "كود الطفل / كود الحالة"},
    "patient_code_help": {"en": "Use a code instead of the child's real name to protect privacy.", "ar": "استخدم كودًا بدلًا من اسم الطفل الحقيقي لحماية الخصوصية."},
    "child_age": {"en": "Child Age", "ar": "عمر الطفل"},
    "gender": {"en": "Gender", "ar": "النوع"},
    "jaundice": {"en": "Jaundice at birth?", "ar": "هل حدث صفراء عند الولادة؟"},
    "family_history": {"en": "Family history of autism or developmental conditions?", "ar": "هل توجد حالات توحد أو تأخر نمائي في العائلة؟"},
    "language_delay": {"en": "Language delay observed?", "ar": "هل يوجد تأخر لغوي ملحوظ؟"},
    "ethnicity": {"en": "Ethnicity", "ar": "الخلفية / العِرق"},
    "completed_by": {"en": "Who completed the screening form?", "ar": "من قام بملء نموذج الفحص؟"},
    "others": {"en": "Others", "ar": "أخرى"},
    "family_member": {"en": "Family member", "ar": "أحد أفراد الأسرة"},
    "general_development_information": {"en": "General Development Information", "ar": "معلومات نمائية عامة"},
    "sleep_issues": {"en": "Sleep problems?", "ar": "هل توجد مشكلات في النوم؟"},
    "screen_time": {"en": "Screen time concerns?", "ar": "هل توجد مخاوف من وقت الشاشة؟"},
    "school_notes": {"en": "School or nursery concerns?", "ar": "هل توجد ملاحظات من المدرسة أو الحضانة؟"},
    "parent_notes": {"en": "Parent or school notes (optional)", "ar": "ملاحظات ولي الأمر أو المدرسة (اختياري)"},
    "guardian_consent": {"en": "🔐 Guardian Consent", "ar": "🔐 موافقة ولي الأمر"},
    "consent_text": {
        "en": "I understand that this is an initial screening support tool, and I have permission to enter image, audio, or text data for this child.",
        "ar": "أفهم أن هذه أداة دعم للفحص الأولي فقط، ولديّ إذن بإدخال صورة أو صوت أو نص يخص هذا الطفل.",
    },
    "next_screening": {"en": "Next: Screening Inputs ➜", "ar": "التالي: بيانات الفحص ➜"},
    "patient_code_error": {"en": "Please enter a patient code. Avoid using the child's real name.", "ar": "من فضلك أدخل كود الحالة وتجنب كتابة اسم الطفل الحقيقي."},
    "consent_error": {"en": "Guardian consent is required before continuing.", "ar": "يجب الموافقة على إقرار ولي الأمر قبل المتابعة."},

    "screening_inputs": {"en": "📝 Screening Inputs", "ar": "📝 بيانات الفحص"},
    "screening_inputs_caption": {"en": "Complete the questionnaire and optionally add a clear image and a speech sample.", "ar": "أكمل الأسئلة ويمكنك اختياريًا إضافة صورة واضحة وعينة كلام."},
    "start_child_info_warning": {"en": "Please start with the child information page.", "ar": "من فضلك ابدأ بصفحة بيانات الطفل."},
    "go_child_info": {"en": "Go to Child Information", "ar": "الذهاب إلى بيانات الطفل"},
    "behavioral_assessment": {"en": "Behavioral Assessment", "ar": "تقييم سلوكي"},
    "behavioral_caption": {"en": "Move each slider based on your observations. 0 means no concern and 1 means a strong concern.", "ar": "حرّك كل مؤشر حسب ملاحظتك. 0 يعني لا توجد مشكلة و 1 يعني وجود قلق واضح."},
    "social_concerns": {"en": "Social interaction concerns", "ar": "مخاوف في التفاعل الاجتماعي"},
    "communication_concerns": {"en": "Communication concerns", "ar": "مخاوف في التواصل"},
    "repetitive_concerns": {"en": "Repetitive behavior concerns", "ar": "مخاوف من سلوكيات متكررة"},
    "early_years_info": {"en": "The early-years questionnaire will be used for this age group.", "ar": "سيتم استخدام أسئلة المرحلة العمرية المبكرة لهذا العمر."},
    "behavioral_questionnaire": {"en": "📋 Behavioral Questionnaire", "ar": "📋 أسئلة السلوك"},
    "questionnaire_caption": {"en": "Answer based on the child's usual behavior.", "ar": "أجب بناءً على سلوك الطفل المعتاد."},
    "visual_assessment": {"en": "👁️ Visual Assessment", "ar": "👁️ تقييم الصورة"},
    "visual_caption": {"en": "Optional. Upload a clear facial image when available.", "ar": "اختياري. ارفع صورة واضحة للوجه إذا كانت متاحة."},
    "upload_image": {"en": "Upload child image", "ar": "رفع صورة الطفل"},
    "image_preview": {"en": "Uploaded image preview", "ar": "معاينة الصورة المرفوعة"},
    "speech_assessment": {"en": "🎤 Speech and Communication Assessment", "ar": "🎤 تقييم الكلام والتواصل"},
    "speech_caption": {"en": "Optional. Enter a written sample, upload audio, or record a short sample.", "ar": "اختياري. أدخل عينة مكتوبة أو ارفع ملفًا صوتيًا أو سجل عينة قصيرة."},
    "input_mode": {"en": "Input mode", "ar": "طريقة الإدخال"},
    "written_sample": {"en": "Written Speech Sample", "ar": "عينة كلام مكتوبة"},
    "upload_audio": {"en": "Upload Audio", "ar": "رفع ملف صوتي"},
    "record": {"en": "Record", "ar": "تسجيل"},
    "written_speech_sample": {"en": "Written speech sample", "ar": "عينة الكلام المكتوبة"},
    "speech_placeholder": {"en": "Type the child's speech sample here...", "ar": "اكتب عينة كلام الطفل هنا..."},
    "upload_audio_file": {"en": "Upload audio file", "ar": "رفع ملف صوتي"},
    "transcription_unavailable": {"en": "Automatic transcription is not currently available. You may use the written speech sample instead.", "ar": "التفريغ الصوتي التلقائي غير متاح حاليًا. يمكنك استخدام عينة الكلام المكتوبة بدلًا منه."},
    "record_child_speech": {"en": "Record child speech", "ar": "تسجيل كلام الطفل"},
    "recording_captured": {"en": "Recording captured.", "ar": "تم التقاط التسجيل."},
    "recording_unavailable": {"en": "Microphone recording is not available in this version. Use audio upload or the written speech sample.", "ar": "التسجيل من الميكروفون غير متاح في هذه النسخة. استخدم رفع الصوت أو عينة الكلام المكتوبة."},
    "back": {"en": "⬅ Back", "ar": "⬅ رجوع"},
    "run_screening": {"en": "🔍 Run Screening", "ar": "🔍 تشغيل الفحص"},
    "answer_all_questions_error": {"en": "Please answer all 10 questionnaire items before running the screening.", "ar": "من فضلك أجب على كل الأسئلة العشرة قبل تشغيل الفحص."},
    "preparing_report": {"en": "Preparing the screening report...", "ar": "جاري تجهيز تقرير الفحص..."},
    "screening_error": {"en": "We could not complete the screening. Please review the entered information and try again later.", "ar": "لم نتمكن من إكمال الفحص. راجع البيانات المدخلة ثم حاول مرة أخرى."},

    "report_header": {"en": "📊 Screening Report", "ar": "📊 تقرير الفحص"},
    "no_report_warning": {"en": "No screening report is available yet.", "ar": "لا يوجد تقرير فحص متاح حتى الآن."},
    "go_screening_inputs": {"en": "Go to Screening Inputs", "ar": "الذهاب إلى بيانات الفحص"},
    "screening_result": {"en": "Screening Result", "ar": "نتيجة الفحص"},
    "estimated_probability": {"en": "Estimated Screening Probability", "ar": "النسبة التقديرية للفحص"},
    "initial_indicator": {"en": "This result is an initial screening indicator only and is not a final medical diagnosis.", "ar": "هذه النتيجة مؤشر فحص أولي فقط وليست تشخيصًا طبيًا نهائيًا."},
    "assessment_summary": {"en": "Assessment Summary", "ar": "ملخص التقييم"},
    "overall_screening": {"en": "Overall Screening Result", "ar": "النتيجة العامة للفحص"},
    "questionnaire_assessment": {"en": "Questionnaire Assessment", "ar": "تقييم الأسئلة"},
    "no_image_info": {"en": "No image was provided, so the visual assessment was not included.", "ar": "لم يتم رفع صورة، لذلك لم يتم إدراج تقييم الصورة."},
    "vision_warning": {"en": "The visual assessment could not be completed. Please upload another clear image or continue without it.", "ar": "لم يكتمل تقييم الصورة. يمكنك رفع صورة أوضح أو المتابعة بدونه."},
    "no_speech_info": {"en": "No speech sample was provided, so this assessment was not included.", "ar": "لم يتم إدخال عينة كلام، لذلك لم يتم إدراج هذا التقييم."},
    "speech_warning": {"en": "The speech assessment could not be completed. You may enter a written speech sample instead.", "ar": "لم يكتمل تقييم الكلام. يمكنك إدخال عينة كلام مكتوبة بدلًا من ذلك."},
    "observed_indicators": {"en": "🔍 Observed Indicators", "ar": "🔍 مؤشرات ملاحظة"},
    "general_recommendations": {"en": "General Recommendations", "ar": "توصيات عامة"},
    "support_focus": {"en": "🎯 Age-Appropriate Support Focus", "ar": "🎯 نقاط دعم مناسبة للعمر"},
    "optional_parts_error": {"en": "One or more optional parts of the assessment could not be completed. You may continue or try again later.", "ar": "لم يكتمل جزء أو أكثر من الأجزاء الاختيارية. يمكنك المتابعة أو المحاولة لاحقًا."},
    "scoring_notes": {"en": "Scoring notes", "ar": "ملاحظات التقييم"},
    "scoring_source": {"en": "Scoring method", "ar": "طريقة التقييم"},
    "model_scoring": {"en": "Trained model", "ar": "الموديل المدرب"},
    "fallback_scoring": {"en": "Backup rule-based score because the questionnaire model could not run", "ar": "تقييم احتياطي بالقواعد لأن موديل الأسئلة لم يعمل"},
    "download_pdf": {"en": "⬇️ Download Full PDF Report", "ar": "⬇️ تحميل التقرير PDF"},
    "pdf_unavailable": {"en": "PDF export is temporarily unavailable. Please install the PDF reporting dependency and try again.", "ar": "تصدير PDF غير متاح حاليًا. تأكد من تثبيت مكتبات التقرير ثم حاول مرة أخرى."},
    "next_step": {"en": "Next Step", "ar": "الخطوة التالية"},
    "continue_support_question": {"en": "Continue to developmental support activities and the therapeutic story?", "ar": "هل تريد المتابعة إلى أنشطة الدعم النمائي والقصة العلاجية؟"},
    "back_inputs": {"en": "⬅ Back to Inputs", "ar": "⬅ الرجوع للمدخلات"},
    "finish_here": {"en": "Finish Here", "ar": "إنهاء هنا"},
    "report_saved": {"en": "The screening report has been saved.", "ar": "تم حفظ تقرير الفحص."},
    "continue_support": {"en": "Continue to Support ➜", "ar": "المتابعة إلى الدعم ➜"},

    "therapy_header": {"en": "💙 Therapy and Development Support", "ar": "💙 الدعم العلاجي والنمائي"},
    "suggested_support_activities": {"en": "🏥 Suggested Support Activities", "ar": "🏥 أنشطة دعم مقترحة"},
    "parent_guidance": {"en": "👪 Parent Guidance", "ar": "👪 إرشادات لولي الأمر"},
    "development_focus_areas": {"en": "🎯 Development Focus Areas", "ar": "🎯 مجالات التركيز النمائي"},
    "choose_story_name": {"en": "📖 Choose a Story Name", "ar": "📖 اختر اسم القصة"},
    "story_name": {"en": "Story name", "ar": "اسم القصة"},
    "enter_another_story_name": {"en": "Enter another story name", "ar": "إدخال اسم قصة آخر"},
    "create_my_story": {"en": "📖 Create My Story", "ar": "📖 إنشاء القصة"},
    "choose_story_warning": {"en": "Please choose or enter a story name.", "ar": "من فضلك اختر أو اكتب اسم القصة."},
    "selected_story": {"en": "📖 Selected Therapeutic Story", "ar": "📖 القصة العلاجية المختارة"},
    "story": {"en": "Story", "ar": "قصة"},
    "generate_another_story": {"en": "🔄 Generate Another Story", "ar": "🔄 إنشاء قصة أخرى"},
    "story_questions": {"en": "❓ Story Questions", "ar": "❓ أسئلة القصة"},
    "story_questions_caption": {"en": "Answer the questions after reading the story. This activity helps practice understanding, memory, and communication.", "ar": "أجب عن الأسئلة بعد قراءة القصة. هذا النشاط يساعد على الفهم والذاكرة والتواصل."},
    "start_optional_questions": {"en": "Start optional story questions", "ar": "بدء أسئلة القصة الاختيارية"},
    "select_answer": {"en": "— Select an answer —", "ar": "— اختر إجابة —"},
    "answer": {"en": "Answer", "ar": "إجابة"},
    "finish_quiz": {"en": "✅ Finish Quiz and Show Result", "ar": "✅ إنهاء الأسئلة وعرض النتيجة"},
    "answer_all_quiz": {"en": "Please answer all questions before finishing the quiz.", "ar": "من فضلك أجب على كل الأسئلة قبل إنهاء الاختبار."},
    "quiz_result": {"en": "Quiz Result", "ar": "نتيجة الأسئلة"},
    "correct_answers": {"en": "correct answers", "ar": "إجابات صحيحة"},
    "question": {"en": "Question", "ar": "السؤال"},
    "child_answer": {"en": "Child's Answer", "ar": "إجابة الطفل"},
    "correct_answer": {"en": "Correct Answer", "ar": "الإجابة الصحيحة"},
    "simple_explanation": {"en": "Simple Explanation", "ar": "شرح بسيط"},
    "skill_to_practice": {"en": "Skill to Practice", "ar": "مهارة للتدريب"},
    "correct_answer_msg": {"en": "Correct answer", "ar": "إجابة صحيحة"},
    "review_question_msg": {"en": "Review this question together and practice the suggested skill.", "ar": "راجع هذا السؤال مع الطفل وتدرّبوا على المهارة المقترحة."},
    "suggested_focus_next": {"en": "Suggested focus for the next activity: ", "ar": "التركيز المقترح للنشاط القادم: "},
    "excellent_result": {"en": "Excellent result. Continue with similar activities and gradually increase the difficulty.", "ar": "نتيجة ممتازة. استمر في أنشطة مشابهة وزِد الصعوبة تدريجيًا."},
    "questions_optional_info": {"en": "The story questions are optional. Start them when the child is ready.", "ar": "أسئلة القصة اختيارية. ابدأ بها عندما يكون الطفل مستعدًا."},
    "support_disclaimer": {"en": "These suggestions are general developmental support ideas only. A certified specialist should create the final treatment plan.", "ar": "هذه الاقتراحات أفكار دعم نمائي عامة فقط، ويجب أن يضع الأخصائي المعتمد الخطة العلاجية النهائية."},
    "back_report": {"en": "⬅ Back to Report", "ar": "⬅ الرجوع للتقرير"},

    "previous_reports_header": {"en": "📁 Previous Screening Reports", "ar": "📁 تقارير الفحص السابقة"},
    "previous_reports_caption": {"en": "Review previous screening cases and download their printable PDF reports.", "ar": "راجع الحالات السابقة وقم بتحميل تقارير PDF قابلة للطباعة."},
    "no_previous_reports": {"en": "No previous reports are available.", "ar": "لا توجد تقارير سابقة متاحة."},
    "saved_reports": {"en": "Saved Reports", "ar": "التقارير المحفوظة"},
    "story_label": {"en": "Story", "ar": "القصة"},
    "not_selected": {"en": "Not selected", "ar": "لم يتم الاختيار"},
    "date": {"en": "Date", "ar": "التاريخ"},
    "patient_code_short": {"en": "Patient Code", "ar": "كود الطفل"},
    "age_short": {"en": "Age", "ar": "العمر"},
    "saved_pdf_error": {"en": "This saved report could not be opened.", "ar": "تعذر فتح هذا التقرير المحفوظ."},
    "download_pdf_short": {"en": "⬇️ Download PDF Report", "ar": "⬇️ تحميل تقرير PDF"},

    "not_included": {"en": "Not included", "ar": "غير مدرج"},
    "not_provided": {"en": "Not provided", "ar": "غير متوفر"},
    "no_additional_info": {"en": "No additional information was listed.", "ar": "لا توجد معلومات إضافية."},
    "no_specific_indicators": {"en": "No specific indicators were listed. Continue regular developmental monitoring.", "ar": "لا توجد مؤشرات محددة. استمر في المتابعة النمائية المنتظمة."},
}

QUESTIONS = {
    "en": [
        "Q1: Does the child respond when their name is called?",
        "Q2: Does the child make appropriate eye contact?",
        "Q3: Does the child point to show interest?",
        "Q4: Does the child enjoy playing with other children?",
        "Q5: Does the child use simple words or phrases appropriately?",
        "Q6: Does the child imitate facial expressions or actions?",
        "Q7: Does the child show interest in social games?",
        "Q8: Does the child follow simple instructions?",
        "Q9: Does the child avoid repetitive speech or repeated phrases?",
        "Q10: Does the child adapt well to changes in routine?",
    ],
    "ar": [
        "س١: هل يستجيب الطفل عند مناداة اسمه؟",
        "س٢: هل يتواصل بصريًا بشكل مناسب؟",
        "س٣: هل يشير بيده ليُظهر اهتمامه بشيء؟",
        "س٤: هل يستمتع باللعب مع الأطفال الآخرين؟",
        "س٥: هل يستخدم كلمات أو جمل بسيطة بشكل مناسب؟",
        "س٦: هل يقلد تعبيرات الوجه أو الأفعال؟",
        "س٧: هل يهتم بالألعاب الاجتماعية؟",
        "س٨: هل يتبع التعليمات البسيطة؟",
        "س٩: هل يتجنب تكرار الكلام أو العبارات بشكل ملحوظ؟",
        "س١٠: هل يتكيف جيدًا مع تغيير الروتين؟",
    ],
}

STORY_OPTIONS = {
    "en_young": ["The Colorful Blocks", "The Friendly Balloon", "A Day in the Garden", "The Little Star", "The Happy Train", "Enter another story name"],
    "en_old": ["The Robot Club", "The Secret Garden Adventure", "The Friendship Challenge", "The Brave Explorer", "The Creative Team", "Enter another story name"],
    "ar_young": ["المكعبات الملونة", "البالونة الصديقة", "يوم في الحديقة", "النجمة الصغيرة", "القطار السعيد", "إدخال اسم قصة آخر"],
    "ar_old": ["نادي الروبوت", "مغامرة الحديقة السرية", "تحدي الصداقة", "المستكشف الشجاع", "الفريق المبدع", "إدخال اسم قصة آخر"],
}


def init_state() -> None:
    defaults = {
        "page": 1,
        "language": "en",
        "case_id": str(uuid.uuid4())[:8].upper(),
        "child_profile": {},
        "screening_data": {},
        "result": None,
        "story": None,
        "selected_story_title": None,
        "story_questions": None,
        "quiz_feedback": None,
        "saved_report": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Compatibility with older saved session values from the previous version.
    if st.session_state.language in ["English", "en"]:
        st.session_state.language = "en"
    elif st.session_state.language in ["Arabic / عربي", "Arabic", "العربية", "ar"]:
        st.session_state.language = "ar"
    else:
        st.session_state.language = "en"


def lang() -> str:
    value = st.session_state.get("language", "en")
    return "ar" if value in ["ar", "Arabic", "Arabic / عربي", "العربية"] else "en"


def tr(key: str, default: str | None = None, language: str | None = None) -> str:
    code = language or lang()
    data = T.get(key)
    if isinstance(data, dict):
        return data.get(code) or data.get("en") or default or key
    return default or key


def localize_yes_no(value: str, language: str | None = None) -> str:
    code = language or lang()
    return YES_NO.get(value, {}).get(code, value)


def localize_gender(value: str, language: str | None = None) -> str:
    code = language or lang()
    return GENDERS.get(value, {}).get(code, value)


def localize_risk(value: str, language: str | None = None) -> str:
    code = language or lang()
    return RISK_LABELS.get(value, {}).get(code, value)


def display_value(value, language: str | None = None) -> str:
    code = language or lang()
    if value in [None, ""]:
        return tr("not_provided", language=code)
    if value in YES_NO:
        return localize_yes_no(value, code)
    if value in GENDERS:
        return localize_gender(value, code)
    if value in RISK_LABELS:
        return localize_risk(value, code)
    return str(value)


def percentage(value, language: str | None = None) -> str:
    if value is None:
        return tr("not_included", language=language)
    return f"{float(value) * 100:.1f}%"


def clamp_probability(value) -> float:
    """Convert any score value to a safe probability between 0 and 1."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def asd_status(score: float) -> tuple[str, str]:
    """Return the short ASD label and color used by the visual result cards."""
    score = clamp_probability(score)
    if score < 0.4:
        return "ASD Negative", "#34b7ad"
    if score < 0.7:
        return "ASD Possible", "#f59e0b"
    return "ASD Positive", "#ef4444"


def result_card(title: str, score, note: str | None = None) -> None:
    """Render a compact result card matching the requested ASD probability style."""
    value = clamp_probability(score)
    percent = value * 100
    status, accent = asd_status(value)
    note_html = f'<div class="taif-result-note">{html.escape(note)}</div>' if note else ""
    st.markdown(
        f"""
        <div class="taif-result-card">
            <div class="taif-result-circle" style="--p:{percent:.1f}; --accent:{accent};">
                <div class="taif-result-inner">{percent:.1f}%</div>
            </div>
            <div class="taif-result-text">
                <div class="taif-result-title">{html.escape(title)}</div>
                <div class="taif-result-status">{html.escape(status)}</div>
                <div class="taif-result-subtitle">Probability (ASD+)</div>
                {note_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def logo_data_uri() -> str | None:
    """Return the local TAIF logo as a data URI for reliable Streamlit display."""
    try:
        if not LOGO_PATH.exists():
            return None
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None


def show_logo(width: int = 310) -> None:
    """Show the TAIF logo centered when the asset is available."""
    uri = logo_data_uri()
    if not uri:
        return
    st.markdown(
        f"""
        <div class="taif-logo-wrap">
            <img src="{uri}" class="taif-logo" style="max-width:{int(width)}px;" alt="TAIF logo">
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_app() -> None:
    current_language = lang()
    st.session_state.case_id = str(uuid.uuid4())[:8].upper()
    st.session_state.child_profile = {}
    st.session_state.screening_data = {}
    st.session_state.result = None
    st.session_state.story = None
    st.session_state.selected_story_title = None
    st.session_state.story_questions = None
    st.session_state.quiz_feedback = None
    st.session_state.saved_report = None
    st.session_state.page = 1
    st.session_state.language = current_language
    st.rerun()


def go_to(page_number: int) -> None:
    st.session_state.page = page_number
    st.rerun()


def change_language(new_language: str) -> None:
    """Switch interface language and clear language-dependent story content."""
    if new_language != lang():
        st.session_state.language = new_language
        st.session_state.story = None
        st.session_state.selected_story_title = None
        st.session_state.story_questions = None
        st.session_state.quiz_feedback = None
    else:
        st.session_state.language = new_language
    st.rerun()


def yes_no_to_int(value: str) -> int:
    return 1 if value == "Yes" else 0


def safe_uploaded_file_seek(file_obj) -> None:
    try:
        if file_obj is not None:
            file_obj.seek(0)
    except Exception:
        pass


def risk_color(risk_level: str) -> str:
    if risk_level == "High Risk":
        return "#dc3545"
    if risk_level == "Moderate Risk":
        return "#fd7e14"
    return "#28a745"


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

DATA_DIR = Path(BASE_DIR) / "data"
DB_PATH = DATA_DIR / "taif_cases.db"


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE,
                created_at TEXT,
                patient_code TEXT,
                age INTEGER,
                gender TEXT,
                risk_level TEXT,
                final_score REAL,
                questionnaire_score REAL,
                vision_score REAL,
                audio_score REAL,
                report_json TEXT
            )
            """
        )
        conn.commit()


def save_case(report: dict) -> None:
    """Save or refresh the latest user-facing report for a case."""
    init_db()
    profile = report.get("child_profile", {})
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO cases (
                case_id, created_at, patient_code, age, gender, risk_level,
                final_score, questionnaire_score, vision_score, audio_score, report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(case_id) DO UPDATE SET
                created_at = excluded.created_at,
                patient_code = excluded.patient_code,
                age = excluded.age,
                gender = excluded.gender,
                risk_level = excluded.risk_level,
                final_score = excluded.final_score,
                questionnaire_score = excluded.questionnaire_score,
                vision_score = excluded.vision_score,
                audio_score = excluded.audio_score,
                report_json = excluded.report_json
            """,
            (
                report.get("case_id"),
                report.get("generated_at"),
                profile.get("patient_code"),
                profile.get("age"),
                profile.get("gender"),
                report.get("risk_level"),
                report.get("final_score"),
                report.get("questionnaire_score"),
                report.get("vision_score"),
                report.get("audio_score"),
                json.dumps(report, ensure_ascii=False),
            ),
        )
        conn.commit()


def load_history(limit: int = 50) -> list[dict]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT * FROM cases
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


# -----------------------------------------------------------------------------
# Parent-facing content helpers
# -----------------------------------------------------------------------------


def page_progress() -> None:
    labels = [tr("progress_1"), tr("progress_2"), tr("progress_3"), tr("progress_4")]
    current = min(int(st.session_state.page), 4)
    st.progress((current - 1) / 3)
    cols = st.columns(4)
    for index, col in enumerate(cols, 1):
        with col:
            if index == current:
                st.success(labels[index - 1])
            elif index < current:
                st.info(labels[index - 1])
            else:
                st.caption(labels[index - 1])


def age_risk_focus(age: int, risk: str, language: str | None = None) -> list[str]:
    code = language or lang()
    if code == "ar":
        if age <= 3:
            items = [
                "درّب الطفل على الاستجابة لاسمه، والتواصل البصري، والإشارة، والتقليد، واتباع تعليمات بسيطة من خطوة واحدة.",
                "استخدم جلسات لعب قصيرة من 5 إلى 10 دقائق عدة مرات يوميًا.",
            ]
        elif age <= 6:
            items = [
                "درّب الطفل على اللعب الاجتماعي، تبادل الدور، تسمية المشاعر، والمحادثات القصيرة.",
                "استخدم جداول مصورة وروتينًا بسيطًا في البيت والحضانة.",
            ]
        else:
            items = [
                "درّب الطفل على التواصل الاجتماعي، المرونة في التفكير، التفاعل مع الأقران، ومهارات الاستقلال اليومية.",
                "استخدم أهدافًا واضحة وتعزيزًا إيجابيًا وتعاونًا مع المدرسة.",
            ]
        if risk == "High Risk":
            items.insert(0, "رتّب تقييمًا متخصصًا في أقرب وقت ممكن.")
        elif risk == "Moderate Risk":
            items.insert(0, "يُفضل إجراء تقييم نمائي متخصص مع الاستمرار في المتابعة القريبة.")
        else:
            items.insert(0, "استمر في المتابعة النمائية وناقش أي مخاوف مستمرة مع أخصائي.")
        return items

    items: list[str] = []
    if age <= 3:
        items.extend(
            [
                "Practice responding to the child's name, eye contact, pointing, imitation, and simple one-step instructions.",
                "Use short play sessions of 5-10 minutes several times per day.",
            ]
        )
    elif age <= 6:
        items.extend(
            [
                "Practice social play, turn-taking, naming emotions, and short conversations.",
                "Use visual schedules and simple routines at home and nursery.",
            ]
        )
    else:
        items.extend(
            [
                "Practice social communication, flexible thinking, peer interaction, and daily independence skills.",
                "Use clear goals, positive reinforcement, and collaboration with the school.",
            ]
        )
    if risk == "High Risk":
        items.insert(0, "Arrange a specialist evaluation as soon as possible.")
    elif risk == "Moderate Risk":
        items.insert(0, "Consider a professional developmental assessment and continue close monitoring.")
    else:
        items.insert(0, "Continue developmental monitoring and discuss any ongoing concerns with a specialist.")
    return items


def parent_friendly_indicator(text: str, language: str | None = None) -> str:
    """Translate internal indicator wording into cautious parent-friendly language."""
    code = language or lang()
    value = str(text or "").lower()
    if code == "ar":
        if any(word in value for word in ["image", "vision", "facial", "visual"]):
            return "يشير تقييم الصورة إلى أن المتابعة مع أخصائي قد تكون مفيدة."
        if any(word in value for word in ["social", "interaction", "eye contact"]):
            return "تشير بعض الإجابات إلى أن الطفل قد يستفيد من دعم إضافي في التفاعل الاجتماعي."
        if any(word in value for word in ["speech", "language", "communication", "echolalia", "pronoun", "repeat"]):
            return "تشير بعض الإجابات إلى أهمية الاهتمام بتطور الكلام والتواصل."
        if any(word in value for word in ["routine", "repetitive", "behavior"]):
            return "تشير بعض الإجابات إلى أن الطفل قد يستفيد من دعم في الروتين والمرونة السلوكية."
        return "تشير نتائج الفحص إلى أن المتابعة مع أخصائي قد تكون مفيدة."

    if any(word in value for word in ["image", "vision", "facial", "visual"]):
        return "The visual assessment indicates that further specialist evaluation may be helpful."
    if any(word in value for word in ["social", "interaction", "eye contact"]):
        return "Some responses suggest that the child may benefit from additional support with social interaction."
    if any(word in value for word in ["speech", "language", "communication", "echolalia", "pronoun", "repeat"]):
        return "Some responses suggest that additional attention to speech and communication development may be helpful."
    if any(word in value for word in ["routine", "repetitive", "behavior"]):
        return "Some responses suggest that the child may benefit from support with routines and flexible behavior."
    return "The screening responses suggest that additional follow-up with a specialist may be helpful."


def observed_indicators(result: dict, language: str | None = None) -> list[str]:
    code = language or lang()
    recs = result.get("recommendations", {}) or {}
    source = recs.get("indicators", []) or []
    cleaned = list(dict.fromkeys(parent_friendly_indicator(item, code) for item in source))
    return cleaned or [tr("no_specific_indicators", language=code)]


def general_recommendations(result: dict, profile: dict, language: str | None = None) -> list[str]:
    code = language or lang()
    if code == "ar":
        risk = result.get("risk_level", "Low Risk")
        base = [
            "هذه الأداة للفحص الأولي فقط وليست تشخيصًا نهائيًا.",
            "استشر طبيب أطفال أو أخصائي نمو معتمد عند وجود أي قلق.",
        ]
        if risk == "High Risk":
            base += [
                "اطلب تقييمًا متخصصًا في أقرب وقت.",
                "التدخل المبكر مهم جدًا لدعم الطفل.",
                "فكر في علاج التخاطب والدعم السلوكي عند الحاجة.",
            ]
        elif risk == "Moderate Risk":
            base += [
                "حدد موعد متابعة مع طبيب أو أخصائي نمو.",
                "تابع تطور التواصل والتفاعل الاجتماعي.",
                "فكر في برامج دعم مبكر مناسبة لعمر الطفل.",
            ]
        else:
            base += [
                "استمر في المتابعة الدورية للنمو.",
                "شجع اللعب التفاعلي والأنشطة اليومية المناسبة للعمر.",
            ]
        return base

    recs = result.get("recommendations", {}) or {}
    source = recs.get("recommendations", []) or []
    cleaned = [str(item) for item in source if item]
    if cleaned:
        return cleaned
    return age_risk_focus(int(profile.get("age", 5)), result.get("risk_level", "Low Risk"), code)


def therapy_plan_localized(risk: str, age: int, language: str | None = None) -> dict:
    code = language or lang()
    if code == "ar":
        plans = {
            "High Risk": {
                "summary": "تشير نتيجة الفحص إلى وجود مؤشرات تحتاج إلى تقييم متخصص ودعم مبكر.",
                "therapies": [
                    "تقييم متخصص لدى طبيب أو أخصائي نمو",
                    "جلسات تخاطب ولغة عند الحاجة",
                    "علاج وظيفي لدعم المهارات الحسية والحركية",
                    "تدريب على المهارات الاجتماعية",
                    "تدخل بمشاركة ولي الأمر داخل المنزل",
                ],
                "parent_guidance": [
                    "حدد موعدًا مع أخصائي في أقرب وقت.",
                    "حافظ على روتين يومي واضح وثابت.",
                    "استخدم صورًا أو بطاقات لتوضيح الخطوات اليومية.",
                    "خصص وقتًا يوميًا للتفاعل وجهًا لوجه مع الطفل.",
                    "سجل الملاحظات المهمة لعرضها على الأخصائي.",
                ],
            },
            "Moderate Risk": {
                "summary": "توجد بعض المؤشرات التي تستحق المتابعة والتقييم النمائي.",
                "therapies": [
                    "جلسات تخاطب ولغة عند الحاجة",
                    "علاج باللعب لتنمية التواصل",
                    "أنشطة مهارات اجتماعية بسيطة",
                    "تفاعل مشترك بين ولي الأمر والطفل",
                ],
                "parent_guidance": [
                    "حدد متابعة مع طبيب الأطفال أو أخصائي نمو.",
                    "شجع اللعب مع الأطفال بشكل تدريجي.",
                    "اقرأ قصصًا قصيرة مع الطفل يوميًا.",
                    "قلل وقت الشاشة وزد التفاعل المباشر.",
                    "تابع مؤشرات النمو واللغة." ,
                ],
            },
            "Low Risk": {
                "summary": "تظهر نتيجة الفحص مؤشرات قليلة. استمر في المتابعة النمائية المعتادة.",
                "therapies": ["متابعة نمائية دورية", "أنشطة لعب وتواصل مناسبة للعمر"],
                "parent_guidance": [
                    "حافظ على مواعيد المتابعة الطبية المعتادة.",
                    "استمر في أنشطة اللعب والقراءة اليومية.",
                    "تابع تطور اللغة والتواصل.",
                ],
            },
        }
        return plans.get(risk, plans["Low Risk"])
    return therapy_plan(risk, age)


def story_title_options(age: int, language: str | None = None) -> list[str]:
    code = language or lang()
    if code == "ar":
        return STORY_OPTIONS["ar_young" if age <= 5 else "ar_old"]
    return STORY_OPTIONS["en_young" if age <= 5 else "en_old"]


def create_named_story(age: int, risk: str, title: str, language: str | None = None) -> dict:
    """Generate the project's story content while preserving the child's chosen title."""
    code = language or lang()
    if code == "ar":
        if age <= 3:
            text = (
                "كان زيد يحب المكعبات الملونة جدًا. في كل صباح كان يرتبها: أحمر، أزرق، أصفر، وأخضر. "
                "في يوم من الأيام جاءت سارة لتلعب معه. أمسكت سارة بالمكعب الأحمر وابتسمت لزيد. "
                "نظر زيد إليها ببطء ثم ابتسم. بنيا معًا برجًا طويلًا وجميلًا. "
                "وعندما وقع البرج ضحكا معًا. تعلم زيد أن اللعب مع صديق يجعل الوقت أجمل."
            )
        elif age <= 6:
            text = (
                "كانت ليلى تحب الفراشات وتجلس في الحديقة تراقبها وهي تطير. "
                "جلس بجانبها طفل اسمه عمر وسألها: هل تحبين الفراشات أيضًا؟ "
                "أومأت ليلى وقالت: الفراشات الصفراء هي المفضلة عندي. قال عمر: وأنا أيضًا! "
                "من ذلك اليوم صار الاثنان يلتقيان في الحديقة، يعدان الفراشات، ويرسمانها. "
                "اكتشفت ليلى أن الصديق يجعل الأشياء الجميلة أكثر جمالًا."
            )
        else:
            text = (
                "كان أحمد يحب الروبوتات كثيرًا. في المدرسة كان يجد صعوبة أحيانًا في بدء الحديث مع زملائه. "
                "أنشأت المعلمة ناديًا لصناعة الروبوتات. صنع أحمد روبوتًا سريعًا فأعجب به زملاؤه وطلبوا منه أن يعلمهم. "
                "بدأ أحمد يشرح لهم بهدوء، ومع الوقت أصبح الحديث أسهل. "
                "تعلم أحمد أن مشاركة الاهتمامات المفضلة يمكن أن تساعدنا على تكوين صداقات."
            )
        return {"title": title, "text": text}

    story = generate_story(age, risk) or {}
    story = dict(story)
    story["title"] = title
    return story


def build_story_quiz(age: int, story_title: str = "", language: str | None = None) -> list[dict]:
    """Build optional child-friendly multiple-choice questions."""
    code = language or lang()
    if code == "ar":
        if age <= 3:
            return [
                {"question": "ما ألوان مكعبات زيد؟", "options": ["أحمر وأزرق وأصفر وأخضر", "أسود وأبيض", "برتقالي وبنفسجي"], "correct": "أحمر وأزرق وأصفر وأخضر", "explanation": "القصة ذكرت أن المكعبات كانت أحمر وأزرق وأصفر وأخضر.", "focus": "تذكر الألوان والتفاصيل."},
                {"question": "من جاءت لتلعب مع زيد؟", "options": ["سارة", "عمر", "أحمد"], "correct": "سارة", "explanation": "سارة جاءت لتلعب مع زيد.", "focus": "تذكر أسماء الشخصيات."},
                {"question": "ماذا بنيا معًا؟", "options": ["برجًا طويلًا", "سيارة صغيرة", "روبوتًا"], "correct": "برجًا طويلًا", "explanation": "زيد وسارة بنيا برجًا طويلًا وجميلًا.", "focus": "فهم الأحداث."},
                {"question": "ماذا فعلا عندما وقع البرج؟", "options": ["ضحكا", "غضبا", "ذهبا إلى البيت"], "correct": "ضحكا", "explanation": "القصة تقول إنهما ضحكا عندما وقع البرج.", "focus": "فهم المشاعر وردود الفعل."},
                {"question": "ماذا تعلم زيد؟", "options": ["اللعب مع صديق أجمل", "أن يخاف من اللعب", "أن يترك المكعبات"], "correct": "اللعب مع صديق أجمل", "explanation": "تعلم زيد أن اللعب مع صديق يجعل الوقت أجمل.", "focus": "ربط الأحداث بالمشاعر."},
            ]
        if age <= 6:
            return [
                {"question": "ماذا كانت ليلى تحب أن تشاهد؟", "options": ["الفراشات", "الروبوتات", "السيارات"], "correct": "الفراشات", "explanation": "ليلى كانت تحب مشاهدة الفراشات في الحديقة.", "focus": "تحديد الفكرة الرئيسية."},
                {"question": "ما لون الفراشات المفضل عند ليلى؟", "options": ["الأصفر", "الأزرق", "الأحمر"], "correct": "الأصفر", "explanation": "قالت ليلى إن الفراشات الصفراء هي المفضلة عندها.", "focus": "تذكر التفاصيل."},
                {"question": "ماذا فعلت ليلى وعمر معًا؟", "options": ["عدّا الفراشات ورسماها", "صنعا روبوتًا", "لعبا كرة"], "correct": "عدّا الفراشات ورسماها", "explanation": "القصة ذكرت أنهما عدا الفراشات ورسماها.", "focus": "تذكر تسلسل الأحداث."},
                {"question": "كيف شعرت ليلى بعد أن أصبح لديها صديق؟", "options": ["سعيدة", "غاضبة", "خائفة"], "correct": "سعيدة", "explanation": "القصة توضح أن الصداقة جعلت الأشياء أجمل.", "focus": "فهم المشاعر."},
                {"question": "ما النشاط الإيجابي الذي يمكن فعله مع صديق؟", "options": ["الرسم أو الاستكشاف في الخارج", "تجاهل الجميع", "كسر الألعاب"], "correct": "الرسم أو الاستكشاف في الخارج", "explanation": "هذا نشاط اجتماعي إيجابي.", "focus": "اختيار أنشطة اجتماعية مناسبة."},
            ]
        return [
            {"question": "ما اهتمام أحمد المفضل؟", "options": ["الروبوتات", "الفراشات", "المكعبات"], "correct": "الروبوتات", "explanation": "القصة تذكر أن أحمد يحب الروبوتات.", "focus": "تحديد الفكرة الرئيسية."},
            {"question": "ما الصعوبة التي واجهها أحمد في المدرسة؟", "options": ["بدء الحديث مع زملائه", "فهم المواد الدراسية", "فقدان الروبوت"], "correct": "بدء الحديث مع زملائه", "explanation": "كان أحمد يجد صعوبة أحيانًا في بدء الحديث.", "focus": "فهم التحديات."},
            {"question": "ما الذي ساعد أحمد على التواصل مع زملائه؟", "options": ["نادي الروبوتات", "ترك المدرسة", "شراء هاتف جديد"], "correct": "نادي الروبوتات", "explanation": "نادي الروبوتات أعطاه فرصة لمشاركة اهتمامه.", "focus": "فهم السبب والنتيجة."},
            {"question": "ماذا علّم أحمد زملاءه؟", "options": ["صناعة الروبوت", "رسم الفراشات", "ترتيب المكعبات"], "correct": "صناعة الروبوت", "explanation": "زملاؤه طلبوا منه أن يعلمهم عن الروبوت.", "focus": "تذكر النتائج."},
            {"question": "ما الدرس من القصة؟", "options": ["مشاركة الاهتمامات تساعد على تكوين صداقات", "يجب تجنب الزملاء", "الفوز فقط هو المهم"], "correct": "مشاركة الاهتمامات تساعد على تكوين صداقات", "explanation": "القصة توضح أن مشاركة الاهتمامات تساعد على التواصل.", "focus": "فهم الدرس الاجتماعي."},
        ]

    generated_questions = generate_questions(age, story_title)
    if age <= 3:
        answer_bank = [
            {"options": ["Red, blue, yellow, and green", "Black and white", "Orange and purple"], "correct": "Red, blue, yellow, and green", "explanation": "The story mentions red, blue, yellow, and green blocks.", "focus": "Remembering colors and details."},
            {"options": ["Sara", "Omar", "Ahmed"], "correct": "Sara", "explanation": "Sara came to play.", "focus": "Remembering character names."},
            {"options": ["A tall tower", "A small car", "A robot"], "correct": "A tall tower", "explanation": "The children built a tall tower together.", "focus": "Understanding actions."},
            {"options": ["They laughed", "They became angry", "They went home"], "correct": "They laughed", "explanation": "They laughed when the tower fell.", "focus": "Recognizing emotions and reactions."},
            {"options": ["Happy because playing together was fun", "Sad because he lost the blocks", "Afraid of Sara"], "correct": "Happy because playing together was fun", "explanation": "The story shows that playing together can be fun.", "focus": "Linking events with emotions."},
        ]
    elif age <= 6:
        answer_bank = [
            {"options": ["Butterflies", "Robots", "Cars"], "correct": "Butterflies", "explanation": "The story focuses on butterflies in the garden.", "focus": "Identifying the main topic."},
            {"options": ["Yellow", "Blue", "Red"], "correct": "Yellow", "explanation": "The children liked the yellow butterflies.", "focus": "Remembering a detail."},
            {"options": ["They counted butterflies, named them, and drew pictures", "They built a robot", "They played football"], "correct": "They counted butterflies, named them, and drew pictures", "explanation": "These are the activities described in the story.", "focus": "Remembering a sequence."},
            {"options": ["Happy because she made a friend", "Angry because Omar left", "Bored because she disliked the garden"], "correct": "Happy because she made a friend", "explanation": "The character felt happy after making a friend.", "focus": "Understanding emotions."},
            {"options": ["Drawing or exploring outside with a friend", "Ignoring everyone", "Breaking toys"], "correct": "Drawing or exploring outside with a friend", "explanation": "This is a positive social activity.", "focus": "Choosing positive social activities."},
        ]
    else:
        answer_bank = [
            {"options": ["Robots", "Butterflies", "Colorful blocks"], "correct": "Robots", "explanation": "The central interest in the story is robots.", "focus": "Identifying the central idea."},
            {"options": ["It was hard for him to join conversations", "He did not like school subjects", "He lost his robot"], "correct": "It was hard for him to join conversations", "explanation": "The character found it difficult to join conversations.", "focus": "Understanding a challenge."},
            {"options": ["His teacher started a robot-building club", "He stopped attending school", "He bought a new phone"], "correct": "His teacher started a robot-building club", "explanation": "The club helped the character connect with classmates.", "focus": "Recognizing cause and effect."},
            {"options": ["How to build robots", "How to draw butterflies", "How to arrange blocks"], "correct": "How to build robots", "explanation": "The character shared robot-building skills.", "focus": "Remembering an outcome."},
            {"options": ["Sharing a positive interest can help us connect with others", "We should avoid classmates", "Only the fastest robot matters"], "correct": "Sharing a positive interest can help us connect with others", "explanation": "The story shows how a shared interest can support communication.", "focus": "Understanding the social lesson."},
        ]

    quiz = []
    for index, item in enumerate(answer_bank):
        question_text = generated_questions[index] if index < len(generated_questions) else f"Question {index + 1}"
        quiz.append({"question": question_text, **item})
    return quiz


def evaluate_story_quiz(quiz: list[dict], answers: list[str]) -> tuple[int, list[dict]]:
    feedback = []
    correct_count = 0
    for item, answer in zip(quiz, answers):
        selected = answer or ""
        is_correct = selected == item["correct"]
        if is_correct:
            correct_count += 1
        feedback.append(
            {
                "status": "correct" if is_correct else "wrong",
                "selected": selected,
                "correct_answer": item["correct"],
                "explanation": item["explanation"],
                "focus": item["focus"],
            }
        )
    return correct_count, feedback


# -----------------------------------------------------------------------------
# Report generation
# -----------------------------------------------------------------------------


def build_report_dict(include_therapy: bool = False) -> dict:
    code = lang()
    result = st.session_state.get("result") or {}
    profile = st.session_state.get("child_profile") or {}
    audio_result = result.get("audio_result") or {}
    plan = therapy_plan_localized(result.get("risk_level", "Low Risk"), int(profile.get("age", 5)), code)
    report = {
        "case_id": st.session_state.case_id,
        "language": code,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "child_profile": profile,
        "risk_level": result.get("risk_level", "Low Risk"),
        "risk_level_display": localize_risk(result.get("risk_level", "Low Risk"), code),
        "final_score": round(float(result.get("final_score", 0) or 0), 4),
        "questionnaire_score": round(float(result.get("questionnaire_score", 0) or 0), 4),
        "vision_score": round(float(result.get("vision_score")), 4) if result.get("vision_score") is not None else None,
        "audio_score": round(float(audio_result.get("audio_text_score", 0) or 0), 4) if audio_result else None,
        "has_image": bool((st.session_state.get("screening_data") or {}).get("has_image")),
        "has_audio_or_text": bool((st.session_state.get("screening_data") or {}).get("has_audio_or_text")),
        "speech_transcript": audio_result.get("transcript"),
        "observed_indicators": observed_indicators(result, code),
        "recommendations": general_recommendations(result, profile, code),
        "age_risk_focus": age_risk_focus(int(profile.get("age", 5)), result.get("risk_level", "Low Risk"), code),
        "therapy_plan": {
            "summary": plan.get("summary", ""),
            "activities": plan.get("therapies", []),
            "parent_guidance": plan.get("parent_guidance", []),
        },
        "selected_story_title": st.session_state.get("selected_story_title"),
        "medical_disclaimer": tr("medical_disclaimer", language=code),
        "scoring_source": result.get("scoring_source", "model"),
        "errors": result.get("errors", []),
    }
    if include_therapy and st.session_state.get("story"):
        report["therapy_story"] = st.session_state.story
        report["story_questions"] = st.session_state.get("story_questions")
        report["quiz_feedback"] = st.session_state.get("quiz_feedback")
    return report


def make_pdf_report(report: dict) -> bytes | None:
    """Create a printable, parent-friendly PDF report with wrapped paragraphs."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except Exception:
        return None

    report_language = report.get("language", "en")
    is_arabic = report_language == "ar"

    # Optional Arabic shaping support. The PDF still works without these packages,
    # but installing arabic-reshaper and python-bidi improves Arabic text rendering.
    reshaper = None
    get_display = None
    if is_arabic:
        try:
            import arabic_reshaper  # type: ignore
            from bidi.algorithm import get_display as bidi_get_display  # type: ignore
            reshaper = arabic_reshaper
            get_display = bidi_get_display
        except Exception:
            reshaper = None
            get_display = None

    def register_font() -> tuple[str, str]:
        if not is_arabic:
            return "Helvetica", "Helvetica-Bold"
        candidates = [
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        bold_candidates = [
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
        regular_name, bold_name = "Helvetica", "Helvetica-Bold"
        for path in candidates:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont("TAIFArabic", path))
                    regular_name = "TAIFArabic"
                    break
                except Exception:
                    pass
        for path in bold_candidates:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont("TAIFArabicBold", path))
                    bold_name = "TAIFArabicBold"
                    break
                except Exception:
                    pass
        return regular_name, bold_name

    body_font, bold_font = register_font()

    def rtl(value: str) -> str:
        text = str(value)
        if is_arabic and reshaper and get_display:
            try:
                return get_display(reshaper.reshape(text))
            except Exception:
                return text
        return text

    buffer = BytesIO()
    case_id = str(report.get("case_id", ""))
    generated_at = str(report.get("generated_at", ""))
    profile = report.get("child_profile", {}) or {}
    styles = getSampleStyleSheet()

    dark_blue = colors.HexColor("#17365D")
    light_blue = colors.HexColor("#EAF1F8")
    pale_yellow = colors.HexColor("#FFF7DC")
    align = TA_RIGHT if is_arabic else TA_LEFT

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=18,
        leading=23,
        alignment=TA_CENTER,
        textColor=dark_blue,
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=12,
        leading=16,
        alignment=align,
        textColor=dark_blue,
        spaceBefore=9,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName=body_font,
        fontSize=9.5,
        leading=14,
        alignment=align,
        textColor=colors.black,
        spaceAfter=4,
    )
    small_style = ParagraphStyle("Small", parent=body_style, fontSize=8.5, leading=12)
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=body_style,
        fontName=bold_font,
        backColor=pale_yellow,
        borderColor=colors.HexColor("#D6A108"),
        borderWidth=0.6,
        borderPadding=8,
        leading=14,
    )

    def safe(value) -> str:
        return html.escape(rtl(str(value if value not in [None, ""] else tr("not_provided", language=report_language))))

    def p(value, style=body_style):
        return Paragraph(safe(value), style)

    def bullet_list(items: list[str]) -> list:
        if not items:
            return [Paragraph(safe(tr("no_additional_info", language=report_language)), body_style)]
        marker = "•"
        return [Paragraph(safe(f"{marker} {item}"), body_style) for item in items]

    def table(rows: list[tuple[str, object]], widths=(5.6 * cm, 11.4 * cm)):
        data = [[Paragraph(f"<b>{safe(label)}</b>", body_style), p(value)] for label, value in rows]
        result_table = Table(data, colWidths=list(widths), hAlign="RIGHT" if is_arabic else "LEFT")
        result_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), light_blue),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C7D6")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return result_table

    def header_footer(canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setFont(body_font, 8)
        canvas.setFillColor(colors.HexColor("#566573"))
        if is_arabic:
            canvas.drawRightString(width - 1.6 * cm, height - 1.0 * cm, rtl(f"تقرير طيف | رقم الحالة: {case_id}"))
            canvas.drawString(1.6 * cm, height - 1.0 * cm, rtl(f"تاريخ التقرير: {generated_at}"))
            canvas.drawCentredString(width / 2, 0.85 * cm, rtl(f"صفحة {doc.page}"))
        else:
            canvas.drawString(1.6 * cm, height - 1.0 * cm, f"TAIF Screening Report | Case ID: {case_id}")
            canvas.drawRightString(width - 1.6 * cm, height - 1.0 * cm, f"Report Date: {generated_at}")
            canvas.drawCentredString(width / 2, 0.85 * cm, f"Page {doc.page}")
        canvas.restoreState()

    story = report.get("therapy_story") or {}
    feedback = report.get("quiz_feedback") or {}
    quiz = report.get("story_questions") or []

    title = "تقرير طيف للفحص الأولي" if is_arabic else "TAIF Screening Report"
    subtitle = tr("app_subtitle", language=report_language)

    elements = [
        Paragraph(safe(title), title_style),
        Paragraph(safe(subtitle), small_style),
        Spacer(1, 0.15 * cm),
        table([(tr("date", language=report_language), generated_at), (tr("case_id", language=report_language), case_id)]),
        Paragraph(safe(tr("child_information", language=report_language).replace("👤 ", "")), heading_style),
        table(
            [
                (tr("patient_code_short", language=report_language), profile.get("patient_code")),
                (tr("age_short", language=report_language), profile.get("age")),
                (tr("gender", language=report_language), display_value(profile.get("gender"), report_language)),
            ]
        ),
        Paragraph(safe(tr("general_development_information", language=report_language)), heading_style),
        table(
            [
                (tr("jaundice", language=report_language), display_value(profile.get("jaundice"), report_language)),
                (tr("family_history", language=report_language), display_value(profile.get("family_history"), report_language)),
                (tr("language_delay", language=report_language), display_value(profile.get("language_delay"), report_language)),
                (tr("sleep_issues", language=report_language), display_value(profile.get("sleep_issues"), report_language)),
                (tr("screen_time", language=report_language), display_value(profile.get("screen_time"), report_language)),
                (tr("school_notes", language=report_language), display_value(profile.get("school_notes"), report_language)),
                (tr("parent_notes", language=report_language), profile.get("notes")),
            ]
        ),
        Paragraph(safe(tr("screening_result", language=report_language)), heading_style),
        table(
            [
                (tr("screening_result", language=report_language), localize_risk(report.get("risk_level"), report_language)),
                (tr("overall_screening", language=report_language), percentage(report.get("final_score"), report_language)),
                (tr("questionnaire_assessment", language=report_language), percentage(report.get("questionnaire_score"), report_language)),
                (tr("visual_assessment", language=report_language), percentage(report.get("vision_score"), report_language) if report.get("has_image") else tr("no_image_info", language=report_language)),
                (tr("speech_assessment", language=report_language), percentage(report.get("audio_score"), report_language) if report.get("has_audio_or_text") else tr("no_speech_info", language=report_language)),
            ]
        ),
        Paragraph(safe(tr("observed_indicators", language=report_language).replace("🔍 ", "")), heading_style),
        *bullet_list(report.get("observed_indicators", [])),
        Paragraph(safe(tr("general_recommendations", language=report_language)), heading_style),
        *bullet_list(report.get("recommendations", [])),
        Paragraph(safe(tr("support_focus", language=report_language).replace("🎯 ", "")), heading_style),
        *bullet_list(report.get("age_risk_focus", [])),
        Paragraph(safe(tr("therapy_header", language=report_language).replace("💙 ", "")), heading_style),
        Paragraph(safe((report.get("therapy_plan") or {}).get("summary", "")), body_style),
        *bullet_list((report.get("therapy_plan") or {}).get("activities", [])),
        Paragraph(safe(tr("parent_guidance", language=report_language).replace("👪 ", "")), heading_style),
        *bullet_list((report.get("therapy_plan") or {}).get("parent_guidance", [])),
    ]

    if story:
        elements.extend(
            [
                PageBreak(),
                Paragraph(safe(tr("selected_story", language=report_language).replace("📖 ", "")), heading_style),
                Paragraph(safe(story.get("title", report.get("selected_story_title") or tr("story", language=report_language))), heading_style),
                Paragraph(safe(story.get("text", "")), body_style),
            ]
        )

    if quiz:
        elements.append(Paragraph(safe(tr("story_questions", language=report_language).replace("❓ ", "")), heading_style))
        for index, item in enumerate(quiz, 1):
            question_text = item.get("question", f"{tr('question', language=report_language)} {index}") if isinstance(item, dict) else str(item)
            elements.append(Paragraph(f"<b>{safe(str(index) + '. ' + question_text)}</b>", body_style))
        if feedback:
            elements.append(Spacer(1, 0.1 * cm))
            elements.append(
                Paragraph(
                    f"<b>{safe(tr('quiz_result', language=report_language))}:</b> {safe(feedback.get('correct_count', 0))} / {safe(feedback.get('total', 0))}",
                    body_style,
                )
            )
            for index, item in enumerate(feedback.get("feedback", []), 1):
                elements.extend(
                    [
                        Paragraph(f"<b>{safe(tr('question', language=report_language) + ' ' + str(index))}</b>", body_style),
                        Paragraph(f"{safe(tr('child_answer', language=report_language))}: {safe(item.get('selected', tr('not_provided', language=report_language)))}", small_style),
                        Paragraph(f"{safe(tr('correct_answer', language=report_language))}: {safe(item.get('correct_answer', ''))}", small_style),
                        Paragraph(f"{safe(tr('simple_explanation', language=report_language))}: {safe(item.get('explanation', ''))}", small_style),
                        Paragraph(f"{safe(tr('skill_to_practice', language=report_language))}: {safe(item.get('focus', ''))}", small_style),
                    ]
                )

    elements.extend(
        [
            Spacer(1, 0.2 * cm),
            Paragraph(safe(tr("medical_disclaimer_title", language=report_language)), heading_style),
            Paragraph(safe(report.get("medical_disclaimer", "")), disclaimer_style),
        ]
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.4 * cm,
    )
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer.read()


# -----------------------------------------------------------------------------
# App start and styling
# -----------------------------------------------------------------------------

init_state()
init_db()

base_css = """
<style>
.main-title {
    font-size: 2.45rem;
    font-weight: 850;
    background: linear-gradient(135deg, #5b6ee1, #7056b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
}
.sub-title {
    text-align: center;
    color: #9ca3af;
    font-size: 1.05rem;
    margin-bottom: 1rem;
}
.disclaimer {
    background: #fff7dc;
    border-left: 5px solid #d6a108;
    padding: 0.95rem 1rem;
    border-radius: 8px;
    font-size: 0.95rem;
    color: #7a5b00;
}
.risk-box {
    border-radius: 18px;
    padding: 1.35rem;
    text-align: center;
}
.taif-logo-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0.35rem auto 0.8rem auto;
}
.taif-logo {
    width: 100%;
    height: auto;
    object-fit: contain;
}
.taif-result-card {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    background: #ffffff;
    color: #111827;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 18px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    margin: 0.7rem 0 1rem 0;
    min-height: 116px;
}
.taif-result-circle {
    --p: 0;
    --accent: #34b7ad;
    width: 82px;
    height: 82px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    flex: 0 0 82px;
    background: conic-gradient(var(--accent) calc(var(--p) * 1%), #eef2f7 0);
    position: relative;
}
.taif-result-circle::before {
    content: "";
    position: absolute;
    inset: 9px;
    border-radius: 50%;
    background: #ffffff;
    box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.03);
}
.taif-result-inner {
    position: relative;
    z-index: 1;
    font-size: 0.88rem;
    font-weight: 800;
    color: #374151;
}
.taif-result-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
}
.taif-result-title {
    font-size: 0.86rem;
    font-weight: 700;
    color: #9ca3af;
    margin-bottom: 0.18rem;
}
.taif-result-status {
    font-size: 1.25rem;
    line-height: 1.25;
    font-weight: 850;
    color: #111827;
}
.taif-result-subtitle {
    font-size: 0.86rem;
    font-weight: 650;
    color: #6b7280;
    margin-top: 0.22rem;
}
.taif-result-note {
    margin-top: 0.35rem;
    color: #6b7280;
    font-size: 0.82rem;
}
@media (max-width: 640px) {
    .taif-result-card {
        gap: 0.9rem;
        padding: 1rem;
    }
    .taif-result-circle {
        width: 72px;
        height: 72px;
        flex-basis: 72px;
    }
    .taif-result-status {
        font-size: 1.05rem;
    }
}
.support-card {
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 1rem;
    background: rgba(255,255,255,0.035);
    min-height: 220px;
}
.history-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
    background: rgba(255,255,255,0.035);
}
.small-muted {
    color: #9ca3af;
    font-size: 0.9rem;
}
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

if lang() == "ar":
    st.markdown(
        """
        <style>
        .stApp, .stMarkdown, .stText, .stCaption, label, p, h1, h2, h3, h4, h5, h6, div {
            direction: rtl;
            text-align: right;
            font-family: "Tahoma", "Arial", sans-serif;
        }
        .main-title, .sub-title, .risk-box, .risk-box *, .taif-logo-wrap {
            text-align: center !important;
        }
        .taif-result-card {
            direction: ltr;
            text-align: left;
        }
        .taif-result-card * {
            direction: ltr;
            text-align: left;
        }
        .disclaimer {
            border-left: none;
            border-right: 5px solid #d6a108;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Header and sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown("# 🧠 TAIF")
    st.caption(tr("sidebar_caption"))
    st.divider()
    st.markdown(f"### 🌐 {tr('choose_language')}")
    c_lang1, c_lang2 = st.columns(2)
    with c_lang1:
        if st.button("English", type="primary" if lang() == "en" else "secondary", use_container_width=True):
            change_language("en")
    with c_lang2:
        if st.button("العربية", type="primary" if lang() == "ar" else "secondary", use_container_width=True):
            change_language("ar")
    st.caption(f"{tr('current_language')}: {LANG_NAMES[lang()]}")

    st.divider()
    if st.button(tr("start_new_case"), use_container_width=True):
        reset_app()

    st.divider()
    if st.button(tr("previous_cases"), use_container_width=True):
        st.session_state.page = 5
        st.rerun()

    if st.session_state.page == 5:
        if st.button(tr("back_current_case"), use_container_width=True):
            st.session_state.page = 1 if not st.session_state.result else 3
            st.rerun()

    st.divider()
    st.caption(f"{tr('case_id')}: {st.session_state.case_id}")

show_logo(width=340)
st.markdown(f'<div class="main-title">{html.escape(tr("app_title"))}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{html.escape(tr("app_subtitle"))}</div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="disclaimer">
⚠️ <b>{html.escape(tr('medical_disclaimer_title'))}:</b> {html.escape(tr('medical_disclaimer'))}
</div>
""",
    unsafe_allow_html=True,
)
st.divider()
if st.session_state.page in [1, 2, 3, 4]:
    page_progress()
st.divider()

# -----------------------------------------------------------------------------
# Page 1: Child information
# -----------------------------------------------------------------------------

if st.session_state.page == 1:
    st.header(tr("child_information"))
    st.caption(tr("child_information_caption"))

    old = st.session_state.get("child_profile") or {}

    col1, col2 = st.columns(2)
    with col1:
        patient_code = st.text_input(
            tr("patient_code"),
            value=old.get("patient_code", f"TAIF-{st.session_state.case_id}"),
            help=tr("patient_code_help"),
        )
        age = st.slider(tr("child_age"), min_value=1, max_value=12, value=int(old.get("age", 5)), step=1)
        gender = st.radio(
            tr("gender"),
            ["Female", "Male"],
            index=0 if old.get("gender", "Female") == "Female" else 1,
            horizontal=True,
            format_func=lambda value: localize_gender(value),
        )
    with col2:
        jaundice = st.selectbox(tr("jaundice"), ["No", "Yes"], index=1 if old.get("jaundice") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))
        family_history = st.selectbox(tr("family_history"), ["No", "Yes"], index=1 if old.get("family_history") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))
        language_delay = st.selectbox(tr("language_delay"), ["No", "Yes"], index=1 if old.get("language_delay") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))
        ethnicity = st.text_input(tr("ethnicity"), value=old.get("ethnicity", tr("others")))
        completed_by = st.text_input(tr("completed_by"), value=old.get("completed_by", tr("family_member")))

    st.subheader(tr("general_development_information"))
    col3, col4, col5 = st.columns(3)
    with col3:
        sleep_issues = st.selectbox(tr("sleep_issues"), ["No", "Yes"], index=1 if old.get("sleep_issues") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))
    with col4:
        screen_time = st.selectbox(tr("screen_time"), ["No", "Yes"], index=1 if old.get("screen_time") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))
    with col5:
        school_notes = st.selectbox(tr("school_notes"), ["No", "Yes"], index=1 if old.get("school_notes") == "Yes" else 0, format_func=lambda value: localize_yes_no(value))

    notes = st.text_area(tr("parent_notes"), value=old.get("notes", ""), height=100)

    st.subheader(tr("guardian_consent"))
    consent = st.checkbox(tr("consent_text"), value=bool(old.get("consent", False)))

    if st.button(tr("next_screening"), type="primary", use_container_width=True):
        if not patient_code.strip():
            st.error(tr("patient_code_error"))
        elif not consent:
            st.error(tr("consent_error"))
        else:
            st.session_state.child_profile = {
                "patient_code": patient_code.strip(),
                "age": age,
                "gender": gender,
                "gender_val": 1 if gender == "Male" else 0,
                "jaundice": jaundice,
                "jaundice_val": yes_no_to_int(jaundice),
                "family_history": family_history,
                "family_val": yes_no_to_int(family_history),
                "language_delay": language_delay,
                "language_delay_val": yes_no_to_int(language_delay),
                "ethnicity": ethnicity.strip() or "Others",
                "completed_by": completed_by.strip() or "Family member",
                "sleep_issues": sleep_issues,
                "screen_time": screen_time,
                "school_notes": school_notes,
                "notes": notes,
                "consent": consent,
            }
            go_to(2)

# -----------------------------------------------------------------------------
# Page 2: Screening inputs
# -----------------------------------------------------------------------------

elif st.session_state.page == 2:
    profile = st.session_state.get("child_profile") or {}
    if not profile:
        st.warning(tr("start_child_info_warning"))
        if st.button(tr("go_child_info")):
            go_to(1)
        st.stop()

    age = int(profile["age"])
    st.header(tr("screening_inputs"))
    st.caption(tr("screening_inputs_caption"))

    if age > 3:
        st.subheader(tr("behavioral_assessment"))
        st.caption(tr("behavioral_caption"))
        c1, c2, c3 = st.columns(3)
        social = c1.slider(tr("social_concerns"), 0.0, 1.0, 0.0, 0.05)
        communication = c2.slider(tr("communication_concerns"), 0.0, 1.0, 0.0, 0.05)
        repetitive = c3.slider(tr("repetitive_concerns"), 0.0, 1.0, 0.0, 0.05)
    else:
        social = communication = repetitive = 0.0
        st.info(tr("early_years_info"))

    st.divider()
    st.subheader(tr("behavioral_questionnaire"))
    st.caption(tr("questionnaire_caption"))

    questions = QUESTIONS[lang()]
    answers = []
    cols = st.columns(2)
    for index, question_text in enumerate(questions):
        with cols[index % 2]:
            answer = st.radio(
                question_text,
                ["Yes", "No"],
                key=f"q_{index}",
                horizontal=True,
                index=None,
                format_func=lambda value: localize_yes_no(value),
            )
            answers.append(None if answer is None else (0 if answer == "Yes" else 1))

    st.divider()
    image_file = None
    audio_file = None
    manual_transcript = None
    api_key = os.getenv("ASSEMBLYAI_API_KEY")

    c_img, c_audio = st.columns(2)
    with c_img:
        st.subheader(tr("visual_assessment"))
        st.caption(tr("visual_caption"))
        uploaded_image = st.file_uploader(tr("upload_image"), type=["jpg", "jpeg", "png"])
        if uploaded_image:
            st.image(uploaded_image, width=240, caption=tr("image_preview"))
            image_file = uploaded_image

    with c_audio:
        st.subheader(tr("speech_assessment"))
        st.caption(tr("speech_caption"))
        audio_modes = ["Written Speech Sample", "Upload Audio", "Record"]
        audio_mode = st.radio(
            tr("input_mode"),
            audio_modes,
            horizontal=True,
            format_func=lambda value: {
                "Written Speech Sample": tr("written_sample"),
                "Upload Audio": tr("upload_audio"),
                "Record": tr("record"),
            }[value],
        )
        if audio_mode == "Written Speech Sample":
            manual_transcript = st.text_area(tr("written_speech_sample"), placeholder=tr("speech_placeholder"), height=130)
        elif audio_mode == "Upload Audio":
            audio_file = st.file_uploader(tr("upload_audio_file"), type=["wav", "mp3", "m4a", "ogg"])
            if audio_file:
                st.audio(audio_file)
            if not api_key:
                st.caption(tr("transcription_unavailable"))
        else:
            try:
                recorded = st.audio_input(tr("record_child_speech"))
                if recorded:
                    audio_file = recorded
                    st.success(tr("recording_captured"))
                if not api_key:
                    st.caption(tr("transcription_unavailable"))
            except AttributeError:
                st.info(tr("recording_unavailable"))

    st.divider()
    col_back, col_run = st.columns(2)
    with col_back:
        if st.button(tr("back"), use_container_width=True):
            go_to(1)
    with col_run:
        if st.button(tr("run_screening"), type="primary", use_container_width=True):
            if any(answer is None for answer in answers):
                st.error(tr("answer_all_questions_error"))
                st.stop()

            with st.spinner(tr("preparing_report")):
                try:
                    safe_uploaded_file_seek(image_file)
                    safe_uploaded_file_seek(audio_file)
                    result = diagnose(
                        age=age,
                        answers=answers,
                        gender=profile["gender_val"],
                        jaundice=profile["jaundice_val"],
                        family_history=profile["family_val"],
                        language_delay=profile["language_delay_val"],
                        social_interaction=social,
                        communication=communication,
                        repetitive=repetitive,
                        ethnicity=profile.get("ethnicity", "Others"),
                        completed_by=profile.get("completed_by", "Family member"),
                        image_file=image_file,
                        audio_file=audio_file,
                        manual_transcript=manual_transcript,
                        api_key=api_key if api_key else None,
                    )
                    st.session_state.screening_data = {
                        "has_image": image_file is not None,
                        "has_audio_or_text": audio_file is not None or bool(manual_transcript),
                    }
                    st.session_state.result = result
                    report = build_report_dict(include_therapy=False)
                    st.session_state.saved_report = report
                    save_case(report)
                    go_to(3)
                except Exception:
                    st.error(tr("screening_error"))

# -----------------------------------------------------------------------------
# Page 3: Screening report
# -----------------------------------------------------------------------------

elif st.session_state.page == 3:
    result = st.session_state.get("result")
    profile = st.session_state.get("child_profile") or {}
    if not result:
        st.warning(tr("no_report_warning"))
        if st.button(tr("go_screening_inputs")):
            go_to(2)
        st.stop()

    st.header(tr("report_header"))
    risk = result.get("risk_level", "Low Risk")
    score = float(result.get("final_score", 0) or 0)
    color = risk_color(risk)
    screening_data = st.session_state.get("screening_data", {}) or {}
    audio_result = result.get("audio_result") or {}

    result_card(tr("overall_screening"), score, tr("initial_indicator"))

    st.divider()
    st.subheader(tr("assessment_summary"))

    c_overall, c_questionnaire = st.columns(2)
    with c_overall:
        result_card(tr("overall_screening"), score)

    questionnaire_score = float(result.get("questionnaire_score", 0) or 0)
    with c_questionnaire:
        result_card(tr("questionnaire_assessment"), questionnaire_score)

    c_visual, c_speech = st.columns(2)
    with c_visual:
        if not screening_data.get("has_image"):
            st.info(tr("no_image_info"))
        elif result.get("vision_score") is None:
            st.warning(tr("vision_warning"))
        else:
            vision_score = float(result.get("vision_score", 0) or 0)
            result_card(tr("visual_assessment"), vision_score)

    with c_speech:
        if not screening_data.get("has_audio_or_text"):
            st.info(tr("no_speech_info"))
        elif not audio_result:
            st.warning(tr("speech_warning"))
        else:
            audio_score = float(audio_result.get("audio_text_score", 0) or 0)
            result_card(tr("speech_assessment"), audio_score)

    indicators = observed_indicators(result)
    st.subheader(tr("observed_indicators"))
    for item in indicators:
        st.write(f"• {item}")

    st.subheader(tr("general_recommendations"))
    for item in general_recommendations(result, profile):
        st.write(f"• {item}")

    st.subheader(tr("support_focus"))
    for item in age_risk_focus(int(profile.get("age", 5)), risk):
        st.write(f"• {item}")

    if result.get("errors"):
        scoring_source = result.get("scoring_source", "model")
        if scoring_source == "fallback":
            st.warning(f"{tr('scoring_source')}: {tr('fallback_scoring')}")
        else:
            st.info(tr("optional_parts_error"))
        with st.expander(tr("scoring_notes")):
            for error in result.get("errors", []):
                st.write(f"• {error}")

    st.divider()
    report = build_report_dict(include_therapy=False)
    st.session_state.saved_report = report
    save_case(report)
    pdf_bytes = make_pdf_report(report)

    if pdf_bytes:
        st.download_button(
            tr("download_pdf"),
            data=pdf_bytes,
            file_name=f"TAIF_report_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info(tr("pdf_unavailable"))

    st.subheader(tr("next_step"))
    st.write(tr("continue_support_question"))
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button(tr("back_inputs"), use_container_width=True):
            go_to(2)
    with b2:
        if st.button(tr("finish_here"), use_container_width=True):
            st.success(tr("report_saved"))
    with b3:
        if st.button(tr("continue_support"), type="primary", use_container_width=True):
            go_to(4)

# -----------------------------------------------------------------------------
# Page 4: Therapy support and story
# -----------------------------------------------------------------------------

elif st.session_state.page == 4:
    result = st.session_state.get("result")
    profile = st.session_state.get("child_profile") or {}
    if not result:
        st.warning(tr("no_report_warning"))
        if st.button(tr("go_screening_inputs")):
            go_to(2)
        st.stop()

    age = int(profile.get("age", 5))
    risk = result.get("risk_level", "Low Risk")
    plan = therapy_plan_localized(risk, age)

    st.header(tr("therapy_header"))
    st.write(plan.get("summary", ""))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="support-card"><h3>{html.escape(tr("suggested_support_activities"))}</h3>', unsafe_allow_html=True)
        for item in plan.get("therapies", []):
            st.write(f"• {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="support-card"><h3>{html.escape(tr("parent_guidance"))}</h3>', unsafe_allow_html=True)
        for item in plan.get("parent_guidance", []):
            st.write(f"• {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="support-card"><h3>{html.escape(tr("development_focus_areas"))}</h3>', unsafe_allow_html=True)
        for item in age_risk_focus(age, risk):
            st.write(f"• {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader(tr("choose_story_name"))
    options = story_title_options(age)
    other_label = tr("enter_another_story_name")
    if st.session_state.selected_story_title in options:
        default_index = options.index(st.session_state.selected_story_title)
    elif st.session_state.selected_story_title:
        default_index = options.index(other_label)
    else:
        default_index = 0
    selected_option = st.selectbox(tr("story_name"), options, index=default_index)
    custom_title = ""
    if selected_option == other_label:
        custom_title = st.text_input(other_label, value=st.session_state.selected_story_title or "")
    chosen_title = custom_title.strip() if selected_option == other_label else selected_option

    if st.button(tr("create_my_story"), type="primary", use_container_width=True):
        if not chosen_title:
            st.warning(tr("choose_story_warning"))
        else:
            st.session_state.selected_story_title = chosen_title
            st.session_state.story = create_named_story(age, risk, chosen_title)
            st.session_state.story_questions = None
            st.session_state.quiz_feedback = None
            st.rerun()

    if st.session_state.story:
        story = st.session_state.story
        st.divider()
        st.subheader(tr("selected_story"))
        st.markdown(f"### {html.escape(str(story.get('title', tr('story'))))}")
        st.write(story.get("text", ""))

        if st.button(tr("generate_another_story"), use_container_width=True):
            title = st.session_state.selected_story_title or story.get("title", tr("story"))
            st.session_state.story = create_named_story(age, risk, title)
            st.session_state.story_questions = None
            st.session_state.quiz_feedback = None
            st.rerun()

        st.divider()
        st.subheader(tr("story_questions"))
        st.caption(tr("story_questions_caption"))

        enable_quiz = st.checkbox(tr("start_optional_questions"), value=False)
        if enable_quiz:
            if st.session_state.story_questions is None:
                st.session_state.story_questions = build_story_quiz(age, story.get("title", ""))
            quiz = st.session_state.story_questions or []

            child_answers = []
            for index, item in enumerate(quiz, 1):
                st.markdown(f"**{index}. {item['question']}**")
                choices = [tr("select_answer")] + item["options"]
                selected = st.radio(
                    f"{tr('answer')} {index}",
                    choices,
                    key=f"story_mcq_answer_{index}",
                    index=0,
                    label_visibility="collapsed",
                )
                child_answers.append("" if selected == tr("select_answer") else selected)

            if st.button(tr("finish_quiz"), type="primary", use_container_width=True):
                if any(not answer for answer in child_answers):
                    st.warning(tr("answer_all_quiz"))
                else:
                    correct_count, feedback = evaluate_story_quiz(quiz, child_answers)
                    st.session_state.quiz_feedback = {
                        "correct_count": correct_count,
                        "total": len(quiz),
                        "feedback": feedback,
                        "answers": child_answers,
                    }
                    st.rerun()

            if st.session_state.quiz_feedback:
                feedback = st.session_state.quiz_feedback
                result_percentage = (feedback["correct_count"] / feedback["total"] * 100) if feedback["total"] else 0
                st.success(f"{tr('quiz_result')}: {feedback['correct_count']} / {feedback['total']} {tr('correct_answers')} ({result_percentage:.0f}%)")
                for index, item in enumerate(feedback["feedback"], 1):
                    st.markdown(f"#### {tr('question')} {index}")
                    st.write(f"**{tr('child_answer')}:** {item['selected']}")
                    st.write(f"**{tr('correct_answer')}:** {item['correct_answer']}")
                    st.write(f"**{tr('simple_explanation')}:** {item['explanation']}")
                    st.write(f"**{tr('skill_to_practice')}:** {item['focus']}")
                    if item["status"] == "correct":
                        st.success(tr("correct_answer_msg"))
                    else:
                        st.warning(tr("review_question_msg"))

                wrong_focus = [item["focus"] for item in feedback["feedback"] if item["status"] != "correct"]
                if wrong_focus:
                    st.info(tr("suggested_focus_next") + " | ".join(dict.fromkeys(wrong_focus)))
                else:
                    st.info(tr("excellent_result"))
        else:
            st.info(tr("questions_optional_info"))

    st.divider()
    st.info(tr("support_disclaimer"))

    final_report = build_report_dict(include_therapy=True)
    save_case(final_report)
    pdf_bytes = make_pdf_report(final_report)

    c_back, c_pdf = st.columns(2)
    with c_back:
        if st.button(tr("back_report"), use_container_width=True):
            go_to(3)
    with c_pdf:
        if pdf_bytes:
            st.download_button(
                tr("download_pdf"),
                data=pdf_bytes,
                file_name=f"TAIF_full_report_{datetime.now():%Y%m%d_%H%M}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info(tr("pdf_unavailable"))

# -----------------------------------------------------------------------------
# Page 5: Previous reports
# -----------------------------------------------------------------------------

elif st.session_state.page == 5:
    st.header(tr("previous_reports_header"))
    st.caption(tr("previous_reports_caption"))

    history = load_history(limit=50)
    if not history:
        st.info(tr("no_previous_reports"))
    else:
        st.metric(tr("saved_reports"), len(history))
        for row in history:
            color = risk_color(row.get("risk_level") or "Low Risk")
            try:
                previous_report = json.loads(row.get("report_json") or "{}")
            except Exception:
                previous_report = {}
            # Use the current interface language when opening old reports unless the report has its own language.
            previous_report.setdefault("language", lang())
            story_title = previous_report.get("selected_story_title") or tr("not_selected")
            st.markdown(
                f"""
                <div class="history-card">
                    <b>{html.escape(tr('case_id'))}:</b> {html.escape(str(row.get('case_id')))} &nbsp; | &nbsp;
                    <b>{html.escape(tr('patient_code_short'))}:</b> {html.escape(str(row.get('patient_code')))} &nbsp; | &nbsp;
                    <b>{html.escape(tr('age_short'))}:</b> {html.escape(str(row.get('age')))} &nbsp; | &nbsp;
                    <b>{html.escape(tr('gender'))}:</b> {html.escape(display_value(row.get('gender')))}<br>
                    <b>{html.escape(tr('screening_result'))}:</b>
                    <span style="color:{color}; font-weight:700;">{html.escape(localize_risk(str(row.get('risk_level'))))}</span>
                    &nbsp; | &nbsp;
                    <b>{html.escape(tr('story_label'))}:</b> {html.escape(str(story_title))}
                    &nbsp; | &nbsp;
                    <b>{html.escape(tr('date'))}:</b> {html.escape(str(row.get('created_at')))}
                </div>
                """,
                unsafe_allow_html=True,
            )
            try:
                previous_pdf = make_pdf_report(previous_report)
                if previous_pdf:
                    st.download_button(
                        tr("download_pdf_short"),
                        data=previous_pdf,
                        file_name=f"TAIF_report_{row.get('case_id')}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{row.get('case_id')}",
                    )
                else:
                    st.info(tr("pdf_unavailable"))
            except Exception:
                st.warning(tr("saved_pdf_error"))

    if st.button(tr("back_current_case"), type="primary"):
        st.session_state.page = 1 if not st.session_state.result else 3
        st.rerun()
