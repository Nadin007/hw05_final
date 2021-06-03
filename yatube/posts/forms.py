from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст сообщения',
            'group': 'Выберите группу для публикации',
            'image': 'Загрузите картинку',
        }


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Введите текст комментария',
        }
