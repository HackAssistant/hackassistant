# Email

Class that creates the mails and subjects from the template/mails folder
In debug mode the mail is stored in `mails/[name]` folder otherwise it sends the email to `list_mails`.

Also converts from HTML to Plain text email messages in order if some participant inbox doesn't support HTML.
Examples can be seen in every `emails.py` from any application.

## EmailList

Optimization of the Email feature thanks that sends all the emails at once. 
You need to add the emails on the Class instance and then send them all at the same moment.

**Please use this if you are planning on sending massive emails or just more than 5.**
