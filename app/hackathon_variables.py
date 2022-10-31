HACKATHON_NAME = 'BitsxlaMarató'
HACKATHON_DESCRIPTION = 'Join us for BarcelonaSolidary\'s hackathon. 16h.'
HACKATHON_ORG = 'FIB and Hackers@UPC'

HACKATHON_CONTACT_EMAIL = 'bitsxlamarato@fib.upc.edu'
HACKATHON_SOCIALS = {
    'Facebook FIB': ('https://www.facebook.com/fib.upc/', 'bi-facebook'),
    'Instagram FIB': ('https://www.instagram.com/fib.upc/', 'bi-instagram'),
    'Twitter FIB': ('https://twitter.com/fib_upc', 'bi-twitter'),
    'Facebook Hackers@UPC': ('https://www.facebook.com/hackersupc', 'bi-facebook'),
    'Instagram Hackers@UPC': ('https://www.instagram.com/hackersupc/', 'bi-instagram'),
    'Twitter Hackers@UPC': ('https://twitter.com/hackersupc', 'bi-twitter'),
    'Youtube Hackers@UPC': ('https://www.youtube.com/c/HackersUPC', 'bi-youtube'),
    'Twitch Hackers@UPC': ('https://www.twitch.tv/hackersupc', 'bi-twitch'),
    'Github BitsxlaMarató': ('https://github.com/BitsxlaMarato', 'bi-github'),
}
if HACKATHON_CONTACT_EMAIL:
    HACKATHON_SOCIALS['Contact'] = ('mailto:' + HACKATHON_CONTACT_EMAIL, 'bi-envelope')

HACKATHON_LANDING = 'https://www.fib.upc.edu/ca/la-marato'
HACKATHON_ORGANIZER_EMAILS = []
APP_NAME = 'MyBits'
SERVER_EMAIL = 'MyBits <bitsxlamarato@hackersatupc.org>'
ADMINS = [('Admins', 'devs@hackupc.com')]

SUPPORTED_RESUME_EXTENSIONS = ['.pdf']
