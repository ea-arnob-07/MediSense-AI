from __future__ import annotations

SYMPTOM_BN = {
    "Fever": "জ্বর", "Chills": "কাঁপুনি", "Fatigue": "ক্লান্তি", "Weakness": "দুর্বলতা",
    "Malaise": "শরীর খারাপ লাগা", "Night_Sweats": "রাতে ঘাম হওয়া", "Weight_Loss": "ওজন কমা",
    "Weight_Gain": "ওজন বাড়া", "Loss_of_Appetite": "ক্ষুধামন্দা", "Dehydration": "পানিশূন্যতা",
    "Pallor": "ফ্যাকাশে ভাব", "Swollen_Lymph_Nodes": "লিম্ফ নোড ফুলে যাওয়া", "Body_Ache": "শরীর ব্যথা",
    "Cold_Sweat": "ঠান্ডা ঘাম", "Exercise_Intolerance": "ব্যায়াম সহ্য না হওয়া", "Sleepiness": "অতিরিক্ত ঘুমভাব",
    "Loss_of_Consciousness": "জ্ঞান হারানো", "Cough": "কাশি", "Dry_Cough": "শুকনো কাশি",
    "Productive_Cough": "কফসহ কাশি", "Sore_Throat": "গলা ব্যথা", "Runny_Nose": "নাক দিয়ে পানি পড়া",
    "Nasal_Congestion": "নাক বন্ধ", "Sneezing": "হাঁচি", "Shortness_of_Breath": "শ্বাসকষ্ট",
    "Wheezing": "শ্বাসে সাঁই সাঁই শব্দ", "Chest_Tightness": "বুকে চাপ লাগা", "Chest_Pain": "বুক ব্যথা",
    "Pleuritic_Chest_Pain": "শ্বাসে বাড়ে এমন বুক ব্যথা", "Rapid_Breathing": "দ্রুত শ্বাস নেওয়া",
    "Coughing_Blood": "কাশির সঙ্গে রক্ত", "Hoarseness": "কণ্ঠস্বর ভাঙা", "Loss_of_Smell": "গন্ধ না পাওয়া",
    "Loss_of_Taste": "স্বাদ না পাওয়া", "Snoring": "নাক ডাকা", "Apnea_Episodes": "ঘুমে শ্বাস বন্ধ হওয়ার পর্ব",
    "Blue_Lips": "ঠোঁট নীল হওয়া", "Stridor": "শ্বাসে কর্কশ শব্দ", "Nausea": "বমি বমি ভাব",
    "Vomiting": "বমি", "Diarrhea": "ডায়রিয়া", "Bloody_Diarrhea": "রক্তমিশ্রিত ডায়রিয়া",
    "Constipation": "কোষ্ঠকাঠিন্য", "Abdominal_Pain": "পেট ব্যথা", "Epigastric_Pain": "পেটের উপরের অংশে ব্যথা",
    "Right_Upper_Abdominal_Pain": "পেটের ডান ওপরের অংশে ব্যথা", "Right_Lower_Abdominal_Pain": "পেটের ডান নিচের অংশে ব্যথা",
    "Pelvic_Pain": "তলপেটে ব্যথা", "Abdominal_Bloating": "পেট ফাঁপা", "Heartburn": "বুক জ্বালা",
    "Acid_Regurgitation": "টক পানি উঠে আসা", "Difficulty_Swallowing": "গিলতে কষ্ট", "Painful_Swallowing": "গিলতে ব্যথা",
    "Indigestion": "বদহজম", "Early_Satiety": "অল্পতেই পেট ভরে যাওয়া", "Excessive_Gas": "অতিরিক্ত গ্যাস",
    "Black_Stool": "কালো পায়খানা", "Blood_in_Stool": "পায়খানায় রক্ত", "Jaundice": "জন্ডিস",
    "Pale_Stool": "ফ্যাকাশে পায়খানা", "Dark_Urine": "গাঢ় প্রস্রাব", "Rectal_Pain": "মলদ্বারে ব্যথা",
    "Rectal_Itching": "মলদ্বারে চুলকানি", "Fecal_Urgency": "হঠাৎ পায়খানার তীব্র চাপ", "Greasy_Stool": "তেলতেলে পায়খানা",
    "Abdominal_Rigidity": "পেট শক্ত হয়ে যাওয়া", "Headache": "মাথাব্যথা", "Severe_Headache": "তীব্র মাথাব্যথা",
    "One_Sided_Headache": "একপাশে মাথাব্যথা", "Neck_Stiffness": "ঘাড় শক্ত হওয়া", "Dizziness": "মাথা ঘোরা",
    "Vertigo": "চারপাশ ঘোরা অনুভূতি", "Fainting": "অজ্ঞান হওয়া", "Confusion": "বিভ্রান্তি",
    "Memory_Problems": "স্মৃতির সমস্যা", "Difficulty_Concentrating": "মনোযোগ দিতে সমস্যা", "Seizure": "খিঁচুনি",
    "Tremor": "হাত-পা কাঁপা", "Balance_Problems": "ভারসাম্যের সমস্যা", "Numbness": "অবশভাব",
    "Tingling": "ঝিনঝিনি", "Muscle_Weakness": "পেশির দুর্বলতা", "One_Sided_Weakness": "শরীরের একপাশ দুর্বল হওয়া",
    "Facial_Droop": "মুখের একপাশ বেঁকে যাওয়া", "Slurred_Speech": "কথা জড়িয়ে যাওয়া", "Vision_Loss": "দৃষ্টিশক্তি হারানো",
    "Blurred_Vision": "ঝাপসা দেখা", "Double_Vision": "দুইটি দেখা", "Light_Sensitivity": "আলো সহ্য না হওয়া",
    "Sound_Sensitivity": "শব্দ সহ্য না হওয়া", "Aura": "অরা বা পূর্বলক্ষণ", "Restlessness": "অস্থিরতা",
    "Insomnia": "অনিদ্রা", "Brain_Fog": "মস্তিষ্ক ঝাপসা লাগা", "Post_Exertional_Malaise": "পরিশ্রমের পর অসুস্থতা বেড়ে যাওয়া",
    "Muscle_Rigidity": "পেশি শক্ত হওয়া", "Palpitations": "বুক ধড়ফড়", "Rapid_Heartbeat": "দ্রুত হৃদস্পন্দন",
    "Slow_Heartbeat": "ধীর হৃদস্পন্দন", "Irregular_Heartbeat": "অনিয়মিত হৃদস্পন্দন", "Leg_Swelling": "পা ফুলে যাওয়া",
    "Ankle_Swelling": "গোড়ালি ফুলে যাওয়া", "Orthopnea": "শুয়ে শ্বাসকষ্ট", "Paroxysmal_Nocturnal_Dyspnea": "রাতে হঠাৎ শ্বাসকষ্ট",
    "Low_Blood_Pressure_Symptoms": "নিম্ন রক্তচাপের লক্ষণ", "High_Blood_Pressure_Symptoms": "উচ্চ রক্তচাপের লক্ষণ",
    "Calf_Pain": "পায়ের পেছনের পেশিতে ব্যথা", "Cold_Extremities": "হাত-পা ঠান্ডা", "Frequent_Urination": "ঘন ঘন প্রস্রাব",
    "Urgency_Urination": "হঠাৎ প্রস্রাবের তীব্র চাপ", "Painful_Urination": "প্রস্রাবে জ্বালা বা ব্যথা", "Blood_in_Urine": "প্রস্রাবে রক্ত",
    "Cloudy_Urine": "ঘোলা প্রস্রাব", "Foul_Smelling_Urine": "দুর্গন্ধযুক্ত প্রস্রাব", "Flank_Pain": "কোমরের পাশে ব্যথা",
    "Reduced_Urine_Output": "প্রস্রাব কম হওয়া", "Excessive_Thirst": "অতিরিক্ত তৃষ্ণা", "Nocturia": "রাতে বারবার প্রস্রাব",
    "Urinary_Retention": "প্রস্রাব আটকে থাকা", "Incontinence": "প্রস্রাব ধরে রাখতে না পারা", "Foamy_Urine": "ফেনাযুক্ত প্রস্রাব",
    "Rash": "চামড়ায় ফুসকুড়ি", "Itching": "চুলকানি", "Hives": "চাকা ওঠা", "Red_Skin": "ত্বক লাল হওয়া",
    "Dry_Skin": "শুষ্ক ত্বক", "Scaly_Skin": "খসখসে ত্বক", "Blisters": "ফোসকা", "Skin_Pain": "ত্বকে ব্যথা",
    "Skin_Ulcer": "ত্বকে ঘা", "Pus_Discharge": "পুঁজ বের হওয়া", "Hair_Loss": "চুল পড়া", "Bruising": "সহজে কালশিটে পড়া",
    "Petechiae": "ত্বকে ক্ষুদ্র লাল দাগ", "Purple_Rash": "বেগুনি ফুসকুড়ি", "Facial_Swelling": "মুখ ফুলে যাওয়া",
    "Lip_Tongue_Swelling": "ঠোঁট বা জিহ্বা ফুলে যাওয়া", "Local_Warmth": "স্থানীয়ভাবে গরম লাগা", "Skin_Discoloration": "ত্বকের রং বদলানো",
    "Non_Healing_Wound": "না শুকানো ক্ষত", "Joint_Pain": "জয়েন্টে ব্যথা", "Joint_Swelling": "জয়েন্ট ফুলে যাওয়া",
    "Joint_Stiffness": "জয়েন্ট শক্ত হওয়া", "Morning_Stiffness": "সকালে জয়েন্ট শক্ত থাকা", "Muscle_Pain": "পেশিতে ব্যথা",
    "Muscle_Cramps": "পেশিতে খিঁচ ধরা", "Back_Pain": "পিঠ ব্যথা", "Low_Back_Pain": "কোমর ব্যথা", "Neck_Pain": "ঘাড় ব্যথা",
    "Shoulder_Pain": "কাঁধে ব্যথা", "Knee_Pain": "হাঁটু ব্যথা", "Hip_Pain": "নিতম্বে ব্যথা", "Bone_Pain": "হাড়ে ব্যথা",
    "Limited_Mobility": "নড়াচড়া সীমিত", "Sciatic_Pain": "সায়াটিকার ব্যথা", "Heel_Pain": "গোড়ালিতে ব্যথা", "Jaw_Pain": "চোয়ালে ব্যথা",
    "Red_Eyes": "চোখ লাল", "Eye_Pain": "চোখে ব্যথা", "Eye_Discharge": "চোখে পুঁজ বা স্রাব", "Watery_Eyes": "চোখ দিয়ে পানি পড়া",
    "Dry_Eyes": "চোখ শুষ্ক", "Halo_Around_Lights": "আলোর চারপাশে বলয় দেখা", "Ear_Pain": "কানে ব্যথা", "Ear_Discharge": "কান থেকে স্রাব",
    "Hearing_Loss": "শ্রবণশক্তি কমা", "Ringing_in_Ears": "কানে শব্দ হওয়া", "Sinus_Pressure": "সাইনাসে চাপ", "Facial_Pain": "মুখে ব্যথা",
    "Toothache": "দাঁত ব্যথা", "Gum_Swelling": "মাড়ি ফুলে যাওয়া", "Bad_Breath": "মুখে দুর্গন্ধ", "Mouth_Ulcers": "মুখে ঘা",
    "Nosebleed": "নাক দিয়ে রক্ত পড়া", "Heat_Intolerance": "গরম সহ্য না হওয়া", "Cold_Intolerance": "ঠান্ডা সহ্য না হওয়া",
    "Excessive_Sweating": "অতিরিক্ত ঘাম", "Dry_Mouth": "মুখ শুকিয়ে যাওয়া", "Increased_Hunger": "অতিরিক্ত ক্ষুধা",
    "Delayed_Wound_Healing": "ক্ষত শুকাতে দেরি", "Brittle_Nails": "ভঙ্গুর নখ", "Puffy_Face": "মুখ ফোলা",
    "Central_Weight_Gain": "পেটের দিকে ওজন বাড়া", "Salt_Craving": "লবণ খাওয়ার তীব্র ইচ্ছা", "Irregular_Periods": "অনিয়মিত মাসিক",
    "Heavy_Periods": "অতিরিক্ত মাসিক রক্তপাত", "Painful_Periods": "ব্যথাযুক্ত মাসিক", "Missed_Period": "মাসিক বন্ধ বা মিস হওয়া",
    "Vaginal_Discharge": "যোনিপথে স্রাব", "Vaginal_Bleeding": "যোনিপথে রক্তপাত", "Painful_Intercourse": "সহবাসে ব্যথা",
    "Genital_Itching": "যৌনাঙ্গে চুলকানি", "Testicular_Pain": "অণ্ডকোষে ব্যথা", "Erectile_Dysfunction": "উত্থানজনিত সমস্যা",
    "Breast_Lump": "স্তনে গাঁট", "Nipple_Discharge": "নিপল থেকে স্রাব", "Infertility": "বন্ধ্যাত্ব", "Anxiety": "উদ্বেগ",
    "Panic": "আতঙ্ক", "Depressed_Mood": "বিষণ্ন মন", "Loss_of_Interest": "আগ্রহ হারানো", "Irritability": "খিটখিটে মেজাজ",
    "Mood_Swings": "মেজাজের পরিবর্তন", "Racing_Thoughts": "দ্রুত চিন্তা চলা", "Hallucinations": "ভ্রম দেখা বা শোনা",
    "Self_Harm_Thoughts": "নিজেকে ক্ষতি করার চিন্তা", "Social_Withdrawal": "সামাজিকভাবে দূরে সরে যাওয়া", "Compulsive_Behavior": "বাধ্যতামূলক আচরণ",
}

DISEASE_BN = {
    "Acute_Myocardial_Infarction": "তীব্র হৃদ্‌যন্ত্রের রক্তনালী বন্ধ বা হার্ট অ্যাটাক", "Aortic_Dissection": "অর্টিক ডিসেকশন",
    "Atrial_Fibrillation": "এট্রিয়াল ফাইব্রিলেশন", "Cardiomyopathy": "হৃদপেশির রোগ", "Deep_Vein_Thrombosis": "গভীর শিরায় রক্ত জমাট",
    "Heart_Failure": "হৃদ্‌যন্ত্রের অকার্যকারিতা", "Hypertension": "উচ্চ রক্তচাপ", "Hypotension": "নিম্ন রক্তচাপ",
    "Infective_Endocarditis": "সংক্রমণজনিত এন্ডোকার্ডাইটিস", "Pericarditis": "হৃদ্‌আবরণে প্রদাহ", "Peripheral_Artery_Disease": "পেরিফেরাল ধমনী রোগ",
    "Sepsis": "সেপসিস", "Stable_Angina": "স্থিতিশীল এনজাইনা", "Supraventricular_Tachycardia": "সুপ্রাভেন্ট্রিকুলার ট্যাকিকার্ডিয়া",
    "Acne": "ব্রণ", "Alopecia_Areata": "গোলাকার চুল পড়া", "Atopic_Dermatitis": "অ্যাটোপিক ডার্মাটাইটিস", "Cellulitis": "সেলুলাইটিস",
    "Chickenpox": "জলবসন্ত", "Contact_Dermatitis": "স্পর্শজনিত ত্বকের প্রদাহ", "Impetigo": "ইমপেটিগো", "Measles": "হাম",
    "Melanoma": "মেলানোমা", "Mumps": "মাম্পস", "Psoriasis": "সোরিয়াসিস", "Rubella": "রুবেলা", "Scabies": "খোসপাঁচড়া",
    "Shingles": "হারপিস জস্টার বা শিংলস", "Tinea_Infection": "দাদ বা টিনিয়া সংক্রমণ", "Urticaria": "চাকা ওঠা বা আর্টিকারিয়া",
    "Adrenal_Insufficiency": "অ্যাড্রিনাল হরমোনের ঘাটতি", "Cushing_Syndrome": "কুশিং সিনড্রোম", "Dehydration": "পানিশূন্যতা",
    "Diabetic_Ketoacidosis": "ডায়াবেটিক কিটোঅ্যাসিডোসিস", "Gout": "গেঁটেবাত", "Hyperkalemia": "রক্তে পটাশিয়াম বেশি",
    "Hyperthyroidism": "থাইরয়েড হরমোন বেশি", "Hypoglycemia": "রক্তে শর্করা কম", "Hyponatremia": "রক্তে সোডিয়াম কম",
    "Hypothyroidism": "থাইরয়েড হরমোন কম", "Iron_Deficiency_Anemia": "আয়রনের ঘাটতিজনিত রক্তস্বল্পতা", "Leukemia": "লিউকেমিয়া",
    "Lymphoma": "লিম্ফোমা", "Type_1_Diabetes": "টাইপ ১ ডায়াবেটিস", "Type_2_Diabetes": "টাইপ ২ ডায়াবেটিস",
    "Vitamin_B12_Deficiency": "ভিটামিন বি১২-এর ঘাটতি", "Acute_Angle_Closure_Glaucoma": "তীব্র অ্যাঙ্গেল-ক্লোজার গ্লুকোমা",
    "Acute_Otitis_Media": "মধ্যকর্ণের তীব্র সংক্রমণ", "Bacterial_Conjunctivitis": "ব্যাকটেরিয়াজনিত চোখ ওঠা", "Cataract": "ছানি",
    "Corneal_Abrasion": "কর্নিয়ায় আঁচড়", "Dental_Abscess": "দাঁতের ফোঁড়া", "Dry_Eye_Syndrome": "শুষ্ক চোখের সিনড্রোম",
    "Meniere_Disease": "মেনিয়ের রোগ", "Otitis_Externa": "বাহ্যিক কানের সংক্রমণ", "Periodontitis": "মাড়ির গভীর সংক্রমণ",
    "Retinal_Detachment": "রেটিনা বিচ্ছিন্ন হওয়া", "Temporomandibular_Disorder": "চোয়ালের জয়েন্টের সমস্যা", "Viral_Conjunctivitis": "ভাইরাসজনিত চোখ ওঠা",
    "Acute_Cholecystitis": "পিত্তথলির তীব্র প্রদাহ", "Acute_Pancreatitis": "অগ্ন্যাশয়ের তীব্র প্রদাহ", "Appendicitis": "অ্যাপেন্ডিসাইটিস",
    "Celiac_Disease": "সিলিয়াক রোগ", "Cholera": "কলেরা", "Cirrhosis": "লিভার সিরোসিস", "Colorectal_Cancer": "বৃহদান্ত্র ও মলাশয়ের ক্যান্সার",
    "Constipation": "কোষ্ঠকাঠিন্য", "Crohn_Disease": "ক্রোন রোগ", "Diverticulitis": "ডাইভার্টিকুলাইটিস", "Fatty_Liver_Disease": "ফ্যাটি লিভার রোগ",
    "Food_Poisoning": "খাদ্যে বিষক্রিয়া", "GERD": "গ্যাস্ট্রোইসোফেজিয়াল রিফ্লাক্স রোগ", "Gallstones": "পিত্তপাথর", "Gastritis": "গ্যাস্ট্রাইটিস",
    "Hemorrhoids": "অর্শ বা পাইলস", "Hepatitis_A": "হেপাটাইটিস এ", "Hepatitis_B": "হেপাটাইটিস বি", "Irritable_Bowel_Syndrome": "ইরিটেবল বাওয়েল সিনড্রোম",
    "Lactose_Intolerance": "ল্যাকটোজ অসহিষ্ণুতা", "Peptic_Ulcer_Disease": "পেপটিক আলসার", "Typhoid_Fever": "টাইফয়েড জ্বর",
    "Ulcerative_Colitis": "আলসারেটিভ কোলাইটিস", "Viral_Gastroenteritis": "ভাইরাসজনিত গ্যাস্ট্রোএন্টারাইটিস",
    "Bipolar_Mania": "বাইপোলার ম্যানিয়া", "Generalized_Anxiety_Disorder": "সাধারণ উদ্বেগজনিত ব্যাধি", "Insomnia_Disorder": "অনিদ্রাজনিত ব্যাধি",
    "Major_Depressive_Disorder": "গুরুতর বিষণ্নতা", "Panic_Disorder": "প্যানিক ডিসঅর্ডার", "Post_Traumatic_Stress_Disorder": "আঘাত-পরবর্তী মানসিক চাপজনিত ব্যাধি",
    "Schizophrenia": "স্কিজোফ্রেনিয়া", "Somatic_Symptom_Disorder": "শারীরিক লক্ষণকেন্দ্রিক মানসিক ব্যাধি", "Ankylosing_Spondylitis": "অ্যাঙ্কাইলোজিং স্পন্ডিলাইটিস",
    "Bursitis": "বার্সাইটিস", "Fibromyalgia": "ফাইব্রোমায়ালজিয়া", "Lumbar_Strain": "কোমরের পেশিতে টান", "Myositis": "পেশিতে প্রদাহ",
    "Osteoarthritis": "অস্টিওআর্থ্রাইটিস", "Osteoporosis_Fracture": "অস্টিওপোরোসিসজনিত হাড় ভাঙা", "Polymyalgia_Rheumatica": "পলিমায়ালজিয়া রিউমাটিকা",
    "Rheumatoid_Arthritis": "রিউমাটয়েড আর্থ্রাইটিস", "Sciatica": "সায়াটিকা", "Septic_Arthritis": "সংক্রমণজনিত জয়েন্ট প্রদাহ",
    "Sjogren_Syndrome": "শোগ্রেন সিনড্রোম", "Systemic_Lupus_Erythematosus": "সিস্টেমিক লুপাস এরিথেমাটোসাস", "Tendinitis": "টেন্ডনে প্রদাহ",
    "Bells_Palsy": "বেলস পালসি", "Benign_Positional_Vertigo": "অবস্থান পরিবর্তনে মাথা ঘোরা", "Carpal_Tunnel_Syndrome": "কারপাল টানেল সিনড্রোম",
    "Cluster_Headache": "ক্লাস্টার মাথাব্যথা", "Concussion": "মস্তিষ্কে আঘাতজনিত ঝাঁকুনি", "Dementia": "ডিমেনশিয়া", "Encephalitis": "মস্তিষ্কে প্রদাহ",
    "Epilepsy": "মৃগী রোগ", "Ischemic_Stroke": "রক্তনালী বন্ধজনিত স্ট্রোক", "Labyrinthitis": "অন্তঃকর্ণের প্রদাহ", "Meningitis": "মেনিনজাইটিস",
    "Migraine": "মাইগ্রেন", "Multiple_Sclerosis": "মাল্টিপল স্ক্লেরোসিস", "Parkinson_Disease": "পারকিনসন রোগ", "Peripheral_Neuropathy": "পেরিফেরাল নিউরোপ্যাথি",
    "Tension_Headache": "টেনশন মাথাব্যথা", "Transient_Ischemic_Attack": "সাময়িক মস্তিষ্কে রক্তপ্রবাহ কমে যাওয়া", "Trigeminal_Neuralgia": "ট্রাইজেমিনাল নিউরালজিয়া",
    "Acute_Kidney_Injury": "কিডনির তীব্র ক্ষতি", "Benign_Prostatic_Hyperplasia": "প্রোস্টেটের অ-ক্যান্সারজনিত বৃদ্ধি", "Bladder_Cancer": "মূত্রথলির ক্যান্সার",
    "Chronic_Kidney_Disease": "দীর্ঘমেয়াদি কিডনি রোগ", "Glomerulonephritis": "কিডনির গ্লোমেরুলাসে প্রদাহ", "Kidney_Stone": "কিডনিতে পাথর",
    "Lower_UTI": "নিম্ন মূত্রনালির সংক্রমণ", "Nephrotic_Syndrome": "নেফ্রোটিক সিনড্রোম", "Overactive_Bladder": "অতিরিক্ত সক্রিয় মূত্রথলি",
    "Prostatitis": "প্রোস্টেটের প্রদাহ", "Pyelonephritis": "কিডনির সংক্রমণ", "Cervical_Cancer": "জরায়ুমুখের ক্যান্সার", "Dysmenorrhea": "ব্যথাযুক্ত মাসিক",
    "Ectopic_Pregnancy": "জরায়ুর বাইরে গর্ভধারণ", "Endometriosis": "এন্ডোমেট্রিওসিস", "Epididymitis": "এপিডিডাইমিসের প্রদাহ", "Menopause": "রজোনিবৃত্তি",
    "Pelvic_Inflammatory_Disease": "পেলভিক ইনফ্ল্যামেটরি ডিজিজ", "Polycystic_Ovary_Syndrome": "পলিসিস্টিক ওভারি সিনড্রোম", "Testicular_Torsion": "অণ্ডকোষ পেঁচিয়ে যাওয়া",
    "Vulvovaginal_Candidiasis": "যোনিপথে ক্যান্ডিডা সংক্রমণ", "Acute_Bronchitis": "তীব্র ব্রংকাইটিস", "Acute_Sinusitis": "তীব্র সাইনুসাইটিস",
    "Allergic_Rhinitis": "অ্যালার্জিজনিত নাকের প্রদাহ", "Asthma_Exacerbation": "হাঁপানি বেড়ে যাওয়া", "Bacterial_Pneumonia": "ব্যাকটেরিয়াজনিত নিউমোনিয়া",
    "COPD_Exacerbation": "সিওপিডি বেড়ে যাওয়া", "COVID_19": "কোভিড-১৯", "Common_Cold": "সাধারণ সর্দি", "Influenza": "ইনফ্লুয়েঞ্জা বা ফ্লু",
    "Laryngitis": "স্বরযন্ত্রের প্রদাহ", "Obstructive_Sleep_Apnea": "ঘুমের সময় শ্বাসনালী বন্ধ হওয়া", "Pertussis": "হুপিং কাশি",
    "Pleurisy": "ফুসফুসের আবরণে প্রদাহ", "Pneumothorax": "ফুসফুস চুপসে যাওয়া", "Pulmonary_Embolism": "ফুসফুসের রক্তনালীতে জমাট",
    "RSV_Infection": "আরএসভি সংক্রমণ", "Streptococcal_Pharyngitis": "স্ট্রেপটোকক্কাল গলা সংক্রমণ", "Tonsillitis": "টনসিলের প্রদাহ",
    "Tuberculosis": "যক্ষ্মা", "Viral_Pneumonia": "ভাইরাসজনিত নিউমোনিয়া", "Acute_HIV_Syndrome": "তীব্র এইচআইভি সিনড্রোম",
    "Anaphylaxis": "তীব্র অ্যালার্জিক প্রতিক্রিয়া", "Chikungunya": "চিকুনগুনিয়া", "Dengue": "ডেঙ্গু", "Hand_Foot_Mouth_Disease": "হাত-পা-মুখ রোগ",
    "Heat_Exhaustion": "গরমে অতিরিক্ত দুর্বলতা", "Heat_Stroke": "হিট স্ট্রোক", "Infectious_Mononucleosis": "ইনফেকশাস মনোনিউক্লিওসিস",
    "Japanese_Encephalitis": "জাপানিজ এনসেফালাইটিস", "Kala_Azar": "কালাজ্বর", "Leptospirosis": "লেপ্টোস্পাইরোসিস", "Lyme_Disease": "লাইম রোগ",
    "Malaria": "ম্যালেরিয়া", "Rabies": "জলাতঙ্ক", "Tetanus": "ধনুষ্টংকার",
}

CATEGORY_BN = {
    "All": "সব", "General": "সাধারণ", "Respiratory": "শ্বাসতন্ত্র", "Gastrointestinal": "পরিপাকতন্ত্র",
    "Neurological": "স্নায়বিক", "Cardiovascular": "হৃদ্‌যন্ত্র ও রক্তনালী", "Urinary_Renal": "মূত্র ও কিডনি",
    "Renal_Urological": "কিডনি ও মূত্রতন্ত্র", "Skin": "ত্বক", "Dermatological": "ত্বক",
    "Musculoskeletal": "পেশি ও অস্থি", "Musculoskeletal_Autoimmune": "পেশি, অস্থি ও অটোইমিউন",
    "Eye_ENT_Dental": "চোখ, কান, নাক, গলা ও দাঁত", "Endocrine_Metabolic": "হরমোন ও বিপাক",
    "Reproductive": "প্রজনন স্বাস্থ্য", "Mental_Behavioral": "মানসিক ও আচরণগত", "Tropical_Infectious_Other": "সংক্রামক ও উষ্ণমণ্ডলীয়",
}

RISK_BN = {"Low": "কম", "Moderate": "মাঝারি", "High": "উচ্চ", "Critical": "জরুরি", "Unknown": "অজানা"}
URGENCY_BN = {
    "Emergency care now": "এখনই জরুরি চিকিৎসা নিন",
    "Same-day urgent clinical assessment": "আজই জরুরি চিকিৎসা মূল্যায়ন নিন",
    "Clinical review within 24–48 hours": "২৪–৪৮ ঘণ্টার মধ্যে চিকিৎসকের পরামর্শ নিন",
    "Monitor and arrange routine care if symptoms persist or worsen": "লক্ষণ পর্যবেক্ষণ করুন এবং না কমলে বা বাড়লে চিকিৎসা নিন",
}


def bilingual(english: str, bangla: str | None) -> str:
    return f"{english} ({bangla})" if bangla else english


def symptom_bn(name: str) -> str:
    return SYMPTOM_BN.get(name, name.replace("_", " "))


def disease_bn(name: str) -> str:
    return DISEASE_BN.get(name, name.replace("_", " "))


def category_bn(name: str | None) -> str:
    if not name:
        return "অন্যান্য"
    return CATEGORY_BN.get(name, name.replace("_", " "))
