from django.utils import timezone
from apps.complaints.models import Complaint

def generate_formal_letter(complaint: Complaint, language: str = 'hi') -> dict:
    """Auto-generate formatted formal grievance or RTI letter addressed to designated civic authority."""
    today_str = timezone.now().strftime('%d-%m-%Y')
    
    # Identify authority
    if complaint.administrative_unit and complaint.administrative_unit.authorities.exists():
        auth = complaint.administrative_unit.authorities.first()
        auth_title = auth.name_hi if language == 'hi' else auth.name_en
        auth_desig = auth.designation_hi if language == 'hi' else auth.designation_en
        office = auth.office_address_hi if language == 'hi' else auth.office_address_en
    else:
        auth_title = complaint.authority_name_override or ("श्रीमान सक्षम अधिकारी महोदय" if language == 'hi' else "The Competent Authority")
        auth_desig = complaint.authority_designation or ("विभागीय प्रमुख" if language == 'hi' else "Head of Department")
        office = complaint.sub_location

    loc = complaint.sub_location
    admin_name = complaint.administrative_unit.name_hi if complaint.administrative_unit else loc
    co_sign = complaint.co_sign_count
    duration_label = complaint.duration.label_hi if (complaint.duration and language == 'hi') else (complaint.duration.label_en if complaint.duration else 'काफी समय')

    evidence_hashes = "\n".join([f"- साक्ष्य #{i+1} [{e.media_type}] SHA-256: {e.sha256_hash}" for i, e in enumerate(complaint.evidence.all())]) or "- लाइव वेबकैम/माइक्रोफोन द्वारा जियो-टैग्ड साक्ष्य संलग्न।"

    if language == 'hi':
        subject = f"जनहित याचिका / औपचारिक शिकायत: {complaint.category.name_hi} - {loc} ({complaint.public_id})"
        content = f"""दिनांक: {today_str}

सेवा में,
{auth_desig} / {auth_title}
{office}, {admin_name}

विषय: {subject}

महोदय/महोदया,

आवाज़ (Awaaz) नागरिक जन-उत्तरदायित्व मंच के माध्यम से आपको अवगत कराया जाता है कि {loc} क्षेत्र में नागरिक निम्नलिखित गंभीर समस्या से {duration_label} से जूझ रहे हैं:

समस्या का विवरण:
{complaint.description}

सार्वजनिक साक्ष्य एवं जन-समर्थन विवरण:
1. आवाज़ ट्रैकिंग आईडी: {complaint.public_id}
2. प्रभावित नागरिकों की सह-पुष्टि (Co-Signs): {co_sign} नागरिकों ने इस समस्या की पुष्टि करते हुए मंच पर आवाज़ उठाई है।
3. समस्या की अवधि: {duration_label}
4. सटीक जीपीएस निर्देशांक (GPS): Latitude {complaint.latitude}, Longitude {complaint.longitude}
5. पूर्व में की गई शिकायतें: {complaint.prior_attempts_count} बार ({complaint.prior_channel.label_hi if complaint.prior_channel else 'स्थानीय स्तर पर'})

डिजिटल साक्ष्य की सत्यता (Tamper-Evident SHA-256 Hash):
{evidence_hashes}

अतः आपसे सविनय अनुरोध है कि जनहित में इस समस्या की त्वरित जांच करवाकर संबंधित एजेंसी को नियमानुसार समयबद्ध समाधान कराने का आदेश जारी करने की कृपा करें।

सादर,
नागरिक प्रतिनिधिमंडल ({loc})
प्रमाणित प्रति: आवाज़ (Awaaz) नागरिक साक्ष्य मंच
URL: https://awaaz.civic.in/complaint/{complaint.public_id}
"""
    else:
        subject = f"Formal Grievance Petition: {complaint.category.name_en} at {loc} ({complaint.public_id})"
        content = f"""Date: {today_str}

To,
{auth_desig} / {auth_title}
{office}, {admin_name}

Subject: {subject}

Respected Authority,

This formal grievance is submitted on behalf of local residents of {loc} through the Awaaz Civic Accountability Layer. The community has been severely affected by the following grievance for {duration_label}:

Description of Grievance:
{complaint.description}

Public Evidence & Community Corroboration:
1. Awaaz Public Docket ID: {complaint.public_id}
2. Corroborated Citizens Count (Co-Signs): {co_sign} verified residents
3. Duration of Problem: {duration_label}
4. Verified GPS Coordinates: Latitude {complaint.latitude}, Longitude {complaint.longitude}
5. Prior Grievance Reference: {complaint.prior_attempts_count} attempt(s) ({complaint.prior_channel.label_en if complaint.prior_channel else 'Departmental channel'})

Tamper-Evident Media Integrity (SHA-256 Hashes):
{evidence_hashes}

We formally request the department to inspect the site and initiate resolution within the statutory grievance redressal timeframe.

Yours sincerely,
Citizens of {loc}
Public Docket: Awaaz Civic Accountability Platform
Web Record: https://awaaz.civic.in/complaint/{complaint.public_id}
"""

    return {
        'subject': subject,
        'content': content,
        'addressed_to': f"{auth_desig}, {office}",
        'language': language,
        'public_id': complaint.public_id,
        'corroboration_count': co_sign
    }
