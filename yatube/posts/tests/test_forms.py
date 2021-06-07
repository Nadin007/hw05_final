import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User


class TestCreateNewPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create a record in the database
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create(
            first_name="Dima", last_name="Smirnov", username="Dimon",
            email="dimon@gmail.com")
        cls.group_check = Group.objects.create(
            title='Unstoppable',
            description='For people who are ready to conquer the world.',
            slug='group-slug2'
        )
        cls.post_check = Post.objects.create(
            text='I will do it!',
            author=cls.author,
            group=cls.group_check
        )
        # Create a form to check attributes
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Recursively delete the temp after the tests are completed
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = TestCreateNewPostForm.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''A valid form creates a post'''
        post_count = Post.objects.count()
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_img,
            content_type='image/jpg'
        )
        form_data = {
            'text': 'Unique text to check if post has been created!',
            'group': TestCreateNewPostForm.group_check.id,
            'author': TestCreateNewPostForm.author,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # checking the work of the redirect
        self.assertRedirects(response, reverse('index'))
        # checking if the number of posts has increased
        self.assertEqual(Post.objects.count(), post_count + 1)
        # checking if post with our slug has been created
        self.assertEqual(
            len(Post.objects.filter(
                text=form_data['text'],
                group=TestCreateNewPostForm.group_check,
                author=TestCreateNewPostForm.author
            )), 1
        )

    def test_text_label(self):
        text_label = TestCreateNewPostForm.form.fields['text'].label
        self.assertEqual(text_label, 'Введите текст сообщения')

    def test_group_help_text(self):
        group_label = TestCreateNewPostForm.form.fields['group'].label
        self.assertEqual(group_label, 'Выберите группу для публикации')

    def test_edit_post(self):
        '''when you edit a post through a form on the page

        /<username>/<post_id>/edit/, the corresponding record
        in the database changes.
        '''
        post_count = Post.objects.count()
        form_data = {
            'text': TestCreateNewPostForm.post_check.text + ' EDITED',
            'group': TestCreateNewPostForm.group_check.id,
        }
        response = self.authorized_client.post(
            reverse('edit', kwargs={
                'post_id': TestCreateNewPostForm.post_check.id,
                'username': TestCreateNewPostForm.post_check.author.username
            }),
            data=form_data,
            follow=True
        )
        # checking the work of the redirect
        self.assertRedirects(response, reverse(
            'post',
            kwargs={
                'post_id': TestCreateNewPostForm.post_check.id,
                'username': TestCreateNewPostForm.post_check.author.username
            }))
        # checking if the number of posts has not increased
        self.assertEqual(Post.objects.count(), post_count)
        # checking if post with our slug has been changed
        self.assertEqual(
            Post.objects.get(pk=TestCreateNewPostForm.post_check.id).text,
            form_data['text']
        )

    def test_leave_comment(self):
        '''A valid form creates a comment'''
        count_comm = Comment.objects.count()
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': self.user.username,
                'post_id': TestCreateNewPostForm.post_check.id
            }),
            data={'text': 'Ok!'},
            Follow=True
        )
        self.assertEqual(
            count_comm + 1, Comment.objects.filter(
                post_id=TestCreateNewPostForm.post_check.id).count()
        )
        self.assertEqual(
            response.url,
            f'/{self.user.username}/{TestCreateNewPostForm.post_check.id}/'
        )
        self.assertEqual(len(Post.objects.filter(comments__text='Ok!')), 1)
