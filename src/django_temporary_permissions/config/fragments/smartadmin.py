# Add this to settings.INSTALLED_APPS
from django.urls.conf import path, include

SMART_ADMIN_APPS = [
    "django_sysinfo",  # optional
    "adminactions",  # optional
    "adminfilters",  # optional
    "admin_extra_buttons",  # optional

    "smart_admin.apps.SmartLogsConfig",  # optional:  log application
    'smart_admin.apps.SmartTemplateConfig',
    "smart_admin.apps.SmartAuthConfig",  # optional: django.contrib.auth enhancements
    "smart_admin.apps.SmartConfig",  # optional: django.contrib.auth enhancements

]

SMART_ADMIN_SECTIONS = {
    'Accounting': [
        'core.Invoice',
        'core.InvoiceEntry',
    ],
    'Core': [
        'core.City',
        'core.Client',
        'core.Country',
        'core.Project',
        'core.Resource',
    ],
    'Missions': [
        'core.Mission',
        'core.ExpenseCategory',
        'core.Expense',
        'core.PaymentCategory',
        'core.DocumentType',
        'core.ReimbursementCategory',
        'core.Reimbursement',
    ],
    'Projects': [
        'core.Project',
        'core.Task',
        'core.Basket',
        'core.PO',
    ],
    'Timesheets': [
        'core.TimeEntry',
    ],
    '_hidden_': ['sites'],
    'Security': [
        'auth',
        'admin.LogEntry',
        'social_django',
        'core.UserProfile',
        'core.User',
        'token_blacklist'
    ],
    'Configuration': [
        'constance',
        'flags',
        'currencies'
    ]
}

SMART_ADMIN_URLS = [
    path('adminactions/', include('adminactions.urls')),
]


# add some bookmark
SMART_ADMIN_BOOKMARKS = [('GitHub', 'https://github.com/saxix/django-smart-admin')]

# no special permissions to see bookmarks
SMART_ADMIN_BOOKMARKS_PERMISSION = None

# add 'profile' link on the header
SMART_ADMIN_PROFILE_LINK = True

# display all users action log, not only logged user
SMART_ADMIN_ANYUSER_LOG = True