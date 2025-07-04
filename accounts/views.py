from django.shortcuts import render , redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse



def register(request):
    if request.method == 'POST':
        print("CSRF Token from cookie:", request.META.get("CSRF_COOKIE"))  # Debug
        print("CSRF Token from POST:", request.POST.get('csrfmiddlewaretoken'))  # Debug
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            #USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Veuillez activer votre compte'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject , message , to=[to_email])
            send_email.send()

            #messages.success(request,f"{first_name.capitalize()} {last_name.capitalize()}, merci de votre inscription. Nous vous avons envoyé un e-mail de vérification à votre adresse e-mail. Veuillez le vérifier !")
            return redirect('/accounts/login/?command=verification&email='+email)
        # Si le formulaire n'est pas valide, il sera passé au template avec les erreurs
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a bien été activé. Vous pouvez maintenant vous connecter.")
        return redirect('login')
    else:
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
        return render(request, 'accounts/activation_invalid.html')

def login(request):
    if request.method == 'POST':
        # Use .get() for safer access and provide default empty string
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Check if fields are not empty
        if not email or not password:
            messages.error(request, 'Veuillez remplir tous les champs')
            return redirect('login')
        
        # Authenticate user
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:  # Fixed: was 'is None' before
            auth.login(request, user)
            messages.success(request, 'Vous êtes maintenant connecté.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants de connexion invalides')
            return redirect('login')
    
    return render(request, 'accounts/login.html')
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request , 'Vous êtes déconnecté.')
    return redirect('login')

@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Réinitialisation du mot de passe'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject , message , to=[to_email])
            send_email.send()
            messages.success(request ,'Un e-mail de réinitialisation du mot de passe a été envoyé.')
            return redirect('login')
        else:
            messages.error(request , 'Adresse e-mail introuvable!') 
            return redirect('forgotPassword') 
    return render(request,'accounts/forgotPassword.html')


def resetpassword_validate(request,uidb64 , token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request , 'Veuillez réinitialiser votre mot de passe')
        return redirect('resetPassword')
    else:
        messages.error(request,'Ce lien a expiré')
        return redirect('login')


def resetPassword(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(request, 'Lien invalide ou expiré.')
            return redirect('login')

        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, 'Mot de passe réinitialisé avec succès')
            return redirect('login')
        else:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return redirect('resetPassword', uidb64=uidb64, token=token)

    else:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account.objects.get(pk=uid)
        except:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            context = {
                'uid': uidb64,
                'token': token,
            }
            return render(request, 'accounts/resetPassword.html', context)
        else:
            messages.error(request, 'Lien invalide ou expiré.')
            return redirect('login')
