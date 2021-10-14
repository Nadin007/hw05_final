from django import forms
from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст сообщения',
            'group': 'Выберите группу для публикации',
            'image': 'Загрузите картинку',
        }


class CommentForm(forms.Form):
    parent_comment = forms.IntegerField(
        widget=forms.HiddenInput,
        required=False
    )
    text = forms.CharField(
        label="Share your opinion about it",
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 5})
    )


"""
    class Meta:
        model = Comment
        labels = {
            'text': 'Share your opinion about it',
        }
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 5})}"""
