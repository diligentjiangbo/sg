from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils import timezone

import re
import json
import socket

#从一个处理函数重定向到另一个处理函数
from django.core.urlresolvers import reverse

#json
from django.core import serializers

#分页
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#模板类
from .models import Service, Environment, ServiceEnv

#zk操作框架
from kazoo.client import KazooClient

#自定义解析文件函数
from file.file_analyze import analyze
#自定义zk工具
from zk.zk_tool import add_route, delete_route, createZkNode
#自定义giraffe工具
from giraffe.giraffe_tcp_tool import connect, close, create_topic, delete_broker_topic, delete_namesrv_topic

# Create your views here.
def index(request):
  s = say()
  print(s)
  return HttpResponse(s)
  
#显示service列表页面
def service(request):
  #获取所有数据
  service_list = Service.objects.order_by('-create_time').all()
  #每页显示10条，少于5条显示到上一页
  paginator = Paginator(service_list, 10, 5)
  #获取页数，不设置默认为第一页
  page = request.GET.get('page')
  
  try:
    services = paginator.page(page)
  except PageNotAnInteger:
    services = paginator.page(1)
  except EmptyPage:
    services = paginator.page(paginator.num_pages)
  
  
  template = loader.get_template('route/service.html')
  context = {
    'services': services,
    'paginator': paginator
  }
  return HttpResponse(template.render(context, request))
  
#增加service页面
def add_service(request):
  return render(request, 'route/add_service.html')
  
#增加service操作
def service_add(request):
  if request.method == 'POST':
    #service_id = request.POST["service_id"]
    service_id = request.POST.get('service_id')
    scene_id = request.POST.get('scene_id')
    dfa = request.POST.get('dfa')
    print(service_id," ",scene_id,"",dfa)
    service = Service(service_id=service_id, scene_id=scene_id, dfa=dfa, create_time=timezone.now())
    service.save()
  return HttpResponseRedirect("/route/service")
  
#跳转到上传文件页面
def uploadH(request):
  return render(request, "route/upload.html")
  
#处理上传文件
def upload(request):
  if request.method == "POST":
    myFile = request.FILES.get("myfile", None)
    if not myFile:
      return HttpResponse("no files for upload!")
    #fileData = myFile.read()
    #return HttpResponse(fileData)
    #line = myFile.readline()
    #while line:
      #print(line)
      #line = myFile.readline()
    retDict = analyze(myFile)
    result = retDict.get('result')
    if result == 0:
      add_set = retDict.get('add')
      delete_set = retDict.get('delete')
      service_list = list()
      if add_set:
        for service in add_set:
          service_id = service.service_id
          scene_id = service.scene_id
          dfa = service.dfa
          #判断是否存在，不存在则添加
          if not Service.objects.filter(service_id=service_id, scene_id=scene_id, dfa=dfa).exists():
            s = Service(service_id=service_id, scene_id=scene_id, dfa=dfa, create_time=timezone.now())
            service_list.append(s)
          else:
            print("service_id=",service_id," scene_id=",scene_id," dfa=",dfa,"已存在")         
          
      #批量插入
      if service_list:
        Service.objects.bulk_create(service_list)
        print("插入%d条"%(len(service_list)))
      
      #删除
      if delete_set:
        delete_count = 0
        for service in delete_set:
          service_id = service.service_id
          scene_id = service.scene_id
          dfa = service.dfa
          num_tuple = Service.objects.filter(service_id=service_id, scene_id=scene_id, dfa=dfa).delete()
          num = num_tuple[0]
          delete_count += num
          
        print("删除%d条"%delete_count)
  return HttpResponseRedirect("/route/service")
  
#跳转到新增环境页面
def add_envH(request):
  return render(request, 'route/add_env.html')
  
#处理新增环境请求
def add_env(request):
  if request.method == 'POST':
    name = request.POST.get('name')
    desc = request.POST.get('desc')
    zk_idc1 = request.POST.get('zk_idc1')
    zk_idc2 = request.POST.get('zk_idc2')
    namesrv = request.POST.get('namesrv')
    broker_idc1 = request.POST.get('broker_idc1')
    broker_idc2 = request.POST.get('broker_idc2')
    cluster_name_idc1 = request.POST.get('cluster_name_idc1')
    cluster_name_idc2 = request.POST.get('cluster_name_idc2')
    idc1_code = request.POST.get('idc1_code')
    idc2_code = request.POST.get('idc2_code')
    broadcast = request.POST.get('broadcast')
    env = Environment(name=name, desc=desc, zk_idc1=zk_idc1, zk_idc2=zk_idc2, namesrv=namesrv, broker_idc1=broker_idc1, broker_idc2=broker_idc2, cluster_name_idc1=cluster_name_idc1, cluster_name_idc2=cluster_name_idc2, broadcast=broadcast)
    env.zk_root_path = "/cn/onebank/gns/" + name
    env.idc1_code = idc1_code
    env.idc2_code = idc2_code
    idc1_rdfa_list = request.POST.getlist('idc1_rdfa_list')
    idc2_rdfa_list = request.POST.getlist('idc2_rdfa_list')
    rdfa_list = list()
    for rdfa in idc1_rdfa_list:
      rdfa_list.append(idc1_code + rdfa)
      
    for rdfa in idc2_rdfa_list:
      rdfa_list.append(idc2_code + rdfa)
      
    env.rdfa_list = ",".join(rdfa_list)
      
    env.save()
  return HttpResponseRedirect("/route/env")
  
#展示环境列表
def env(request):
  #获取所有数据
  env_list = Environment.objects.all()
  #每页显示10条，少于5条显示到上一页
  paginator = Paginator(env_list, 10, 5)
  #获取页数，不设置默认为第一页
  page = request.GET.get('page')

  try:
    envs = paginator.page(page)
  except PageNotAnInteger:
    envs = paginator.page(1)
  except EmptyPage:
    envs = paginator.page(paginator.num_pages)
  
  
  template = loader.get_template('route/env.html')
  context = {
    'envs': envs,
    'paginator': paginator
  }
  return HttpResponse(template.render(context, request))
  
#将服务发布至环境
def publish2env(request):
  if request.method == 'POST':
    env_list = request.POST.getlist('env_list')
    s_id = request.POST.get("id")
    print("s_id=%s"%(s_id))
    if env_list:
      #将全量表中不存在于环境相关表的导入，并将zk_type和giraffe_type置为True
      insert_list = list()
      if s_id:
        services = [Service.objects.get(pk=s_id)]
      else:
        services = Service.objects.all()
      for env in env_list:
        for service in services:
          if not ServiceEnv.objects.filter(env=env,service_id=service.service_id,scene_id=service.scene_id,dfa=service.dfa).exists():
            insert_list.append(ServiceEnv(env=env,service_id=service.service_id,scene_id=service.scene_id,dfa=service.dfa,zk_type=True,giraffe_type=True,create_time=timezone.now()))
      if insert_list:
        ServiceEnv.objects.bulk_create(insert_list)
      
      #将环境相关表中不存在于全量表的operate_type置为False
      for env in env_list:
        env_services = ServiceEnv.objects.filter(env=env)
        for env_service in env_services:
          if not Service.objects.filter(service_id=env_service.service_id,scene_id=env_service.scene_id,dfa=env_service.dfa).exists():
            ServiceEnv.objects.filter(env=env,service_id=env_service.service_id,scene_id=env_service.scene_id,dfa=env_service.dfa).update(zk_type=False,giraffe_type=False)
        
  return HttpResponseRedirect("/route/service")
  
#获取各环境信息
def get_env(request):
  envs = Environment.objects.all()
  envs_json = serializers.serialize("json", envs)
  return HttpResponse(envs_json, content_type="application/json")
  
#展示环境中的服务
def env_info(request, env):
  #获取所有数据
  serviceEnv_list = ServiceEnv.objects.filter(env=env).order_by('-create_time')
  #每页显示10条，少于5条显示到上一页
  paginator = Paginator(serviceEnv_list, 10, 5)
  #获取页数，不设置默认为第一页
  page = request.GET.get('page')

  try:
    services = paginator.page(page)
  except PageNotAnInteger:
    services = paginator.page(1)
  except EmptyPage:
    services = paginator.page(paginator.num_pages)
    
  return render(request, 'route/env_info.html', {"services":services,"env":env})
  
#将环境中的服务下发至zk
def env2zk(request, env):
  env_obj = Environment.objects.get(name=env)
  #获取idc编号，构造dfa区域和虚拟dfa的映射
  idc1_code = env_obj.idc1_code
  idc2_code = env_obj.idc2_code
  dfa_dict = {}
  dfa_dict.setdefault("RDFA", env_obj.rdfa_list)
  dfa_dict.setdefault("CDFA", idc1_code+"80")
  dfa_dict.setdefault("CM", idc1_code+"M0")
  dfa_dict.setdefault("CS", ",".join([idc1_code+"C0",idc2_code+"C0"]))
  dfa_dict.setdefault("DMZ", ",".join([idc1_code+"Z0",idc2_code+"Z0"]))
  dfa_dict.setdefault("ECA", ",".join([idc1_code+"E0",idc2_code+"E0"]))
  dfa_dict.setdefault("BM", idc1_code+"B0")
  dfa_dict.setdefault("MGMT", idc1_code+"G0")
  dfa_dict.setdefault("DA", idc1_code+"Z0")

  # 拿到根路径
  root_path = env_obj.zk_root_path + "/route"
  
  #拿到zk的信息，建立连接
  zk_idc1 = env_obj.zk_idc1
  zk_idc2 = env_obj.zk_idc2
  zk_list = list()
  print(zk_idc1)
  try:
    zk1 = KazooClient(zk_idc1)
    zk1.start()
    zk_list.append(zk1)
    if not zk_idc1 == zk_idc2:
      zk2 = KazooClient(zk_idc2)
      zk2.start()
      zk_list.append(zk2)
  except:  
    data = {}
    data.setdefault("code", "-1")
    data.setdefault("msg", "连接zk失败")
    return HttpResponse(json.dumps(data), content_type="application/json")
    
  add_serviceEnv = ServiceEnv.objects.filter(env=env,zk_type=True)
  #新增
  for service in add_serviceEnv:
    dfaList = dfa_dict.get(service.dfa).split(",")
    if dfaList:
      for client in zk_list:
        add_route(client, service.service_id, service.scene_id, dfaList, root_path)
      #修改operate_type
      ServiceEnv.objects.filter(pk=service.id).update(zk_type=None)
    else:
      print("%sdfa为空"%(service))
  delete_serviceEnv = ServiceEnv.objects.filter(env=env,zk_type=False)
  #删除
  for service in delete_serviceEnv:
    dfaList = dfa_dict.get(service.dfa).split(",")
    if dfaList:
      for client in zk_list:
        delete_route(client, service.service_id, service.scene_id, dfaList, root_path)
      #删除数据，要zk和giraffe的标志位都为None才能删除
      ServiceEnv.objects.filter(pk=service.id).update(zk_type=None)
      ServiceEnv.objects.filter(pk=service.id, zk_type=None, giraffe_type=None).delete()
    else:
      print("%sdfa为空"%(service))
      
  for zk in zk_list:
    zk.stop()
  
  return HttpResponseRedirect(reverse("route:env_info", kwargs={"env":env}))
  
#将环境中的服务下发至giraffe
def env2giraffe(request, env):
  env_obj = Environment.objects.get(name=env)
  #获取idc编号，构造dfa区域和虚拟dfa的映射
  idc1_code = env_obj.idc1_code
  idc2_code = env_obj.idc2_code
  dfa_dict = {}
  dfa_dict.setdefault("RDFA", env_obj.rdfa_list)
  dfa_dict.setdefault("CDFA", idc1_code+"80")
  dfa_dict.setdefault("CM", idc1_code+"M0")
  dfa_dict.setdefault("CS", ",".join([idc1_code+"C0",idc2_code+"C0"]))
  dfa_dict.setdefault("DMZ", ",".join([idc1_code+"Z0",idc2_code+"Z0"]))
  dfa_dict.setdefault("ECA", ",".join([idc1_code+"E0",idc2_code+"E0"]))
  dfa_dict.setdefault("BM", idc1_code+"B0")
  dfa_dict.setdefault("MGMT", idc1_code+"G0")
  dfa_dict.setdefault("DA", idc1_code+"Z0")
  
  #广播地址
  broadcast = env_obj.broadcast
  
  #拿到broker和namesrv的地址
  broker_idc1 = env_obj.broker_idc1
  broker_idc2 = env_obj.broker_idc2
  namesrv = env_obj.namesrv
  #地址之间用;分隔，将其分解存储在list中
  broker_idc1_list = list()
  broker_idc2_list = list()
  namesrv_list = list()
  for broker_idc1_addr in re.split(';', broker_idc1):
    try:
      ip_port = re.split(':', broker_idc1_addr)
      s = connect(ip_port[0], int(ip_port[1]))
      broker_idc1_list.append(s)
    except socket.error as e:
      print("cant connect to broker_idc1 addr=%s, error=%s"%(broker_idc1_addr, e))
      continue
  #如果idc1的地址等于idc2的地址就不用连接
  if not broker_idc1 == broker_idc2:
    for broker_idc2_addr in re.split(';', broker_idc2):
      try:
        ip_port = re.split(':', broker_idc2_addr)
        s = connect(ip_port[0], int(ip_port[1]))
        broker_idc2_list.append(s)
      except socket.error as e:
        print("cant connect to broker_idc2 addr=%s, error=%s"%(broker_idc2_addr, e))
        continue
  for namesrv_addr in re.split(';', namesrv):
    try:
      ip_port = re.split(':', namesrv_addr)
      s = connect(ip_port[0], int(ip_port[1]))
      namesrv_list.append(s)
    except socket.error as e:
      print("cant connect to namesrv addr=%s, error=%s"%(namesrv_addr, e))
      continue
      
  #判断是否建立连接成功
  if not broker_idc1_list:
    data = {}
    data.setdefault("code", "-2")
    data.setdefault("msg", "连接broker idc1失败")
    return HttpResponse(json.dumps(data), content_type="application/json")
  elif not broker_idc1 == broker_idc2 and not broker_idc2_list:
    data = {}
    data.setdefault("code", "-3")
    data.setdefault("msg", "连接broker idc2失败")
    return HttpResponse(json.dumps(data), content_type="application/json")
  elif not namesrv_list:
    data = {}
    data.setdefault("code", "-4")
    data.setdefault("msg", "连接namesrv失败")
    return HttpResponse(json.dumps(data), content_type="application/json")
    
  add_serviceEnv = ServiceEnv.objects.filter(env=env,giraffe_type=True)
  #新增
  for service in add_serviceEnv:
    dfaList = dfa_dict.get(service.dfa).split(",")
    if dfaList:
      for dfa in dfaList:
        topic = "-".join([dfa, service.service_id, service.scene_id])
        if dfa.startswith(idc1_code):
          for s in broker_idc1_list:
            create_topic(s, topic)
        else:
          for s in broker_idc2_list:
            create_topic(s, topic)
        #事件，创建对应的广播地址
        if len(service.service_id) > 5 and service.service_id[4] != '0':
          topic = "-".join([broadcast, service.service_id, service.scene_id])
          for s in broker_idc1_list:
            create_topic(s, topic)
          
      #修改giraffe_type
      ServiceEnv.objects.filter(pk=service.id).update(giraffe_type=None)
    else:
      print("%sdfa为空"%(service))
      
  delete_serviceEnv = ServiceEnv.objects.filter(env=env,giraffe_type=False)
  #删除
  for service in delete_serviceEnv:
    dfaList = dfa_dict.get(service.dfa).split(",")
    if dfaList:
      for dfa in dfaList:
        topic = "-".join([dfa, service.service_id, service.scene_id])
        if dfa.startswith(idc1_code):
          for s in broker_idc1_list:
            delete_broker_topic(s, topic)
          for s in namesrv_list:
            delete_namesrv_topic(s, topic)
        else:
          for s in broker_idc2_list:
            delete_broker_topic(s, topic)
          for s in namesrv_list:
            delete_namesrv_topic(s, topic)
        #删除事件topic
        if len(service.service_id) > 5 and service.service_id[4] != '0':
          topic = "-".join([broadcast, service.service_id, service.scene_id])
          for s in broker_idc1_list:
            delete_broker_topic(s, topic)
          for s in namesrv_list:
            delete_namesrv_topic(s, topic)
      #删除数据，要zk和giraffe的标志位都为None才能删除
      ServiceEnv.objects.filter(pk=service.id).update(giraffe_type=None)
      ServiceEnv.objects.filter(pk=service.id, giraffe_type=None, zk_type=None).delete()
    else:
      print("%sdfa为空"%(service))
      
      
  for s in broker_idc1_list:
    close(s)
  for s in broker_idc2_list:
    close(s)
  for s in namesrv_list:
    close(s)
      
  
  # s = connect('localhost', 6609)
  # create_topic(s, "hello")
  # close(s)
  
  return HttpResponseRedirect(reverse("route:env_info", kwargs={"env":env}))
  
#删除一个服务
def delete_service(request, id):
  Service.objects.filter(pk=id).delete()
  return HttpResponseRedirect(reverse("route:service"))
  
#删除一个环境
def delete_env(request, name):
  env_obj = Environment.objects.get(name=name)
  root_path = env_obj.zk_root_path
  zk_idc1 = env_obj.zk_idc1
  zk_idc2 = env_obj.zk_idc2

  # 初始化zk连接
  zk_list = list()
  print(zk_idc1)
  try:
    zk1 = KazooClient(zk_idc1)
    zk1.start()
    zk_list.append(zk1)
    if not zk_idc1 == zk_idc2:
      zk2 = KazooClient(zk_idc2)
      zk2.start()
      zk_list.append(zk2)
  except:
    data = {}
    data.setdefault("code", "-1")
    data.setdefault("msg", "连接zk失败")
    zk_list.clear()
    #return HttpResponse(json.dumps(data), content_type="application/json")

  # 删除该环境的根节点
  for zk in zk_list:
    if zk.exists(root_path):
      zk.delete(root_path, recursive=True)


  # 删除数据库信息
  Environment.objects.filter(pk=name).delete()
  return HttpResponseRedirect(reverse("route:env"))

# 初始化环境
def init_env(request, name):
  env_obj = Environment.objects.get(name=name)
  root_path = env_obj.zk_root_path
  zk_idc1 = env_obj.zk_idc1
  zk_idc2 = env_obj.zk_idc2
  idc1_code = env_obj.idc1_code
  idc2_code = env_obj.idc2_code
  broadcast = env_obj.broadcast
  rdfa_list = env_obj.rdfa_list

  # 初始化zk连接
  zk_list = list()
  print(zk_idc1)
  try:
    zk1 = KazooClient(zk_idc1)
    zk1.start()
    zk_list.append(zk1)
    if not zk_idc1 == zk_idc2:
      zk2 = KazooClient(zk_idc2)
      zk2.start()
      zk_list.append(zk2)
  except:
    data = {}
    data.setdefault("code", "-1")
    data.setdefault("msg", "连接zk失败")
    return HttpResponse(json.dumps(data), content_type="application/json")

  # 创建根节点
  root_value = idc1_code + "," + idc2_code
  for zk in zk_list:
    if not zk.exists(root_path):
      createZkNode(zk, root_path, root_value.encode("utf8"))
    else:
      zk.set(root_path, root_value.encode("utf8"))

  # 初始化broadcast
  broadcast_path = root_path + "/broadcast"
  for zk in zk_list:
    if not zk.exists(broadcast_path):
      createZkNode(zk, broadcast_path, broadcast.encode("utf8"))
    else:
      zk.set(broadcast_path, broadcast.encode("utf8"))

  # 初始化cdfa
  cdfa_path = root_path + "/cdfa"
  cdfa_value = idc1_code + "80"
  for zk in zk_list:
    if not zk.exists(cdfa_path):
      createZkNode(zk, cdfa_path, cdfa_value.encode("utf8"))
    else:
      zk.set(cdfa_path, cdfa_value.encode("utf8"))

  # 初始化cmdfa
  cmdfa_path = root_path + "/cmdfa"
  cmdfa_value = idc1_code + "M0"
  for zk in zk_list:
    if not zk.exists(cmdfa_path):
      createZkNode(zk, cmdfa_path, cmdfa_value.encode("utf8"))
    else:
      zk.set(cmdfa_path, cmdfa_value.encode("utf8"))

  # 创建rdfa节点，不赋值
  rdfa_path = root_path + "/rdfa"
  # rdfa_value = "[" + ",".join(rdfa_list) + "]"
  for zk in zk_list:
    if not zk.exists(rdfa_path):
      createZkNode(zk, rdfa_path, "".encode("utf8"))

  # 创建appId节点，不赋值
  appId_path = root_path + "/appId"
  for zk in zk_list:
    if not zk.exists(appId_path):
      createZkNode(zk, appId_path, "".encode("utf8"))

  # 创建dfatable节点，不赋值
  dfatable_path = root_path + "/dfatable"
  for zk in zk_list:
    if not zk.exists(dfatable_path):
      createZkNode(zk, dfatable_path, "".encode("utf8"))

  return HttpResponseRedirect(reverse("route:env_info", kwargs={"env": name}))

def test(request):
  print("hello world111")
  service = Service.objects.all()
  for s in service:
    print(s.service_id)
  h = HttpResponse(content = ','.join([s.service_id for s in service]))
  print(h.content)
  return h
