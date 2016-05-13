from django.db import models
from django.template.defaultfilters import linebreaks
from django.utils import timezone
import hashlib
import os


max_name_length = 100
identifier_length = 20


def get_hash_value():
    return hashlib.sha224(os.urandom(64)).hexdigest()[:identifier_length]


def datetime_min():
    return timezone.make_aware(timezone.datetime.min,
                               timezone.get_default_timezone())


class HandoutEvent(models.Model):
    due_date = models.DateTimeField()

    @property
    def url_parameter(self):
        return '?event_id=%s' % self.id

    def __str__(self):
        return str(self.due_date)


class Candidate(models.Model):
    first_name = models.CharField(max_length=max_name_length)
    last_name = models.CharField(max_length=max_name_length)

    date_of_birth = models.DateField()

    @property
    def has_bicycle(self):
        try:
            return self.bicycle is not None
        except Bicycle.DoesNotExist:
            return False

    @property
    def events_not_invited_to(self):
        event_ids_invited_to = self.invitations.all().values_list(
            'handout_event_id',
            flat=True)
        return HandoutEvent.objects.exclude(id__in=event_ids_invited_to)

    @classmethod
    def total_in_line(cls):
        return cls.objects.filter(bicycle__isnull=True).count()

    @classmethod
    def waiting_for_bicycle(cls, kind):
        without_bicycles = cls.objects.filter(bicycle__isnull=True)
        registered = without_bicycles.filter(user_registration__isnull=False)
        return filter(lambda c: c.user_registration.bicycle_kind == kind,
                      registered)

    def __str__(self):
        return " ".join((self.first_name, self.last_name,
                         str(self.date_of_birth)))


class User_Registration(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='user_registration')

    MALE = 1
    FEMALE = 2
    CHILD_SMALL = 3
    CHILD_BIG = 4

    BICYCLE_CHOICES = (
        (MALE, "men's bicycle"), (FEMALE, "ladies' bicycle"),
        (CHILD_SMALL, "children's bicycle small"),
        (CHILD_BIG, "children's bicycle big"))

    bicycle_kind = models.IntegerField(choices=BICYCLE_CHOICES)

    identifier = models.CharField(default=get_hash_value,
                                  max_length=identifier_length,
                                  primary_key=True)

    email = models.EmailField()
    email_validated = models.BooleanField(default=False)
    time_of_email_validation = models.DateTimeField(default=datetime_min)

    time_of_registration = models.DateTimeField(default=timezone.now)

    def number_in_line(self):
        cls = self.__class__
        i = 0
        for registration in cls.objects.filter(bicycle_kind=self.bicycle_kind):
            if not registration.candidate.has_bicycle:
                i += 1
            if self.candidate == registration.candidate:
                return i
        assert False, "Could not find object"

    def validate_email(self):
        if not self.email_validated:
            self.email_validated = True
            self.time_of_email_validation = timezone.now()
            self.save()

    def __str__(self):
        return " ".join((str(self.candidate), self.email,
                         self.get_bicycle_kind_display()))


class Invitation(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                  related_name='invitations')

    handout_event = models.ForeignKey(HandoutEvent,
                                      on_delete=models.CASCADE,
                                      related_name='invitations')

    time_of_invitation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s %s' % (self.candidate, self.handout_event)


class Bicycle(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE,
                                     related_name='bicycle')

    bicycle_number = models.PositiveIntegerField()
    lock_combination = models.PositiveIntegerField()
    color = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    general_remarks = models.TextField(default='')

    @property
    def url_parameter(self):
        return '?bicycle_id=%s' % self.id

    @property
    def information(self):
        l1 = "bicycle number: %s, color: %s, brand: %s" % (
            self.bicycle_number, self.color, self.brand)
        l2 = "lock combination: %s, general remarks: %s" % (
            self.lock_combination, self.general_remarks)
        return '%s\n%s' % (l1, l2)

    def __str__(self):
        return "number: %s color: %s  brand: %s" % \
            (self.bicycle_number, self.color, self.brand)
