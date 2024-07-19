from django.urls import path

from QRHome.views import login_page, logout_page, home, deactivate_code, generate, gen_2fa_code, \
    retrieve_2fa_code_image, scanner, debug_get, validate, authenticate, gen_multi_2fa_codes, generate_multi, check_key_count

app_name = 'home'
urlpatterns = [
    path('login', login_page),
    path('logout', logout_page),
    path('deactivate_code', deactivate_code),
    path('generate', generate),
    path('generate_multi', generate_multi),

    path('generate_2fa_code', gen_2fa_code),
    path('gen_multi_2fa_codes', gen_multi_2fa_codes),

    path('retrieve_2fa_code_image',retrieve_2fa_code_image),
    path('scanner', scanner),
    path('debug_get',debug_get),
    path('validate', validate),
    path('authenticate', authenticate),
    path('get_count', check_key_count),

    path('', home),


]