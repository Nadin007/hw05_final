from django.test import TestCase
from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create a record in the database
        cls.group = Group.objects.create(
            title='Dogs',
            description='For people who into dogs'
        )

    def test_object_name_is_title_field(self):
        '''__str__ group is the line with the content of group.title.'''
        test_group = GroupModelTest.group
        expected_object_name = test_group.title
        self.assertEqual(expected_object_name, str(test_group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create a record in the database
        author = User.objects.create(first_name="Victor", last_name="Victor",
                                     username="Vic", email="vic@gmail.com")
        cls.post = Post.objects.create(
            text='I love dogs so much!',
            author=author
        )

    def test_object_name_is_text_field(self):
        '''__str__ post is the line with the content of post.text[:15]'''
        test_post = PostModelTest.post
        expected_object_name = test_post.text[:15]
        self.assertEqual(expected_object_name, str(test_post))
