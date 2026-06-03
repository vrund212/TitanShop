

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



SECRET_KEY = '+)&mi89-=v@-7o=qvf-kq+v7)9j9@0r%a#*x!h+^o2ne3e6%^$'


DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
# Application definition

INSTALLED_APPS = [
    'shop.apps.ShopConfig',
     'blog',
    # 'shop'
    'TitanMarketplace',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'bootstrap_datepicker_plus',
    # 'markdownx',
    # 'markdown_deux',
    'zxcvbn_password',
    'profiles',
    'social_django',
    'order',
    'tfidf',
    'reviews',
    'matrixfactorization',

]
AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend'
]
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'TitanMarketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'TitanMarketplace.context_processors.language_ui',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'TitanMarketplace.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'


TIME_ZONE = 'America/Los_Angeles'
USE_TZ = True

USE_I18N = True

USE_L10N = True




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LOGIN_REDIRECT_URL = 'shophome'
SOCIAL_AUTH_URL_NAMESPACE = 'users:social'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '911875216013-m2t2lkpavpfaqmfk9ije51la0vgpd7ck.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'fLmXYRvv-pdbHzWDEl7KIL9a'

MEDIA_ROOT= os.path.join(BASE_DIR, 'media/')
MEDIA_URL= "/media/"
