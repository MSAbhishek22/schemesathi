"""SchemeSathi core engine — SLAY HACKS 2026 (fresh build, 5 Nov 2026).

On-device, explainable eligibility matching for Indian government schemes.
No network calls, no accounts, no data leaves the machine.

Honesty note: the scheme figures below are a curated snapshot of widely
published headline criteria as of November 2026 (benefit amounts, income
caps, age windows). They are NOT an official source. Every scheme card in
the UI links to the official discovery portal (myscheme.gov.in) and tells
the user to verify the current criteria there before applying. If a figure
is wrong, the matcher is wrong in the open — the rule trace shows exactly
which rule produced each verdict, so a wrong figure is checkable, not hidden.

Design: the "AI" here is deliberately neurosymbolic, not a cloud LLM:
  1. NLP layer — parses plain English/Hinglish free text into a profile
     (age, income, gender, occupation, state, life-situation flags).
  2. Symbolic layer — a deterministic rules engine evaluates every scheme
     and returns a per-rule trace. No black box, no hallucinated verdict.
This separation (language understanding vs. eligibility decision) follows
the governed-benefits pattern: the decision is always the rules, never
generated prose.
"""

import re

# ---------------------------------------------------------------------------
# Scheme database (curated snapshot, Nov 2026 — see module docstring)
# ---------------------------------------------------------------------------
# Rule fields (all optional):
#   min_age, max_age      — inclusive age window
#   max_income            — annual family income cap in rupees (None = no cap)
#   genders               — set of accepted genders, None = any
#   occupations           — set of accepted occupations, None = any
#   requires_any          — set of flags, at least one must be present
#   requires_all          — set of flags, all must be present
#   excludes              — set of flags that disqualify
#   needs                 — profile fields that must be known to decide
#                           (unknown -> NEEDS INFO instead of a false verdict)

SCHEMES = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN Samman Nidhi",
        "name_hi": "पीएम-किसान",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "category": "Agriculture",
        "benefit": "₹6,000 per year in three instalments, straight to the bank account",
        "blurb": "Income support for landholding farmer families.",
        "requires_all": ["landholding"],
        "occupations": {"farmer"},
        "excludes": {"govt_employee", "income_tax_payer"},
        "docs": ["Aadhaar card", "Bank account details", "Land ownership papers (khatauni)"],
        "steps": ["Check your status on the PM-KISAN portal", "Apply via CSC / state agriculture office with land papers", "e-KYC with Aadhaar, then instalments arrive in the bank account"],
    },
    {
        "id": "pmjay",
        "name": "Ayushman Bharat PM-JAY",
        "name_hi": "आयुष्मान भारत",
        "ministry": "Ministry of Health & Family Welfare",
        "category": "Health",
        "benefit": "Free hospital treatment up to ₹5 lakh per family per year",
        "blurb": "Health cover for poor and vulnerable families; all Indians aged 70+ are covered.",
        "requires_any": ["bpl", "senior70"],
        "docs": ["Aadhaar card", "Ration card / family ID", "Income certificate (if asked)"],
        "steps": ["Check eligibility on the PM-JAY beneficiary portal", "Get your Ayushman card at a CSC or empanelled hospital", "Show the card at any empanelled hospital — cashless treatment"],
    },
    {
        "id": "vaya-vandana",
        "name": "Ayushman Vaya Vandana (70+)",
        "name_hi": "वय वंदना",
        "ministry": "Ministry of Health & Family Welfare",
        "category": "Health",
        "benefit": "Free hospital treatment up to ₹5 lakh per year for every senior citizen aged 70+",
        "blurb": "Health cover for all Indians aged 70 and above, regardless of income.",
        "min_age": 70,
        "docs": ["Aadhaar card (age proof)"],
        "steps": ["Enrol on the PM-JAY portal or at a CSC", "Get the Vaya Vandana card", "Use it cashless at empanelled hospitals"],
    },
    {
        "id": "mudra",
        "name": "PM Mudra Yojana (PMMY)",
        "name_hi": "मुद्रा योजना",
        "ministry": "Ministry of Finance",
        "category": "Business",
        "benefit": "Business loans up to ₹10 lakh (Shishu / Kishore / Tarun); Tarun Plus up to ₹20 lakh",
        "blurb": "Collateral-free loans to start or grow a small business.",
        "min_age": 18,
        "occupations": {"entrepreneur", "vendor", "artisan", "self_employed"},
        "requires_any": ["business_idea", "existing_business"],
        "docs": ["Aadhaar + PAN", "Business plan / project report", "Bank statements (for existing business)", "Address proof"],
        "steps": ["Prepare a one-page business plan", "Apply at any bank / NBFC / MFI under Mudra", "Loan is sanctioned in Shishu, Kishore or Tarun category by size"],
    },
    {
        "id": "standup-india",
        "name": "Stand-Up India",
        "name_hi": "स्टैंड-अप इंडिया",
        "ministry": "Ministry of Finance",
        "category": "Business",
        "benefit": "Bank loans from ₹10 lakh to ₹1 crore for greenfield enterprises",
        "blurb": "Big-ticket enterprise loans for SC/ST and women entrepreneurs.",
        "min_age": 18,
        "genders": None,
        "occupations": {"entrepreneur"},
        "requires_any": ["sc_st", "woman_entrepreneur"],
        "requires_all": ["business_idea"],
        "docs": ["Aadhaar + PAN", "Caste certificate (SC/ST) if applicable", "Detailed project report", "Proof of business premises"],
        "steps": ["Draft a project report for a new (greenfield) enterprise", "Apply through the Stand-Up India portal or your bank", "Bank sanctions the loan; handholding support is available via the portal"],
    },
    {
        "id": "pmegp",
        "name": "PM Employment Generation Programme (PMEGP)",
        "name_hi": "पीएमईजीपी",
        "ministry": "Ministry of MSME",
        "category": "Business",
        "benefit": "Subsidy of 15–35% on project cost for new micro-enterprises (up to ₹50 lakh manufacturing / ₹20 lakh service)",
        "blurb": "Margin-money subsidy to start a village or town micro-enterprise.",
        "min_age": 18,
        "occupations": {"entrepreneur", "self_employed", "unemployed"},
        "requires_all": ["business_idea"],
        "docs": ["Aadhaar card", "Project report", "Educational certificates (Class 8 pass for larger projects)", "Caste certificate if claiming higher subsidy"],
        "steps": ["Apply online on the PMEGP portal via KVIC / KVIB / DIC", "Project is appraised by the task force", "Bank sanctions loan; subsidy is released as margin money"],
    },
    {
        "id": "svanidhi",
        "name": "PM SVANidhi",
        "name_hi": "स्वनिधि",
        "ministry": "Ministry of Housing & Urban Affairs",
        "category": "Business",
        "benefit": "Working-capital loan of ₹10,000 (then ₹20,000 / ₹50,000 on timely repayment) + 7% interest subsidy",
        "blurb": "Collateral-free micro-loans for street vendors.",
        "min_age": 18,
        "occupations": {"vendor"},
        "requires_all": ["street_vendor"],
        "docs": ["Aadhaar card", "Vending certificate / LoR from ULB", "Bank account details", "Mobile number"],
        "steps": ["Apply on the PM SVANidhi portal or via CSC", "Get the first ₹10,000 loan", "Repay on time to unlock the next, larger tranche"],
    },
    {
        "id": "vishwakarma",
        "name": "PM Vishwakarma",
        "name_hi": "विश्वकर्मा",
        "ministry": "Ministry of MSME",
        "category": "Skills",
        "benefit": "₹15,000 toolkit grant, skill training with stipend, loans ₹1 lakh + ₹2 lakh at 5%",
        "blurb": "Recognition and support for traditional artisans and craftspeople in 18 trades.",
        "min_age": 18,
        "occupations": {"artisan"},
        "requires_all": ["artisan"],
        "docs": ["Aadhaar card", "Proof of trade / occupation", "Bank account details"],
        "steps": ["Enrol on the PM Vishwakarma portal via CSC", "Complete skill training and verification", "Receive toolkit grant and become eligible for the low-interest loan"],
    },
    {
        "id": "sukanya",
        "name": "Sukanya Samriddhi Yojana",
        "name_hi": "सुकन्या समृद्धि",
        "ministry": "Ministry of Finance",
        "category": "Women & Child",
        "benefit": "High-interest savings account for a girl child (deposit ₹250–₹1.5 lakh/year, matures at 21)",
        "blurb": "Long-term savings for a daughter's education and marriage.",
        "max_age": 10,
        "genders": {"female"},
        "requires_all": ["girl_child"],
        "docs": ["Girl child's birth certificate", "Parent/guardian Aadhaar + PAN", "Address proof"],
        "steps": ["Open the account at a post office or authorised bank before she turns 10", "Deposit at least ₹250 every year", "Withdraw for higher education at 18; matures at 21"],
    },
    {
        "id": "ujjwala",
        "name": "PM Ujjwala Yojana 2.0",
        "name_hi": "उज्ज्वला",
        "ministry": "Ministry of Petroleum & Natural Gas",
        "category": "Women & Child",
        "benefit": "Free LPG connection (deposit-free) + first refill and stove support",
        "blurb": "Clean cooking fuel for adult women in households without an LPG connection.",
        "min_age": 18,
        "genders": {"female"},
        "requires_all": ["no_lpg"],
        "docs": ["Aadhaar card", "Ration card / state family ID", "Address proof", "Bank account details"],
        "steps": ["Apply online on the Ujjwala portal or at an LPG distributor", "Verification that no LPG connection exists in the household", "Connection is issued deposit-free"],
    },
    {
        "id": "post-matric-sc",
        "name": "Post-Matric Scholarship for SC Students",
        "name_hi": "पोस्ट-मैट्रिक छात्रवृत्ति",
        "ministry": "Ministry of Social Justice & Empowerment",
        "category": "Education",
        "benefit": "Tuition fees + maintenance allowance for SC students after Class 10",
        "blurb": "Scholarship for SC students studying beyond Class 10.",
        "max_income": 250000,
        "occupations": {"student"},
        "requires_all": ["sc_st", "post_matric"],
        "docs": ["Caste certificate", "Income certificate", "Class 10 marksheet", "Bonafide / admission proof", "Bank account (Aadhaar-seeded)"],
        "steps": ["Register on the National Scholarship Portal", "Fill the Post-Matric SC application with institute verification", "Scholarship is credited after state verification"],
    },
    {
        "id": "nmms",
        "name": "National Means-cum-Merit Scholarship (NMMS)",
        "name_hi": "राष्ट्रीय मेधा छात्रवृत्ति",
        "ministry": "Ministry of Education",
        "category": "Education",
        "benefit": "₹12,000 per year (₹1,000/month) from Class 9 to 12 for meritorious students",
        "blurb": "Merit scholarship to stop dropout after Class 8.",
        "max_income": 350000,
        "occupations": {"student"},
        "requires_all": ["class8", "merit"],
        "docs": ["Class 7 marksheet", "Income certificate", "School bonafide certificate"],
        "steps": ["Appear for the state NMMS selection test in Class 8", "Qualify on merit", "Apply on the National Scholarship Portal; amount comes yearly till Class 12"],
    },
    {
        "id": "pmay-g",
        "name": "PM Awas Yojana – Gramin",
        "name_hi": "पीएम आवास ग्रामीण",
        "ministry": "Ministry of Rural Development",
        "category": "Housing",
        "benefit": "₹1.20 lakh assistance (plain areas) to build a pucca house + toilet and LPG support",
        "blurb": "A pucca house for rural families living in kutcha or dilapidated houses.",
        "requires_all": ["rural", "kutcha_house"],
        "excludes": {"pucca_house", "govt_employee", "income_tax_payer"},
        "docs": ["Aadhaar card", "MGNREGA job card / SECC record", "Bank account details", "Land / house-site proof"],
        "steps": ["Check the PMAY-G permanent waitlist at your Gram Panchayat", "Apply via the Gram Sabha / AwaasApp", "Instalments are released as construction stages complete"],
    },
    {
        "id": "pmay-u",
        "name": "PM Awas Yojana – Urban 2.0",
        "name_hi": "पीएम आवास शहरी",
        "ministry": "Ministry of Housing & Urban Affairs",
        "category": "Housing",
        "benefit": "Interest subsidy on home loans for EWS / LIG / MIG families buying or building a first house",
        "blurb": "Interest subsidy that makes a first urban home affordable.",
        "max_income": 1800000,
        "requires_all": ["urban", "first_house"],
        "excludes": {"pucca_house"},
        "docs": ["Aadhaar card", "Income certificate", "Property / loan documents", "Affidavit of first house"],
        "steps": ["Apply on the PMAY-U portal or at a CSC", "Choose BLC / AHP / ISS vertical as applicable", "Subsidy is credited to the loan account after verification"],
    },
    {
        "id": "apy",
        "name": "Atal Pension Yojana",
        "name_hi": "अटल पेंशन",
        "ministry": "Ministry of Finance",
        "category": "Finance",
        "benefit": "Guaranteed pension of ₹1,000–₹5,000 per month after age 60",
        "blurb": "A small monthly pension for unorganised-sector workers.",
        "min_age": 18,
        "max_age": 40,
        "occupations": {"unorganised_worker", "self_employed", "unemployed", "farmer", "vendor", "artisan"},
        "excludes": {"govt_employee", "income_tax_payer"},
        "docs": ["Aadhaar card", "Bank account details", "Mobile number"],
        "steps": ["Open an APY account at your bank (savings account needed)", "Choose your pension amount; contribution is auto-debited monthly", "Pension starts at 60"],
    },
    {
        "id": "pmjdy",
        "name": "PM Jan Dhan Yojana",
        "name_hi": "जन धन",
        "ministry": "Ministry of Finance",
        "category": "Finance",
        "benefit": "Zero-balance bank account + RuPay debit card + ₹10,000 overdraft + accident insurance",
        "blurb": "A bank account for every household, with no minimum balance.",
        "min_age": 10,
        "docs": ["Aadhaar card (or any official ID)", "Passport-size photo"],
        "steps": ["Walk into any bank branch or Bank Mitra with Aadhaar", "Open the Jan Dhan account — no minimum balance", "RuPay card and overdraft facility follow"],
    },
    {
        "id": "pmfby",
        "name": "PM Fasal Bima Yojana",
        "name_hi": "फसल बीमा",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "category": "Agriculture",
        "benefit": "Crop insurance against drought, flood and pests — farmer pays only 1.5–2% premium",
        "blurb": "Insurance for crops, so one bad season does not wipe out a farmer.",
        "occupations": {"farmer"},
        "requires_all": ["landholding"],
        "docs": ["Aadhaar card", "Land records (khatauni)", "Bank account details", "Sowing certificate"],
        "steps": ["Enrol via bank / CSC / the PMFBY portal before the season cut-off", "Premium is deducted (1.5% rabi, 2% kharif)", "Claims are assessed from satellite and crop-cutting data"],
    },
    {
        "id": "pmkvy",
        "name": "PM Kaushal Vikas Yojana 4.0",
        "name_hi": "कौशल विकास",
        "ministry": "Ministry of Skill Development & Entrepreneurship",
        "category": "Skills",
        "benefit": "Free short-term skill training with certification (400+ job roles, incl. AI and new-age skills)",
        "blurb": "Free, certified skill training for school/college dropouts and job seekers.",
        "min_age": 15,
        "max_age": 45,
        "occupations": {"student", "unemployed", "school_dropout"},
        "docs": ["Aadhaar card", "Educational certificates", "Bank account details"],
        "steps": ["Register on the Skill India Digital portal", "Pick a training centre and job role near you", "Complete training and get certified"],
    },
]

CATEGORIES = ["Agriculture", "Business", "Education", "Finance", "Health",
              "Housing", "Skills", "Women & Child"]

OFFICIAL_PORTAL = "https://www.myscheme.gov.in"
DATA_AS_OF = "November 2026"
SCHEME_COUNT = len(SCHEMES)

# ---------------------------------------------------------------------------
# Plain-language profile parser (NLP layer)
# ---------------------------------------------------------------------------

_NUMBER = r"(\d+(?:\.\d+)?)"
_MULTIPLIERS = {"lakh": 100000, "lac": 100000, "lakhs": 100000,
                "crore": 10000000, "crores": 10000000,
                "thousand": 1000, "k": 1000, "": 1}

_GENDER_WORDS = {
    "female": ["woman", "women", "female", "girl", "lady", "ladies", "beti",
               "daughter", "mahila", "aurat", "wife", "mother", "widow"],
    "male": ["man", "men", "male", "boy", "beta", "son", "husband", "father"],
}

_OCCUPATION_WORDS = {
    "student": ["student", "studying", "padhai", "padh+", "college", "school",
                "class 10", "class 12", "graduate", "undergraduate"],
    "farmer": ["farmer", "kisan", "farming", "kheti", "agriculture", "cultivat+"],
    "vendor": ["vendor", "street vendor", "thela", "rehri", "hawk", "stall",
               "sabzi", "vegetable seller", "fruit seller"],
    "artisan": ["artisan", "carpenter", "tailor", "potter", "blacksmith",
                "weaver", "goldsmith", "craftsman", "craftsperson", "mistri",
                "darzi", "kumhar", "badhai", "lohar"],
    "entrepreneur": ["business", "entrepreneur", "startup", "shop", "dukaan",
                     "enterprise", "company", "msme", "udyam", "self-employed",
                     "self employed"],
    "unemployed": ["unemployed", "jobless", "no job", "looking for work",
                    "berozgar", "naukri nahi"],
    "self_employed": ["self-employed", "self employed", "freelance"],
    "unorganised_worker": ["daily wage", "labour", "labourer", "mazdoor",
                           "construction worker", "domestic worker", "daily wager"],
    "school_dropout": ["dropout", "dropped out", "left school"],
}

_FLAG_WORDS = {
    "landholding": ["land", "khet", "khatauni", "acre", "farm land", "own land",
                    "zameen", "kisan", "farming"],
    "girl_child": ["girl child", "daughter", "beti", "baby girl"],
    "sc_st": ["sc", "st", "scheduled caste", "scheduled tribe", "dalit",
              "adivasi", "sc/st"],
    "obc": ["obc", "other backward"],
    "ews": ["ews", "economically weaker"],
    "bpl": ["bpl", "below poverty", "poor", "gareeb", "ration card"],
    "no_lpg": ["no lpg", "no gas", "no cylinder", "firewood", "chulha",
               "no gas connection"],
    "street_vendor": ["street vendor", "thela", "rehri", "hawk", "stall"],
    "artisan": ["artisan", "carpenter", "tailor", "potter", "weaver"],
    "business_idea": ["want to start", "start a business", "open a shop",
                      "start a shop", "new business", "business idea",
                      "want to open", "plan to start"],
    "existing_business": ["my shop", "my business", "own shop", "running a shop",
                          "have a shop", "existing business", "my stall"],
    "woman_entrepreneur": ["woman entrepreneur", "women entrepreneur",
                           "female entrepreneur"],
    "rural": ["village", "rural", "gaon", "gram"],
    "urban": ["city", "urban", "town", "sheher", "metro"],
    "kutcha_house": ["kutcha", "mud house", "thatched", "no pucca", "kaccha"],
    "first_house": ["first house", "no house", "no own house", "rented house",
                    "rent", "first home"],
    "pucca_house": ["pucca house", "own house", "have a house"],
    "govt_employee": ["government employee", "govt employee", "sarkari naukri",
                      "government job"],
    "income_tax_payer": ["income tax", "tax payer", "file itr", "pay tax"],
    "senior70": ["seventy"],
    "class8": ["class 8", "eighth", "8th"],
    "post_matric": ["class 11", "class 12", "college", "after 10th",
                    "after class 10", "intermediate", "undergraduate"],
    "merit": ["merit", "topper", "good marks", "first division", "90%"],
    "disability": ["disabled", "disability", "divyang"],
}

_STATE_WORDS = {
    "Uttar Pradesh": ["uttar pradesh", "meerut", "lucknow", "kanpur"],
    "Bihar": ["bihar", "patna"],
    "Delhi": ["delhi"],
    "Maharashtra": ["maharashtra", "mumbai", "pune"],
    "Rajasthan": ["rajasthan", "jaipur"],
    "Madhya Pradesh": ["madhya pradesh", "bhopal", "indore"],
    "West Bengal": ["west bengal", "kolkata"],
    "Tamil Nadu": ["tamil nadu", "chennai"],
    "Karnataka": ["karnataka", "bengaluru", "bangalore"],
    "Gujarat": ["gujarat", "ahmedabad"],
    "Punjab": ["punjab", "ludhiana", "amritsar"],
    "Haryana": ["haryana", "gurgaon", "faridabad"],
    "Kerala": ["kerala", "kochi"],
    "Odisha": ["odisha", "orissa", "bhubaneswar"],
    "Telangana": ["telangana", "hyderabad"],
    "Andhra Pradesh": ["andhra pradesh", "vijayawada"],
}


def _has(text, word):
    """Token-aware match: whole words/phrases only, so 'sc' never matches
    'school' and '70' never matches '70000'. A trailing '+' means prefix
    match (for stems like 'cultivat' in 'cultivating')."""
    if word.endswith("+"):
        return re.search(r"(?<![a-z])" + re.escape(word[:-1]), text) is not None
    return re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])", text) is not None


def _extract_age(text):
    m = re.search(r"(?:age[d]?\s*(?:is|:)?\s*|i am\s+|i'm\s+|meri umar\s+)"
                  r"(\d{1,3})\b", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|saal\s*ka)\b", text)
    if m:
        return int(m.group(1))
    return None


def _extract_income(text):
    # "family income 2 lakh", "earn 50000", "₹2.5 lakh per year", "income of 3 lakhs"
    m = re.search(r"(?:income|earn\w*|salary|kamai|kamata)\D{0,25}?"
                  r"₹?\s*" + _NUMBER + r"\s*(lakh|lakhs|lac|crore|crores|thousand|k)?\b",
                  text)
    if not m:
        m = re.search(r"₹\s*" + _NUMBER + r"\s*(lakh|lakhs|lac|crore|crores|thousand|k)?\b", text)
    if not m:
        return None
    value = float(m.group(1))
    unit = (m.group(2) or "").lower()
    rupees = value * _MULTIPLIERS.get(unit, 1)
    # Monthly figures ("2 lakh per month") are annualised; a bare number is
    # only trusted as annual rupees when it looks like a salary (>= 10000).
    if re.search(r"(per month|/month|monthly|mahina)", text):
        rupees *= 12
    if not unit and rupees < 10000:
        return None
    return int(rupees)


def parse_profile(text):
    """Parse free text into a profile dict. Never raises on weird input."""
    t = " " + (text or "").lower() + " "
    profile = {"age": None, "annual_income": None, "gender": None,
               "occupations": set(), "state": None, "flags": set(),
               "raw_text": text or ""}
    profile["age"] = _extract_age(t)
    profile["annual_income"] = _extract_income(t)
    for gender, words in _GENDER_WORDS.items():
        if any(_has(t, w) for w in words):
            profile["gender"] = gender
            break
    for occ, words in _OCCUPATION_WORDS.items():
        if any(_has(t, w) for w in words):
            profile["occupations"].add(occ)
    for flag, words in _FLAG_WORDS.items():
        if any(_has(t, w) for w in words):
            profile["flags"].add(flag)
    # senior70 only counts if age is actually 70+ (the word "seventy" alone
    # is weak evidence, and "70" inside "70000" must never trigger it).
    if profile["age"] is not None and profile["age"] >= 70:
        profile["flags"].add("senior70")
    else:
        profile["flags"].discard("senior70")
    for state, words in _STATE_WORDS.items():
        if any(_has(t, w) for w in words):
            profile["state"] = state
            break
    # A girl child under 10 + female + "daughter/beti" implies a parent
    # describing their daughter; keep the flag, gender stays the child's.
    return profile


def profile_from_form(form):
    """Build a profile from the structured form fields (all optional)."""
    profile = {"age": None, "annual_income": None, "gender": None,
               "occupations": set(), "state": None, "flags": set(),
               "raw_text": ""}
    try:
        if form.get("age"):
            profile["age"] = int(form["age"])
    except (TypeError, ValueError):
        pass
    try:
        if form.get("annual_income"):
            profile["annual_income"] = int(form["annual_income"])
    except (TypeError, ValueError):
        pass
    if form.get("gender") in ("female", "male"):
        profile["gender"] = form["gender"]
    occ = form.get("occupation")
    if occ:
        profile["occupations"] = {occ}
    if form.get("state"):
        profile["state"] = form["state"]
    for key in ("landholding", "girl_child", "sc_st", "bpl", "no_lpg",
                "street_vendor", "artisan", "business_idea", "existing_business",
                "rural", "urban", "kutcha_house", "first_house", "pucca_house",
                "govt_employee", "income_tax_payer", "class8", "post_matric",
                "merit", "woman_entrepreneur"):
        if form.get(key):
            profile["flags"].add(key)
    if profile["age"] is not None and profile["age"] >= 70:
        profile["flags"].add("senior70")
    return profile


# ---------------------------------------------------------------------------
# Explainable matcher (symbolic layer)
# ---------------------------------------------------------------------------

def _check(label, passed, detail):
    # passed may be None (unknown) — preserve it, do NOT coerce to False.
    return {"label": label, "passed": None if passed is None else bool(passed),
            "detail": detail}


def evaluate(scheme, profile):
    """Evaluate one scheme. Returns (verdict, checks, missing_info).

    Verdicts: ELIGIBLE / CLOSE / NOT ELIGIBLE / NEEDS INFO.
    CLOSE = exactly one failed check, and it is a *soft* failure:
    income at most 50% over the cap, or up to 3 years too young for a
    minimum-age rule (you age into it). A maximum-age miss is always a
    hard no — you can never get younger. Anything else that fails is a
    hard no — and the trace says why.
    """
    checks = []
    missing = []
    age = profile.get("age")
    income = profile.get("annual_income")
    gender = profile.get("gender")
    occs = profile.get("occupations") or set()
    flags = profile.get("flags") or set()

    if scheme.get("min_age") is not None:
        if age is None:
            missing.append("age")
            checks.append(_check("Age %d+ years" % scheme["min_age"], None,
                                 "Age not given — cannot decide this rule"))
        else:
            checks.append(_check("Age %d+ years" % scheme["min_age"],
                                 age >= scheme["min_age"],
                                 "Your age: %d" % age))
    if scheme.get("max_age") is not None:
        if age is None:
            missing.append("age")
            checks.append(_check("Age up to %d years" % scheme["max_age"], None,
                                 "Age not given — cannot decide this rule"))
        else:
            checks.append(_check("Age up to %d years" % scheme["max_age"],
                                 age <= scheme["max_age"],
                                 "Your age: %d" % age))
    if scheme.get("max_income") is not None:
        if income is None:
            missing.append("annual family income")
            checks.append(_check("Family income up to ₹%s a year"
                                 % format(scheme["max_income"], ",d"), None,
                                 "Income not given — cannot decide this rule"))
        else:
            checks.append(_check("Family income up to ₹%s a year"
                                 % format(scheme["max_income"], ",d"),
                                 income <= scheme["max_income"],
                                 "Your income: ₹%s" % format(income, ",d")))
    if scheme.get("genders"):
        if gender is None:
            missing.append("gender")
            checks.append(_check("For %s applicants" % "/".join(sorted(scheme["genders"])), None,
                                 "Gender not given — cannot decide this rule"))
        else:
            checks.append(_check("For %s applicants" % "/".join(sorted(scheme["genders"])),
                                 gender in scheme["genders"],
                                 "You: %s" % gender))
    if scheme.get("occupations"):
        if not occs:
            missing.append("occupation")
            checks.append(_check("For: %s" % ", ".join(sorted(scheme["occupations"])), None,
                                 "Occupation not given — cannot decide this rule"))
        else:
            hit = occs & scheme["occupations"]
            checks.append(_check("For: %s" % ", ".join(sorted(scheme["occupations"])),
                                 bool(hit),
                                 "You: %s" % ", ".join(sorted(occs))))
    for flag in sorted(scheme.get("requires_all") or []):
        checks.append(_check("Must have: %s" % flag.replace("_", " "),
                             flag in flags,
                             "Present" if flag in flags else "Not mentioned"))
    if scheme.get("requires_any"):
        opts = sorted(scheme["requires_any"])
        hit = [f for f in opts if f in flags]
        checks.append(_check("Needs at least one of: %s" % ", ".join(f.replace("_", " ") for f in opts),
                             bool(hit),
                             ("You have: %s" % ", ".join(f.replace("_", " ") for f in hit))
                             if hit else "None of these mentioned"))
    for flag in sorted(scheme.get("excludes") or []):
        checks.append(_check("Must NOT be: %s" % flag.replace("_", " "),
                             flag not in flags,
                             "Applies to you" if flag in flags else "Does not apply"))

    failed = [c for c in checks if c["passed"] is False]
    unknown = [c for c in checks if c["passed"] is None]

    if unknown and not failed:
        return "NEEDS INFO", checks, sorted(set(missing))
    if not failed:
        return "ELIGIBLE", checks, []
    if len(failed) == 1:
        f = failed[0]
        # Soft failures that make a scheme CLOSE rather than a hard no.
        if scheme.get("max_income") is not None and income is not None \
                and "income" in f["label"].lower() \
                and income <= scheme["max_income"] * 1.5:
            return "CLOSE", checks, []
        # Too young by <= 3 years is CLOSE (you age into it). Too old is a
        # hard no — you can never get younger, so a max-age miss is final.
        if age is not None and f["label"].startswith("Age") \
                and "years" in f["label"] and "+" in f["label"]:
            if scheme.get("min_age") is not None and age < scheme["min_age"] \
                    and scheme["min_age"] - age <= 3:
                return "CLOSE", checks, []
    return "NOT ELIGIBLE", checks, []


def match_all(profile):
    """Match the profile against every scheme. Returns list of results."""
    results = []
    for scheme in SCHEMES:
        verdict, checks, missing = evaluate(scheme, profile)
        results.append({"scheme": scheme, "verdict": verdict,
                        "checks": checks, "missing": missing})
    order = {"ELIGIBLE": 0, "CLOSE": 1, "NEEDS INFO": 2, "NOT ELIGIBLE": 3}
    results.sort(key=lambda r: (order[r["verdict"]], r["scheme"]["name"]))
    return results


def what_if(profile, **overrides):
    """Re-run matching with one field changed (the what-if simulator)."""
    p = {"age": profile.get("age"), "annual_income": profile.get("annual_income"),
         "gender": profile.get("gender"),
         "occupations": set(profile.get("occupations") or []),
         "state": profile.get("state"),
         "flags": set(profile.get("flags") or []),
         "raw_text": profile.get("raw_text", "")}
    p.update(overrides)
    return match_all(p)


def summarise(results):
    counts = {"ELIGIBLE": 0, "CLOSE": 0, "NEEDS INFO": 0, "NOT ELIGIBLE": 0}
    for r in results:
        counts[r["verdict"]] += 1
    return counts
