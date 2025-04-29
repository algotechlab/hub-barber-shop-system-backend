from django import forms
from django.contrib.auth.models import User

class UserRegisterForm(forms.ModelForm):
    phone = forms.CharField(max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Caso tenha um model de perfil, como UserProfile, crie-o aqui
            # UserProfile.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user