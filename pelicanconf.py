import datetime

CURRENT_YEAR = datetime.datetime.now().year

AUTHOR = "Ashwini Chaudhary(Monty)"
SITENAME = "Ashwini's blog"
SITEURL = ""

PATH = "content"

TIMEZONE = "America/Toronto"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
GITHUB_URL = "http://github.com/ashwch/"

DISPLAY_PAGES_ON_MENU = True


TWITTER_USERNAME = "suicide_chewie"
GITHUB_USERNAME = "ashwch"
STACKOVERFLOW_ADDRESS = "https://stackoverflow.com/users/846892/ashwini-chaudhary"
AUTHOR_WEBSITE = "http://ashwch.com"
AUTHOR_BLOG = "http://ashwch.com"
LINKEDIN_ADDRESS = "https://www.linkedin.com/in/ashwch/"
INSTAGRAM_USERNAME = "suicide_chewbacca"

DEFAULT_PAGINATION = 5
ABOUT_PAGE = "/pages/about.html"
PROJECTS_PAGE = "/pages/projects.html"
SHOW_ARCHIVES = True

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# THEME = 'themes/pelican-haerwu-theme'
OUTPUT_PATH = "output"
PATH = "content"


# Conf related to https://github.com/pelican-plugins/read-more
SUMMARY_MAX_LENGTH = 127
READ_MORE_LINK = "<span></span>"


# Footer info
LICENSE_URL = "https://github.com/ashwch/ashwch.github.io/blob/master/LICENSE"
LICENSE_NAME = "MIT"

CURRENT_YEAR = datetime.datetime.now().year

# Static files configuration
STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}}
