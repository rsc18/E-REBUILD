import secrets


SECRET_KEY = secrets.token_urlsafe(16)   # '23422.14432017405'

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'sqlite:///erebuild.sqlite'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/erebuild_dup'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}
