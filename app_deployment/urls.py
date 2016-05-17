from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.index, name='index'),   
    url(r'^$', views.IndexView.as_view()),  
    url(r'^index/', views.IndexView.as_view()),    
    url(r'^installSoftwares/', views.installSoftwares), 
    url(r'^getDeployInfo/', views.getDeployInfo),  
    
    #url(r'^test_fn/', views.test_fn),  
    
     
    
       
    
]