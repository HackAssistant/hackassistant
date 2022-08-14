import os
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Class that creates the mails and subjects from the template/mails folder
# In debug mode the mail is stored in mails/[name] folder otherwise it sends the email to [list_mails]
# Author Arnau Casas Saez
class Email:

    def __init__(self, name, context, to, request, **kwargs) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.name = name
        self.list_mails = [to, ] if isinstance(to, str) else to
        self.request = request
        self.context = context
        self.__get_subject__()
        self.__get_content__()

    # Private method that renders and save the subject of the mail
    def __get_subject__(self):
        file_template = 'mails/%s.txt' % self.name
        self.subject = render_to_string(template_name=file_template, context=self.context, request=self.request)

    # Private method that renders and save the HTML content of the mail
    def __get_content__(self):
        file_template = 'mails/%s.html' % self.name
        self.html_message = render_to_string(template_name=file_template, context=self.context, request=self.request)
        self.plain_message = strip_tags(self.html_message)

    # Public method that sends the mail to [list_mails] if not debug else saves the file at mails folder
    def send(self):
        email_from = '%s Team <%s>' % (getattr(settings, 'HACKATHON_NAME', ''),
                                       getattr(settings, 'HACKATHON_CONTACT_EMAIL'))

        if settings.DEBUG:
            base_dir = getattr(settings, 'BASE_DIR', '')

            mails_folder = os.path.join(base_dir, 'mails')
            Path(mails_folder).mkdir(parents=True, exist_ok=True)
            path_mail_test = os.path.join(mails_folder, self.name)
            Path(path_mail_test).mkdir(parents=True, exist_ok=True)
            separator = '_'
            final_path = os.path.join(path_mail_test, separator.join(self.list_mails) + '.html')
            with open(final_path, "w", encoding='utf-8') as text_file:
                text_file.write(self.html_message)
        else:
            msg = EmailMultiAlternatives(subject=self.subject, body=self.plain_message, from_email=email_from,
                                         to=self.list_mails, **self.kwargs)
            msg.attach_alternative(self.html_message, "text/html")
            msg.content_subtype = "html"
            msg.send()
