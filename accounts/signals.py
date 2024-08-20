from django.contrib.gis.geoip2 import GeoIP2
from accounts.models import HistoryOfEntries, Verification
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver



def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

@receiver(user_logged_in)
def add_entry_info(request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    user_agent = request.user_agent
    system = user_agent.os.family
    g = GeoIP2()
    
    if ip == '127.0.0.1':
        country = 'localhost'
        city = 'localhost'
    else:
        try:
            country = g.country(ip)['country_name']
            city = g.city(ip)['city']
        except:
            return "Country or city not found"
    
    update_last_login(sender=user, user=user)
    obj = HistoryOfEntries(user=user, ip=ip, device=system, address=f"{city}, {country}")
    obj.save()
   
    try:
        obj = Verification.objects.get(phone_number=user.phone_number)
        obj.step_reset = ''
        obj.save()
    except Verification.DoesNotExist:
        pass
