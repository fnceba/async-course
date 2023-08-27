from django.urls import path
from ates_auth.views import v_auth, v_parse_token

urlpatterns = [
    path('', v_auth),
    path('api/parse_token', v_parse_token),
]
