from django.conf.urls import url

from . import views

app_name = "route"
urlpatterns = [
  #name属性方便html页面写url
  url(r'^$', views.index, name='index'),
  url(r'^service/$', views.service, name='service'),
  url(r'^add_service/$', views.add_service, name='add_service'),
  url(r'^service_add/$', views.service_add, name='service_add'),
  url(r'^uploadH/$', views.uploadH, name='uploadH'),
  url(r'^upload/$', views.upload, name="upload"),
  url(r'^add_envH/$', views.add_envH, name='add_envH'),
  url(r'^add_env/$', views.add_env, name='add_env'),
  url(r'^env/$', views.env, name='env'),
  url(r'^publish2env/$', views.publish2env, name='publish2env'),
  url(r'^get_env/$', views.get_env, name='get_env'),
  url(r'^env_info/(?P<env>.*)/$', views.env_info, name='env_info'),
  url(r'^env2zk/(?P<env>.*)/$', views.env2zk, name='env2zk'),
  url(r'^env2giraffe/(?P<env>.*)/$', views.env2giraffe, name='env2giraffe'),
  url(r'^delete_service/(?P<id>.*)/$', views.delete_service, name='delete_service'),
  url(r'^delete_env/(?P<name>.*)/$', views.delete_env, name='delete_env'),
  url(r'^init_env/(?P<name>.*)/$', views.init_env, name='init_env')
]