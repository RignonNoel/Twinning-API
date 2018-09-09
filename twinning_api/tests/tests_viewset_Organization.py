import json

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from ..factories import UserFactory, AdminFactory
from ..models import Organization

User = get_user_model()


class OrganizationTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super(OrganizationTests, cls).setUpClass()
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

        self.organization.owners.add(self.user)
        self.organization.save()

    def test_create(self):
        """
        Ensure we can create an organization if user has permission.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "custom_organization",
            'description': 'long description',
            'godson_value': "description for godson",
            'godfather_value': 'description for godfather',
            'city': 'random_city',
            'country': 'random_country',
            'owners': ['http://testserver/users/1'],
        }

        response = self.client.post(
            reverse('organization-list'),
            data,
            format='json',
        )

        content = {
            'name': "custom_organization",
            'description': 'long description',
            'godson_value': "description for godson",
            'godfather_value': 'description for godfather',
            'city': 'random_city',
            'country': 'random_country',
            'url': 'http://testserver/organizations/2',
            'id': 2,
            'logo': None,
            'categories': [],
            'owners': ['http://testserver/users/1'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate_name(self):
        """
        Ensure we can't create an organization with same name.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "random_organization",
            'description': 'long description',
            'godson_value': "description for godson",
            'godfather_value': 'description for godfather',
            'city': 'random_city',
            'country': 'Random_Country',
            'owners': ['http://testserver/users/1']
        }

        response = self.client.post(
            reverse('organization-list'),
            data,
            format='json',
        )

        content = {'name': ['This field must be unique.']}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_field(self):
        """
        Ensure we can't create an organization when required field are missing.
        """
        self.client.force_authenticate(user=self.admin)

        data = {}

        response = self.client.post(
            reverse('organization-list'),
            data,
            format='json',
        )

        content = {
            'name': ['This field is required.'],
            'description': ['This field is required.'],
            'godson_value': ['This field is required.'],
            'godfather_value': ['This field is required.'],
            'owners': ['This field is required.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_field(self):
        """
        Ensure we can't create an organization with invalid fields.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': ("invalid",),
            'description': ("invalid",),
            'godson_value': ("invalid",),
            'godfather_value': ("invalid",),
            'city': ("invalid",),
            'country': ("invalid",),
            'owners': ("invalid",),
        }

        response = self.client.post(
            reverse('organization-list'),
            data,
            format='json',
        )

        content = {
            'name': ['Not a valid string.'],
            'description': ['Not a valid string.'],
            'godson_value': ['Not a valid string.'],
            'godfather_value': ['Not a valid string.'],
            'city': ['Not a valid string.'],
            'country': ['Not a valid string.'],
            'owners': ['Invalid hyperlink - No URL match.'],
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        """
        Ensure we can update an organization.
        """
        self.client.force_authenticate(user=self.admin)

        data = {
            'name': "new_organization",
            'description': 'new description',
            'godson_value': "new description for godson",
            'godfather_value': 'new description for godfather',
            'city': 'new_city',
            'country': 'new_Country',
            'owners': ['http://testserver/users/1']
        }

        response = self.client.put(
            reverse(
                'organization-detail',
                kwargs={'pk': 1},
            ),
            data,
            format='json',
        )

        content = {
            'city': 'new_city',
            'country': 'new_Country',
            'description': 'new description',
            'godson_value': "new description for godson",
            'id': 1,
            'logo': None,
            'categories': [],
            'owners': ['http://testserver/users/1'],
            'godfather_value': 'new description for godfather',
            'name': "new_organization",
            'url': 'http://testserver/organizations/1'
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """
        Ensure we can delete an organization.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            reverse(
                'organization-detail',
                kwargs={'pk': 1},
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list(self):
        """
        Ensure we can list organizations as an unauthenticated user.
        """

        response = self.client.get(
            reverse('organization-list'),
            format='json',
        )

        content = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'city': 'random_city',
                'country': 'random_country',
                'description': 'long description',
                'godson_value': "description for godson",
                'id': 1,
                'logo': None,
                'categories': [],
                'owners': ['http://testserver/users/1'],
                'godfather_value': 'description for godfather',
                'name': "random_organization",
                'url': 'http://testserver/organizations/1'
            }]
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read(self):
        """
        Ensure we can read an organization as an unauthenticated user.
        """

        response = self.client.get(
            reverse(
                'organization-detail',
                kwargs={'pk': 1},
            ),
        )

        content = {
            'city': 'random_city',
            'country': 'random_country',
            'description': 'long description',
            'godson_value': "description for godson",
            'id': 1,
            'logo': None,
            'categories': [],
            'owners': ['http://testserver/users/1'],
            'godfather_value': 'description for godfather',
            'name': "random_organization",
            'url': 'http://testserver/organizations/1'
        }

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_non_existent_organization(self):
        """
        Ensure we get not found when asking for an organization
        that doesn't exist.
        """

        response = self.client.get(
            reverse(
                'organization-detail',
                kwargs={'pk': 999},
            ),
        )

        content = {'detail': 'Not found.'}

        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
