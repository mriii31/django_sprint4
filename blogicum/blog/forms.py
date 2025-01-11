from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm): #1.3 Поля is_published и pub_date в форме для постов
    class Meta:
        model = Post
        exclude = ('author',) #2.2 PostForm через exclude
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M', attrs={'type': 'datetime-local'}
            )
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
