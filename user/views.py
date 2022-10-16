from axes.handlers.proxy import AxesProxyHandler
from axes.helpers import get_client_ip_address, get_cool_off
from axes.models import AccessAttempt
from axes.utils import reset_request
from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from app.mixins import TabsViewMixin
from user import emails
from user.forms import LoginForm, UserProfileForm, ForgotPasswordForm, SetPasswordForm, \
    RegistrationForm, RecaptchaForm
from user.mixins import LoginRequiredMixin, EmailNotVerifiedMixin
from user.models import User
from user.tokens import AccountActivationTokenGenerator


class AuthTemplateViews(TabsViewMixin, TemplateView):
    template_name = 'auth.html'
    names = {
        'login': 'log in',
        'register': 'register',
    }
    forms = {
        'login': LoginForm,
        'register': RegistrationForm,
    }

    def get_current_tabs(self, **kwargs):
        return [('Log in', reverse('login')), ('Register', reverse('register'))]

    def redirect_successful(self):
        next_ = self.request.GET.get('next', reverse('home'))
        if next_[0] != '/':
            next_ = reverse('home')
        return redirect(next_)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.redirect_successful()
        return super().get(request, *args, **kwargs)

    @property
    def get_url_name(self):
        return resolve(self.request.path_info).url_name

    def get_form_class(self):
        return self.forms.get(self.get_url_name)

    def get_form(self):
        form_class = self.get_form_class()
        return form_class()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': self.get_form(), 'auth': self.names.get(self.get_url_name, 'register')})
        if getattr(settings, 'RECAPTCHA_%s' % self.get_url_name.upper(), False) and RecaptchaForm.active():
            context.update({'recaptcha_form': RecaptchaForm(request=self.request)})
        return context

    def forms_are_valid(self, form, context):
        if getattr(settings, 'RECAPTCHA_%s' % self.get_url_name.upper(), False) and RecaptchaForm.active():
            recaptcha_form = RecaptchaForm(self.request.POST, request=self.request)
            if not recaptcha_form.is_valid():
                context.update({'recaptcha_form': recaptcha_form})
                return False
        return form.is_valid()


class Login(AuthTemplateViews):
    def add_axes_context(self, context):
        if not AxesProxyHandler.is_allowed(self.request):
            ip_address = get_client_ip_address(self.request)
            attempt = AccessAttempt.objects.get(ip_address=ip_address)
            time_left = (attempt.attempt_time + get_cool_off()) - timezone.now()
            minutes_left = int((time_left.total_seconds() + 59) // 60)
            axes_error_message = _('Too many login attempts. Please try again in %s minutes.') % minutes_left
            context.update({'blocked_message': axes_error_message})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_axes_context(context)
        return context

    def post(self, request, **kwargs):
        form = LoginForm(request.POST)
        context = self.get_context_data(**kwargs)
        if self.forms_are_valid(form, context):
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(email=email, password=password, request=request)
            if user and user.is_active:
                auth.login(request, user)
                reset_request(request)
                messages.success(request, _('Successfully logged in!'))
                return self.redirect_successful()
            elif getattr(request, 'axes_locked_out', False):
                return redirect(reverse('login'))
            else:
                form.add_error(None, _('Incorrect username or password. Please try again.'))
        form.reset_status_fields()
        context.update({'form': form})
        return self.render_to_response(context)


class Register(Login):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': RegistrationForm(), 'auth': 'register'})
        context.pop("blocked_message", None)
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        form = RegistrationForm(request.POST)
        recaptcha = RecaptchaForm(request.POST, request=request)
        if self.forms_are_valid(form, context):
            user = form.save()
            auth.login(request, user)
            emails.send_verification_email(request=request, user=user)
            messages.success(request, _('Successfully registered!'))
            return self.redirect_successful()
        context.update({'form': form, 'recaptcha_form': recaptcha})
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
            uid = User.decode_encoded_pk(kwargs.get('uid'))
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
            uid = User.decode_encoded_pk(self.kwargs.get('uid'))
            user = User.objects.get(pk=uid)
            context.update({'user': user})
        except User.DoesNotExist:
            form.add_error(None, _('Invalid link'))
        context.update({'form': form, 'new': self.request.GET.get('new', None)})
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
