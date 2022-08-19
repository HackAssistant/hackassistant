from django.contrib import auth, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from app.mixins import TabsViewMixin
from user import emails
from user.forms import LoginForm, UserProfileForm, ForgotPasswordForm, SetPasswordForm, \
    RegistrationForm
from user.mixins import LoginRequiredMixin, EmailNotVerifiedMixin
from user.models import User
from user.tokens import AccountActivationTokenGenerator
from user.verification import check_client_ip, reset_tries, check_recaptcha


class Login(TabsViewMixin, TemplateView):
    template_name = 'auth.html'

    def redirect_successful(self):
        next_ = self.request.GET.get('next', reverse('home'))
        if next_[0] != '/':
            next_ = reverse('home')
        return redirect(next_)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.redirect_successful()
        return super().get(request, *args, **kwargs)

    def get_current_tabs(self):
        return [('Log in', reverse('login')), ('Register', reverse('register'))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': LoginForm(), 'auth': 'log in'})
        return context

    @check_client_ip
    def post(self, request, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid() and request.client_req_is_valid:
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(email=email, password=password)
            if user and user.is_active:
                auth.login(request, user)
                reset_tries(request)
                messages.success(request, _('Successfully logged in!'))
                return self.redirect_successful()
            else:
                form.add_error(None, _('Incorrect username or password. Please try again.'))
        if not request.client_req_is_valid:
            form.add_error(None, _('Too many login attempts. Please try again in 5 minutes.'))
        context = self.get_context_data(**kwargs)
        form.reset_status_fields()
        context.update({'form': form})
        return self.render_to_response(context)


class Register(Login):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': RegistrationForm(), 'auth': 'register'})
        return context

    @check_recaptcha
    def post(self, request, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            user = form.save()
            auth.login(request, user)
            emails.send_verification_email(request=request, user=user)
            messages.success(request, _('Successfully registered!'))
            return self.redirect_successful()
        context = self.get_context_data(**kwargs)
        context.update({'form': form})
        return self.render_to_response(context)


class Logout(View):
    def get(self, request, **kwargs):
        auth.logout(request)
        messages.success(request, _('Successfully logged out!'))
        return self.redirect_successful()

    def redirect_successful(self):
        next_ = self.request.GET.get('next', reverse('login'))
        if next_[0] != '/':
            next_ = reverse('login')
        return redirect(next_)


class Profile(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': UserProfileForm(instance=self.request.user)})
        return context

    def post(self, request, **kwargs):
        delete = request.POST.get('delete', '')
        if delete != '' and delete == request.user.email:
            request.user.set_unknown()
            request.user.save()
            auth.logout(request)
            messages.success(request, _('User deleted!'))
            return redirect('login')
        form = UserProfileForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile changed!'))
            return redirect('profile')
        context = self.get_context_data(**kwargs)
        context.update({'form': form})
        return self.render_to_response(context)


class NeedsVerification(EmailNotVerifiedMixin, TemplateView):
    template_name = 'needs_verification.html'

    def post(self, request, **kwargs):
        emails.send_verification_email(request=request, user=request.user)
        messages.success(request, "Verification email successfully sent")
        return redirect('home')


class VerifyEmail(EmailNotVerifiedMixin, View):
    def get(self, request, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs.get('uid')))
            user = User.objects.get(pk=uid)
            if request.user.is_authenticated and request.user != user:
                messages.warning(request, _("Trying to verify wrong user. Log out please!"))
                return redirect('home')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.warning(request, _("This user no longer exists. Please sign up again!"))
            return redirect('register')
        if AccountActivationTokenGenerator().check_token(user=user, token=kwargs.get('token')):
            messages.success(request, _("Email verified!"))
            user.email_verified = True
            user.save()
            return redirect('home')
        else:
            messages.error(request, _("Email verification url has expired. Log in so we can send it again!"))
        return redirect('needs_verification')


class ForgotPassword(TemplateView):
    template_name = 'forgot_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': ForgotPasswordForm(), 'success': self.request.GET.get('success', 'false') == 'true'})
        return context

    def post(self, request, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data.get('email')
                user = User.objects.get(email=email)
                emails.send_password_reset_email(request=request, user=user)
            except User.DoesNotExist:
                pass
            messages.success(request, 'Email sent if it exists!')
            return redirect(reverse('forgot_password') + '?success=true')
        context = self.get_context_data(**kwargs)
        context.update({'form': form})
        return self.render_to_response(context)


class ChangePassword(TemplateView):
    template_name = 'password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SetPasswordForm()
        try:
            uid = force_str(urlsafe_base64_decode(self.kwargs.get('uid')))
            user = User.objects.get(pk=uid)
            context.update({'user': user})
        except User.DoesNotExist:
            form.add_error(None, _('Invalid link'))
        context.update({'form': form})
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        form = SetPasswordForm(request.POST)
        if form.is_valid() and context.get('user', None) is not None:
            form.save(context.get('user'))
            context.update({'success': True})
        else:
            context.update({'form': form})
        return self.render_to_response(context)
