DEBUG = False

ADMINS = []

TIME_ZONE = "America/Chicago"

LANGUAGE_CODE = "en-us"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

FILE_UPLOAD_DIRECTORY_PERMISSIONS = None

DATE_FORMAT = "N j, Y"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2

AUTH_USER_MODEL = "auth.User"

LOGIN_URL = "/accounts/login/"

CSRF_COOKIE_PATH = "/"
