from django.contrib import admin

from review.models import Vote, FileReview

admin.site.register(Vote)
admin.site.register(FileReview)
