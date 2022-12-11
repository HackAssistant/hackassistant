import os
import re
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Class that creates the mails and subjects from the template/mails folder
# In debug mode the mail is stored in mails/[name] folder otherwise it sends the email to [list_mails]
# Author Arnau Casas Saez
class Email:

    def __init__(self, name, context, to, request=None, **kwargs) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.name = name
        self.list_mails = [to, ] if isinstance(to, str) else to
        self.request = request
        self.context = context
        self.render_kwargs = {}
        if request is not None:
            self.render_kwargs['request'] = request
        self.__get_subject__()
        self.__get_content__()

    # Private method that renders and save the subject of the mail
    def __get_subject__(self):
        file_template = 'mails/%s.txt' % self.name
        self.subject = render_to_string(template_name=file_template, context=self.context, **self.render_kwargs)

    # Private method that renders and save the HTML content of the mail
    def __get_content__(self):
        file_template = 'mails/%s.html' % self.name
        self.html_message = render_to_string(template_name=file_template, context=self.context, **self.render_kwargs)
        self.__get_plain_text_from_html()

    # Private method that converts the html to plaintext
    def __get_plain_text_from_html(self):
        soup = BeautifulSoup(self.html_message, 'html.parser')
        html_mail_content = soup.find('div', id='email-content')  # We get only the email-content div
        html_mail_content.find('div', id='socials-content').clear()
        mail_content = strip_tags(html_mail_content)
        self.plain_text = re.sub(r'\n\n+', '\n\n', re.sub(r'\n[ \t\r\f\v]+', '\n',
                                                          re.sub(r'[ \t\r\f\v]+', ' ', mail_content).strip()))

    def __save_email_debug(self, path, extension):
        content = {'.html': self.html_message, '.txt': self.plain_text}.get(extension)
        separator = '_'
        final_path = os.path.join(path, separator.join(self.list_mails) + extension)
        with open(final_path, "w", encoding='utf-8') as text_file:
            text_file.write(content)

    # Public method that sends the mail to [list_mails] if not debug else saves the file at mails folder
    def send(self, immediate=True, fail_silently=False):
        email_from = getattr(settings, 'SERVER_EMAIL', '')

        if settings.DEBUG:
            base_dir = getattr(settings, 'BASE_DIR', '')

            mails_folder = os.path.join(base_dir, 'mails')
            Path(mails_folder).mkdir(parents=True, exist_ok=True)
            path_mail_test = os.path.join(mails_folder, self.name)
            Path(path_mail_test).mkdir(parents=True, exist_ok=True)
            self.__save_email_debug(path_mail_test, '.html')
            self.__save_email_debug(path_mail_test, '.txt')
            return 1
        else:
            mail = EmailMultiAlternatives(subject=self.subject, body=self.plain_text, from_email=email_from,
                                          to=self.list_mails, **self.kwargs)
            mail.attach_alternative(self.html_message, "text/html")
            if immediate:
                return mail.send(fail_silently=fail_silently)
            return mail


# Class that improves Email class for reduce connections and improve code readability
# Author Arnau Casas Saez
class EmailList:

    def __init__(self):
        super().__init__()
        self.massive_email_list = []

    # Public email to add an email to the list to send them
    def add(self, mail: Email):
        self.massive_email_list.append(mail.send(immediate=False))

    # Public sends all mails stored
    def send_all(self, fail_silently=False):
        if settings.DEBUG:
            return len(self.massive_email_list)
        else:
            connection = get_connection(fail_silently=fail_silently)
            return connection.send_messages(self.massive_email_list)
