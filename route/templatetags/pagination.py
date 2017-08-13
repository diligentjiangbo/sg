from django import template

register = template.Library()

@register.assignment_tag
def get_current_time():
  return "Hello Wolrd"
  
@register.assignment_tag
def pagination(current_page, paginator, num_of_displaypages=10, num_of_backpages=4):
  num_of_frontpages = num_of_displaypages - num_of_backpages - 3
  html = ''
  
  #当总页数小于等于显示页数时，则将总页数全部显示
  if paginator.num_pages <= num_of_displaypages:
    for i in range(1, paginator.num_pages+1):
      html += '<li><a href="?page=%s">%s</a></li>'%(i,i)
    return html
  
  #第一种情况
  elif current_page.number <= num_of_displaypages - num_of_backpages:
    for i in range(1, num_of_displaypages+1):
      html += '<li><a href="?page=%s">%s</a></li>'%(i,i)
    return html
    
  #第二种情况
  elif num_of_displaypages-num_of_frontpages <= current_page.number <= paginator.num_pages-num_of_backpages:
    html = '''
      <li><a href="?page=1">1</a></li>
      <li class="disabled"><a href="?page=1">...</a></li>
    '''
    for i in range(current_page.number-num_of_frontpages, current_page.number+num_of_backpages+1):
      html += '<li><a href="?page=%s">%s</a><li>'%(i,i)
    return html
    
  #第三种情况
  else:
    html = '''
      <li><a href="?page=1">1</a></li>
      <li class="disabled"><a href="?page=1">...</a></li>
    '''
    
    for i in range(paginator.num_pages-num_of_backpages-num_of_frontpages, paginator.num_pages+1):
      html += '<li><a href="?page=%s">%s</a></li>'%(i,i)
    return html