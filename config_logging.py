import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'
        },
        'simple_console': {
            'format': '%(message)s'
        },
        'email': {
            'format': '%(message)s\n\n%(asctime)s %(levelname)s %(name)s'
        },
        'push_notification':{
            'format': '%(message)s\n%(levelname)s %(name)s'
        }
    },
    'handlers': {
        # 'null': {
        #     'level':'DEBUG',
        #     'class':'django.utils.log.NullHandler',
        # },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple_console'
        },
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['special']
        # }

        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(ROOT_PATH, 'logs/MyMediaFolder.log'),
            'maxBytes': 10000,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'email': {
            'level': 'WARNING',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': ('192.168.1.3', 25),
            'fromaddr': 'admin@suhenky.com',
            'toaddrs': ['serafim@suhenky.com'],
            'subject': 'MyMediaLib log',
            'credentials': ('admin', 'outrun96#tints'),
            'secure': (),
            'formatter': 'email'
        },
        # 'push_notification': {
        #     'level': 'INFO',
        #     'class': 'util.logging_handlers.PushoverHandler',
        #     'formatter': 'push_notification',
        #     'api_token': POPOVER_API_TOKEN,
        #     'user_key': POPOVER_USER_KEY
        # }
    },
    'loggers': {
        'app': {
            # 'handlers':['console', 'file', 'email', 'push_notification'],
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        # 'files': {
        #     # 'handlers':['console', 'file', 'email', 'push_notification'],
        #     'handlers':['console'],
        #     'propagate': True,
        #     'level':'DEBUG',
        # },
        # 'devices': {
        #     # 'handlers':['console', 'file', 'email', 'push_notification'],
        #     'handlers':['console'],
        #     'propagate': True,
        #     'level':'DEBUG',
        # },
        # 'nas.find-torrents': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        # 'myproject.custom': {
        #     'handlers': ['console', 'mail_admins'],
        #     'level': 'INFO',
        #     'filters': ['special']
        # }
    }
}
