from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, ButtonHolder
from crispy_forms.bootstrap import FormActions
from django import forms
from django.forms.fields import DateField
from django.forms.widgets import SelectDateWidget
from django_filters import FilterSet
from django_filters.filters import ChoiceFilter, MethodFilter
from django.db.models import Q
from operator import or_
from functools import reduce

from register.models import Candidate, Bicycle, UserRegistration


EMPTY_CHOICE = ('', '---------'),


class CandidateFilter(FilterSet):
    name = MethodFilter(action='name_filter', help_text="")
    status = ChoiceFilter(choices=EMPTY_CHOICE + Candidate.CANDIDATE_STATUS,
                          help_text="")
    bicycle_kind = ChoiceFilter(name='user_registration__bicycle_kind',
                                choices=EMPTY_CHOICE +
                                UserRegistration.BICYCLE_CHOICES,
                                help_text="")

    def __init__(self, *args, **kwargs):
        super(CandidateFilter, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'

        layout = Div(Div(Div(Field('name'),
                         css_class='col-xs-12 col-md-5'),
                     Div(Field('status'),
                         css_class='col-xs-12 col-md-3'),
                     Div(Field('bicycle_kind'),
                         css_class='col-xs-12 col-md-4'),
                     css_class='row'),
                     FormAction(Submit('submit', 'Filter'))
                 )

        self.helper.layout = Layout(*layout)


    class Meta:
        model = Candidate
        fields = ['name', 'status', 'bicycle_kind']

    def name_filter(self, queryset, value):
        if value:
            return queryset.filter(
                    reduce(or_, (Q(first_name__icontains=name) |
                                 Q(last_name__icontains=name)
                                 for name in value.split()))
            )
        else:
            return queryset


class HandoutDateWidget(SelectDateWidget):

    def __init__(self, *args, **kwargs):
        min_year = Bicycle.objects.earliest(
            'date_of_handout').date_of_handout.year
        max_year = Bicycle.objects.latest(
            'date_of_handout').date_of_handout.year
        super(HandoutDateWidget, self).__init__(
            years=range(min_year, max_year + 1)[::-1], *args, **kwargs)


class BicycleForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BicycleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'

        layout = Div(Div(Field('date_of_handout_begin'),
                         css_class='col-xs-12 col-md-6'),
                     Div(Field('date_of_handout_end'),
                         css_class='col-xs-12 col-md-6'))

        self.helper.layout = Layout(*layout)

        self.helper.add_input(Submit('submit', 'Filter',
                                     css_class='btn-info'))

    def clean(self):
        for date_id in ['date_of_handout_begin', 'date_of_handout_end']:
            date_as_str = self.cleaned_data.get(date_id)
            DateField().to_python(date_as_str)


class BicycleFilter(FilterSet):
    date_of_handout_begin = MethodFilter(widget=HandoutDateWidget,
                                         help_text="")
    date_of_handout_end = MethodFilter(widget=HandoutDateWidget, help_text="")

    class Meta:
        form = BicycleForm
        model = Bicycle
        fields = ['date_of_handout_begin', 'date_of_handout_end']

    # pylint: disable= no-self-use
    def filter_date_of_handout_begin(self, queryset, value):
        return queryset.filter(
            date_of_handout__gt=DateField().to_python(value))

    def filter_date_of_handout_end(self, queryset, value):
        return queryset.filter(
            date_of_handout__date__lte=DateField().to_python(value))
