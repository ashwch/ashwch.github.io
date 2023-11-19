AUTHOR = 'Ashwini Chaudhary(Monty)'
SITENAME = 'Ashwini\'s blog'
SITEURL = ""

PATH = "content"

TIMEZONE = 'America/Toronto'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
GITHUB_URL = "http://github.com/ashwch/"

DISPLAY_PAGES_ON_MENU = True

# Social widget
SOCIAL = (
    ("Stack Overflow", "https://stackoverflow.com/users/846892/ashwini-chaudhary"),
    ("Unsplash", "https://unsplash.com/@suicide_chewbacca"),
    ("twitter", "https://twitter.com/suicide_chewie"),
)

DEFAULT_PAGINATION = 5
ABOUT_PAGE = '/pages/about.html'

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# THEME = 'themes/pelican-haerwu-theme'
OUTPUT_PATH = 'output'
PATH = 'content'


# Conf related to https://github.com/pelican-plugins/read-more
SUMMARY_MAX_LENGTH = 127
READ_MORE_LINK = '<span></span>'
