"""
Adversarial & Hostile Concurrency Test Suite for Feedora REST API.
Verifies runtime survivability under:
  1. Threaded concurrent survey submissions.
  2. Schema drift & orphaned question inputs.
  3. Oversized and unbounded text inputs.
"""
import concurrent.futures
import json
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from surveys.models import Survey, Question, MCQOption, Response, Answer

User = get_user_model()


class HostileConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username='lab_creator',
            email='lab_creator@feedora.org',
            password='Password123!',
            role='creator',
            is_active=True,
        )
        self.survey = Survey.objects.create(
            organization=self.creator,
            title='Concurrency Stress Survey',
            description='Test survey under adversarial multi-threaded load',
            is_active=True,
        )
        self.q_likert = Question.objects.create(
            survey=self.survey,
            code='STRESS_L1',
            text='Stress test Likert item',
            question_type='likert',
            order=1,
        )
        self.q_open = Question.objects.create(
            survey=self.survey,
            code='STRESS_O1',
            text='Stress test open text item',
            question_type='open',
            order=2,
        )
        self.q_mcq = Question.objects.create(
            survey=self.survey,
            code='STRESS_M1',
            text='Stress test choice item',
            question_type='mcq',
            order=3,
        )
        self.opt1 = MCQOption.objects.create(question=self.q_mcq, text='Alpha', order=1)
        self.opt2 = MCQOption.objects.create(question=self.q_mcq, text='Beta', order=2)

    def test_concurrent_submissions_do_not_deadlock_sqlite(self):
        """Simulate concurrent threads submitting answers to the same survey simultaneously."""
        num_workers = 8
        url = f'/api/v1/surveys/{self.survey.access_uuid}/submit/'

        def submit_worker(worker_id):
            from django.test import Client
            client = Client()
            payload = {
                'answers': {
                    'STRESS_L1': 4,
                    'STRESS_O1': f'Worker {worker_id} qualitative feedback',
                    'STRESS_M1': self.opt1.id,
                }
            }
            res = client.post(url, data=json.dumps(payload), content_type='application/json')
            return res.status_code, res.json()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(submit_worker, i) for i in range(num_workers)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        for status_code, data in results:
            self.assertEqual(status_code, 200)
            self.assertTrue(data.get('ok'))
            self.assertGreater(data.get('pointsEarned', 0), 0)

        # Assert exactly num_workers responses were recorded
        self.assertEqual(Response.objects.filter(survey=self.survey).count(), num_workers)
        self.assertEqual(Answer.objects.filter(question=self.q_likert).count(), num_workers)

    def test_schema_drift_reconciles_when_client_submits_unknown_questions(self):
        """Verify client submitting orphaned or deleted question IDs does not trigger 500 error."""
        from django.test import Client
        client = Client()
        url = f'/api/v1/surveys/{self.survey.access_uuid}/submit/'
        payload = {
            'answers': {
                'STRESS_L1': 5,
                'ORPHANED_UNKNOWN_QUESTION_CODE': 'Should be ignored gracefully',
                '99999999': 'Unknown ID',
            }
        }
        res = client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('ok'))
        self.assertEqual(data.get('pointsEarned'), 10)  # Only STRESS_L1 scored

    def test_unbounded_text_payload_is_safely_truncated(self):
        """Verify 50 KB text payload is safely accepted and truncated to 10,000 characters."""
        from django.test import Client
        client = Client()
        url = f'/api/v1/surveys/{self.survey.access_uuid}/submit/'
        huge_text = 'A' * 50000
        payload = {
            'answers': {
                'STRESS_O1': huge_text,
            }
        }
        res = client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        ans = Answer.objects.filter(question=self.q_open).last()
        self.assertIsNotNone(ans)
        self.assertLessEqual(len(ans.text_value), 10000)
