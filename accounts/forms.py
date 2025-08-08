from django import forms
from .models import Account ,UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Entrez le mot de passe' , 
        'class' : 'form-control',

    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirmez le mot de passe',
        'class': 'form-control',

    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
    
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Les mots de passe ne correspondent pas!")
        
        return cleaned_data   
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email existe déjà!")
        return email  
    

    def __init__(self, *args , **kwargs):
        super(RegistrationForm , self).__init__(*args , **kwargs) 
        self.fields['first_name'].widget.attrs['placeholder'] = 'Entrer votre Prénom'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Entrer votre nom'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Entrer votre numéro de téléphone'
        self.fields['email'].widget.attrs['placeholder'] = 'Entrer votre adresse mail'


        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control' 
    


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name' , 'last_name' , 'phone_number')

    def __init__(self, *args , **kwargs):
        super(UserForm , self).__init__(*args , **kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control' 
    





class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address_line_1' , 'address_line_2' , 'city' , 'region')  

    def __init__(self, *args , **kwargs):
        super(UserProfileForm , self).__init__(*args , **kwargs) 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control' 
        
            