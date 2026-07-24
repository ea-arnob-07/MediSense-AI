from __future__ import annotations

from typing import Any


CATEGORY_ASSESSMENTS = {
    "Cardiovascular": ["cardiovascular examination (কার্ডিওভাসকুলার পরীক্ষা)", "ECG and blood-pressure review if a clinician considers them appropriate (চিকিৎসক প্রয়োজন মনে করলে ইসিজি এবং রক্তচাপ পরীক্ষা)"],
    "Respiratory": ["respiratory examination (শ্বাসযন্ত্রের পরীক্ষা)", "oxygen saturation and chest assessment (অক্সিজেন স্যাচুরেশন এবং বুকের পরীক্ষা)"],
    "Neurological": ["focused neurological examination (স্নায়বিক পরীক্ষা)", "urgent imaging or specialist review if warning signs are present (সতর্কতা লক্ষণ থাকলে জরুরি ইমেজিং বা বিশেষজ্ঞের পরামর্শ)"],
    "Gastrointestinal": ["abdominal examination (পেটের পরীক্ষা)", "hydration status and targeted laboratory testing (হাইড্রেশনের অবস্থা এবং প্রয়োজনীয় ল্যাব টেস্ট)"],
    "Renal_Urinary": ["urinalysis (ইউরিনালাইসিস বা মূত্র পরীক্ষা)", "kidney function and hydration assessment (কিডনির কার্যকারিতা এবং হাইড্রেশন মূল্যায়ন)"],
    "Endocrine_Metabolic": ["glucose and metabolic assessment (গ্লুকোজ এবং মেটাবলিক মূল্যায়ন)", "targeted hormone testing when clinically indicated (চিকিৎসাগত নির্দেশনায় হরমোন পরীক্ষা)"],
    "Dermatological": ["skin examination (ত্বক পরীক্ষা)", "allergy, infection, or autoimmune assessment as appropriate (অ্যালার্জি, সংক্রমণ বা অটোইমিউন মূল্যায়ন)"],
    "Musculoskeletal": ["musculoskeletal examination (পেশী ও হাড়ের পরীক্ষা)", "mobility, injury, and inflammation assessment (গতিশীলতা, আঘাত এবং প্রদাহ মূল্যায়ন)"],
    "Mental_Health": ["confidential mental-health assessment (গোপনীয় মানসিক স্বাস্থ্য মূল্যায়ন)", "immediate safety planning when self-harm risk exists (আত্মঘাতী ঝুঁকি থাকলে তাৎক্ষণিক সুরক্ষা পরিকল্পনা)"],
    "Tropical_Infectious_Other": ["infection-focused examination (সংক্রমণ-ভিত্তিক পরীক্ষা)", "locally appropriate blood tests and exposure history (স্থানীয় রক্ত পরীক্ষা এবং সংক্রমণের ইতিহাস)"],
    "Infectious": ["infection-focused examination (সংক্রমণ-ভিত্তিক পরীক্ষা)", "testing based on exposure, duration, and local outbreaks (সংক্রমণ, সময়কাল এবং স্থানীয় প্রাদুর্ভাবের উপর ভিত্তি করে পরীক্ষা)"],
}


def build_guidance(
    patient: dict[str, Any],
    predictions: list[dict[str, Any]],
    triage: dict[str, Any],
    emergency_number: str,
) -> dict[str, Any]:
    actions: list[str] = []
    monitoring: list[str] = []
    clinician_may_consider: list[str] = []
    safety: list[str] = [
        "Do not start, stop, or change prescription medicine based only on this result. (শুধুমাত্র এই ফলাফলের উপর ভিত্তি করে ওষুধের পরিবর্তন করবেন না।)",
        "Do not use leftover antibiotics or steroids without a licensed clinician's advice. (চিকিৎসকের পরামর্শ ছাড়া আগের অ্যান্টিবায়োটিক বা স্টেরয়েড ব্যবহার করবেন না।)",
        "Seek care sooner if symptoms are rapidly worsening, new warning signs appear, or you are worried. (লক্ষণ দ্রুত খারাপ হলে বা নতুন সতর্কতা দেখা দিলে দ্রুত চিকিৎসকের পরামর্শ নিন।)",
    ]

    if triage["emergency"]:
        actions.extend([
            f"Contact local emergency services now ({emergency_number} where applicable). (অবিলম্বে স্থানীয় জরুরি সেবার সাথে যোগাযোগ করুন।)",
            "Do not drive yourself if you are faint, confused, severely short of breath, or having severe chest pain. (ক্লান্তি, বিভ্রান্তি, শ্বাসকষ্ট বা বুকে তীব্র ব্যথা হলে নিজে গাড়ি চালাবেন না।)",
            "Stay with the person, keep the airway clear, and follow emergency-dispatch instructions. (রোগীর সাথে থাকুন, শ্বাসনালী পরিষ্কার রাখুন এবং জরুরি নির্দেশিকা অনুসরণ করুন।)",
            "Bring a list of medicines, allergies, medical conditions, and the time symptoms started. (ওষুধের তালিকা, অ্যালার্জি, আগের রোগ এবং লক্ষণ শুরুর সময় সাথে নিয়ে যান।)",
        ])
    elif triage["risk_level"] == "High":
        actions.extend([
            "Arrange same-day in-person clinical assessment. (আজই সরাসরি চিকিৎসকের পরামর্শ নিন।)",
            "Avoid strenuous activity until assessed, especially with chest, breathing, fainting, or neurological symptoms. (চিকিৎসকের পরামর্শের আগে শারীরিক পরিশ্রম এড়িয়ে চলুন।)",
            "Have another person assist if you feel weak, dizzy, or unsafe travelling alone. (দুর্বল বা মাথা ঘোরার অনুভূতি হলে চলাফেরায় অন্য কারও সাহায্য নিন।)",
        ])
    elif triage["risk_level"] == "Moderate":
        actions.extend([
            "Arrange a clinician review within 24–48 hours. (২৪ থেকে ৪৮ ঘণ্টার মধ্যে চিকিৎসকের পরামর্শ নিন।)",
            "Record symptom changes and any home measurements to discuss during the visit. (লক্ষণের পরিবর্তন ও পরিমাপগুলো নোট করে রাখুন।)",
        ])
    else:
        actions.extend([
            "Monitor symptoms and arrange routine clinical care if they persist, recur, or interfere with normal activity. (লক্ষণ পর্যবেক্ষণ করুন এবং স্বাভাবিক কাজ ব্যাহত হলে চিকিৎসকের পরামর্শ নিন।)",
            "Rest and maintain fluids when appropriate for you, unless a clinician has restricted your fluid intake. (পর্যাপ্ত বিশ্রাম নিন এবং তরল খাবার পান করুন।)",
        ])

    monitoring.extend([
        "Track temperature, symptom severity, and duration. (তাপমাত্রা, লক্ষণের তীব্রতা এবং সময়কাল পর্যবেক্ষণ করুন।)",
        "Track breathing difficulty, chest pain, mental status, hydration, urine output, and new weakness. (শ্বাসকষ্ট, বুকে ব্যথা, মানসিক অবস্থা এবং নতুন দুর্বলতা খেয়াল রাখুন।)",
        "Re-check abnormal home measurements with a reliable device when safe to do so. (অস্বাভাবিক পরিমাপগুলো নির্ভরযোগ্য যন্ত্র দিয়ে পুনরায় যাচাই করুন।)",
    ])

    categories = []
    for prediction in predictions[:3]:
        category = prediction.get("category")
        if category and category not in categories:
            categories.append(category)
    for category in categories:
        clinician_may_consider.extend(CATEGORY_ASSESSMENTS.get(category, []))

    if patient.get("symptoms", {}).get("Self_Harm_Thoughts", 0) > 0:
        actions.insert(0, "Stay with a trusted person and seek immediate crisis or emergency support; do not remain alone with access to means of self-harm. (একজন বিশ্বস্ত মানুষের সাথে থাকুন এবং দ্রুত মানসিক স্বাস্থ্য সহায়তার জন্য যোগাযোগ করুন।)")

    return {
        "recommended_actions": list(dict.fromkeys(actions)),
        "what_to_monitor": list(dict.fromkeys(monitoring)),
        "clinician_may_consider": list(dict.fromkeys(clinician_may_consider))[:8],
        "medication_safety": safety,
    }
