
from django.db import models


class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GoogleTransitTimeCall(CommonInfo):
    ordernumber = models.CharField(max_length=45, null=True)
    shipper_city = models.CharField(max_length=45, null=True)
    shipper_stateprovince = models.CharField(max_length=45, null=True)
    shipper_postalcode = models.CharField(max_length=45, null=True)
    consignee_city = models.CharField(max_length=45, null=True)
    consignee_stateprovince = models.CharField(max_length=45, null=True)
    consignee_postalcode = models.CharField(max_length=45, null=True)
    servicedays = models.IntegerField(null=True)
    miles = models.FloatField(default=0.0)


MASTER_ADDRESS_TIMEZONE_MAP = {
    '4': 'Canada/Atlantic',
    '5': 'US/Eastern',
    '6': 'US/Central',
    '7': 'US/Mountain',
    '8': 'US/Pacific',
    '9': 'US/Alaska',
    '10': 'US/Hawaii',
    '11': 'US/Samoa',
}


class MasterAddress(CommonInfo):
    city = models.CharField(max_length=35, null=True, blank=True)
    city_alias_abbreviation = models.CharField(max_length=13, null=True, blank=True)
    city_alias_code = models.CharField(max_length=5, null=True, blank=True)
    city_alias_mixed_case = models.CharField(max_length=35, null=True, blank=True)
    city_alias_name = models.CharField(max_length=35, null=True, blank=True)
    city_delivery_indicator = models.CharField(max_length=1, null=True, blank=True)
    city_mixed_case = models.CharField(max_length=35, null=True, blank=True)
    city_state_key = models.CharField(max_length=6, null=True, blank=True)
    city_type = models.CharField(max_length=1, null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    stateprovince = models.CharField(max_length=2, null=True, blank=True)
    stateprovince_fullname = models.CharField(max_length=35, null=True, blank=True)
    postalcode = models.CharField(max_length=10)
    countrycode = models.CharField(max_length=10, null=True, blank=True)
    timezone = models.CharField(max_length=2, null=True, blank=True)
    daylightsaving = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = u'master_address'

    def get_timezone(self):
        return MASTER_ADDRESS_TIMEZONE_MAP.get(self.timezone, 'UTC')
