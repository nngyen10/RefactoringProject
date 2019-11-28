from datetime import timedelta
from django.db.models import Q


default_app_config = 'transsend.apps.TransSendConfig'


def get_permission_filter(user, *args, **kwargs):
    try:
        return user.mguser.getPermissionFilter(*args)
    except:
        return Q(pk=-1)


def get_model_fields(model, verbose=False, exclude=[]):
    exclude = ['id', 'created_at', 'updated_at', ] + exclude
    if not verbose:
        return [f.name for f in model._meta.fields if f.name not in exclude]
    else:
        return [f.verbose_name for f in model._meta.fields if f.name not in exclude]


def map_verbose_fields(model, reverse=False):
    """
    Return a dict with verbose_name => name
    Pass reverse = True to return name => verbose_name instead
    """
    res = {}
    fields = list(model._meta.fields) + list(model._meta.many_to_many)
    for f in fields:
        if f.name not in ['id', 'created_at', 'updated_at', ]:
            if not reverse:
                res[f.verbose_name] = f.name
            else:
                res[f.name] = f.verbose_name

    return res


MODE_CHOICES = (('Accessorial', 'Accessorial'),
                ('Air', 'Air'),
                ('Air Freight', 'Air Freight'),
                ('Balance Due', 'Balance Due'),
                ('Bulk', 'Bulk'),
                ('Drayage', 'Drayage'),
                ('Expedite', 'Expedite'),
                ('Flatbed', 'Flatbed'),
                ('Intermodal', 'Intermodal'),
                ('International', 'International'),
                ('LTL', 'LTL'),
                ('Last Mile', 'Last Mile'),
                ('Mixed', 'Mixed'),
                ('Ocean', 'Ocean'),
                ('Other', 'Other'),
                ('Parcel', 'Parcel'),
                ('Pool', 'Pool'),
                ('Rail', 'Rail'),
                ('Service Mode', 'Service Mode'),
                ('Small Package', 'Small Package'),
                ('Spot Quote', 'Spot Quote'),
                ('Truckload', 'Truckload'),
                )


def safe_add(current, days_to_add):
    new_date = current
    x = 0
    while x < days_to_add:
        new_date = new_date + timedelta(days=1)
        if new_date.weekday() in [5, 6, ]:
            pass
        else:
            x = x + 1
    return new_date


def safe_minus(current, days_to_subtract):
    new_date = current
    x = 0
    while x < days_to_subtract:
        new_date = new_date - timedelta(days=1)
        if new_date.weekday() in [5, 6, ]:
            pass
        else:
            x = x + 1
    return new_date


def safe_str(value):
    try:
        return str(value)
    except UnicodeEncodeError:
        return value.encode('ascii', 'ignore')
