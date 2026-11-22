"""
CitizenAssist — scripts/generate_sample_pdfs.py
Generates realistic synthetic government scheme PDFs for demo/testing.
Run once: python scripts/generate_sample_pdfs.py
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT_DIR = Path("data/schemes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = A4

# Color palette
NAVY = HexColor("#1a3a5c")
BLUE = HexColor("#2563eb")
LIGHT_BLUE = HexColor("#eff6ff")
ORANGE = HexColor("#ea580c")
GREEN = HexColor("#15803d")
GRAY = HexColor("#6b7280")
LIGHT_GRAY = HexColor("#f9fafb")

styles = getSampleStyleSheet()


def make_heading_style(size=16, color=NAVY, bold=True):
    return ParagraphStyle(
        "CustomHeading",
        parent=styles["Normal"],
        fontSize=size,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        textColor=color,
        spaceAfter=8,
        spaceBefore=12,
    )


def make_body_style(size=11, color=black):
    return ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=size,
        fontName="Helvetica",
        textColor=color,
        spaceAfter=6,
        leading=16,
        alignment=TA_JUSTIFY
    )


def make_bullet_style():
    return ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=4,
        leading=15,
    )


h1 = make_heading_style(18, NAVY)
h2 = make_heading_style(14, BLUE)
h3 = make_heading_style(12, NAVY)
body = make_body_style()
bullet = make_bullet_style()
small = make_body_style(9, GRAY)


def divider():
    return HRFlowable(width="100%", thickness=1, color=HexColor("#e5e7eb"), spaceAfter=8, spaceBefore=4)


def build_pdf(filename: str, content_builder):
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )
    story = content_builder()
    doc.build(story)
    print(f"[OK] Generated: {path}")


# =============================================================================
# 1. Telangana State Merit Scholarship
# =============================================================================

def ts_merit_scholarship():
    story = []

    story.append(Paragraph("GOVERNMENT OF TELANGANA", make_heading_style(10, GRAY)))
    story.append(Paragraph("Department of Education — Scholarships Division", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("TELANGANA STATE MERIT SCHOLARSHIP SCHEME", h1))
    story.append(Paragraph("Guidelines and Instructions — 2024–25", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Paragraph("Document Reference: TS/EDU/SCHOLAR/2024-25/001 | Date: April 2024", small))
    story.append(Spacer(1, 0.4 * cm))

    # 1. Objective
    story.append(Paragraph("1. OBJECTIVE OF THE SCHEME", h2))
    story.append(Paragraph(
        "The Telangana State Merit Scholarship Scheme is established by the Government of Telangana to provide "
        "financial assistance to meritorious students from the state of Telangana who are pursuing higher education "
        "in recognized institutions. The scheme aims to ensure that financial constraints do not hinder academically "
        "capable students from accessing quality higher education.",
        body
    ))
    story.append(Spacer(1, 0.2 * cm))

    # 2. Eligibility
    story.append(Paragraph("2. ELIGIBILITY CRITERIA", h2))
    story.append(Paragraph("2.1 Domicile Requirement", h3))
    story.append(Paragraph(
        "The applicant must be a bonafide resident of the State of Telangana. The applicant must possess a valid "
        "Telangana State Domicile Certificate issued by the competent Revenue Authority. Students who have studied "
        "for a minimum of five years in Telangana State schools or colleges shall also be considered eligible, "
        "subject to production of relevant certificates.",
        body
    ))

    story.append(Paragraph("2.2 Age Limit", h3))
    story.append(Paragraph(
        "The applicant must not have attained the age of 30 years as on the date of application. "
        "For applicants belonging to SC, ST, and Persons with Disabilities (PWD) categories, "
        "the upper age limit shall be relaxed by 5 years, i.e., up to 35 years.",
        body
    ))

    story.append(Paragraph("2.3 Academic Qualification", h3))
    story.append(Paragraph(
        "The applicant must have passed the qualifying examination (10+2 or equivalent) with a minimum aggregate "
        "of 60% marks from a recognized Board. Applicants belonging to SC, ST, BC, and EWS categories shall be "
        "eligible with a minimum of 50% aggregate marks in the qualifying examination. "
        "The applicant must be enrolled in a full-time regular program in an institution recognized by UGC, AICTE, "
        "MCI, or the relevant statutory body.",
        body
    ))

    story.append(Paragraph("2.4 Income Criterion", h3))
    story.append(Paragraph(
        "The annual family income of the applicant from all sources shall not exceed Rs. 2,50,000 (Rupees Two Lakh "
        "Fifty Thousand only) per annum. Income from agriculture, business, employment, and all other sources shall "
        "be included in the computation of annual family income. The income limit shall apply to the combined income "
        "of the applicant's parents/guardians.",
        body
    ))

    story.append(Paragraph("2.5 Category Requirements", h3))
    story.append(Paragraph(
        "The scholarship is available to students belonging to Scheduled Castes (SC), Scheduled Tribes (ST), "
        "Backward Classes (BC-A, BC-B, BC-C, BC-D, BC-E), Economically Weaker Sections (EWS), and other eligible "
        "categories as notified by the Government from time to time. General category students may apply under "
        "the merit-cum-means component of the scheme.",
        body
    ))

    story.append(Paragraph("2.6 Eligible Courses", h3))
    story.append(Paragraph(
        "The scholarship covers the following programs: Engineering and Technology (B.Tech/B.E.), Medical Sciences "
        "(MBBS, BDS, B.Pharm), Sciences (B.Sc, M.Sc), Commerce (B.Com), Arts (B.A.), Management (MBA), "
        "Computer Applications (MCA), and Ph.D. programs. Diploma programs of minimum two years duration in "
        "government polytechnics are also eligible.",
        body
    ))

    story.append(Spacer(1, 0.2 * cm))

    # 3. Benefit
    story.append(Paragraph("3. SCHOLARSHIP AMOUNT AND BENEFITS", h2))
    data = [
        ["Category", "Annual Scholarship Amount"],
        ["SC/ST Students (Professional Courses)", "Rs. 20,000 per year"],
        ["BC Students (Professional Courses)", "Rs. 15,000 per year"],
        ["EWS Students (Professional Courses)", "Rs. 12,000 per year"],
        ["All Categories (Degree Courses)", "Rs. 10,000 per year"],
        ["All Categories (PG Courses)", "Rs. 12,000 per year"],
    ]
    table = Table(data, colWidths=[9 * cm, 7 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BLUE, white]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "In addition to the scholarship amount, students are entitled to receive a maintenance allowance of "
        "Rs. 500 per month for hostellers and Rs. 300 per month for day scholars during the academic year.",
        body
    ))

    # 4. Documents Required
    story.append(Paragraph("4. DOCUMENTS REQUIRED FOR APPLICATION", h2))
    docs = [
        "Recent passport-size photograph (white background)",
        "Aadhaar Card (original and self-attested copy)",
        "Telangana State Domicile/Residence Certificate issued by MRO",
        "Caste Certificate issued by competent authority (for SC/ST/BC/EWS applicants)",
        "Income Certificate for the financial year 2023–24, issued by MRO/Tahsildar",
        "10th Class Marks Memo (SSC or equivalent)",
        "Inter/12th/Qualifying Examination Marks Memo",
        "Bonafide Certificate/College ID Card from the current institution",
        "Fee receipt/Admission receipt from the institution",
        "Bank passbook copy (nationalized bank, Aadhaar-linked, applicant as account holder)",
        "Mobile number registered with Aadhaar"
    ]
    for doc in docs:
        story.append(Paragraph(f"• {doc}", bullet))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Note: All photocopies submitted must be self-attested by the applicant. 'Self-attested' means you sign "
        "and write 'True Copy' on the photocopy yourself. Original documents must be presented for verification "
        "if required by the scholarship authority.",
        body
    ))

    # 5. Application Process
    story.append(Paragraph("5. APPLICATION PROCEDURE", h2))
    steps = [
        "Visit the official Telangana Scholarships Portal at telanganaepass.cgg.gov.in.",
        "Register using your Aadhaar-linked mobile number. An OTP will be sent for verification.",
        "Complete the online application form with accurate personal, academic, and income details.",
        "Upload scanned copies of all required documents (PDF/JPG, max 200 KB each).",
        "Verify all entries before submission. Corrections may not be allowed after submission.",
        "Submit the application and note down the Application Reference Number.",
        "The application will be forwarded to your institution for verification.",
        "The institution will verify and forward to the District Scholarship Committee.",
        "Scholarship amount will be credited directly to the Aadhaar-linked bank account after approval.",
        "Track your application status on the portal using your Application Reference Number."
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {step}", bullet))

    story.append(Spacer(1, 0.2 * cm))

    # 6. Important Dates
    story.append(Paragraph("6. IMPORTANT DATES AND DEADLINES", h2))
    dates = [
        ["Activity", "Tentative Date"],
        ["Online Application Opens", "1st July 2024"],
        ["Last Date for Application", "30th September 2024"],
        ["Verification by Institutions", "October 2024"],
        ["District Committee Review", "November 2024"],
        ["Scholarship Disbursement", "December 2024 onwards"],
    ]
    dt = Table(dates, colWidths=[9 * cm, 7 * cm])
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GRAY, white]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(dt)
    story.append(Spacer(1, 0.2 * cm))

    # 7. Conditions and Renewal
    story.append(Paragraph("7. CONDITIONS FOR RENEWAL", h2))
    story.append(Paragraph(
        "The scholarship shall be renewed annually subject to the following conditions:",
        body
    ))
    conditions = [
        "The applicant must pass all subjects in the annual examinations without any arrears or backlogs.",
        "The applicant must maintain a minimum attendance of 75% during the academic year.",
        "The scholarship shall be discontinued if the applicant fails to pass the year's examination.",
        "Any change in course, institution, or personal details must be reported immediately to the Scholarship Authority.",
        "Duplicate scholarships are not permitted. If the applicant is found to be availing of another scholarship for the same purpose, the scholarship shall be cancelled and the amount recovered."
    ]
    for c in conditions:
        story.append(Paragraph(f"• {c}", bullet))

    story.append(Spacer(1, 0.3 * cm))
    story.append(divider())
    story.append(Paragraph(
        "For further information and grievance redressal, contact the District Welfare Officer or visit "
        "the Telangana State Scholarship Portal. Helpline: 040-23120114.",
        small
    ))

    return story


# =============================================================================
# 2. PM-KISAN
# =============================================================================

def pm_kisan():
    story = []

    story.append(Paragraph("GOVERNMENT OF INDIA", make_heading_style(10, GRAY)))
    story.append(Paragraph("Ministry of Agriculture & Farmers Welfare", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("PRADHAN MANTRI KISAN SAMMAN NIDHI (PM-KISAN)", h1))
    story.append(Paragraph("Scheme Guidelines and Operational Manual — 2024", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Paragraph("Ref: PM-KISAN/GUIDELINES/2024 | Revised Edition", small))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. SCHEME OVERVIEW", h2))
    story.append(Paragraph(
        "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector Scheme launched by the Government of "
        "India to provide income support to all landholding farmer families in the country. Under this scheme, "
        "income support of Rs. 6,000 per year is provided in three equal instalments of Rs. 2,000 each, "
        "transferred directly to the bank accounts of the beneficiary farmers.",
        body
    ))

    story.append(Paragraph("2. ELIGIBILITY CRITERIA", h2))
    story.append(Paragraph("2.1 Who is Eligible", h3))
    story.append(Paragraph(
        "All landholding farmer families, i.e., families comprising husband, wife, and minor children who own "
        "cultivable land, are eligible for income support under PM-KISAN, subject to certain exclusion criteria. "
        "The benefit is available to farmer families holding cultivable land in their own name. "
        "Tenant farmers who cultivate leased land are NOT eligible for benefits under this scheme.",
        body
    ))

    story.append(Paragraph("2.2 Who is Not Eligible (Exclusion Categories)", h3))
    story.append(Paragraph(
        "The following categories of persons/families are NOT eligible to receive benefits under PM-KISAN:",
        body
    ))
    exclusions = [
        "Former and present holders of Constitutional posts including President, Vice-President, Prime Minister, Chief Ministers, Governors, Cabinet Ministers, Members of Parliament and State Legislatures.",
        "All serving and retired officers and employees of Central/State Government Ministries, Departments, Field Units, Central/State PSUs, and Government autonomous bodies (excluding Multi-Tasking Staff/Class IV/Group D employees).",
        "All superannuated/retired pensioners whose monthly pension is Rs. 10,000 or more (excluding Multi-Tasking Staff/Class IV/Group D employees).",
        "Persons who paid Income Tax in the last assessment year.",
        "Professionals such as Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies and carrying out their professions.",
    ]
    for e in exclusions:
        story.append(Paragraph(f"• {e}", bullet))

    story.append(Paragraph("2.3 Land Holding", h3))
    story.append(Paragraph(
        "The scheme applies to small and marginal farmers as well as larger landholding farmers, provided they are "
        "not in an exclusion category. The land must be cultivable agricultural land. Fallow land, forest land, "
        "or land used for non-agricultural purposes does not qualify.",
        body
    ))

    story.append(Paragraph("3. BENEFIT", h2))
    story.append(Paragraph(
        "An annual income support of Rs. 6,000 (Rupees Six Thousand only) is provided to each eligible farmer "
        "family. The amount is transferred in three instalments of Rs. 2,000 each approximately every four months "
        "(April–July, August–November, December–March). The amount is transferred directly into the beneficiary's "
        "Aadhaar-seeded bank account through Direct Benefit Transfer (DBT).",
        body
    ))

    story.append(Paragraph("4. REQUIRED DOCUMENTS", h2))
    docs = [
        "Aadhaar Card (mandatory for all beneficiaries)",
        "Land ownership documents / Khasra-Khatauni / ROR (Record of Rights)",
        "Bank account passbook (Aadhaar-linked, IFSC code clearly visible)",
        "Mobile number registered with Aadhaar"
    ]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet))

    story.append(Paragraph("5. REGISTRATION PROCESS", h2))
    steps = [
        "Visit the official PM-KISAN portal at pmkisan.gov.in.",
        "Click on 'New Farmer Registration' under the Farmers Corner section.",
        "Select Rural or Urban farmer as applicable.",
        "Enter your Aadhaar number and State. Click 'Search'.",
        "Complete the registration form with land, bank, and personal details.",
        "Upload land documents as required.",
        "Submit the form. Note your registration number.",
        "Your application will be verified by the state government.",
        "On approval, the first installment will be credited to your Aadhaar-linked bank account.",
        "Existing registered farmers: Benefits are automatically released on verification. No re-registration needed."
    ]
    for i, s in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    story.append(Paragraph("6. GRIEVANCE REDRESSAL", h2))
    story.append(Paragraph(
        "For complaints or grievances, farmers may contact the PM-KISAN Helpline at 155261 or 1800115526 "
        "(Toll Free). Grievances may also be submitted online at pmkisan.gov.in under the 'Help Desk' section. "
        "State Nodal Officers are also available in each state for resolution of local issues.",
        body
    ))

    return story


# =============================================================================
# 3. PMAY
# =============================================================================

def pmay():
    story = []

    story.append(Paragraph("GOVERNMENT OF INDIA", make_heading_style(10, GRAY)))
    story.append(Paragraph("Ministry of Housing and Urban Affairs", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("PRADHAN MANTRI AWAS YOJANA — URBAN (PMAY-U)", h1))
    story.append(Paragraph("Housing for All — Scheme Guidelines 2024–25", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. SCHEME OBJECTIVE", h2))
    story.append(Paragraph(
        "Pradhan Mantri Awas Yojana (Urban) aims to address the urban housing shortage among the EWS/LIG/MIG "
        "segments with the vision of 'Housing for All' by providing central assistance to eligible beneficiaries. "
        "The scheme provides Credit Linked Subsidy for purchase/construction/extension/improvement of pucca houses.",
        body
    ))

    story.append(Paragraph("2. ELIGIBILITY CRITERIA", h2))
    story.append(Paragraph("2.1 Basic Eligibility", h3))
    basic = [
        "The beneficiary family must not own a pucca house in his/her name or in the name of any member of the family anywhere in India.",
        "The beneficiary must not have availed of central assistance under any housing scheme from the Government of India earlier.",
        "Preference shall be given to: manual scavengers, women (with priority to widows), persons belonging to SC/ST/OBCs, persons with disabilities, minorities, transgender persons, and ex-servicemen.",
        "The property to be purchased, constructed, or improved must be located within the urban area of a State or Union Territory."
    ]
    for b in basic:
        story.append(Paragraph(f"• {b}", bullet))

    story.append(Paragraph("2.2 Income Categories", h3))
    income_data = [
        ["Category", "Annual Household Income", "Interest Subsidy", "Max Loan Amount"],
        ["EWS (Economically Weaker Section)", "Up to Rs. 3 lakh", "6.5%", "Rs. 6 lakh"],
        ["LIG (Low Income Group)", "Rs. 3 to 6 lakh", "6.5%", "Rs. 6 lakh"],
        ["MIG-I (Middle Income Group-I)", "Rs. 6 to 12 lakh", "4%", "Rs. 9 lakh"],
        ["MIG-II (Middle Income Group-II)", "Rs. 12 to 18 lakh", "3%", "Rs. 12 lakh"],
    ]
    t = Table(income_data, colWidths=[4.5 * cm, 4 * cm, 3 * cm, 3.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BLUE, white]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("3. REQUIRED DOCUMENTS", h2))
    docs = [
        "Aadhaar card (all adult family members)",
        "Income proof (salary slip / IT return / income certificate from competent authority)",
        "Address proof (ration card / voter ID / utility bill)",
        "Property documents / allotment letter (if applicable)",
        "Bank account details with IFSC code (Aadhaar-linked account preferred)",
        "Affidavit confirming that no family member owns a pucca house",
        "Photographs of the existing dwelling (if applying for improvement)"
    ]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet))

    story.append(Paragraph("4. APPLICATION PROCESS — CLSS COMPONENT", h2))
    steps = [
        "Identify a housing loan provider (Scheduled Commercial Bank, Housing Finance Company, or any Primary Lending Institution empanelled under PMAY).",
        "Apply for a home loan at the selected lending institution.",
        "Submit your application for PMAY-CLSS benefit along with the home loan application.",
        "The lending institution will verify your documents and assess your eligibility.",
        "On approval, the subsidy amount will be credited directly to your loan account, reducing your outstanding principal.",
        "Track your subsidy status at pmaymis.gov.in using your Aadhaar number."
    ]
    for i, s in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    story.append(Paragraph("5. IMPORTANT CONDITIONS", h2))
    story.append(Paragraph(
        "The dwelling unit constructed or purchased under PMAY shall be in the name of the female head of the "
        "household, or jointly in the names of male and female heads of household. Only one member from each "
        "household is eligible for the scheme. The dwelling unit must be used for residential purposes only.",
        body
    ))

    return story


# =============================================================================
# 4. Ayushman Bharat
# =============================================================================

def ayushman_bharat():
    story = []

    story.append(Paragraph("NATIONAL HEALTH AUTHORITY", make_heading_style(10, GRAY)))
    story.append(Paragraph("Government of India", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("AYUSHMAN BHARAT — PRADHAN MANTRI JAN AROGYA YOJANA (PM-JAY)", h1))
    story.append(Paragraph("Operational Guidelines for Beneficiaries — 2024", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. OVERVIEW", h2))
    story.append(Paragraph(
        "Ayushman Bharat – Pradhan Mantri Jan Arogya Yojana (PM-JAY) is the world's largest health assurance "
        "scheme. It provides health coverage of up to Rs. 5 lakh per family per year for secondary and tertiary "
        "hospitalization to over 50 crore beneficiaries. The scheme covers medical expenses for pre-existing "
        "conditions from day one, including hospitalization, surgery, diagnostics, and medicines.",
        body
    ))

    story.append(Paragraph("2. ELIGIBILITY", h2))
    story.append(Paragraph("2.1 Primary Eligibility — SECC 2011", h3))
    story.append(Paragraph(
        "Eligibility under PM-JAY is primarily determined by the Socio-Economic Caste Census (SECC) 2011. "
        "All rural and urban families listed in SECC 2011 under the prescribed deprivation and occupational "
        "criteria are eligible for PM-JAY benefits. Families do NOT need to apply separately — eligibility is "
        "pre-determined from the SECC database.",
        body
    ))

    story.append(Paragraph("2.2 How to Check if Your Family is Eligible", h3))
    methods = [
        "Visit the official website: beneficiary.nha.gov.in and search using your Aadhaar number, ration card number, or mobile number.",
        "Call the PM-JAY Helpline at 14555 (Toll Free).",
        "Visit the nearest empanelled hospital and ask the Ayushman Mitra at the helpdesk to check your eligibility.",
        "Visit the Common Service Centre (CSC) in your area."
    ]
    for m in methods:
        story.append(Paragraph(f"• {m}", bullet))

    story.append(Paragraph("2.3 Aadhaar Requirement", h3))
    story.append(Paragraph(
        "While Aadhaar is the preferred identification document, families without Aadhaar may use alternative "
        "identity documents such as voter ID, ration card, or MNREGA job card for eligibility verification, "
        "subject to state-level guidelines. It is strongly recommended to have your mobile number registered "
        "with Aadhaar for smooth processing.",
        body
    ))

    story.append(Paragraph("3. HEALTH COVERAGE — KEY FEATURES", h2))
    features = [
        "Coverage of Rs. 5 lakh per family per year on a family floater basis.",
        "Covers over 1,949 medical packages and procedures.",
        "Coverage for pre-existing diseases and conditions from day one.",
        "Covers hospitalization, surgeries, day care procedures, follow-up care.",
        "No premium or co-payment required by the beneficiary.",
        "Cashless treatment available at all empanelled government and private hospitals.",
        "Coverage extends to all family members regardless of family size, age, or gender.",
        "Covers costs of medicines, diagnostics, consultation fees, pre and post-hospitalization."
    ]
    for f in features:
        story.append(Paragraph(f"• {f}", bullet))

    story.append(Paragraph("4. HOW TO ACCESS BENEFITS", h2))
    steps = [
        "Confirm your eligibility at beneficiary.nha.gov.in or at any empanelled hospital.",
        "Obtain your Ayushman Bharat Health Account (ABHA) number if not already done.",
        "In case of hospitalization, visit an empanelled hospital (look for the PM-JAY empanelled hospital sign).",
        "Contact the Ayushman Mitra at the hospital's helpdesk for assistance.",
        "Submit your Aadhaar card for verification at the hospital.",
        "Treatment will be provided on a cashless basis. You do not need to pay from your pocket.",
        "The hospital will file the claim directly with PM-JAY — you are not required to handle the claim process."
    ]
    for i, s in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    story.append(Paragraph("5. REQUIRED DOCUMENTS FOR ACCESSING TREATMENT", h2))
    story.append(Paragraph("One of the following documents is sufficient for identification:", body))
    docs = ["Aadhaar Card", "Voter Identity Card", "Ration Card", "MNREGA Job Card", "Government-issued Photo ID"]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet))

    return story


# =============================================================================
# 5. NSP Post-Matric
# =============================================================================

def nsp_post_matric():
    story = []

    story.append(Paragraph("MINISTRY OF EDUCATION, GOVERNMENT OF INDIA", make_heading_style(10, GRAY)))
    story.append(Paragraph("National Scholarship Portal", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("POST-MATRIC SCHOLARSHIP FOR SC/ST/OBC/MINORITY STUDENTS", h1))
    story.append(Paragraph("Scheme Guidelines — Academic Year 2024–25", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. OBJECTIVE", h2))
    story.append(Paragraph(
        "The Post-Matric Scholarship Schemes under the National Scholarship Portal (NSP) aim to provide "
        "financial assistance to students belonging to Scheduled Castes (SC), Scheduled Tribes (ST), "
        "Other Backward Classes (OBC), and Minority communities who are pursuing post-secondary education. "
        "The objective is to remove financial barriers and enable eligible students to complete their education.",
        body
    ))

    story.append(Paragraph("2. ELIGIBILITY CRITERIA", h2))
    story.append(Paragraph("2.1 Category Eligibility", h3))
    story.append(Paragraph(
        "The scholarship is available to students belonging to the following categories: "
        "Scheduled Castes (SC), Scheduled Tribes (ST), Other Backward Classes (OBC), "
        "Minority communities (Muslim, Christian, Sikh, Buddhist, Jain, Zoroastrian), "
        "and Economically Backward Classes (EBC) as defined by the respective scheme guidelines.",
        body
    ))

    story.append(Paragraph("2.2 Income Limit", h3))
    story.append(Paragraph(
        "The annual family income limit varies by category and component: "
        "For SC/ST students: annual family income must not exceed Rs. 2,50,000 (Rupees Two Lakh Fifty Thousand). "
        "For OBC students: annual family income must not exceed Rs. 1,50,000 (Rupees One Lakh Fifty Thousand). "
        "For Minority students: annual family income must not exceed Rs. 2,00,000 (Rupees Two Lakh). "
        "Income from all sources, including agriculture and business, is included in computing family income.",
        body
    ))

    story.append(Paragraph("2.3 Educational Level", h3))
    story.append(Paragraph(
        "The scholarship applies to courses beyond Class 10 (Matriculation), including: Class 11 and 12, "
        "ITI/Diploma programs, Graduation (UG), Post-Graduation (PG), Ph.D., and other post-secondary courses. "
        "The student must be enrolled in a recognized institution affiliated with a recognized university or board.",
        body
    ))

    story.append(Paragraph("2.4 Other Conditions", h3))
    conditions = [
        "The applicant must not be availing of any other scholarship from Central or State Government for the same purpose.",
        "The applicant must maintain satisfactory academic progress as defined by the institution.",
        "The institution must be recognized by the respective statutory authority (UGC, AICTE, NMC, etc.).",
        "The applicant's Aadhaar number must be linked to the bank account for DBT payment."
    ]
    for c in conditions:
        story.append(Paragraph(f"• {c}", bullet))

    story.append(Paragraph("3. SCHOLARSHIP AMOUNT", h2))
    story.append(Paragraph(
        "The scholarship amount covers maintenance allowance and mandatory fees. Rates vary by level of study: "
        "For hostellers pursuing professional courses: up to Rs. 1,200 per month maintenance. "
        "For day scholars: up to Rs. 550 per month maintenance. "
        "In addition, compulsory non-refundable fees, study tour charges, thesis printing charges (for Ph.D. students) "
        "are also reimbursed as per the NSP guidelines.",
        body
    ))

    story.append(Paragraph("4. REQUIRED DOCUMENTS", h2))
    docs = [
        "Aadhaar Card",
        "Category Certificate (Caste certificate from competent authority for SC/ST/OBC)",
        "Income Certificate from competent authority (issued for financial year 2023–24)",
        "Previous year marksheet/mark memo",
        "Current year admission receipt/fee receipt from institution",
        "Bonafide Certificate from institution",
        "Bank passbook copy (account in applicant's name, Aadhaar-linked)",
        "Domicile/Residence certificate",
        "Passport-size photograph",
        "Self-declaration (non-availing of other scholarship)"
    ]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet))

    story.append(Paragraph("5. APPLICATION PROCESS — NSP PORTAL", h2))
    steps = [
        "Visit scholarships.gov.in (National Scholarship Portal).",
        "Click 'New Registration' and select the appropriate category.",
        "Register using your mobile number and Aadhaar. Verify with OTP.",
        "Complete the application form — personal details, academic details, bank details.",
        "Select the scholarship scheme applicable to your category and state.",
        "Upload all required documents.",
        "Submit the application before the last date.",
        "Your institute will verify the application online.",
        "Track application status on NSP portal using Application ID.",
        "Scholarship amount will be directly credited to your bank account after central/state approval."
    ]
    for i, s in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    return story


# =============================================================================
# 6. MGNREGA
# =============================================================================

def mgnrega():
    story = []

    story.append(Paragraph("MINISTRY OF RURAL DEVELOPMENT, GOVERNMENT OF INDIA", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("MAHATMA GANDHI NATIONAL RURAL EMPLOYMENT GUARANTEE ACT (MGNREGA)", h1))
    story.append(Paragraph("Citizen Guide — Rights, Entitlements & Application Process 2024", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. OVERVIEW", h2))
    story.append(Paragraph(
        "MGNREGA is a legal right of rural citizens. It guarantees 100 days of unskilled manual wage employment "
        "per financial year to every rural household whose adult members are willing to do unskilled manual work. "
        "The employment is provided within 15 days of demand, failing which an unemployment allowance is paid.",
        body
    ))

    story.append(Paragraph("2. WHO IS ELIGIBLE", h2))
    story.append(Paragraph("2.1 Basic Eligibility Conditions", h3))
    conditions = [
        "Must be a resident of a rural area (Gram Panchayat area).",
        "Must be an adult (18 years or above).",
        "Must be willing to do unskilled manual work.",
        "Any member of the rural household can apply — there is no restriction based on gender, caste, or income.",
        "Eligible for urban areas only if the State Government has extended the scheme to those areas under special provisions."
    ]
    for c in conditions:
        story.append(Paragraph(f"• {c}", bullet))

    story.append(Paragraph("2.2 Key Features", h3))
    features = [
        "100 days of employment guaranteed per household per financial year.",
        "Employment provided within 5 km of the applicant's residence.",
        "If work is provided beyond 5 km, additional transportation allowance of 10% of wage rate is paid.",
        "Equal wages for men and women (minimum wage applicable in the state).",
        "Payment of wages within 15 days of completion of work.",
        "If work not provided within 15 days of demand, unemployment allowance must be paid.",
        "Work provided includes water conservation, drought proofing, land development, rural connectivity, etc."
    ]
    for f in features:
        story.append(Paragraph(f"• {f}", bullet))

    story.append(Paragraph("3. JOB CARD — YOUR RIGHT", h2))
    story.append(Paragraph(
        "Every rural household is entitled to a MGNREGA Job Card. The Job Card is the primary document that "
        "records all work demanded and provided under MGNREGA. It is free of cost and must be issued within "
        "15 days of application by the Gram Panchayat.",
        body
    ))

    story.append(Paragraph("4. REQUIRED DOCUMENTS FOR JOB CARD", h2))
    docs = [
        "Aadhaar card (highly recommended; mandatory for wage payment via DBT)",
        "Passport-size photograph of all adult household members",
        "Any address proof confirming residence in rural area",
        "Bank account details (preferably in the name of the applicant)"
    ]
    for d in docs:
        story.append(Paragraph(f"• {d}", bullet))

    story.append(Paragraph("5. HOW TO APPLY FOR JOB CARD", h2))
    steps = [
        "Submit a written or verbal application to the Gram Panchayat in your village.",
        "The application must include names of all adult household members willing to work.",
        "No fee is charged for applying for a Job Card.",
        "The Gram Panchayat must issue the Job Card within 15 days of application.",
        "The Job Card contains your photo and all work and payment records.",
        "Keep your Job Card safely — it is an important document.",
        "You can also register online at nreganet.nic.in or the UMANG app.",
        "Demand for work: Once you have a Job Card, submit a written demand for work at the Gram Panchayat.",
        "Work must be provided within 15 days of your work demand.",
        "Track work and payments at nreganet.nic.in."
    ]
    for i, s in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    story.append(Paragraph("6. WAGES AND PAYMENT", h2))
    story.append(Paragraph(
        "MGNREGA wages are notified by each State Government and must not be less than the statutory minimum "
        "wage for agricultural laborers in the state. For Telangana, the MGNREGA wage rate is Rs. 272 per day "
        "(as notified for 2024–25; subject to revision). Wages are paid through bank/post office accounts directly.",
        body
    ))

    return story


# =============================================================================
# 7. TS Caste / Income Certificate
# =============================================================================

def ts_caste_certificate():
    story = []

    story.append(Paragraph("GOVERNMENT OF TELANGANA", make_heading_style(10, GRAY)))
    story.append(Paragraph("Revenue Department — MeeSeva / TS-ePASS Services", make_heading_style(10, GRAY)))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("CITIZEN GUIDE: CASTE, INCOME & DOMICILE CERTIFICATES", h1))
    story.append(Paragraph("How to Apply and What to Expect — 2024", make_heading_style(13, BLUE)))
    story.append(divider())
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. OVERVIEW", h2))
    story.append(Paragraph(
        "The Telangana Revenue Department issues three important certificates required for availing government "
        "schemes and reservations: (1) Caste Certificate, (2) Income Certificate, and (3) Domicile/Residence "
        "Certificate. These can be obtained online through MeeSeva portals and centers, or at the Tahsildar/MRO "
        "office in your area.",
        body
    ))

    story.append(Paragraph("2. CASTE CERTIFICATE", h2))
    story.append(Paragraph("2.1 Who Needs It", h3))
    story.append(Paragraph(
        "Any person belonging to SC, ST, BC-A, BC-B, BC-C, BC-D, or BC-E categories who wishes to avail "
        "reservations in education, employment, or government schemes requires a Caste Certificate. "
        "The certificate is issued based on community as recorded in revenue and census records.",
        body
    ))
    story.append(Paragraph("2.2 Required Documents", h3))
    docs_caste = [
        "Aadhaar Card",
        "Ration Card (with family caste record) OR Birth Certificate",
        "Previous school/college records mentioning caste",
        "Caste certificate of parent (if available)",
        "Revenue record (if applicable)"
    ]
    for d in docs_caste:
        story.append(Paragraph(f"• {d}", bullet))
    story.append(Paragraph("2.3 Application Process", h3))
    steps_caste = [
        "Visit MeeSeva center or apply at meeseva.telangana.gov.in.",
        "Select 'Caste Certificate' service.",
        "Fill in personal and community details.",
        "Upload required documents.",
        "Pay the prescribed fee (usually nominal, varies by district).",
        "Track application status online.",
        "Certificate will be delivered digitally or physically within 7–15 working days after verification."
    ]
    for i, s in enumerate(steps_caste, 1):
        story.append(Paragraph(f"{i}. {s}", bullet))

    story.append(Paragraph("3. INCOME CERTIFICATE", h2))
    story.append(Paragraph("3.1 Purpose", h3))
    story.append(Paragraph(
        "An Income Certificate is an official document certifying the annual income of a family from all sources. "
        "It is required for most scholarship applications, government scheme eligibility verification, and "
        "EWS/Economically Weaker Section certification. The certificate is issued for a specific financial year "
        "and must be renewed annually for continued use in government applications.",
        body
    ))
    story.append(Paragraph("3.2 Required Documents", h3))
    docs_income = [
        "Aadhaar Card",
        "Salary slips / Form 16 (if salaried) OR agriculture land details (if farmer)",
        "Self-declaration of income from all sources",
        "Ration Card",
        "Previous year IT return (if applicable)"
    ]
    for d in docs_income:
        story.append(Paragraph(f"• {d}", bullet))

    story.append(Paragraph("4. DOMICILE / RESIDENCE CERTIFICATE", h2))
    story.append(Paragraph(
        "A Domicile Certificate, also called a Residence Certificate, certifies that the holder is a bona fide "
        "resident of Telangana State. This certificate is required for state government scholarships, "
        "government jobs, and many other state-specific schemes. "
        "Required documents: Aadhaar Card, Ration Card, Electricity Bill or any address proof, and school "
        "certificates showing study in Telangana for minimum required years.",
        body
    ))

    story.append(Paragraph("5. EWS CERTIFICATE", h2))
    story.append(Paragraph(
        "An EWS (Economically Weaker Section) certificate is issued to citizens from General Category "
        "whose annual family income is below Rs. 8 lakh from all sources and who do not possess more than "
        "5 acres of agricultural land, residential flat of 1000 sq ft or above, residential plot of 100 sq yd "
        "or above in notified municipalities, or residential plot of 200 sq yd or above in non-notified areas. "
        "Required documents: Aadhaar, Ration Card, Income Certificate, Land/Property documents.",
        body
    ))

    story.append(Paragraph("6. IMPORTANT NOTE", h2))
    story.append(Paragraph(
        "All certificates are issued by the Tahsildar/MRO (Mandal Revenue Officer) of your area. "
        "MeeSeva application is the recommended and faster method. Physical verification may be required "
        "in some cases. Processing time is typically 7 to 21 working days depending on the certificate type. "
        "For urgent requirements, contact your District Collector's office.",
        body
    ))

    return story


# =============================================================================
# Main
# =============================================================================

SCHEMES = [
    ("ts_merit_scholarship.pdf", ts_merit_scholarship),
    ("pm_kisan.pdf", pm_kisan),
    ("pmay.pdf", pmay),
    ("ayushman_bharat.pdf", ayushman_bharat),
    ("nsp_post_matric.pdf", nsp_post_matric),
    ("mgnrega.pdf", mgnrega),
    ("ts_caste_certificate.pdf", ts_caste_certificate),
]


if __name__ == "__main__":
    print("Generating sample government scheme PDFs...")
    for filename, builder in SCHEMES:
        build_pdf(filename, builder)
    print(f"\n[DONE] All {len(SCHEMES)} PDFs generated in: {OUTPUT_DIR.absolute()}")
