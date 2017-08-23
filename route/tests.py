from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from route.models import Service

# Create your tests here.
# 单元测试时用的临时数据库，用完就删除，所以不能查询到真是数据，在需要使用数据时先创建

def create_obj():
  Service.objects.create(service_id='111', create_time=timezone.now())

class ViewTest(TestCase):
  def test(self):
    create_obj()
    #response = self.client.get('/route/test/')
    response = self.client.get(reverse('route:test'))
    print(response.content)
    print(response.status_code)
    #self.failUnlessEqual(b'hello world', response.content)
