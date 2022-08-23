from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, F


class Vote(models.Model):
    MAX_VOTES = getattr(settings, 'MAX_VOTES', 5)
    TECH_WEIGHT = 0.2
    PERSONAL_WEIGHT = 0.8
    VOTES = [(i, str(i)) for i in range(1, MAX_VOTES + 1)]

    application = models.ForeignKey('application.Application', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    tech = models.IntegerField(choices=VOTES, null=True)
    personal = models.IntegerField(choices=VOTES, null=True)
    calculated_vote = models.FloatField(null=True, blank=True)

    def __str__(self):
        return '%s voted %s' % (self.user.get_full_name(), self.application.user.get_full_name())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        We are overriding this in order to standarize each review vote with the
        new vote.
        Also, we store a calculated vote for each vote so that we don't need to
        do it later.

        Thanks to Django awesomeness we do all the calculations with only 3
        queries to the database. 2 selects and 1 update. The performance is way
        faster than I thought.
        If improvements need to be done using a better DB than SQLite should
        increase performance. As long as the database can handle aggregations
        efficiently this will be good.

        By casassg
        """
        super().save(force_insert, force_update, using, update_fields)

        User = get_user_model()

        # only recalculate when values are different than None
        if not self.personal or not self.tech:
            return

        # Retrieve averages
        avgs = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg('vote__tech'),
            pers=Avg('vote__personal'))
        p_avg = round(avgs['pers'], 2)
        t_avg = round(avgs['tech'], 2)

        # Calculate standard deviation for each scores
        sds = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg((F('vote__tech') - t_avg) * (F('vote__tech') - t_avg)),
            pers=Avg((F('vote__personal') - p_avg) *
                     (F('vote__personal') - p_avg)))

        # Alternatively, if standard deviation is 0.0, set it as 1.0 to avoid
        # division by 0.0 in the update statement
        p_sd = round(sds['pers'], 2) or 1.0
        t_sd = round(sds['tech'], 2) or 1.0

        # Apply standarization. Standarization formula:
        # x(new) = (x - u)/o
        # where u is the mean and o is the standard deviation
        #
        # See this: http://www.dataminingblog.com/standardization-vs-
        # normalization/
        personal = self.PERSONAL_WEIGHT * (F('personal') - p_avg) / p_sd
        tech = self.TECH_WEIGHT * (F('tech') - t_avg) / t_sd
        Vote.objects.filter(user=self.user).update(calculated_vote=(personal + tech) * self.MAX_VOTES / 10)

    class Meta:
        unique_together = ('application', 'user')
