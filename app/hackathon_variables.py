HACKATHON_NAME = 'HackUPC'
HACKATHON_DESCRIPTION = 'Join us for BarcelonaTech\'s hackathon. 36h.'
HACKATHON_ORG = 'Hackers@UPC'
HACKATHON_START_DATE = '12/12/2012'
HACKATHON_END_DATE = '14/12/2012'
HACKATHON_LOCATION = 'Barcelona'

HACKATHON_CONTACT_EMAIL = 'contact@hackupc.com'
HACKATHON_SOCIALS = {'Facebook': ('https://www.facebook.com/hackupc', 'bi-facebook'),
                     'Instagram': ('https://www.instagram.com/hackupc/', 'bi-instagram'),
                     'Twitter': ('https://twitter.com/hackupc', 'bi-twitter'),
                     'Youtube': ('https://www.youtube.com/channel/UCiiRorGg59Xd5Sjj9bjIt-g', 'bi-youtube'),
                     'Twitch': ('https://www.twitch.tv/hackersupc?lang=es', 'bi-twitch'),
                     'Github': ('https://github.com/HackAssistant', 'bi-github'), }
if HACKATHON_CONTACT_EMAIL:
    HACKATHON_SOCIALS['Contact'] = ('mailto:' + HACKATHON_CONTACT_EMAIL, 'bi-envelope')

HACKATHON_LANDING = 'https://hackupc.com'
REGEX_HACKATHON_ORGANIZER_EMAIL = "^.*@hackupc\.com$"
HACKATHON_ORGANIZER_EMAILS = []
APP_NAME = 'MyHackUPC'
SERVER_EMAIL = 'MyHackUPC <server@my.hackupc.com>'
ADMINS = [('Admins', 'devs@hackupc.com')]

SUPPORTED_RESUME_EXTENSIONS = ['.pdf']
FRIENDS_MAX_CAPACITY = None

REQUIRE_PERMISSION_SLIP_TO_UNDER_AGE = True
SUPPORTED_PERMISSION_SLIP_EXTENSIONS = ['.pdf']
PARTICIPANT_CAN_UPLOAD_PERMISSION_SLIP = True

ATTRITION_RATE = 1.5
