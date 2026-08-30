from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.config_engine.models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption
from apps.authorities.models import State, District, AdministrativeUnit, PublicAuthority
from apps.complaints.models import Complaint, ComplaintEvidence, ComplaintCoSign, StatusAuditLog
from apps.core.utils import compute_sha256, hash_session_id

class Command(BaseCommand):
    help = 'Seed initial config categories, pilot authority directory, and sample complaints'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Awaaz platform data...')

        # 1. Area Types
        village_at, _ = AreaType.objects.get_or_create(
            code='VILLAGE',
            defaults={
                'name_en': 'Village / Gram Panchayat',
                'name_hi': 'ग्रामीण / ग्राम पंचायत',
                'description_en': 'Rural areas governed by Gram Panchayat, Sarpanch, and Janpad Panchayat.',
                'description_hi': 'ग्राम पंचायत, सरपंच एवं सचिव द्वारा प्रशासित ग्रामीण क्षेत्र।',
                'order': 1
            }
        )

        town_at, _ = AreaType.objects.get_or_create(
            code='TOWN',
            defaults={
                'name_en': 'Town / Nagar Panchayat',
                'name_hi': 'कस्बा / नगर पंचायत व पालिका',
                'description_en': 'Semi-urban localities governed by Nagar Palika Parishad or Nagar Panchayat.',
                'description_hi': 'नगर पालिका परिषद अथवा नगर पंचायत द्वारा प्रशासित कस्बाई क्षेत्र।',
                'order': 2
            }
        )

        city_at, _ = AreaType.objects.get_or_create(
            code='CITY',
            defaults={
                'name_en': 'City / Nagar Nigam',
                'name_hi': 'शहर / नगर निगम',
                'description_en': 'Urban cities divided into Municipal Wards and governed by Nagar Nigam.',
                'description_hi': 'नगर निगम एवं वार्ड पार्षदों द्वारा प्रशासित शहरी क्षेत्र।',
                'order': 3
            }
        )

        # 2. Complaint Categories
        categories_data = [
            ('roads', 'Roads & Potholes', 'सड़क एवं गड्ढे', 'Construction', False, 1),
            ('water-supply', 'Water Supply & Quality', 'पेयजल आपूर्ति व गुणवत्ता', 'Droplets', False, 2),
            ('drainage', 'Drainage & Waterlogging', 'जलभराव एवं नाली जाम', 'Waves', False, 3),
            ('garbage', 'Garbage & Waste Disposal', 'कचरा प्रबंधन व सफाई', 'Trash2', False, 4),
            ('electricity', 'Electricity & Power Outage', 'बिजली आपूर्ति व खंभे', 'Zap', False, 5),
            ('street-lights', 'Street Lighting', 'स्ट्रीट लाइट / पथ प्रकाश', 'Lightbulb', False, 6),
            ('school-condition', 'Government School Condition', 'सरकारी स्कूल की दुर्दशा', 'GraduationCap', False, 7),
            ('health-center', 'Primary Health Center (PHC)', 'प्राथमिक स्वास्थ्य केंद्र (अस्पताल)', 'Cross', False, 8),
            ('sanitation', 'Public Toilets & Sanitation', 'सार्वजनिक शौचालय व स्वच्छता', 'Sparkles', False, 9),
            ('encroachment', 'Illegal Construction / Encroachment', 'अवैध निर्माण एवं अतिक्रमण', 'Home', False, 10),
            ('stray-animals', 'Stray Animals Menace', 'आवारा मवेशी एवं पशु समस्या', 'Dog', False, 11),
            ('public-transport', 'Public Transport & Bus Stand', 'सार्वजनिक परिवहन व बस स्टैंड', 'Bus', False, 12),
            ('official-conduct', 'Local Official Conduct & Bribes', 'अधिकारी/कर्मचारी का आचरण व रिश्वत', 'ShieldAlert', True, 13),
            ('other', 'Other Civic Grievance', 'अन्य स्थानीय जन समस्या', 'HelpCircle', False, 14),
        ]

        for slug, name_en, name_hi, icon, strict, order in categories_data:
            ComplaintCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_en': name_en,
                    'name_hi': name_hi,
                    'icon': icon,
                    'requires_strict_moderation': strict,
                    'order': order,
                    'is_active': True
                }
            )

        # 3. Durations
        durations_data = [
            ('LESS_1_MONTH', 'Less than 1 month', '1 माह से कम', 1),
            ('1_TO_6_MONTHS', '1 to 6 months', '1 से 6 महीने', 2),
            ('6_TO_12_MONTHS', '6 to 12 months', '6 से 12 महीने', 3),
            ('MORE_1_YEAR', 'More than 1 year', '1 वर्ष से अधिक', 4),
        ]
        for code, en, hi, order in durations_data:
            DurationOption.objects.update_or_create(
                code=code,
                defaults={'label_en': en, 'label_hi': hi, 'order': order}
            )

        # 4. Prior Channels
        channels_data = [
            ('CM_HELPLINE', 'CM Helpline (181 / Portal)', 'सीएम हेल्पलाइन (181)', 1),
            ('MUNICIPAL_APP', 'Nagar Nigam 311 / Citizen App', 'नगर निगम 311 ऐप', 2),
            ('PANCHAYAT_LETTER', 'Gram Panchayat Written Application', 'ग्राम पंचायत लिखित आवेदन', 3),
            ('DELEGATION', 'In-Person Delegation to Official', 'अधिकारी को व्यक्तिगत रूप से मिलकर', 4),
            ('RTI_QUERY', 'RTI (Right to Information) Request', 'सूचना का अधिकार (RTI) याचिका', 5),
            ('NONE_FIRST_TIME', 'First Time Reporting on Awaaz', 'पहली बार आवाज़ पर दर्ज', 6),
        ]
        for code, en, hi, order in channels_data:
            PriorChannelOption.objects.update_or_create(
                code=code,
                defaults={'label_en': en, 'label_hi': hi, 'order': order}
            )

        # 5. Pilot Authority Directory (Bhopal & Sehore Region - Urban + Rural)
        mp_state, _ = State.objects.get_or_create(code='MP', defaults={'name_en': 'Madhya Pradesh', 'name_hi': 'मध्य प्रदेश'})
        bhopal_dist, _ = District.objects.get_or_create(state=mp_state, code='BHO', defaults={'name_en': 'Bhopal', 'name_hi': 'भोपाल'})
        sehore_dist, _ = District.objects.get_or_create(state=mp_state, code='SEH', defaults={'name_en': 'Sehore', 'name_hi': 'सीहोर'})

        # Urban Units (Bhopal Wards)
        ward45, _ = AdministrativeUnit.objects.get_or_create(
            district=bhopal_dist,
            area_type=city_at,
            name_en='Ward 45 - MP Nagar & Zone 1',
            defaults={
                'name_hi': 'वार्ड 45 - एमपी नगर व ज़ोन 1',
                'unit_type': 'WARD',
                'ward_number': '45',
                'helpline_number': '0755-2701222',
                'official_portal_url': 'https://bhopalmc.mp.gov.in',
                'approx_latitude': 23.2332,
                'approx_longitude': 77.4350,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=ward45,
            name_en='Rajesh Sharma',
            defaults={
                'name_hi': 'राजेश शर्मा',
                'designation_en': 'Ward Corporator / Parshad',
                'designation_hi': 'वार्ड पार्षद',
                'contact_phone': '+91 98260 11234',
                'contact_email': 'parshad.ward45@bhopalmc.org',
                'office_address_en': 'Zone Office 10, Near Jyoti Talkies, MP Nagar, Bhopal',
                'office_address_hi': 'ज़ोन कार्यालय 10, ज्योति टॉकीज़ के पास, एमपी नगर, भोपाल',
            }
        )

        ward28, _ = AdministrativeUnit.objects.get_or_create(
            district=bhopal_dist,
            area_type=city_at,
            name_en='Ward 28 - Kolar Road & Sarvadharma',
            defaults={
                'name_hi': 'वार्ड 28 - कोलार रोड व सर्वधर्म',
                'unit_type': 'WARD',
                'ward_number': '28',
                'helpline_number': '0755-2701222',
                'approx_latitude': 23.1780,
                'approx_longitude': 77.4180,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=ward28,
            name_en='Sunita Malviya',
            defaults={
                'name_hi': 'सुनीता मालवीय',
                'designation_en': 'Ward Corporator',
                'designation_hi': 'वार्ड पार्षद',
                'contact_phone': '+91 94250 88901',
                'contact_email': 'ward28@bhopalmc.org',
                'office_address_en': 'Kolar Nagar Palika Bhavan, Kolar Road, Bhopal',
                'office_address_hi': 'कोलार पालिका भवन, कोलार रोड, भोपाल',
            }
        )

        # Rural Units (Sehore Gram Panchayats)
        bilkisganj_gp, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=village_at,
            name_en='Bilkisganj Gram Panchayat',
            defaults={
                'name_hi': 'बिलकिसगंज ग्राम पंचायत',
                'unit_type': 'GRAM_PANCHAYAT',
                'helpline_number': '07562-224100',
                'approx_latitude': 23.0850,
                'approx_longitude': 77.2340,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=bilkisganj_gp,
            name_en='Rameshwar Patel',
            defaults={
                'name_hi': 'रामेश्वर पटेल',
                'designation_en': 'Sarpanch (Pradhan)',
                'designation_hi': 'ग्राम प्रधान / सरपंच',
                'contact_phone': '+91 97531 44520',
                'office_address_en': 'Panchayat Bhavan, Main Bazaar, Bilkisganj, Sehore',
                'office_address_hi': 'पंचायत भवन, मुख्य बाज़ार, बिलकिसगंज, सीहोर',
            }
        )

        dora_gp, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=village_at,
            name_en='Dora Gram Panchayat',
            defaults={
                'name_hi': 'डोरा ग्राम पंचायत',
                'unit_type': 'GRAM_PANCHAYAT',
                'helpline_number': '07562-224100',
                'approx_latitude': 23.1120,
                'approx_longitude': 77.1980,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=dora_gp,
            name_en='Kamla Bai',
            defaults={
                'name_hi': 'कमला बाई',
                'designation_en': 'Sarpanch',
                'designation_hi': 'सरपंच',
                'contact_phone': '+91 98930 22314',
                'office_address_en': 'Panchayat Bhavan, Dora, Sehore',
                'office_address_hi': 'पंचायत भवन, डोरा, सीहोर',
            }
        )

        # Semi-Urban Town (Sehore Town Nagar Palika)
        sehore_town, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=town_at,
            name_en='Sehore Nagar Palika Parishad - Ward 12',
            defaults={
                'name_hi': 'सीहोर नगर पालिका परिषद - वार्ड 12',
                'unit_type': 'NAGAR_PANCHAYAT',
                'ward_number': '12',
                'helpline_number': '07562-222333',
                'approx_latitude': 23.2000,
                'approx_longitude': 77.0850,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=sehore_town,
            name_en='Pradeep Singh',
            defaults={
                'name_hi': 'प्रदीप सिंह',
                'designation_en': 'Nagar Palika Chairman',
                'designation_hi': 'नगर पालिका अध्यक्ष',
                'contact_phone': '+91 94251 77112',
                'office_address_en': 'Nagar Palika Office, Main Chauraha, Sehore',
                'office_address_hi': 'नगर पालिका कार्यालय, मुख्य चौराहा, सीहोर',
            }
        )

        # 6. Sample Live Pilot Complaints
        cat_roads = ComplaintCategory.objects.get(slug='roads')
        cat_water = ComplaintCategory.objects.get(slug='water-supply')
        cat_school = ComplaintCategory.objects.get(slug='school-condition')
        cat_garbage = ComplaintCategory.objects.get(slug='garbage')
        cat_drainage = ComplaintCategory.objects.get(slug='drainage')

        dur_6_12 = DurationOption.objects.get(code='6_TO_12_MONTHS')
        dur_more_1 = DurationOption.objects.get(code='MORE_1_YEAR')
        dur_1_6 = DurationOption.objects.get(code='1_TO_6_MONTHS')

        chan_cm = PriorChannelOption.objects.get(code='CM_HELPLINE')
        chan_app = PriorChannelOption.objects.get(code='MUNICIPAL_APP')
        chan_panch = PriorChannelOption.objects.get(code='PANCHAYAT_LETTER')

        # Complaint 1: Urban Road Pothole in MP Nagar
        c1, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-8941',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_1'),
                'area_type': city_at,
                'category': cat_roads,
                'duration': dur_6_12,
                'title': 'Dangerous 2-foot Deep Trench & Broken Road near Jyoti Talkies Crossroad',
                'description': 'The main connecting road between Zone 1 and Jyoti Talkies has been dug up for pipeline laying and left unpaved for 8 months. Two-wheelers crash daily during nighttime due to lack of barricading and street lighting. Over 10,000 commuters pass here every day.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 12000,
                'prior_attempts_count': 3,
                'prior_channel': chan_app,
                'prior_reference_number': 'BMC-311-884912',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward45,
                'sub_location': 'MP Nagar Zone 1, Near Jyoti Talkies',
                'authority_name_override': 'Rajesh Sharma (Ward Corporator)',
                'authority_designation': 'Ward 45 Corporator & Executive Engineer PWD',
                'latitude': 23.2335,
                'longitude': 77.4355,
                'gps_accuracy_meters': 4.2,
                'manual_address_text': 'Opposite Hotel Surendra Vilas, Zone 1, MP Nagar, Bhopal',
                'status': 'IN_PROGRESS',
                'moderation_status': 'APPROVED',
                'co_sign_count': 38,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c1,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80',
                sha256_hash='8f4b12a5e921d7b32814c02998a12e3445fb678832c199876543210fedcba987',
                capture_latitude=23.2335,
                capture_longitude=77.4355,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c1,
                from_status='UNDER_REVIEW',
                to_status='ACKNOWLEDGED',
                actor_type='AUTHORITY',
                actor_label='Nagar Nigam Zone 10 Engineer',
                notes='Site inspection conducted. Repair tender issued under Ward development fund.'
            )
            StatusAuditLog.objects.create(
                complaint=c1,
                from_status='ACKNOWLEDGED',
                to_status='IN_PROGRESS',
                actor_type='AUTHORITY',
                actor_label='PWD Sub-Division Bhopal',
                notes='Patchwork and bituminous concrete re-carpeting started on 24-Aug-2026.'
            )

        # Complaint 2: Rural Non-functional Government School Roof in Bilkisganj
        c2, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-3104',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_2'),
                'area_type': village_at,
                'category': cat_school,
                'duration': dur_more_1,
                'title': 'Leaking Roof and Collapsed Boundary Wall at Govt Primary School Bilkisganj',
                'description': 'During heavy rains, water drips directly onto students desks in classrooms 1 to 4. Plaster from the ceiling fell twice near the blackboard. There are no functional girl toilets, forcing 45 village girls to skip school during monsoon. The Sarpanch has ignored 4 written requests.',
                'people_affected_type': 'ENTIRE_VILLAGE',
                'people_affected_count': 320,
                'prior_attempts_count': 4,
                'prior_channel': chan_panch,
                'prior_reference_number': 'GP-BILKIS-2025/44',
                'state': mp_state,
                'district': sehore_dist,
                'administrative_unit': bilkisganj_gp,
                'sub_location': 'Govt Primary School, Bilkisganj Gram',
                'authority_name_override': 'Rameshwar Patel (Sarpanch)',
                'authority_designation': 'Gram Sarpanch & Block Education Officer (BEO)',
                'latitude': 23.0862,
                'longitude': 77.2348,
                'gps_accuracy_meters': 6.1,
                'manual_address_text': 'Near Village Pond, Bilkisganj Tehsil, Sehore',
                'status': 'ACKNOWLEDGED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 64,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c2,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80',
                sha256_hash='3a7e4b90f12c58e7789a44b3c0021e549887cd4a321efcba9876543210fedcba',
                capture_latitude=23.0862,
                capture_longitude=77.2348,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c2,
                from_status='UNDER_REVIEW',
                to_status='ACKNOWLEDGED',
                actor_type='AUTHORITY',
                actor_label='District Collectorate Grievance Portal',
                notes='Complaint escalated with 64 citizen corroborations. BEO Sehore assigned for physical verification.'
            )

        # Complaint 3: Urban Garbage Dump near Kolar Road Ward 28
        c3, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-5520',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_3'),
                'area_type': city_at,
                'category': cat_garbage,
                'duration': dur_1_6,
                'title': 'Overflowing Garbage Open Dump creating Health Hazard near Mandakini Chauraha',
                'description': 'Municipal waste collection bin was removed 3 months ago and replaced by an open dump. Stray cattle, dogs, and toxic stench make it impossible for 800+ families in the adjacent residential societies to open their windows. Vector-borne disease outbreak risk.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 4500,
                'prior_attempts_count': 2,
                'prior_channel': chan_cm,
                'prior_reference_number': 'CM-181-499201',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward28,
                'sub_location': 'Mandakini Colony, Kolar Road',
                'authority_name_override': 'Sunita Malviya (Ward Corporator)',
                'authority_designation': 'Ward 28 Corporator & Health Officer Zone 18',
                'latitude': 23.1795,
                'longitude': 77.4192,
                'gps_accuracy_meters': 3.5,
                'manual_address_text': 'Corner of Mandakini Colony Main Gate, Kolar Road, Bhopal',
                'status': 'RESOLVED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 21,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c3,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=800&q=80',
                sha256_hash='1b994c48a12e3456789abcdef0123456789abcdef0123456789abcdef0123456',
                capture_latitude=23.1795,
                capture_longitude=77.4192,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c3,
                from_status='IN_PROGRESS',
                to_status='RESOLVED',
                actor_type='AUTHORITY',
                actor_label='Sanitation Department BMC',
                notes='Waste cleared with JCB excavator, area sanitized with lime powder, 2 enclosed green waste bins installed.'
            )

        # Complaint 4: Rural Contaminated Borewell Water in Dora Village
        c4, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-9012',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_4'),
                'area_type': village_at,
                'category': cat_water,
                'duration': dur_1_6,
                'title': 'Yellow Muddy Water with Foul Odor from Govt Borewell Pump',
                'description': 'The sole public borewell in Harijan Mohalla has been discharging rusty, contaminated yellow water for 2 months. 14 children have developed gastrointestinal illness. Women are forced to walk 2.5 km to agricultural tube wells to fetch drinking water.',
                'people_affected_type': 'ENTIRE_VILLAGE',
                'people_affected_count': 500,
                'prior_attempts_count': 1,
                'prior_channel': chan_panch,
                'prior_reference_number': '',
                'state': mp_state,
                'district': sehore_dist,
                'administrative_unit': dora_gp,
                'sub_location': 'Harijan Mohalla, Dora Gaon',
                'authority_name_override': 'Kamla Bai (Sarpanch)',
                'authority_designation': 'Gram Sarpanch & PHE Department Executive Engineer',
                'latitude': 23.1130,
                'longitude': 77.1995,
                'gps_accuracy_meters': 5.0,
                'manual_address_text': 'Near Community Handpump, Dora Village, Sehore',
                'status': 'UNDER_REVIEW',
                'moderation_status': 'APPROVED',
                'co_sign_count': 19,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c4,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1584467735815-f778f274e296?auto=format&fit=crop&w=800&q=80',
                sha256_hash='7c9e01f23456789abcdef0123456789abcdef0123456789abcdef0123456789a',
                capture_latitude=23.1130,
                capture_longitude=77.1995,
                is_live_captured=True
            )

        # Complaint 5: Near-duplicate Road complaint in MP Nagar Zone 1 (to demonstrate duplicate detection)
        c5, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-8955',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_5'),
                'area_type': city_at,
                'category': cat_roads,
                'duration': dur_1_6,
                'title': 'Caved-in Manhole and Damaged Asphalt opposite Surendra Vilas',
                'description': 'The asphalt has completely eroded around the storm drain manhole creating a hazardous obstacle right at the intersection. Immediate hot-mix asphalt filling needed.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 8000,
                'prior_attempts_count': 1,
                'prior_channel': chan_app,
                'prior_reference_number': 'BMC-311-901844',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward45,
                'sub_location': 'MP Nagar Zone 1',
                'authority_name_override': 'Rajesh Sharma',
                'authority_designation': 'Ward 45 Corporator',
                'latitude': 23.2340,
                'longitude': 77.4360,
                'gps_accuracy_meters': 4.0,
                'manual_address_text': 'Zone 1, MP Nagar, Bhopal',
                'status': 'ACKNOWLEDGED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 14,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c5,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80',
                sha256_hash='4d88e01f23456789abcdef0123456789abcdef0123456789abcdef0123456789b',
                capture_latitude=23.2340,
                capture_longitude=77.4360,
                is_live_captured=True
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Awaaz platform with categories, authorities, and realistic pilot data!'))
