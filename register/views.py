from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from django.http.response import HttpResponseRedirect
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView

from register.email import send_message_after_registration
from register.forms import RegistrationForm
from register.models import User_Registration, Candidate


def open_for_registration():
    # ToDo: move to general settings
    max_number_of_registrations = 200
    return Candidate.total_in_line() < max_number_of_registrations


class GreetingsView(View):
    template_name = 'register/greeting.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'open_for_registration': open_for_registration(),
                        'show_steps': True,
                        'step_1': 'class="active"'}
        return render(request, self.template_name, context_dict)


class RegistrationErrorUniquenessView(TemplateView):
    template_name = 'register/registration_error_uniqueness.html'


class RegistrationView(FormView):
    template_name = 'register/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('register:thanks')

    def form_valid(self, form):
        if not open_for_registration():
            raise Http404(
                "Currently it is not possible to register for a bicycle.")

        form_data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'date_of_birth': form.cleaned_data['date_of_birth']}

        candidate = Candidate.objects.create(**form_data)

        creation_dict = {'candidate': candidate,
                         'bicycle_kind': form.cleaned_data['bicycle_kind']}

        email = form.cleaned_data['email']
        phone_number = form.cleaned_data['phone_number']

        if not(email or phone_number):
            raise Http404("Please fill in at least email or phone_number.")

        if email:
            creation_dict['email'] = email
        if phone_number:
            creation_dict['phone_number'] = phone_number

        registration = User_Registration.objects.create(**creation_dict)

        send_message_after_registration(registration=registration,
                                        request=self.request)

        return super(RegistrationView, self).form_valid(form)

    def form_invalid(self, form):
        # print form.errors
        return super(RegistrationView, self).form_invalid(form)

    def get(self, request, *args, **kwargs):
        if not open_for_registration():
            raise Http404(
                "Currently it is not possible to register for a bicycle.")

        context_dict = {'choices': User_Registration.BICYCLE_CHOICES,
                        'show_steps': True,
                        'step_2': 'class="active"',
                        'form': RegistrationForm()}
        return render(request, self.template_name, context_dict)


class ThanksView(View):
    template_name = 'register/thanks.html'

    def get(self, request, *args, **kwargs):
        context_dict = {'number_in_line': Candidate.total_in_line(),
                        'show_steps': True,
                        'step_3': 'class="active"'}
        return render(request, self.template_name, context_dict)


class CurrentInLineView(View):
    template_name = 'register/current_in_line.html'

    def get(self, request, *args, **kwargs):
        identifier = request.GET.get('user_id')

        registration = get_object_or_404(
            User_Registration, identifier=identifier)
        registration.validate_email()

        context_dict = {
            'already_viewed': registration.email_validated,
            'number_in_line': registration.number_in_line(),
            'bicycle_kind': registration.get_bicycle_kind_display()}
        return render(request, self.template_name, context_dict)
