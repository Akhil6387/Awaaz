from pathlib import Path

content = '''from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.config_engine.models import ComplaintCategory, AreaType, DurationOption
from apps.complaints.models import Complaint, ComplaintCoSign, StatusAuditLog
from apps.escalation.generators import generate_formal_letter
from apps.core.utils import compute_sha256, hash_session_id, haversine_distance_meters

class AwaazCoreTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.area_city = AreaType.objects.create(
            code='CITY', name_en='City', name_hi='???', order=1
        )
        self.category_roads = ComplaintCategory.objects.create(
            slug='roads', name_en='Roads & Potholes', name_hi='????', order=1
        )
        self.duration_option = DurationOption.objects.create(
            code='1_TO_6_MONTHS', label_en='1 to 6 months', label_hi='1 ?? 6 ?????', order=1
        )

    def test_sha256_computation(self):
        sample_bytes = b'sample media proof bytes'
        hash_val = compute_sha256(sample_bytes)
        self.assertEqual(len(hash_val), 64)
        self.assertEqual(hash_val, compute_sha256(sample_bytes))

    def test_haversine_distance(self):
        dist = haversine_distance_meters(23.2332, 77.4350, 23.1780, 77.4180)
        self.assertTrue(5500 < dist < 7000)

    def test_anonymous_complaint_submission(self):
        payload = {
            'anonymous_session_id': 'test_anon_uuid_12345',
            'revealed_identity': False,
            'area_type': self.area_city.id,
            'category': self.category_roads.id,
            'duration': self.duration_option.id,
            'title': 'Dangerous road excavation at Sector 2 market',
            'description': 'The road has been excavated for laying stormwater pipes and remains completely unpaved for 4 months.',
            'sub_location': 'Sector 2 Main Market',
            'latitude': 23.2335,
            'longitude': 77.4355,
            'file_urls': ['https://example.com/live_proof.jpg'],
            'media_types': ['PHOTO']
        }
        response = self.client.post('/api/v1/complaints/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['public_id'].startswith('AWZ-'))
        self.assertEqual(response.data['status'], 'UNDER_REVIEW')
        
        complaint = Complaint.objects.get(public_id=response.data['public_id'])
        self.assertEqual(complaint.evidence.count(), 1)
        self.assertEqual(complaint.audit_trail.count(), 1)
        self.assertEqual(complaint.anonymous_session_hash, hash_session_id('test_anon_uuid_12345'))

    def test_duplicate_detection(self):
        Complaint.objects.create(
            public_id='AWZ-2026-TEST1',
            anonymous_session_hash=hash_session_id('user1'),
            area_type=self.area_city,
            category=self.category_roads,
            title='Large pothole outside bank',
            description='A huge crater in the road causing accidents every single day during evening rush hour.',
            sub_location='Near SBI Branch',
            latitude=23.2335,
            longitude=77.4355,
            moderation_status='APPROVED'
        )

        response = self.client.get('/api/v1/complaints/check-duplicates/?lat=23.2340&lng=77.4360&category_id=' + str(self.category_roads.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(response.data['duplicates'][0]['distance_meters'] < 200)

    def test_cosign_idempotency(self):
        complaint = Complaint.objects.create(
            public_id='AWZ-2026-TEST2',
            anonymous_session_hash=hash_session_id('creator'),
            area_type=self.area_city,
            category=self.category_roads,
            title='Overflowing sewage line',
            description='Raw sewage overflowing into drinking water pipe network in street 4.',
            sub_location='Street 4',
            latitude=23.2335,
            longitude=77.4355,
            moderation_status='APPROVED'
        )

        res1 = self.client.post(f'/api/v1/complaints/{complaint.id}/co_sign/', {'anonymous_session_id': 'voter_1'}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.data['co_sign_count'], 1)

        res2 = self.client.post(f'/api/v1/complaints/{complaint.id}/co_sign/', {'anonymous_session_id': 'voter_1'}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertTrue(res2.data['already_cosigned'])
        complaint.refresh_from_db()
        self.assertEqual(complaint.co_sign_count, 1)

    def test_escalation_generator(self):
        complaint = Complaint.objects.create(
            public_id='AWZ-2026-TEST3',
            anonymous_session_hash=hash_session_id('creator'),
            area_type=self.area_city,
            category=self.category_roads,
            duration=self.duration_option,
            title='Dilapidated culvert collapse',
            description='The main culvert has collapsed blocking agricultural transport for 3 months.',
            sub_location='South Culvert',
            latitude=23.2335,
            longitude=77.4355,
            moderation_status='APPROVED',
            co_sign_count=12
        )
        letter_hi = generate_formal_letter(complaint, language='hi')
        self.assertIn('AWZ-2026-TEST3', letter_hi['subject'])
        self.assertIn('12', letter_hi['content'])

        letter_en = generate_formal_letter(complaint, language='en')
        self.assertIn('Formal Grievance Petition', letter_en['subject'])
        self.assertIn('12 verified residents', letter_en['content'])
'''

Path('apps/complaints/tests.py').write_text(content, encoding='utf-8')
print('Updated apps/complaints/tests.py')
