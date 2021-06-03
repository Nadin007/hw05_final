from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class YatubeURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(first_name="Dima",
                                         last_name="Smirnov",
                                         username="Dimon",
                                         email="dimon@gmail.com")
        cls.author_2 = User.objects.create(first_name="Vika",
                                           last_name="Varlamova",
                                           username="Viktoria",
                                           email="vika@gmail.com")
        # create a record in the database to check the availability of the
        # address /username/post_id/, /username/post_id/edit/, /username/
        Post.objects.create(
            text='I love dogs so much!',
            author=cls.author,
        )
        cls.group_check = Group.objects.create(
            title='Unstoppable',
            description='For people who are ready to conquer the world.',
            slug='group-slug'
        )

    def setUp(self):
        # Create an unauthorized client
        self.guest_client = Client()
        # Create an authorized client
        self.user = YatubeURLTests.author
        self.user_2 = YatubeURLTests.author_2
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)
        self.post_id = Post.objects.filter(author=self.user)[0].id

    # Check public pages
    def test_url_for_availability_for_all_visitors(self):
        """The pages "/", "/about/author/", "/about/tech/",

        "/auth/signup/", "/username/", "/username/post_id/"
        are available to any user.
        """
        page_addresses = [
            '/',
            '/about/author/',
            '/about/tech/',
            '/auth/signup/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post_id}/',
        ]
        for address in page_addresses:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 200)

    def test_url_post_edit_code_status_for_guest_client(self):
        """The page '/username/post_id/edit/'

        redirects an unauthorized user.
        """
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post_id}/edit/')
        self.assertEqual(response.status_code, 302)

    # Check the availability of pages for an authorized users
    def test_url_for_availability_for_authorized_author(self):
        """The pages '/username/', '/username/post_id/', '/username/post_id/edit/',

        '/new/', "/", group/<slug:slug>/ are available
        to an authorized user.
        """
        page_addresses = (f'/{self.user.username}/',
                          f'/{self.user.username}/{self.post_id}/',
                          f'/{self.user.username}/{self.post_id}/edit/',
                          '/new/',
                          '/',
                          '/group/group-slug/')
        for adress in page_addresses:
            response = self.authorized_client.get(adress)
            self.assertEqual(response.status_code, 200)

    def test_url_edit_post_for_availability_for_authorized_visitors(self):
        '''Page '/username/post_id/edit/' redirects the authorized

        user if he/she is not the author of the post.
        '''
        page_adress = f'/{self.user.username}/{self.post_id}/edit/'
        response = self.authorized_client_2.get(page_adress, follow=True)
        self.assertRedirects(
            response, f'/{self.user.username}/{self.post_id}/')

    def test_url_edit_post_redirects_unauthorized_visitors(self):
        '''Page '/username/post_id/edit/' redirects the unauthorized client to

        the  signup page.
        '''
        page_adress = f'/{self.user.username}/{self.post_id}/edit/'
        response = self.guest_client.get(page_adress, follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{self.user.username}/{self.post_id}/edit/')

    # Checking called templates for each address
    def test_urls_uses_correct_template(self):
        """The URL uses the appropriate template"""
        templates_url_names = [
            ('index.html', '/'),
            ('about/author.html', '/about/author/'),
            ('about/tech.html', '/about/tech/'),
            ('signup.html', '/auth/signup/'),
            ('profile.html', f'/{self.user.username}/'),
            ('post.html', f'/{self.user.username}/{self.post_id}/'),
            ('new_post.html', f'/{self.user.username}/{self.post_id}/edit/'),
            ('new_post.html', '/new/'),
        ]
        for template, address in templates_url_names:
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_for_404(self):
        """The server returns 404 status code if page doesn't exist."""
        response = self.guest_client.get('/404/')
        self.assertEqual(response.status_code, 404)
