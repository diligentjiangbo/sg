from django.db import models

# Create your models here.

#全量服务表结构
class Service(models.Model):
  service_id = models.CharField(max_length=20)
  scene_id = models.CharField(max_length=20)
  dfa = models.CharField(max_length=20)
  create_time = models.DateTimeField('service create time')
  
  def __str__(self):
    return "%s-%s-%s"%(self.service_id,self.scene_id,self.dfa)
    
  class Meta:
    unique_together = ("service_id", "scene_id", "dfa")
    
#环境表结构
class Environment(models.Model):
  name = models.CharField(max_length=20, primary_key=True)
  desc = models.CharField(max_length=50)
  zk_idc1 = models.CharField(max_length=50)
  zk_idc2 = models.CharField(max_length=50)
  namesrv = models.CharField(max_length=50)
  broker_idc1 = models.CharField(max_length=50)
  broker_idc2 = models.CharField(max_length=50)
  cluster_name_idc1 = models.CharField(max_length=50)
  cluster_name_idc2 = models.CharField(max_length=50)
  idc1_code = models.CharField(max_length=10, verbose_name='idc1的编号')
  idc2_code = models.CharField(max_length=10, verbose_name='idc2的编号')
  rdfa_list = models.CharField(max_length=50, verbose_name='虚拟RDFA列表')
  zk_root_path = models.CharField(max_length=50, verbose_name='zk的根地址')
  orgId = models.CharField(max_length=10, verbose_name='法人号')
  broadcast = models.CharField(max_length=20, verbose_name='广播地址')
  
  def __str__(self):
    return "%s(%s)"%(self.name, self.desc)
    
# 和环境关联的服务表结构
class ServiceEnv(models.Model):
  # env = models.ForeignKey(Environment, on_delete=models.CASCADE)
  # 应用层做校验，这里直接放环境字段
  env = models.CharField(max_length=20)
  service_id = models.CharField(max_length=20)
  scene_id = models.CharField(max_length=20)
  dfa = models.CharField(max_length=20)
  zk_type = models.NullBooleanField()
  giraffe_type = models.NullBooleanField()
  create_time = models.DateTimeField('service create time')
  
  def __str__(self):
    return "%s(%s-%s-%s)"%(self.env,self.service_id,self.scene_id,self.dfa)
    
  class Meta:
    unique_together = ("env", "service_id", "scene_id", "dfa")