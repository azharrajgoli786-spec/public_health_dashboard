"""Structured disease information library for the Public Health Dashboard.

Architecture note (follows existing project pattern):
- Like `health_data` in app.py (loaded from CSV at startup, kept in memory,
  no external database), this module keeps disease info in a Python data
  file loaded once at startup. To add a disease, append one dict to
  DISEASES following the template below — no other code changes needed.
- Surveillance case counts (states/charts) stay separate from this
  educational library. No fake statistics are stored here.

Content guidance: general information aligned with WHO / MoHFW / NCDC
public guidance, written in simple English. No medicines, antibiotics or
dosages are recommended. Every detail page carries a medical disclaimer.
"""

CATEGORIES = [
    "Infectious Diseases",
    "Vector-Borne Diseases",
    "Waterborne Diseases",
    "Respiratory Diseases",
    "Non-Communicable Diseases",
    "Nutritional Diseases",
    "Lifestyle Diseases",
]

# Short label for a category, used where the full name is too long
# (card subtitles, compact lists).
CATEGORY_SHORT = {
    "Infectious Diseases": "Infectious",
    "Vector-Borne Diseases": "Vector-borne",
    "Waterborne Diseases": "Waterborne",
    "Respiratory Diseases": "Respiratory",
    "Non-Communicable Diseases": "Non-communicable",
    "Nutritional Diseases": "Nutritional",
    "Lifestyle Diseases": "Lifestyle",
}

# Icon key per category. Individual diseases may override this - see
# DISEASE_ICONS - and anything without an entry falls back to its
# category's icon, so adding a disease never breaks the page.
CATEGORY_ICONS = {
    "Infectious Diseases": "virus",
    "Vector-Borne Diseases": "mosquito",
    "Waterborne Diseases": "droplet",
    "Respiratory Diseases": "lungs",
    "Non-Communicable Diseases": "heart",
    "Nutritional Diseases": "leaf",
    "Lifestyle Diseases": "bowl",
}

# Icon key per disease slug, for diseases that deserve their own symbol
# (diabetes is a blood condition, not just an infection, and so on).
DISEASE_ICONS = {
    "tuberculosis": "lungs",
    "influenza": "virus",
    "covid-19": "virus",
    "hiv-aids": "shield",
    "hepatitis": "liver",
    "measles": "child",
    "chickenpox": "skin",
    "rabies": "virus",
    "dengue": "mosquito",
    "malaria": "mosquito",
    "chikungunya": "mosquito",
    "lymphatic-filariasis": "mosquito",
    "typhoid": "thermometer",
    "cholera": "droplet",
    "diarrhoeal-diseases": "stomach",
    "food-poisoning": "stomach",
    "amoebiasis": "stomach",
    "leptospirosis": "droplet",
    "asthma": "lungs",
    "pneumonia": "lungs",
    "copd": "lungs",
    "bronchitis": "lungs",
    "diabetes": "blood",
    "hypertension": "heart",
    "stroke": "brain",
    "cancer": "dna",
    "chronic-kidney-disease": "body",
    "chronic-liver-disease": "liver",
    "epilepsy": "brain",
    "arthritis": "body",
    "thyroid-disorders": "body",
    "iron-deficiency-anaemia": "blood",
    "vitamin-d-deficiency": "leaf",
    "iodine-deficiency": "leaf",
    "obesity": "bowl",
    "fatty-liver-disease": "liver",
    "cardiovascular-diseases": "heart",
}

# Featured in the "Popular diseases" strip on the library page. Ordered by
# how often these come up in general health questions.
POPULAR_SLUGS = [
    "dengue",
    "diabetes",
    "tuberculosis",
    "malaria",
    "hypertension",
    "covid-19",
]

# Transmission route for entries whose category default would misdescribe
# them. Each route is taken from the entry's own "spreads" text.
TRANSMISSION_OVERRIDES = {
    # Types A and E spread through contaminated food and water; types B and
    # C spread through blood and body fluids.
    "hepatitis": "Blood / water-borne",
    # Rabies reaches people through bites and scratches from an infected
    # animal. It is transmissible, just not by casual contact.
    "rabies": "Person-to-person possible",
    # People fall ill from the same contaminated food; it is not usually
    # passed from person to person.
    "food-poisoning": "Water / food-borne",
    # Enters through skin cuts or mucous membranes in contaminated water
    # or soil.
    "leptospirosis": "Water / food-borne",
}

# Conditions that do not spread between people, even though their category
# also holds conditions that do.
NON_TRANSMISSIBLE = {
    "asthma",
    "copd",
}

# Pastel colour tone per category, used for the round icon badge.
CATEGORY_TONES = {
    "Infectious Diseases": "green",
    "Vector-Borne Diseases": "pink",
    "Waterborne Diseases": "blue",
    "Respiratory Diseases": "orange",
    "Non-Communicable Diseases": "violet",
    "Nutritional Diseases": "lime",
    "Lifestyle Diseases": "yellow",
}

# Tones for individual diseases, so cards in the same category are not all
# the same colour (e.g. dengue and malaria are both vector-borne).
DISEASE_TONES = {
    "dengue": "pink",
    "diabetes": "red",
    "tuberculosis": "orange",
    "malaria": "green",
    "hypertension": "red",
    "covid-19": "violet",
    "chikungunya": "violet",
    "cholera": "blue",
    "typhoid": "blue",
    "asthma": "orange",
    "pneumonia": "orange",
    "cancer": "violet",
    "obesity": "yellow",
    "fatty-liver-disease": "yellow",
}

DISEASES = [
    # ---------------- Infectious Diseases (8) ----------------
    {
        "slug": "tuberculosis",
        "name": "Tuberculosis (TB)",
        "category": "Infectious Diseases",
        "short": "A bacterial lung infection that spreads through air and needs long medical treatment.",
        "overview": "Tuberculosis (TB) is an infection caused by Mycobacterium tuberculosis bacteria. It most often affects the lungs but can affect other parts of the body. TB develops slowly and can be cured with complete treatment supervised by a doctor.",
        "causes": ["Bacteria called Mycobacterium tuberculosis", "Close, prolonged contact with a person who has active lung TB", "Weakened immunity (for example due to undernutrition, diabetes, or HIV) increases risk"],
        "spreads": "Spreads from person to person through the air when a person with active lung TB coughs, sneezes, or talks. It does not spread by sharing food, water, clothes, or by touch alone.",
        "symptoms": ["Cough lasting 2 weeks or more", "Fever, especially in the evening, and night sweats", "Weight loss and loss of appetite", "Chest pain or blood in sputum in some cases"],
        "prevention": ["Cover mouth and nose while coughing or sneezing", "Keep rooms airy with good ventilation and sunlight", "Complete vaccination as advised under the national immunisation schedule (BCG for newborns)", "Early testing of prolonged cough; Nikshay/ NTEP services offer free diagnosis and treatment in India"],
        "treatment": "TB is treated with a combination of medicines taken for several months, decided and monitored by a doctor. Treatment in India is available free under the National TB Elimination Programme. Patients should never stop medicines early, even if they feel better, and should attend all follow-up visits.",
        "when_to_visit": ["Cough for 2 weeks or more", "Unexplained weight loss, fever, or night sweats", "Close contact of a person diagnosed with TB", "Blood in sputum"],
        "emergency": ["Coughing up large amounts of blood", "Severe breathing difficulty", "Sudden severe chest pain"],
        "high_risk": ["Young children", "Older adults", "People with HIV, diabetes, or undernutrition", "People living in crowded settings"],
    },
    {
        "slug": "influenza",
        "name": "Influenza (Flu)",
        "category": "Infectious Diseases",
        "short": "A contagious viral fever with body ache that spreads fast in crowds and seasons.",
        "overview": "Influenza, commonly called flu, is a viral infection of the nose, throat, and lungs. Most people recover in a week with rest, but it can become serious for some groups. Seasonal flu spreads widely during monsoon and winter months in India.",
        "causes": ["Influenza viruses (types A and B most commonly)", "Weakened defences from tiredness, cold exposure, or other illness can worsen the episode"],
        "spreads": "Spreads through droplets when an infected person coughs, sneezes, or talks, and by touching contaminated surfaces and then the face.",
        "symptoms": ["Sudden fever, chills, and body ache", "Sore throat, dry cough, and runny or blocked nose", "Headache and tiredness", "Sometimes vomiting or loose motions, mainly in children"],
        "prevention": ["Wash hands often with soap and water", "Avoid close contact with people who have flu-like illness", "Cover coughs and sneezes; wear a mask in crowded places when ill", "Annual flu vaccination as advised by a doctor, especially for high-risk groups"],
        "treatment": "Most cases are managed with rest, fluids, and fever care as advised by a doctor. Antibiotics do not work against flu viruses and should not be taken without prescription. A doctor decides if antiviral or hospital care is needed, especially for breathlessness or high-risk patients.",
        "when_to_visit": ["Fever beyond 3 days or very high fever", "Breathing difficulty, chest pain, or wheezing", "A person from a high-risk group falls ill", "Symptoms improve then suddenly worsen"],
        "emergency": ["Severe breathing difficulty or bluish lips", "Confusion, fainting, or seizures", "Severe chest pain or dehydration (very little urine, dizziness)"],
        "high_risk": ["Children under 5 years", "Adults above 65 years", "Pregnant people", "People with asthma, heart disease, diabetes, or weak immunity"],
    },
    {
        "slug": "covid-19",
        "name": "COVID-19",
        "category": "Infectious Diseases",
        "short": "A coronavirus infection ranging from mild cold-like illness to severe lung disease.",
        "overview": "COVID-19 is an illness caused by the SARS-CoV-2 coronavirus. Most infections are mild, but some people develop lung infection needing hospital care. Vaccination and early care of high-risk people have greatly reduced severe illness.",
        "causes": ["SARS-CoV-2 coronavirus and its variants", "Risk of severe illness is higher with older age and long-standing diseases"],
        "spreads": "Spreads mainly through respiratory droplets and aerosols from an infected person, especially in closed, crowded, poorly ventilated places. Touching contaminated surfaces is a less common route.",
        "symptoms": ["Fever, cough, sore throat, and tiredness", "Loss of taste or smell, headache, and body ache", "Blocked or runny nose", "Breathing difficulty in severe cases"],
        "prevention": ["Stay up to date with COVID-19 vaccination as per national guidance", "Wear a mask in crowded or poorly ventilated places when advised", "Wash hands regularly and keep rooms ventilated", "Isolate when positive and inform close contacts"],
        "treatment": "Mild cases are managed at home with rest, fluids, and medical advice over phone or visit. A doctor decides about testing, isolation period, and any hospital care. Do not self-medicate with steroids, antibiotics, or oxygen; seek guidance if breathlessness or oxygen-level fall occurs.",
        "when_to_visit": ["Persistent fever, worsening cough, or increasing tiredness", "A high-risk person tests positive", "Symptoms last beyond a week", "Any breathing discomfort"],
        "emergency": ["Severe breathing difficulty or inability to complete sentences", "Oxygen saturation persistently low where a meter is available", "Chest pain, confusion, or bluish face or lips"],
        "high_risk": ["Older adults", "Pregnant people", "People with heart, lung, kidney disease, diabetes, cancer, or weak immunity", "Unvaccinated people"],
    },
    {
        "slug": "hiv-aids",
        "name": "HIV / AIDS",
        "category": "Infectious Diseases",
        "short": "A virus that weakens immunity over years; treatment allows a long healthy life.",
        "overview": "HIV (Human Immunodeficiency Virus) attacks the body's defence system. Without treatment, it can advance to AIDS over years. With regular treatment, people with HIV can live long, healthy lives and prevent transmission. Free testing and treatment are available under India's NACO programme.",
        "causes": ["Human Immunodeficiency Virus (HIV)", "Progresses faster without treatment and with other untreated infections or poor nutrition"],
        "spreads": "Spreads through unprotected sex, sharing needles, transfusion of infected blood, and from parent to child during pregnancy, birth, or breastfeeding without preventive care. It does not spread by hugging, sharing food, mosquito bites, or using the same toilet.",
        "symptoms": ["Often no symptoms for years in early stages", "Repeated fevers, weight loss, and long-lasting diarrhoea in later stages", "Frequent infections such as TB or skin infections", "Swollen glands, tiredness"],
        "prevention": ["Safe sexual practices including correct condom use", "Never share needles; ensure tested blood for transfusion", "HIV testing in pregnancy and preventive treatment to protect the baby", "Post-exposure guidance from a doctor immediately after a possible exposure"],
        "treatment": "HIV is treated with lifelong antiretroviral therapy (ART) prescribed and monitored by a trained doctor. ART controls the virus and must never be started, stopped, or changed without medical supervision. Regular check-ups and adherence to the schedule are essential.",
        "when_to_visit": ["After any possible exposure (unprotected sex, needle injury)", "Before planning pregnancy when either partner has HIV", "Repeated infections, weight loss, or long fever", "For confidential testing and counselling (ICTC centres)"],
        "emergency": ["Signs of severe infection such as very high fever with breathing difficulty", "Sudden confusion, severe headache with neck stiffness", "Severe weakness or inability to eat or drink"],
        "high_risk": ["Partners of people with untreated HIV", "People who inject drugs", "Babies born to mothers with untreated HIV", "People needing repeated blood transfusions without safe supply"],
    },
    {
        "slug": "hepatitis",
        "name": "Hepatitis (Liver Inflammation)",
        "category": "Infectious Diseases",
        "short": "Liver inflammation, often viral, causing jaundice, tiredness, and stomach discomfort.",
        "overview": "Hepatitis means inflammation of the liver. Viruses named A, B, C, D, and E are common causes; alcohol, some medicines, and other conditions can also injure the liver. Some types recover fully while others can become long-term and need specialist care.",
        "causes": ["Hepatitis A and E viruses — usually through contaminated food or water", "Hepatitis B, C, D — through infected blood, unprotected sex, or parent to child", "Heavy alcohol use and some medicines or herbal products can also damage the liver"],
        "spreads": "Types A and E spread through contaminated food and water. Types B and C spread through blood, unprotected sex, sharing needles or razors, and from mother to baby. Hepatitis does not spread through casual touch or hugging.",
        "symptoms": ["Yellowing of eyes and skin (jaundice), dark urine", "Tiredness, loss of appetite, nausea", "Pain in the upper right side of the abdomen", "Many chronic cases have no early symptoms"],
        "prevention": ["Drink safe water and eat freshly cooked hygienic food", "Hepatitis B vaccination as per the national schedule", "Safe sex, single-use needles, and screened blood", "Avoid sharing razors or toothbrushes; limit alcohol"],
        "treatment": "Care depends on the type and stage, decided after blood tests by a doctor. Many acute cases need rest, safe diet, and follow-up; long-term types may need specialist medicines taken for months. Avoid alcohol and do not take liver medicines or herbal products without medical advice.",
        "when_to_visit": ["Yellow eyes, dark urine, or persistent nausea", "Known exposure to jaundice or hepatitis", "Pregnancy with jaundice", "Long-term tiredness with abnormal liver tests"],
        "emergency": ["Vomiting blood or black stools", "Confusion, extreme sleepiness, or fainting with jaundice", "Severe abdominal swelling or heavy bleeding"],
        "high_risk": ["Newborns of mothers with hepatitis B", "Healthcare workers with needle exposure", "People needing dialysis or repeated transfusions", "People with heavy alcohol use"],
    },
    {
        "slug": "measles",
        "name": "Measles",
        "category": "Infectious Diseases",
        "short": "A highly contagious childhood rash-fever preventable by safe vaccines.",
        "overview": "Measles is a very contagious viral illness that causes high fever and rash, mainly in children. It can lead to serious problems such as pneumonia or brain infection. Measles is preventable with the safe and effective MR/MMR vaccine given under India's Universal Immunisation Programme.",
        "causes": ["Measles virus", "Lack of vaccination is the main risk"],
        "spreads": "Spreads very easily through air when an infected person coughs or sneezes, and by touching contaminated surfaces. An infected person can spread it from before the rash appears until a few days after.",
        "symptoms": ["High fever, cough, runny nose, and red watery eyes", "Tiny white spots inside the mouth followed by red rash starting on face", "Rash spreading to the body over days", "Loss of appetite and tiredness"],
        "prevention": ["MR/MMR vaccination on schedule (two doses); check the child's card", "Keep the sick child at home and away from other children", "Vitamin A as given in national programmes supports recovery", "Inform the school or anganwadi about the illness"],
        "treatment": "There is no specific medicine that kills the measles virus; care focuses on fever control, fluids, nutrition, and rest under a doctor's guidance. Antibiotics are used only if a doctor finds a bacterial complication. Hospital care is needed for breathing difficulty, dehydration, or fits.",
        "when_to_visit": ["Any child with fever and rash", "Red eyes with cough and fever", "Poor feeding or dehydration", "Missed vaccine doses"],
        "emergency": ["Breathing difficulty or fast breathing", "Fits (seizures)", "Signs of dehydration: no tears, dry mouth, very little urine", "Extreme drowsiness or unconsciousness"],
        "high_risk": ["Infants and children under 5", "Unvaccinated children and adults", "Pregnant people", "Children with undernutrition or weak immunity"],
    },
    {
        "slug": "chickenpox",
        "name": "Chickenpox",
        "category": "Infectious Diseases",
        "short": "An itchy blister-rash illness of childhood that spreads easily but is vaccine-preventable.",
        "overview": "Chickenpox is a viral illness with fever and an itchy rash that turns into fluid-filled blisters and then scabs. Most children recover in 1–2 weeks. Adults, pregnant people, and people with weak immunity can have more severe illness.",
        "causes": ["Varicella-zoster virus", "First infection causes chickenpox; the virus can later cause shingles"],
        "spreads": "Spreads through air, coughs, and direct contact with blister fluid. A person is contagious from 1–2 days before the rash until all blisters form scabs.",
        "symptoms": ["Mild fever, tiredness, and headache", "Itchy red spots turning into blisters, then scabs", "Rash first on chest, back, and face, then spreading", "Loss of appetite"],
        "prevention": ["Chickenpox vaccination as advised by a doctor", "Keep the patient at home until all blisters crust over", "Avoid scratching; keep nails short and skin clean", "Keep newborns and high-risk people away from the patient"],
        "treatment": "Care is usually home-based: rest, fluids, and itch relief as advised by a doctor. Do not use aspirin in children. A doctor decides if antiviral medicine or hospital care is needed, especially for adults, pregnancy, or infected skin.",
        "when_to_visit": ["Rash with high or prolonged fever", "Blisters with pus, severe pain, or spreading redness", "Illness in pregnancy, newborns, or weak immunity", "Vomiting, severe headache, or confusion"],
        "emergency": ["Breathing difficulty or chest pain", "Severe headache with vomiting or fits", "Unconsciousness or severe dehydration"],
        "high_risk": ["Newborns", "Pregnant people", "Adults without past infection or vaccination", "People on cancer treatment or with weak immunity"],
    },
    {
        "slug": "rabies",
        "name": "Rabies",
        "category": "Infectious Diseases",
        "short": "A fatal brain infection after animal bites — prevented by quick wound care and vaccines.",
        "overview": "Rabies is a viral infection of the brain and nerves, usually after the bite or scratch of an infected animal, most often dogs. Once symptoms appear, rabies is almost always fatal, but it is preventable with immediate wound washing, vaccines, and immunoglobulin when advised.",
        "causes": ["Rabies virus present in saliva of infected mammals", "Dog bites are the most common source in India; cats, monkeys, and other mammals can also transmit"],
        "spreads": "Enters the body through bites, scratches, or licks on broken skin or eyes, nose, or mouth by an infected animal. It does not spread by casual contact with a healthy vaccinated pet.",
        "symptoms": ["Pain, tingling, or itching at the bite site", "Fever, headache, and anxiety as illness begins", "Fear of water or air, confusion, and agitation in later stages", "Paralysis and coma in advanced illness"],
        "prevention": ["Wash any animal bite wound immediately with soap and running water for at least 15 minutes", "Visit a doctor or hospital the same day for post-exposure vaccines", "Vaccinate pet dogs and cats yearly; avoid provoking stray animals", "Pre-exposure vaccination for high-risk work as advised"],
        "treatment": "There is no effective treatment after symptoms begin, so prevention is the only protection. After a bite, a doctor decides the vaccine schedule and whether immunoglobulin is needed based on the wound type. Complete every dose on time; do not rely on traditional remedies alone.",
        "when_to_visit": ["Any animal bite, scratch, or lick on broken skin — same day", "Bite from a stray, wild, or unvaccinated animal", "Missed vaccine dose during the course", "Bite on face, neck, hands, or multiple wounds (higher urgency)"],
        "emergency": ["Any bite with heavy bleeding or deep wounds", "Signs of infection: increasing pain, swelling, or fever", "Once fear of water, confusion, or paralysis appears, rush to emergency (though prevention window has passed)"],
        "high_risk": ["Children (more likely to be bitten on face and to not report)", "People handling animals (vets, dog-catchers, lab staff)", "People in areas with many stray dogs", "Travellers in remote areas far from hospitals"],
    },
    # ---------------- Vector-Borne Diseases (4) ----------------
    {
        "slug": "dengue",
        "name": "Dengue",
        "category": "Vector-Borne Diseases",
        "short": "A mosquito-borne fever with severe body pain; most recover, some need hospital care.",
        "overview": "Dengue is a viral illness spread by Aedes mosquitoes that bite mainly in daytime. Most people have mild fever and recover, but a small number develop bleeding or shock and need urgent hospital care. Dengue is common in Indian cities during and after monsoon.",
        "causes": ["Dengue virus (four types); second infection can be more serious", "Breeding of Aedes mosquitoes in stored or stagnant clean water"],
        "spreads": "Spreads only through the bite of an infected Aedes mosquito. It does not spread directly from person to person.",
        "symptoms": ["Sudden high fever with severe headache and pain behind the eyes", "Severe joint and muscle pain, nausea", "Skin rash in some cases", "Warning signs: severe stomach pain, repeated vomiting, bleeding gums or nose, extreme tiredness"],
        "prevention": ["Remove stagnant water from coolers, pots, tyres, and trays weekly", "Use mosquito nets, screens, repellents, and full-sleeve clothes", "Keep overhead tanks covered; support local fogging and larva-control drives", "Seek early testing during fever season"],
        "treatment": "There is no specific medicine that kills the dengue virus; treatment is supportive with fluids, rest, and paracetamol for fever as advised by a doctor. Avoid aspirin, ibuprofen, and other painkillers unless a doctor prescribes them, as they can increase bleeding risk. Platelet transfusion is only given when a doctor finds it necessary.",
        "when_to_visit": ["Fever for more than 2–3 days during dengue season", "Severe pain, vomiting, or rash with fever", "Any warning sign listed above", "Fever in pregnancy or in a person with other diseases"],
        "emergency": ["Severe stomach pain or repeated vomiting", "Bleeding from nose or gums, blood in vomit or stool", "Extreme weakness, cold hands and feet, or fainting", "Very low urine output or breathing difficulty"],
        "high_risk": ["Infants and older adults", "Pregnant people", "People with diabetes, heart, or kidney disease", "People having dengue for the second time"],
    },
    {
        "slug": "malaria",
        "name": "Malaria",
        "category": "Vector-Borne Diseases",
        "short": "A mosquito-borne illness with cycles of high fever, chills, and sweating.",
        "overview": "Malaria is caused by Plasmodium parasites carried by Anopheles mosquitoes that usually bite at night. It causes repeated episodes of fever with chills. With early blood testing and complete treatment, malaria is curable; delayed care can damage vital organs.",
        "causes": ["Plasmodium parasites (P. vivax and P. falciparum most common in India)", "Night-biting Anopheles mosquitoes breeding in stagnant water"],
        "spreads": "Spreads through the bite of an infected female Anopheles mosquito. It does not spread by touch or sharing food.",
        "symptoms": ["Fever with chills and shivering followed by sweating", "Headache, body ache, nausea", "In severe falciparum malaria: confusion, jaundice, very low urine", "Anaemia and weakness with repeated attacks"],
        "prevention": ["Sleep under insecticide-treated mosquito nets, especially at night", "Use repellents, screens, and long clothes after sunset", "Drain stagnant water and keep surroundings clean", "Take preventive medicine only when a doctor prescribes for travel"],
        "treatment": "Diagnosis needs a blood smear or rapid test; treatment type and duration depend on the parasite species and severity, decided by a doctor. Complete the full course even after fever settles. Severe malaria needs urgent hospital care.",
        "when_to_visit": ["Any fever with chills or cyclical fever", "Fever after travel to a malaria-prone area", "Fever in pregnancy or in a young child", "Fever not improving in 2 days"],
        "emergency": ["Confusion, fits, or unconsciousness with fever", "Very dark or very little urine", "Severe vomiting, jaundice, or breathing difficulty", "Severe anaemia (extreme paleness and weakness)"],
        "high_risk": ["Children under 5", "Pregnant people", "Travellers without immunity", "People with weak immunity"],
    },
    {
        "slug": "chikungunya",
        "name": "Chikungunya",
        "category": "Vector-Borne Diseases",
        "short": "A mosquito-borne fever with painful, long-lasting joint pain.",
        "overview": "Chikungunya is a viral illness spread by the same daytime mosquitoes as dengue. Fever settles in days, but joint pain can last weeks or months. Deaths are rare, but joint symptoms can limit daily work and need physiotherapy.",
        "causes": ["Chikungunya virus", "Aedes mosquito breeding in household stored water"],
        "spreads": "Spreads through the bite of an infected Aedes mosquito. It does not spread by touch.",
        "symptoms": ["Sudden fever with severe joint pain, especially hands, wrists, ankles", "Muscle pain, headache, tiredness", "Rash in some people", "Joint stiffness lasting weeks after fever"],
        "prevention": ["Same mosquito control as dengue: remove stagnant water weekly", "Daytime protection with repellents and covered clothes", "Nets and window screens", "Early reporting of fever clusters to health workers"],
        "treatment": "Care is supportive: rest, fluids, and pain and fever relief as advised by a doctor. Gentle movement and physiotherapy help stiff joints recover. Do not take long-term painkillers or steroids without prescription.",
        "when_to_visit": ["Fever with severe joint pain", "Joint pain lasting beyond 2 weeks", "Swollen, red, or deformed joints", "Fever in a newborn, older adult, or pregnancy"],
        "emergency": ["Severe dehydration or inability to move or eat", "Chest pain or breathing difficulty", "High fever with confusion"],
        "high_risk": ["Newborns", "Older adults", "People with arthritis or other joint disease", "Pregnant people near delivery time"],
    },
    {
        "slug": "lymphatic-filariasis",
        "name": "Lymphatic Filariasis (Elephantiasis)",
        "category": "Vector-Borne Diseases",
        "short": "A mosquito-borne parasitic infection that can cause long-term limb swelling.",
        "overview": "Lymphatic filariasis is caused by tiny worms spread by mosquitoes. Many infected people have no symptoms, but some develop swelling of legs, arms, or genitals over years. India's mass drug administration rounds aim to eliminate this disease.",
        "causes": ["Filarial worms (mainly Wuchereria bancrofti in India)", "Repeated mosquito bites over months or years"],
        "spreads": "Spreads through mosquito bites; the worms need mosquitoes to move between people. It does not spread by touch.",
        "symptoms": ["Often no early symptoms", "Repeated fever with painful swelling of lymph glands", "Long-term swelling of legs or arms", "In men, swelling of the scrotum (hydrocele)"],
        "prevention": ["Take the full course during government mass drug administration rounds", "Sleep under mosquito nets and control mosquitoes", "Wash swollen limbs daily and keep skin clean to prevent infection"],
        "treatment": "Medicines that kill the worms are given free in elimination programmes; dosage and rounds are decided by health authorities. Swollen limbs need daily washing, elevation, exercise, and footwear; surgery may help hydrocele. A doctor should evaluate any new swelling.",
        "when_to_visit": ["Repeated fever with gland pain", "New swelling of a limb", "Scrotal swelling", "Skin infection on a swollen limb"],
        "emergency": ["Rapidly spreading redness with high fever on a swollen limb", "Severe pain or pus discharge"],
        "high_risk": ["People in endemic districts of UP, Bihar, Jharkhand, Odisha, and others", "People with repeated mosquito exposure", "People with poor foot hygiene"],
    },
    # ---------------- Waterborne Diseases (6) ----------------
    {
        "slug": "typhoid",
        "name": "Typhoid",
        "category": "Waterborne Diseases",
        "short": "A bacterial fever from unsafe food or water that needs full antibiotic treatment.",
        "overview": "Typhoid is a bacterial infection causing prolonged fever, stomach pain, and weakness. It spreads through contaminated food and water. With timely diagnosis and complete treatment, most people recover fully.",
        "causes": ["Salmonella Typhi bacteria", "Drinking unsafe water or eating food handled unhygienically"],
        "spreads": "Spreads through food or water contaminated with stool or urine of an infected person or carrier. It does not spread through air.",
        "symptoms": ["Fever rising step by step, lasting many days", "Headache, stomach pain, constipation or diarrhoea", "Loss of appetite and weakness", "Sometimes rose-coloured spots or coated tongue"],
        "prevention": ["Drink boiled or purified water; avoid raw street food and cut fruits", "Wash hands with soap before eating and after toilet", "Typhoid vaccination as advised by a doctor", "Eat freshly cooked hot food"],
        "treatment": "Typhoid needs antibiotic treatment prescribed by a doctor after blood tests; the exact medicine and duration depend on local resistance and severity. Complete the full course, take rest and fluids, and return for review. Self-medication can hide the illness and cause complications.",
        "when_to_visit": ["Fever beyond 3 days with stomach symptoms", "Fever after eating outside or travel", "Persistent headache with fever", "Fever in a child with poor feeding"],
        "emergency": ["Severe stomach pain with swelling", "Blood in stool or black stools", "Confusion, very low alertness, or fainting", "Persistent vomiting with dehydration"],
        "high_risk": ["School-age children", "People in areas with unsafe water", "Travellers", "Food handlers without hygiene training"],
    },
    {
        "slug": "cholera",
        "name": "Cholera",
        "category": "Waterborne Diseases",
        "short": "A diarrhoeal disease causing sudden watery stools and rapid dehydration.",
        "overview": "Cholera is an acute diarrhoeal infection that can cause severe dehydration within hours. It spreads through contaminated water and food during outbreaks. Quick replacement of fluids saves lives; most cases are managed with oral rehydration.",
        "causes": ["Vibrio cholerae bacteria", "Unsafe drinking water, unhygienic food, and poor sanitation during outbreaks"],
        "spreads": "Spreads through water or food contaminated with stool of an infected person. It does not spread through air or casual touch.",
        "symptoms": ["Sudden profuse watery diarrhoea (often described as rice-water stools)", "Vomiting and leg cramps", "Thirst, dry mouth, and weakness", "Sunken eyes and very little urine in dehydration"],
        "prevention": ["Drink only boiled, chlorinated, or sealed safe water", "Wash hands with soap; dispose of stool safely", "Eat freshly cooked food; avoid raw salads during outbreaks", "Oral cholera vaccine in high-risk settings as advised"],
        "treatment": "The most important treatment is rapid fluid replacement with ORS; a doctor decides about IV fluids and whether antibiotics are needed. Continue feeding, especially in children, alongside ORS. Severe dehydration needs urgent hospital care.",
        "when_to_visit": ["Three or more loose stools in a day with thirst", "Any suspected cholera during an outbreak", "Diarrhoea in a young child or older adult", "Vomiting preventing ORS intake"],
        "emergency": ["Signs of severe dehydration: extreme thirst, sunken eyes, no urine, cold hands", "Unconsciousness or fits", "Blood in stool with high fever (may indicate another cause needing urgent care)"],
        "high_risk": ["Young children", "Older adults", "People in flood-affected or crowded camps", "People with weak immunity"],
    },
    {
        "slug": "diarrhoeal-diseases",
        "name": "Acute Diarrhoeal Diseases",
        "category": "Waterborne Diseases",
        "short": "Frequent loose stools, mostly from germs in water or food; dehydration is the main danger.",
        "overview": "Diarrhoeal diseases cause frequent loose or watery stools, often with vomiting and stomach cramps. Germs from unsafe water, food, or dirty hands are the usual cause. In children, dehydration can become dangerous quickly, but ORS and zinc (for children, as advised) prevent most deaths.",
        "causes": ["Viruses (such as rotavirus in children), bacteria, or parasites", "Unsafe water, unhygienic food, and poor hand hygiene"],
        "spreads": "Spreads through contaminated water and food, and through dirty hands, utensils, or surfaces. Some viral types spread easily among children in close contact.",
        "symptoms": ["Three or more loose stools in a day", "Stomach cramps, nausea, vomiting", "Fever in some cases", "Thirst, weakness, and reduced urine in dehydration"],
        "prevention": ["Safe water, handwashing with soap, and clean toilets", "Exclusive breastfeeding for 6 months; rotavirus vaccine as per schedule", "Freshly cooked food; safe disposal of child stool", "Keep ORS packets at home during monsoon and travel"],
        "treatment": "Give ORS after every loose stool and continue normal feeding; a doctor advises zinc for children and whether further medicine is needed. Antibiotics are not needed for most cases and should not be given without prescription. Hospital care is needed if dehydration worsens or blood appears in stool.",
        "when_to_visit": ["Diarrhoea beyond 2 days or with fever", "Blood or mucus in stool", "Child refusing feeds or becoming drowsy", "Repeated vomiting"],
        "emergency": ["No urine for many hours, sunken eyes, extreme thirst", "Unconsciousness or fits", "Severe stomach pain with swelling"],
        "high_risk": ["Children under 5", "Older adults", "People with weak immunity", "People in areas with unsafe water"],
    },
    {
        "slug": "food-poisoning",
        "name": "Food Poisoning",
        "category": "Waterborne Diseases",
        "short": "Sudden vomiting and diarrhoea hours after eating contaminated food.",
        "overview": "Food poisoning is sudden illness after eating food contaminated with germs or their toxins. Symptoms usually start within hours and settle in 1–3 days. Most cases need fluids and rest; severe cases need medical care.",
        "causes": ["Bacteria or their toxins in stale, undercooked, or unhygienically stored food", "Contaminated milk, eggs, meat, and street food kept at room temperature"],
        "spreads": "Not usually contagious; people fall ill from the same contaminated food. Good hygiene prevents further spread in the household.",
        "symptoms": ["Nausea, vomiting, and stomach cramps", "Diarrhoea, sometimes with fever", "Weakness and loss of appetite", "Dehydration with repeated episodes"],
        "prevention": ["Eat freshly cooked food; refrigerate leftovers quickly and reheat fully", "Wash fruits, vegetables, hands, and utensils well", "Avoid food from unhygienic vendors; check expiry dates", "Drink safe water"],
        "treatment": "Small frequent sips of ORS and water, rest, and light food as tolerated are the main care. A doctor decides if medicine or hospital fluids are needed. Avoid anti-diarrhoeal medicines without advice, especially in children.",
        "when_to_visit": ["Symptoms beyond 2–3 days", "High fever with diarrhoea", "Blood in stool or vomit", "Illness in pregnancy, infants, or older adults"],
        "emergency": ["Signs of dehydration or fainting", "Severe stomach pain or swelling", "Breathing difficulty or confusion"],
        "high_risk": ["Young children", "Pregnant people", "Older adults", "People with weak immunity or long-standing disease"],
    },
    {
        "slug": "amoebiasis",
        "name": "Amoebiasis",
        "category": "Waterborne Diseases",
        "short": "A parasitic gut infection causing dysentery-like diarrhoea with cramps.",
        "overview": "Amoebiasis is an infection of the intestines by the parasite Entamoeba histolytica. It can cause mild diarrhoea or dysentery with blood and mucus. Rarely, it forms a liver abscess needing hospital care.",
        "causes": ["Entamoeba histolytica parasite in contaminated water or food", "Poor sanitation and unsafe vegetable washing"],
        "spreads": "Spreads through food or water contaminated with stool containing the parasite. It does not spread through air.",
        "symptoms": ["Loose stools with blood or mucus (dysentery)", "Stomach cramps and urge to pass stool frequently", "Low fever and tiredness", "Liver-area pain and fever if abscess forms (rare)"],
        "prevention": ["Drink safe water; wash raw vegetables thoroughly", "Handwashing and safe disposal of stool", "Avoid untreated water while travelling", "Peel fruits and eat freshly cooked food"],
        "treatment": "A doctor confirms the cause with stool tests and prescribes the appropriate course; different stages need different medicines, so self-treatment is unsafe. Complete the full course and return if fever or pain persists.",
        "when_to_visit": ["Blood or mucus in stool", "Diarrhoea beyond 2 days or with fever", "Severe cramps or weight loss", "Pain in the upper right abdomen with fever"],
        "emergency": ["Heavy bleeding in stool", "Severe dehydration", "High fever with severe abdominal pain"],
        "high_risk": ["Young children", "Pregnant people", "People with weak immunity", "People in areas with poor sanitation"],
    },
    {
        "slug": "leptospirosis",
        "name": "Leptospirosis",
        "category": "Waterborne Diseases",
        "short": "A bacterial infection from water or soil contaminated with animal urine.",
        "overview": "Leptospirosis is a bacterial infection caught from water, mud, or soil contaminated with urine of infected animals, especially rats. It is common during monsoon floods and among sewage workers, farmers, and miners. Early treatment prevents kidney and liver damage.",
        "causes": ["Leptospira bacteria", "Contact of cuts or eyes, nose, mouth with floodwater, drains, or wet soil"],
        "spreads": "Enters through skin cuts or mucous membranes from contaminated water or soil. It does not spread from person to person in ordinary contact.",
        "symptoms": ["Sudden fever with severe headache and muscle pain (especially calves)", "Red eyes, nausea, vomiting", "Jaundice or reduced urine in severe cases", "Rash in some cases"],
        "prevention": ["Avoid wading in floodwater; wear boots and gloves for drain or farm work", "Cover cuts with waterproof bandage; wash after exposure", "Control rats and keep surroundings clean", "Preventive medicine only when prescribed for high-risk exposure"],
        "treatment": "A doctor confirms with blood tests and starts the appropriate antibiotics early; timing and choice depend on severity. Severe cases need hospital monitoring of kidneys and liver. Do not delay care waiting for fever to settle on its own.",
        "when_to_visit": ["Fever with muscle pain after floodwater or drain exposure", "Jaundice or reduced urine with fever", "Red eyes with fever during monsoon", "Animal handlers with unexplained fever"],
        "emergency": ["Very little or no urine", "Breathing difficulty or coughing blood", "Confusion or fainting with jaundice"],
        "high_risk": ["Sewage and sanitation workers", "Farmers and miners", "People in flood-affected areas", "Sewage-adjacent slum residents"],
    },
    # ---------------- Respiratory Diseases (4) ----------------
    {
        "slug": "asthma",
        "name": "Asthma",
        "category": "Respiratory Diseases",
        "short": "A long-term airway condition with wheezing and breathlessness, controlled by inhalers.",
        "overview": "Asthma is a long-term condition in which the airways become narrow and swollen, causing wheezing, cough, and breathlessness. Symptoms come and go, often worse at night, with dust, smoke, or colds. With correct inhaler use and follow-up, most people lead normal active lives.",
        "causes": ["Sensitive airways reacting to dust, pollen, smoke, pets, or cold air", "Family tendency, allergies, and repeated viral infections in childhood"],
        "spreads": "Asthma does not spread from person to person. It is not an infection, though infections can trigger attacks.",
        "symptoms": ["Wheezing (whistling sound while breathing out)", "Shortness of breath, tightness in chest", "Dry cough, worse at night or early morning", "Difficulty in speaking full sentences during severe attacks"],
        "prevention": ["Avoid smoke, dust, strong smells, and known triggers", "Keep home dust-free; wash bedding regularly", "Take flu and other vaccines as advised; treat colds early", "Learn correct inhaler technique and keep an action plan from the doctor"],
        "treatment": "Treatment uses inhaled medicines for daily control and quick relief, chosen and adjusted by a doctor. Spacer devices, regular follow-up, and peak-flow monitoring may be advised. Never stop controller inhalers when feeling well without medical advice.",
        "when_to_visit": ["Wheezing or cough beyond a few days", "Needing reliever inhaler more often than advised", "Night-time cough disturbing sleep", "Exercise causing regular breathlessness"],
        "emergency": ["Severe breathlessness, inability to speak full sentences", "Lips or nails turning blue", "Reliever inhaler not helping", "Extreme drowsiness or fainting"],
        "high_risk": ["Young children", "Older adults", "People with allergies", "People exposed to smoke or air pollution"],
    },
    {
        "slug": "pneumonia",
        "name": "Pneumonia",
        "category": "Respiratory Diseases",
        "short": "A lung infection with fever, cough, and fast breathing — dangerous for children and elders.",
        "overview": "Pneumonia is an infection that fills the air sacs of the lungs with fluid or pus. It causes fever, cough, and breathing difficulty. Children under five and older adults face the highest risk, but early treatment cures most cases.",
        "causes": ["Bacteria, viruses, or fungi infecting the lungs", "Weak immunity, smoking, and poor nutrition increase risk"],
        "spreads": "Some types spread through droplets from coughs and sneezes. Good hygiene and vaccination reduce spread.",
        "symptoms": ["Fever with cough producing phlegm", "Fast or difficult breathing, chest pain on breathing", "Tiredness and loss of appetite", "In infants: poor feeding, fast breathing, chest indrawing"],
        "prevention": ["Pneumococcal, Hib, flu, and COVID vaccines as per schedule", "Exclusive breastfeeding; good nutrition", "Avoid smoke and indoor air pollution", "Handwashing and prompt care of colds"],
        "treatment": "A doctor decides treatment after examination and sometimes chest X-ray or blood tests; bacterial cases need prescription medicines while viral cases need supportive care. Home care includes rest, fluids, and fever management; hospital oxygen is needed for breathing difficulty or low oxygen.",
        "when_to_visit": ["Fever with cough and fast breathing", "Chest pain while breathing", "Child with poor feeding or noisy breathing", "No improvement in 2–3 days"],
        "emergency": ["Severe breathing difficulty or bluish lips", "Confusion or extreme drowsiness", "Chest indrawing in a child", "Dehydration with inability to drink"],
        "high_risk": ["Children under 5", "Adults above 65", "People with weak immunity, smoking, or long-standing disease", "Malnourished children"],
    },
    {
        "slug": "copd",
        "name": "COPD (Chronic Lung Disease)",
        "category": "Respiratory Diseases",
        "short": "Long-term lung damage from smoke causing daily breathlessness and cough.",
        "overview": "COPD (Chronic Obstructive Pulmonary Disease) is long-term damage to the airways and lungs, usually from years of smoking or indoor smoke (chulha) exposure. Breathlessness slowly increases and flare-ups need urgent care. Stopping smoke exposure and regular treatment slow the decline.",
        "causes": ["Long-term smoking, including beedis", "Indoor smoke from biomass cooking fuels and air pollution", "Repeated chest infections and occupational dust"],
        "spreads": "COPD does not spread from person to person.",
        "symptoms": ["Daily breathlessness, worse on exertion", "Chronic cough with phlegm", "Wheezing and chest tightness", "Frequent chest infections and tiredness"],
        "prevention": ["Stop smoking completely; avoid second-hand smoke", "Use clean cooking fuel and ventilated kitchens", "Annual flu and pneumococcal vaccines as advised", "Pulmonary rehabilitation exercises and breathing training"],
        "treatment": "Inhaled medicines, oxygen assessment, and exercise programmes are planned by a doctor. Flare-ups may need short hospital care. Long-term oxygen or surgery is decided only by specialists; never adjust inhalers or oxygen on your own.",
        "when_to_visit": ["Daily cough or breathlessness beyond weeks", "Increasing sputum or change in its colour", "Frequent need for reliever medicine", "Weight loss with chronic lung symptoms"],
        "emergency": ["Sudden severe breathlessness not relieved by inhaler", "Bluish lips, confusion, or fainting", "High fever with breathing difficulty (possible severe infection)"],
        "high_risk": ["Long-term smokers", "Women exposed to indoor smoke", "Workers in dusty industries", "Older adults with repeated infections"],
    },
    {
        "slug": "bronchitis",
        "name": "Bronchitis",
        "category": "Respiratory Diseases",
        "short": "Inflamed airways causing persistent cough with mucus after colds or smoke exposure.",
        "overview": "Bronchitis is inflammation of the large airways (bronchi), causing cough with mucus. Acute bronchitis often follows a cold and settles in weeks; chronic bronchitis lasts months and overlaps with COPD. Most acute cases recover without antibiotics.",
        "causes": ["Viral infections following a cold or flu", "Smoking, dust, and air pollution (chronic cases)"],
        "spreads": "Acute infectious bronchitis can spread through cough droplets. Chronic bronchitis itself is not contagious.",
        "symptoms": ["Persistent cough with clear, yellow, or green mucus", "Mild fever, sore throat, and tiredness", "Wheezing or chest discomfort", "Breathlessness in severe or chronic cases"],
        "prevention": ["Avoid smoking and dusty, smoky environments", "Treat colds early; wash hands", "Flu vaccination as advised", "Wear a mask in dusty workplaces"],
        "treatment": "Acute cases are managed with rest, fluids, and symptom relief as advised; antibiotics are used only if a doctor finds a bacterial infection. Chronic cases need long-term inhaler and lifestyle plans with follow-up.",
        "when_to_visit": ["Cough beyond 3 weeks", "Blood in mucus", "Repeated episodes through the year", "Breathlessness or wheezing"],
        "emergency": ["Severe breathing difficulty", "High fever with chest pain", "Coughing large amounts of blood"],
        "high_risk": ["Smokers", "Children in smoky homes", "Older adults", "People with asthma or COPD"],
    },
    # ---------------- Non-Communicable Diseases (9) ----------------
    {
        "slug": "diabetes",
        "name": "Diabetes (High Blood Sugar)",
        "category": "Non-Communicable Diseases",
        "short": "High blood sugar from insulin problems; controlled by lifestyle and medicines.",
        "overview": "Diabetes is a condition in which blood sugar stays higher than normal because the body makes too little insulin or cannot use it well. Over years, uncontrolled sugar damages eyes, kidneys, nerves, and heart. With diet, activity, medicines, and regular checks, complications can be prevented.",
        "causes": ["Type 1: body stops making insulin (needs lifelong insulin)", "Type 2: body resists insulin, linked to excess weight, inactivity, and family history", "Gestational: high sugar first found in pregnancy"],
        "spreads": "Diabetes does not spread from person to person.",
        "symptoms": ["Increased thirst and frequent urination, especially at night", "Tiredness, increased hunger, slow wound healing", "Blurred vision, tingling in feet", "Many people have no early symptoms"],
        "prevention": ["Maintain healthy weight with daily activity (at least 30 minutes brisk walking most days)", "Eat whole grains, vegetables, and controlled portions; limit sweets and sugary drinks", "Avoid tobacco and limit alcohol", "Screen blood sugar yearly after 30, earlier with family history"],
        "treatment": "A doctor sets sugar targets and prescribes tablets or insulin along with diet and exercise plans. Regular sugar, HbA1c, eye, foot, and kidney checks are needed. Never start, stop, or change doses without advice; low sugar can be dangerous and needs prompt sweet intake and medical guidance.",
        "when_to_visit": ["Classic symptoms above or high random sugar", "Non-healing wounds or repeated infections", "Pregnancy with high sugar", "Numbness or vision changes"],
        "emergency": ["Very high sugar with vomiting, stomach pain, deep breathing, or fruity breath", "Fainting, fits, or heavy sweating with confusion (possible low sugar)", "Foot wound with spreading redness and fever"],
        "high_risk": ["People with family history", "People with excess weight", "Women with gestational diabetes history", "People with high blood pressure or cholesterol"],
    },
    {
        "slug": "hypertension",
        "name": "Hypertension (High Blood Pressure)",
        "category": "Non-Communicable Diseases",
        "short": "Often silent high pressure that strains heart, brain, and kidneys; needs regular checks.",
        "overview": "Hypertension means blood pressure stays above healthy limits. It usually has no symptoms but silently damages the heart, brain, kidneys, and eyes. Regular measurement, salt control, activity, and medicines keep it in range.",
        "causes": ["Excess salt, excess weight, inactivity, tobacco, alcohol, and stress", "Family history, older age, kidney or thyroid disease in some cases"],
        "spreads": "Hypertension does not spread from person to person.",
        "symptoms": ["Usually no symptoms; found on routine checking", "Severe headache, nosebleeds, or breathlessness when very high", "Chest discomfort or vision problems in crises"],
        "prevention": ["Less than 5 g salt per day; avoid pickles, papads, and packaged snacks excess", "Daily physical activity and healthy weight", "No tobacco; limit alcohol; manage stress and sleep", "Check BP at least yearly after 30"],
        "treatment": "A doctor confirms with repeated readings and prescribes medicines that must be taken daily even when feeling well. Home BP monitoring, low-salt diet, and follow-up visits are part of care. Never stop BP medicines suddenly.",
        "when_to_visit": ["Repeated readings at or above 140/90", "Headache with high readings", "Pregnancy with swelling and high BP", "Existing patient with uncontrolled readings"],
        "emergency": ["BP very high with chest pain, breathlessness, or weakness on one side", "Sudden vision loss, fits, or confusion", "Severe headache with vomiting"],
        "high_risk": ["Older adults", "People with diabetes, kidney disease, or obesity", "Pregnant people", "Tobacco and heavy alcohol users"],
    },
    {
        "slug": "stroke",
        "name": "Stroke (Brain Attack)",
        "category": "Non-Communicable Diseases",
        "short": "Sudden brain damage from blocked or burst vessels — every minute counts (FAST).",
        "overview": "A stroke happens when blood supply to part of the brain is blocked or a vessel bursts, damaging brain cells within minutes. It causes sudden weakness, speech trouble, or face drooping. Immediate hospital care can save life and reduce disability.",
        "causes": ["Blocked brain artery by a clot (ischemic stroke, most common)", "Burst brain vessel (haemorrhagic stroke)", "High BP, diabetes, smoking, irregular heartbeat, and high cholesterol raise risk"],
        "spreads": "Stroke does not spread from person to person.",
        "symptoms": ["FAST: Face drooping, Arm weakness, Speech difficulty — Time to call emergency", "Sudden numbness on one side", "Sudden vision trouble, dizziness, or severe headache"],
        "prevention": ["Control BP, sugar, and cholesterol; take prescribed medicines", "No tobacco; limit alcohol; active lifestyle and healthy diet", "Treat irregular heartbeat as advised", "Regular check-ups after 40"],
        "treatment": "Stroke is always a hospital emergency; clot treatment must start within a few hours, decided by brain scans. Later care includes medicines, physiotherapy, speech therapy, and prevention of the next stroke. Do not give food, water, or aspirin at home before medical assessment.",
        "when_to_visit": ["Any FAST symptom — go to emergency immediately, note the time of onset", "Transient weakness or speech trouble that recovers (mini-stroke needs same-day care)", "Sudden severe headache unlike before"],
        "emergency": ["Any FAST sign", "Fits, unconsciousness, or repeated vomiting with headache", "Sudden one-side paralysis"],
        "high_risk": ["People with high BP, diabetes, or heart rhythm problems", "Smokers", "Older adults", "People with previous stroke or heart disease"],
    },
    {
        "slug": "cancer",
        "name": "Cancer",
        "category": "Non-Communicable Diseases",
        "short": "Abnormal cell growth needing early detection and specialist treatment.",
        "overview": "Cancer is a group of diseases in which abnormal cells grow uncontrollably and can spread to other parts. Common cancers in India include oral, breast, cervical, and lung cancers. Early detection through screening greatly improves cure chances.",
        "causes": ["Tobacco (smoked and smokeless), alcohol, and areca nut", "Infections such as HPV and hepatitis in some cancers", "Family history, pollution, and unhealthy lifestyle in others"],
        "spreads": "Cancer does not spread from person to person by contact. It spreads within the body from the original site if untreated.",
        "symptoms": ["Non-healing mouth ulcer or white/red patch, lump in breast or neck", "Unexplained weight loss, long fever, or tiredness", "Abnormal bleeding, change in bowel or bladder habits", "Persistent cough or hoarseness"],
        "prevention": ["Avoid all tobacco and limit alcohol", "HPV and hepatitis B vaccination as advised; cervical and breast screening", "Eat vegetables and fruits; maintain healthy weight; stay active", "Oral self-checks and prompt reporting of lumps or ulcers beyond 2–3 weeks"],
        "treatment": "Treatment (surgery, medicines, or radiation, alone or combined) is planned by cancer specialists based on type and stage. Early stages are often curable; do not delay care for alternative-only treatments. Pain relief, nutrition, and counselling are part of complete care.",
        "when_to_visit": ["Ulcer or patch in mouth beyond 2–3 weeks", "New lump anywhere, especially breast or neck", "Abnormal vaginal bleeding or persistent cough", "Unexplained weight loss or long fever"],
        "emergency": ["Heavy uncontrolled bleeding", "Severe breathing difficulty", "Sudden severe pain or fracture with minor injury (possible spread, needs urgent review)", "Confusion with very low blood counts during treatment (seek oncology emergency advice)"],
        "high_risk": ["Tobacco and alcohol users", "People with family history of cancer", "People with HPV or hepatitis infection", "Workers exposed to asbestos, dust, or chemicals"],
    },
    {
        "slug": "chronic-kidney-disease",
        "name": "Chronic Kidney Disease",
        "category": "Non-Communicable Diseases",
        "short": "Slow kidney damage, often from diabetes or BP; early tests protect the kidneys.",
        "overview": "Chronic kidney disease (CKD) is slow, lasting damage to the kidneys that reduces their ability to clean blood. Diabetes and high BP are the leading causes. Early stages have no symptoms and are found only by urine and blood tests.",
        "causes": ["Long-standing diabetes and high blood pressure", "Repeated kidney infections, stones, or harmful medicines", "Family kidney disease in some cases"],
        "spreads": "Kidney disease does not spread from person to person.",
        "symptoms": ["Often none in early stages", "Swelling of feet or face, tiredness", "Reduced or foamy urine, waking to pass urine", "Nausea, itching, and breathlessness in advanced stages"],
        "prevention": ["Control sugar and BP strictly; take medicines regularly", "Avoid painkillers and unknown herbal powders without advice", "Drink adequate water; limit salt and processed food", "Yearly urine and creatinine tests if diabetic or hypertensive"],
        "treatment": "A doctor stages CKD with tests and plans diet, medicines, and cause control; dialysis or transplant is needed only in the last stage, decided by kidney specialists. Avoid nephrotoxic drugs and follow fluid and diet advice strictly.",
        "when_to_visit": ["Swelling, foamy urine, or high BP", "Diabetes with abnormal kidney test", "Repeated urinary infections or stones", "Family history with symptoms"],
        "emergency": ["Very little urine with swelling and breathlessness", "Severe weakness with vomiting", "Chest pain or fits with kidney failure"],
        "high_risk": ["People with diabetes or hypertension", "Older adults", "People with heart disease", "People using long-term painkillers"],
    },
    {
        "slug": "chronic-liver-disease",
        "name": "Chronic Liver Disease",
        "category": "Non-Communicable Diseases",
        "short": "Long-term liver scarring from alcohol, hepatitis, or fatty liver; early care reverses damage.",
        "overview": "Chronic liver disease is long-term liver injury leading to scarring (fibrosis and cirrhosis). Alcohol, hepatitis B and C, and fatty liver are common causes in India. Early stages can improve with cause treatment; late stages need specialist care.",
        "causes": ["Heavy alcohol use", "Chronic hepatitis B or C", "Non-alcoholic fatty liver linked to obesity and diabetes"],
        "spreads": "The liver damage itself is not contagious, though hepatitis viruses that cause it can spread as described under Hepatitis.",
        "symptoms": ["Tiredness and loss of appetite in early stages", "Yellow eyes, dark urine, and itching", "Swelling of abdomen or feet, vomiting blood in advanced stages", "Easy bruising"],
        "prevention": ["Avoid alcohol completely once liver disease is found; limit it otherwise", "Hepatitis B vaccination; safe blood and needles", "Healthy weight, exercise, and sugar control", "Avoid self-medication and unknown herbal products"],
        "treatment": "A liver specialist finds the cause with scans and blood tests and treats it (for example, hepatitis medicines, alcohol de-addiction support, diabetes and weight control). Advanced cases need hospital care for complications; transplant is considered only in selected cases.",
        "when_to_visit": ["Jaundice, long tiredness, or abnormal liver tests", "Alcohol use with liver symptoms", "Hepatitis positive status", "Swelling of abdomen or feet"],
        "emergency": ["Vomiting blood or black stools", "Sudden confusion or extreme sleepiness", "Severe abdominal pain with fever"],
        "high_risk": ["People with heavy alcohol use", "People with hepatitis B or C", "People with obesity and diabetes", "People on long-term liver-harming medicines"],
    },
    {
        "slug": "epilepsy",
        "name": "Epilepsy (Seizure Disorder)",
        "category": "Non-Communicable Diseases",
        "short": "Repeated seizures from abnormal brain activity; medicines control most cases.",
        "overview": "Epilepsy is a brain condition causing repeated seizures (fits). Seizures vary from brief staring to full-body shaking with unconsciousness. With regular medicines and precautions, most people with epilepsy live full, active lives.",
        "causes": ["Abnormal electrical activity from brain injury, infection, stroke, or birth conditions", "Often no single cause is found; it is not caused by spirits or past deeds"],
        "spreads": "Epilepsy does not spread from person to person.",
        "symptoms": ["Sudden shaking of arms and legs with loss of consciousness", "Blank staring or repeated blinking", "Sudden confusion or unusual behaviour", "Tongue bite or bed-wetting during an episode"],
        "prevention": ["Take medicines daily without missing doses; ensure adequate sleep", "Avoid flashing triggers, alcohol, and missed meals if sensitive", "Prevent head injury with helmets; treat brain infections early", "Supervise swimming and heights"],
        "treatment": "Anti-seizure medicines prescribed by a doctor control fits in most people; the drug and dose are individual and need regular review. Never stop medicines suddenly. During a fit, keep the person safe on their side, do not put anything in the mouth, and note the duration.",
        "when_to_visit": ["First-ever fit", "Increasing frequency of fits", "Side effects of medicines", "Planning pregnancy with epilepsy"],
        "emergency": ["Fit lasting more than 5 minutes", "Repeated fits without regaining consciousness", "Breathing difficulty or injury during a fit", "Fit in water or during pregnancy"],
        "high_risk": ["Children with birth injury or brain infection history", "Older adults after stroke", "People missing medicines or sleep", "People with head injury"],
    },
    {
        "slug": "arthritis",
        "name": "Arthritis (Joint Inflammation)",
        "category": "Non-Communicable Diseases",
        "short": "Painful, stiff joints from wear or inflammation; movement and weight control help.",
        "overview": "Arthritis means inflammation of joints, causing pain, stiffness, and swelling. Osteoarthritis (wear with age) and rheumatoid arthritis (immune attack) are common types. Exercise, weight control, and timely treatment protect joint function.",
        "causes": ["Age-related wear of cartilage (osteoarthritis)", "Immune system attacking joints (rheumatoid arthritis)", "Excess weight, joint injury, and family history"],
        "spreads": "Arthritis does not spread from person to person.",
        "symptoms": ["Joint pain and stiffness, worse in the morning or after rest", "Swelling and warmth over joints", "Reduced movement and cracking sounds", "Tiredness and low fever in inflammatory types"],
        "prevention": ["Maintain healthy weight; strengthen muscles with walking and physiotherapy", "Avoid prolonged squatting and sitting cross-legged on the floor", "Protect joints from injury; wear supportive footwear", "Treat joint infections early"],
        "treatment": "A doctor identifies the type with examination and tests and plans pain relief, disease-controlling medicines (for inflammatory types), physiotherapy, and sometimes injections or surgery. Hot or cold packs, gentle exercise, and assistive devices ease daily life.",
        "when_to_visit": ["Joint pain beyond a few weeks", "Morning stiffness beyond 30 minutes", "Swollen, red, or warm joints", "Difficulty walking or using hands"],
        "emergency": ["Sudden single-joint severe pain with fever (possible infection — urgent)", "Joint injury with deformity", "Sudden inability to move a joint"],
        "high_risk": ["Older adults", "People with excess weight", "People with family history of rheumatoid arthritis", "Sportspersons with joint injuries"],
    },
    {
        "slug": "thyroid-disorders",
        "name": "Thyroid Disorders",
        "category": "Non-Communicable Diseases",
        "short": "Under- or over-active thyroid affecting weight, energy, and heart rate.",
        "overview": "The thyroid gland controls body metabolism. Too little hormone (hypothyroidism) slows the body; too much (hyperthyroidism) speeds it up. Iodine deficiency, autoimmunity, and other causes affect the gland. Simple blood tests detect problems and daily medicine corrects them.",
        "causes": ["Autoimmune attack (Hashimoto's or Graves' disease)", "Iodine deficiency or excess, thyroid nodules", "After pregnancy, surgery, or radiation in some cases"],
        "spreads": "Thyroid disorders do not spread from person to person.",
        "symptoms": ["Underactive: weight gain, tiredness, constipation, feeling cold, dry skin", "Overactive: weight loss, trembling, fast heartbeat, heat intolerance, anxiety", "Neck swelling (goitre) in some cases"],
        "prevention": ["Use iodised salt as per national guidance", "Do not start or stop thyroid medicines without testing", "Screening in pregnancy and newborns as advised", "Regular follow-up blood tests"],
        "treatment": "Underactive thyroid is treated with daily hormone replacement; overactive thyroid has several options decided by specialists. Dose is adjusted by blood tests and must be taken as directed, usually on an empty stomach.",
        "when_to_visit": ["Unexplained weight or energy changes", "Neck swelling", "Pregnancy or planning pregnancy with thyroid history", "Fast or very slow heartbeat with tremor or tiredness"],
        "emergency": ["Very low body temperature with extreme drowsiness (severe underactive crisis — rare)", "High fever with fast heartbeat, agitation, and confusion (thyroid storm — rare emergency)"],
        "high_risk": ["Women, especially after pregnancy", "People with family history", "People with other autoimmune diseases", "Newborns of mothers with thyroid disease"],
    },
    # ---------------- Nutritional Diseases (3) ----------------
    {
        "slug": "iron-deficiency-anaemia",
        "name": "Iron-Deficiency Anaemia",
        "category": "Nutritional Diseases",
        "short": "Low iron causing tiredness and paleness; common in women and children.",
        "overview": "Anaemia means low haemoglobin, the substance that carries oxygen in blood. Iron deficiency from poor diet, blood loss, or repeated pregnancies is the most common cause in India. It causes tiredness and reduces learning and work capacity, but improves with diet and supplements.",
        "causes": ["Diet low in iron, especially with frequent tea or coffee with meals", "Blood loss from heavy periods, frequent childbirth, or worms", "Poor absorption in some gut conditions"],
        "spreads": "Anaemia does not spread from person to person.",
        "symptoms": ["Tiredness, weakness, and pale skin or nails", "Breathlessness on mild work, dizziness", "Brittle nails, hair fall, craving for clay or chalk (pica)", "Poor concentration in children"],
        "prevention": ["Eat iron-rich foods: millets, green leafy vegetables, groundnuts, jaggery, eggs, and meat where eaten", "Take vitamin C foods (lemon, amla, guava) with meals to absorb iron", "Deworming and weekly iron-folic acid as per Anaemia Mukt Bharat guidance", "Space pregnancies and treat heavy periods"],
        "treatment": "A doctor confirms anaemia with a haemoglobin test and prescribes iron-folic acid dose and duration; severe cases may need further tests or hospital care. Take iron as directed (often with vitamin C, away from tea), and complete the course even after feeling better.",
        "when_to_visit": ["Persistent tiredness or paleness", "Pregnancy (early screening essential)", "Heavy periods or black stools", "Child with poor growth or learning"],
        "emergency": ["Severe breathlessness or chest pain with paleness", "Fainting", "Heavy bleeding with weakness"],
        "high_risk": ["Adolescent girls and women of childbearing age", "Pregnant people", "Young children", "People with worm infection or poor diet"],
    },
    {
        "slug": "vitamin-d-deficiency",
        "name": "Vitamin D Deficiency",
        "category": "Nutritional Diseases",
        "short": "Low sunshine vitamin causing bone pain, weakness, and frequent illness.",
        "overview": "Vitamin D helps absorb calcium for strong bones and supports immunity. Indoor lifestyle, covered clothing, darker skin needing more sun, and low dietary intake make deficiency very common in India. It causes bone and muscle pain and raises fall and fracture risk.",
        "causes": ["Very little direct sunlight exposure", "Diet low in vitamin D and calcium", "Kidney, liver, or gut diseases reducing absorption"],
        "spreads": "Vitamin D deficiency does not spread from person to person.",
        "symptoms": ["Bone pain, backache, and muscle weakness", "Tiredness and leg cramps", "Delayed walking or bowed legs in severe childhood cases (rickets)", "Frequent fractures with minor falls"],
        "prevention": ["Safe midday sun exposure of arms and face for 15–30 minutes several times a week", "Foods with calcium and vitamin D: milk, ragi, sesame, eggs, and fish where eaten", "Supplements only as advised after testing or medical review", "Treat underlying gut or kidney disease"],
        "treatment": "A doctor checks blood levels when needed and prescribes the correct supplement dose and duration; both deficiency and excess are harmful, so self-dosing is unsafe. Calcium, exercise, and diet support recovery.",
        "when_to_visit": ["Persistent bone or muscle pain", "Child with delayed milestones or bowed legs", "Repeated fractures", "Long indoor confinement with symptoms"],
        "emergency": ["Sudden fracture with minor injury", "Severe muscle spasms or fits with low calcium (rare — urgent)"],
        "high_risk": ["Older adults, especially homebound", "Pregnant and breastfeeding people", "Children with poor sun exposure", "People with kidney, liver, or gut disease"],
    },
    {
        "slug": "iodine-deficiency",
        "name": "Iodine Deficiency Disorders",
        "category": "Nutritional Diseases",
        "short": "Low iodine causing goitre and affecting child brain development.",
        "overview": "Iodine is needed to make thyroid hormones. Deficiency causes neck swelling (goitre) and, in pregnancy and childhood, can harm brain development. Use of adequately iodised salt has greatly reduced this problem in India.",
        "causes": ["Diet low in iodine, especially in mountain and flood-prone regions", "Use of non-iodised salt"],
        "spreads": "Iodine deficiency does not spread from person to person.",
        "symptoms": ["Swelling in front of the neck (goitre)", "Tiredness and weight gain with low thyroid", "Poor school performance in children with long deficiency", "Pregnancy complications in severe cases"],
        "prevention": ["Use adequately iodised salt for daily cooking; store it covered and away from heat", "Antenatal check-ups and thyroid screening as advised", "Balanced diet; avoid self-medicating with iodine drops"],
        "treatment": "A doctor evaluates neck swelling and thyroid levels; most cases need iodised salt correction and thyroid medicines when hormones are abnormal. Large goitres or nodules may need scan or specialist review.",
        "when_to_visit": ["Visible neck swelling", "Pregnancy in an iodine-deficient area", "Child with poor growth or learning", "Abnormal thyroid test"],
        "emergency": ["Neck swelling with breathing or swallowing difficulty", "Sudden painful thyroid swelling with fever"],
        "high_risk": ["Pregnant people", "Young children", "People in Himalayan and north-eastern regions", "Families using non-iodised salt"],
    },
    # ---------------- Lifestyle Diseases (3) ----------------
    {
        "slug": "obesity",
        "name": "Obesity",
        "category": "Lifestyle Diseases",
        "short": "Excess body weight that raises risk of diabetes, BP, and joint problems.",
        "overview": "Obesity means excess body fat that harms health. It develops when energy intake regularly exceeds activity, influenced by diet, inactivity, sleep, stress, and family tendency. It raises the risk of diabetes, hypertension, heart disease, and joint pain, but steady lifestyle change reverses it.",
        "causes": ["Frequent fried food, sweets, sugary drinks, and large portions", "Little physical activity, long sitting, poor sleep", "Some medicines and hormonal conditions (need medical evaluation)"],
        "spreads": "Obesity does not spread from person to person.",
        "symptoms": ["Increasing weight and waist size", "Breathlessness on mild exertion, joint pain", "Snoring, daytime sleepiness", "Often no symptoms until complications appear"],
        "prevention": ["Daily 30–60 minutes of brisk walking or equivalent activity", "Balanced thali: half vegetables, controlled rice/roti, protein, and limited oil and sugar", "Regular sleep, limited screen time, and stress management", "Yearly weight, BP, and sugar checks"],
        "treatment": "A doctor sets a realistic weight target and checks for causes and complications; dietitian guidance, activity plans, and behaviour support are the base. Medicines or surgery are considered only for selected cases by specialists, never as first or solo steps.",
        "when_to_visit": ["Steady weight gain despite efforts", "Obesity with diabetes, BP, or joint pain", "Childhood obesity", "Breathing difficulty or snoring with daytime sleepiness"],
        "emergency": ["Chest pain or severe breathlessness", "Signs of very high sugar or BP"],
        "high_risk": ["People with sedentary jobs", "Children with sugary diets and low activity", "Women with PCOS or post-pregnancy weight retention", "People on long-term steroids or certain medicines"],
    },
    {
        "slug": "fatty-liver-disease",
        "name": "Fatty Liver Disease",
        "category": "Lifestyle Diseases",
        "short": "Extra fat in the liver from weight, sugar, or alcohol; reversible in early stages.",
        "overview": "Fatty liver means extra fat stored in liver cells. Non-alcoholic fatty liver is linked to obesity, diabetes, and high cholesterol; alcohol also causes it. Early stages have no symptoms and improve with weight loss and sugar control; advanced stages scar the liver.",
        "causes": ["Excess weight, diabetes, and high triglycerides", "Heavy alcohol use", "Rapid weight-loss crash diets and some medicines in some cases"],
        "spreads": "Fatty liver does not spread from person to person.",
        "symptoms": ["Usually no symptoms; found on ultrasound or blood tests", "Mild pain in the upper right abdomen", "Tiredness", "Yellow eyes or swelling only in advanced disease"],
        "prevention": ["Maintain healthy weight; lose weight gradually (0.5 kg per week)", "Control sugar and cholesterol; avoid alcohol", "Daily activity and balanced diet low in sugar and refined oil", "Avoid self-medication with liver tonics"],
        "treatment": "No single tablet cures fatty liver; a doctor treats the causes (weight, sugar, cholesterol, alcohol) with diet, activity, and medicines where needed. Follow-up scans and blood tests track improvement.",
        "when_to_visit": ["Abnormal liver test or fatty liver on scan", "Obesity or diabetes with tiredness or abdominal discomfort", "Alcohol use with liver symptoms"],
        "emergency": ["Vomiting blood or black stools", "Sudden confusion with jaundice", "Severe abdominal swelling"],
        "high_risk": ["People with obesity", "People with diabetes or high triglycerides", "People with heavy alcohol use", "People with rapid weight gain"],
    },
    {
        "slug": "cardiovascular-diseases",
        "name": "Cardiovascular Diseases (Heart & Vessels)",
        "category": "Lifestyle Diseases",
        "short": "Heart attack and related vessel diseases — largely preventable by healthy habits.",
        "overview": "Cardiovascular diseases affect the heart and blood vessels, including coronary heart disease (heart attack), heart failure, and related vessel blockages. Blocked heart arteries cause chest pain or heart attack. Healthy lifestyle, BP, sugar, and cholesterol control prevent most cases.",
        "causes": ["Cholesterol deposits narrowing heart arteries over years", "Tobacco, high BP, diabetes, obesity, inactivity, and family history", "Heavy alcohol and chronic stress add to risk"],
        "spreads": "Cardiovascular diseases do not spread from person to person.",
        "symptoms": ["Chest pain, pressure, or heaviness, sometimes spreading to arm, neck, or jaw", "Breathlessness, sweating, nausea during an attack", "Palpitations or swelling of feet in heart weakness", "Many have no warning until an event — hence regular checks matter"],
        "prevention": ["No tobacco in any form; limit alcohol and salt", "30 minutes of brisk activity most days; healthy weight", "Yearly BP, sugar, and cholesterol checks after 30", "Heart-healthy diet: vegetables, whole grains, limited fried food and sweets"],
        "treatment": "Stable disease is managed with lifestyle plus medicines prescribed by a doctor; procedures (stent or bypass) are decided by heart specialists based on tests. A heart attack is an emergency needing immediate hospital care — do not drive yourself; call emergency services.",
        "when_to_visit": ["Chest discomfort, even mild or on exertion", "Breathlessness, palpitations, or ankle swelling", "High BP, diabetes, or cholesterol needing heart-risk review", "Family history of early heart attack"],
        "emergency": ["Chest pain lasting more than a few minutes, or with sweating, nausea, or breathlessness", "Pain spreading to arm, neck, or jaw", "Fainting or fits with chest symptoms", "Sudden severe breathlessness with frothy cough"],
        "high_risk": ["People with diabetes, hypertension, or high cholesterol", "Smokers and tobacco chewers", "People with family history of early heart attack", "People with obesity and sedentary lifestyle"],
    },
]

DISEASE_MAP = {d["slug"]: d for d in DISEASES}


def get_disease(slug):
    return DISEASE_MAP.get(slug)


def search_diseases(query="", category=""):
    q = (query or "").strip().lower()
    out = []
    for d in DISEASES:
        if category and d["category"] != category:
            continue
        if q:
            hay = " ".join([
                d["name"], d["category"], d["short"], d["overview"],
                d["spreads"], " ".join(d["symptoms"]),
            ]).lower()
            if q not in hay:
                continue
        out.append(d)
    return out


def alpha_index():
    letters = sorted({d["name"][0].upper() for d in DISEASES if d["name"]})
    return letters


def transmission_badge(disease):
    """Honest transmission label for a condition.

    The label describes how the condition reaches other people. It is a
    transmission route, never a severity score.

    The route comes from each entry's own "spreads" text. Matching on that
    text alone is unreliable, because most entries add a negated clause
    ("it does not spread by sharing food or mosquito bites") that used to
    make the reader pick up the wrong route. So the decision is made in
    three steps:

      1. An explicit override, for entries whose route the category default
         would misdescribe.
      2. The category default.
      3. Person-to-person for the infectious category, where the entries
         describe transmission between people.

    Returns one of: 'Non-contagious', 'Vector-borne', 'Water / food-borne',
    'Blood / water-borne' or 'Person-to-person possible'.
    """
    slug = disease.get("slug")
    category = disease.get("category") or ""

    if slug in TRANSMISSION_OVERRIDES:
        return TRANSMISSION_OVERRIDES[slug]
    if slug in NON_TRANSMISSIBLE:
        return "Non-contagious"
    if category == "Vector-Borne Diseases":
        return "Vector-borne"
    if category == "Waterborne Diseases":
        return "Water / food-borne"
    if category in ("Non-Communicable Diseases", "Nutritional Diseases",
                    "Lifestyle Diseases"):
        return "Non-contagious"
    if category == "Respiratory Diseases":
        # Pneumonia and bronchitis can be caught from other people; asthma
        # and COPD are handled above.
        return "Person-to-person possible"
    # Infectious conditions describe transmission between people.
    return "Person-to-person possible"


def has_vaccine_note(disease):
    """True when the entry's own prevention text mentions vaccination.

    Reflects library content only ('ask your doctor'); not a coverage claim.
    """
    return "vaccin" in " ".join(disease.get("prevention") or []).lower()


def category_counts():
    counts = {c: 0 for c in CATEGORIES}
    for d in DISEASES:
        counts[d["category"]] = counts.get(d["category"], 0) + 1
    return counts


def icon_for(disease):
    """Icon key for a disease, falling back to its category's icon."""
    key = DISEASE_ICONS.get(disease.get("slug"))
    if key:
        return key
    return CATEGORY_ICONS.get(disease.get("category"), "plus")


def tone_for(disease):
    """Pastel colour tone for a disease's icon badge."""
    key = DISEASE_TONES.get(disease.get("slug"))
    if key:
        return key
    return CATEGORY_TONES.get(disease.get("category"), "blue")


def short_category(disease):
    """Short, human label for a disease's category."""
    return CATEGORY_SHORT.get(disease.get("category"), disease.get("category") or "")


def popular_diseases():
    """The diseases featured in the "Popular diseases" strip.

    Order follows POPULAR_SLUGS. Any slug that is missing from the library
    is skipped, so the list stays valid as entries are added or renamed.
    """
    out = []
    for slug in POPULAR_SLUGS:
        d = DISEASE_MAP.get(slug)
        if d:
            out.append(decorate(d))
    return out


def category_cards():
    """Category metadata for the "Browse by category" grid.

    Returns one dict per category with its display name, short label, icon
    key, pastel tone and how many conditions it holds.
    """
    counts = category_counts()
    out = []
    for c in CATEGORIES:
        out.append({
            "name": c,
            "short": CATEGORY_SHORT.get(c, c),
            "icon": CATEGORY_ICONS.get(c, "plus"),
            "tone": CATEGORY_TONES.get(c, "blue"),
            "count": counts.get(c, 0),
        })
    return out


def decorate(disease):
    """Attach the template-facing extras (icon, tone, short category).

    Returns a copy, so the library data itself stays untouched.
    """
    d = dict(disease)
    d["_icon"] = icon_for(d)
    d["_tone"] = tone_for(d)
    d["_short"] = short_category(d)
    return d
