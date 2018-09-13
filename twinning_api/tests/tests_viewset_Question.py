import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from ..factories import UserFactory, AdminFactory
from ..models import Question, Organization

User = get_user_model()


class QuestionTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(QuestionTests, cls).setUpClass()
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

        self.question.save()

    def test_create(self):
        """
        Ensure we can create a question if user has permission.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'title': "question title 2",
            'text_godson': "question for godson 2",
            'text_godfather': "question for godfather 2",
            'organization': 'http://testserver/organizations/1',
        }

        response = self.client.post(
            reverse('question-list'),
            data,
            format='json',
        )

        content = {
            'title': "question title 2",
            'text_godson': "question for godson 2",
            'text_godfather': "question for godfather 2",
            'url': 'http://testserver/questions/2',
            'severity': 0,
            'organization': 'http://testserver/organizations/1',
            'id': 2
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_field(self):
        """
        Ensure we can't create a question when required field are missing.
        """
        self.client.force_authenticate(user=self.admin)

        data = {}

        response = self.client.post(
            reverse('question-list'),
            data,
            format='json',
        )

        content = {
            'text_godson': ['This field is required.'],
            'text_godfather': ['This field is required.'],
            'organization': ['This field is required.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_field(self):
        """
        Ensure we can't create a question with invalid fields.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'title': ("invalid",),
            'text_godson': ("invalid",),
            'text_godfather': ("invalid",),
            'organization': "invalid",
        }

        response = self.client.post(
            reverse('question-list'),
            data,
            format='json',
        )

        content = {
            'title': ['Not a valid string.'],
            'text_godson': ['Not a valid string.'],
            'text_godfather': ['Not a valid string.'],
            'organization': ['Invalid hyperlink - No URL match.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """
        Ensure we can update a question.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'title': "question title 3",
            'text_godson': "question for godson 3",
            'text_godfather': "question for godfather 3",
            'organization': 'http://testserver/organizations/1'
        }

        response = self.client.put(
            reverse(
                'question-detail',
                kwargs={'pk': 1},
            ),
            data,
            format='json',
        )

        content = {
            'title': "question title 3",
            'text_godson': "question for godson 3",
            'text_godfather': "question for godfather 3",
            'severity': 0,
            'organization': 'http://testserver/organizations/1',
            'id': 1,
            'url': 'http://testserver/questions/1'
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Ensure we can delete a question.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'question-detail',
                kwargs={'pk': 1},
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list(self):
        """
        Ensure we can list questions as an unauthenticated user.
        """

        response = self.client.get(
            reverse('question-list'),
            format='json',
        )

        content = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'title': "question title",
                'text_godson': "question for godson",
                'text_godfather': "question for godfather",
                'severity': 0,
                'organization': 'http://testserver/organizations/1',
                'url': 'http://testserver/questions/1',
                'id': 1
            }]
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_non_existent_question(self):
        """
        Ensure we get not found when asking for a question
        that doesn't exist.
        """

        response = self.client.get(
            reverse(
                'question-detail',
                kwargs={'pk': 999},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
