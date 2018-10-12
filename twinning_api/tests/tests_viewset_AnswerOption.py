import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from ..factories import UserFactory, AdminFactory
from ..models import Question, Organization, AnswerOption

User = get_user_model()


class AnswerOptionTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(AnswerOptionTests, cls).setUpClass()
        cls.client = APIClient()
        cls.user = UserFactory()
        cls.admin = AdminFactory()

    def setUp(self):
        self.organization = Organization.objects.create(
            name='random_organization',
            description='long description',
            godson_value='description for godson',
            godfather_value='description for godfather',
            city='random_city',
            country='random_country',
        )

        self.question = Question.objects.create(
            title='question title',
            text_godson='question for godson',
            text_godfather='question for godfather',
            organization=self.organization
        )

        self.answerOption = AnswerOption.objects.create(
            answer_option='answer option',
            question=self.question
        )

        self.answerOption.save()

    def test_create(self):
        """
        Ensure we can create an answer option if user has permission.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'answer_option': "answer option 2",
            'question': 'http://testserver/questions/1',
        }

        response = self.client.post(
            reverse('answeroption-list'),
            data,
            format='json',
        )

        content = {
            'answer_option': "answer option 2",
            'question': 'http://testserver/questions/1',
            'url': 'http://testserver/answeroptions/2',
            'id': 2
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_field(self):
        """
        Ensure we can't create an answer option when required field are missing.
        """
        self.client.force_authenticate(user=self.admin)

        data = {}

        response = self.client.post(
            reverse('answeroption-list'),
            data,
            format='json',
        )

        content = {
            'answer_option': ['This field is required.'],
            'question': ['This field is required.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_field(self):
        """
        Ensure we can't create an answer option with invalid fields.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'answer_option': ("invalid",),
            'question': "invalid",
        }

        response = self.client.post(
            reverse('answeroption-list'),
            data,
            format='json',
        )

        content = {
            'answer_option': ['Not a valid string.'],
            'question': ['Invalid hyperlink - No URL match.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """
        Ensure we can update an answer option.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'answer_option': "answer option 3",
            'question': 'http://testserver/questions/1'
        }

        response = self.client.put(
            reverse(
                'answeroption-detail',
                kwargs={'pk': 1},
            ),
            data,
            format='json',
        )

        content = {
            'answer_option': "answer option 3",
            'question': 'http://testserver/questions/1',
            'id': 1,
            'url': 'http://testserver/answeroptions/1'
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Ensure we can delete an answer option.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'answeroption-detail',
                kwargs={'pk': 1},
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list(self):
        """
        Ensure we can list answer options as an unauthenticated user.
        """

        response = self.client.get(
            reverse('answeroption-list'),
            format='json',
        )

        content = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'answer_option': "answer option",
                'question': 'http://testserver/questions/1',
                'url': 'http://testserver/answeroptions/1',
                'id': 1
            }]
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_non_existent_question(self):
        """
        Ensure we get not found when asking for an answer option
        that doesn't exist.
        """

        response = self.client.get(
            reverse(
                'answeroption-detail',
                kwargs={'pk': 999},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
