import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image
from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=os.path.join(
            settings.BASE_DIR, 'posts', 'tests'))
        img_path = os.path.join(settings.MEDIA_ROOT, '12.jpg')
        image_file = Image.new("RGB", size=(1, 1), color=(255, 0, 0))
        image_file.save(img_path, 'JPEG')
        image = SimpleUploadedFile(
            name='123.jpg', content=open(
                img_path, 'rb').read(), content_type='image/jpeg')

        cls.author = User.objects.create(
            first_name="Dima", last_name="Smirnov", username="Dimon",
            email="dimon@gmail.com")
        # create a record in the database
        cls.group_check = Group.objects.create(
            title='Unstoppable',
            description='For people who are ready to conquer the world.',
            slug='group-slug2',
        )
        cls.post = Post.objects.create(
            text='I will do it!',
            author=cls.author,
            group=cls.group_check,
            image=image
        )
        cls.group = Group.objects.create(
            title='Boats Boats Boats',
            description='This page is devoted to boats.',
            slug='group-slug',
        )
        for num in range(0, 21):
            Post.objects.create(
                text='I love boats so much!' + str(num),
                author=cls.author,
                group=cls.group if num % 2 == 0 else None,
                image=image
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Recursively delete the temp after the tests are completed
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = PostPagesTest.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_2 = User.objects.create_user(username='Lolita')
        self.user_3 = User.objects.create_user(username='Pikachy')
        self.authorized_client_2 = Client()
        self.authorized_client_3 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_3.force_login(self.user_3)

    def test_pages_uses_correct_template(self):
        '''URL uses the appropriate template'''
        templates_page_names = {
            reverse('index'): 'index.html',
            reverse('group', kwargs={'slug': 'group-slug'}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reversed_name, templete in templates_page_names.items():
            with self.subTest(templreversed_nameete=reversed_name):
                response = self.authorized_client.get(reversed_name)
                self.assertTemplateUsed(response, templete)

    def test_index_page_shows_correct_context_without_group(self):
        '''The index template consists of the appropriate values.'''
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(
            response.context['page'][1].author.get_full_name(),
            'Dima Smirnov')
        self.assertEqual(response.context['page'][1].pub_date,
                         Post.objects.all()[1].pub_date)
        self.assertEqual(
            response.context['page'][1].text, 'I love boats so much!19'
        )
        self.assertIsNone(
            response.context['page'][1].group
        )
        self.assertIsNotNone(
            response.context['page'][1].image
        )

    def test_index_page_shows_correct_context_with_group(self):
        '''The index template consists of the appropriate values.'''
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(
            response.context['page'][0].author.get_full_name(),
            'Dima Smirnov')
        self.assertEqual(response.context['page'][0].pub_date,
                         Post.objects.all()[0].pub_date)
        self.assertEqual(
            response.context['page'][0].text, 'I love boats so much!20'
        )
        self.assertEqual(
            response.context['page'][0].group, PostPagesTest.group
        )
        self.assertIsNotNone(
            response.context['page'][0].image
        )

    def test_group_page_shows_correct_context(self):
        '''The group template consists of the appropriate values.'''
        response = self.guest_client.get(reverse('group',
                                         kwargs={'slug': 'group-slug'}))
        self.assertEqual(
            response.context['group'].description,
            'This page is devoted to boats.')
        self.assertEqual(
            response.context['page'][0].author.get_full_name(), 'Dima Smirnov'
        )
        self.assertEqual(
            response.context['page'][0].pub_date,
            Post.objects.all()[0].pub_date)
        self.assertEqual(
            response.context['page'][0].text, 'I love boats so much!20')
        self.assertIsNotNone(
            response.context['page'][0].image
        )

    def test_group_page_does_not_show_uncorrect_context(self):
        '''The group template does not display posts without a group

        or with unsuitable group.
        '''
        response = self.guest_client.get(reverse('group',
                                         kwargs={'slug': 'group-slug'}))
        self.assertNotIn(
            Post.objects.filter(group=None)[0], response.context['page']
        )
        self.assertIn(
            Post.objects.filter(group=PostPagesTest.group)[0],
            response.context['page']
        )
        self.assertNotIn(
            Post.objects.filter(group=PostPagesTest.group_check)[0],
            response.context['page']
        )

    def test_form_field_correct_context(self):
        '''The new_post and edit_post templates are rendered with the

        appropriate context.
        '''
        reversed_names = (
            reverse('new_post'),
            reverse('edit', kwargs={
                'post_id': PostPagesTest.post.id,
                'username': PostPagesTest.author.username}),
        )
        for reverse_name in reversed_names:
            response = self.authorized_client.get(reverse_name)
            form_field = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }
            for value, expected in form_field.items():
                with self.subTest(value=value, url=reverse_name):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_view_post_page_shows_correct_context(self):
        '''The post template is rendered with the appropriate context.'''
        response = self.authorized_client.get(
            reverse(
                'post', kwargs={'post_id': PostPagesTest.post.id,
                                'username': PostPagesTest.author.username}))
        self.assertEqual(
            response.context['user'].username, 'Dimon'
        )
        self.assertEqual(
            response.context['author'].get_full_name(), 'Dima Smirnov'
        )
        self.assertEqual(
            response.context['post_count'], Post.objects.count()
        )
        self.assertEqual(response.context['post'],
                         PostPagesTest.post)

    def test_profile_page_shows_correct_context(self):
        '''The profile template is rendered with the appropriate context.'''
        response = self.guest_client.get(
            reverse(
                'profile', kwargs={'username': PostPagesTest.author.username}))
        self.assertEqual(
            response.context['author'].get_full_name(), 'Dima Smirnov'
        )
        self.assertEqual(
            response.context['post_count'], Post.objects.count()
        )
        self.assertEqual(
            response.context['page'][0], Post.objects.all()[0]
        )

    def test_pages_contains_ten_posts(self):
        ''' The paginator shows the corresponding number of posts.'''
        reversed_names = (
            reverse('index'),
            reverse('group', kwargs={'slug': 'group-slug'}),
            reverse('profile', kwargs={
                'username': PostPagesTest.post.author.username}),
        )
        for reversed_name in reversed_names:
            with self.subTest(url=reversed_name):
                response = self.authorized_client.get(reversed_name)
                self.assertEqual(len(
                    response.context.get('page').object_list), 10)

    def test_new_post_appears_in_followers_feed(self):
        """A new user post appears in the feed of those who are subscribed to it

        and does not appear in the feed of those who are not subscribed to it.
        """
        self.authorized_client.get(f'/{self.user_2.username}/follow/')
        self.authorized_client_2.post(
            reverse('new_post'),
            data={'text': 'Hello from the other side!'}, follow=True)
        url = self.authorized_client.get('/follow/')
        self.assertEqual(url.context['page'][0].text,
                         'Hello from the other side!')
        url_2 = self.authorized_client_3.get('/follow/')
        self.assertEqual(len(url_2.context.get('page').object_list), 0)
