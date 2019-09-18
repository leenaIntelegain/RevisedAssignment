from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    # quantity = forms.IntegerField(initial=0)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

 
class CreateUserForm(UserCreationForm):
    # username = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2')
        field_classes = {'email': forms.EmailField}


    def clean_remove(self):
        cleaned_data = super(UserCreationForm, self).clean()
        remove = cleaned_data.get('remove', None)
        if remove:
            self.fields['username'].required=False
 
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError("This field is required.")
        if User.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError("Email is taken.")
        return self.cleaned_data['email']
 
    def save(self, request):
 		
        user = super(CreateUserForm, self).save(commit=False)
        user.is_active = True
        user.save()
        return user