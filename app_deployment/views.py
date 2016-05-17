from django.http import HttpResponse, JsonResponse

from django.conf import settings
import os
import time

from django.views.generic import TemplateView
from murano_connect import utils as m_utils


class IndexView(TemplateView):
    template_name = 'app_deployment.html'

    def get(self, request, *args, **kwargs):    
        
        context = {
            'some_dynamic_value': 'This text comes from django view!',
        }
        return self.render_to_response(context)
    

def installSoftwares(request): 
    
    try:      
        selected_pkgs = request.GET.get('ids')
        selected_pkgs = selected_pkgs.rstrip(',');    
        packagelist = selected_pkgs.split(',')    
        
        #Create environment
        response_env = m_utils.create_environment()
        if response_env['id']:        
            env_id = response_env['id']     
        else:        
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating environment'})
        
        #Create session
        response_sess = m_utils.create_session(env_id)
        if response_sess['id']:
            session_id = response_sess['id']
        else:
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating session'})  
        
        '''
        print "env_id \n "
        print env_id
        print "session_id \n"  
        print session_id
        '''
        msg = ""
        err_msg = ""
        print packagelist
        
        for package in packagelist:     
            
            package_name = settings.MURANO_PACKAGE_NAMES[package]         
            repo_url = settings.MURANO_PACKAGE_REPO_URL  
            
            #import package
            app_info = m_utils.import_application_package(repo_url, package_name)  
            #print "app_info \n"
            #print app_info
            
            if(app_info['response']['id']):             
                #Add application to environment
                respose_app = m_utils.add_application(env_id, session_id, app_info)
                #print "add application result \n"
                #print respose_app            
            else:            
                err_msg += 'Error occurred while importing package '+package+'\n'
            
        #Deploy session
        response_deploy = m_utils.deploy_session(env_id, session_id)
            
           
        if response_deploy['status_code'] == 200:
            msg +='Package deployment initiated \n'            
        elif response_deploy['status_code'] == 404:
            err_msg += ' Specified session does not exist \n'             
        elif response_deploy['status_code'] == 401:
            err_msg += ' User is not authorized to access this session \n'             
        elif response_deploy['status_code'] == 403:
            err_msg += ' Session is already deployed or deployment is in progress \n'              
        else:
            err_msg += 'Error occurred while deploying  \n'  
                
        if msg == "":     
            return JsonResponse({'status': 'failed', 'msg': 'Submission completed with below messages \n'+err_msg})     
        else:
            return JsonResponse({'status': 'success', 'msg': 'Submission completed with below messages \n'+msg+err_msg,'envid':env_id,'sessid':session_id})
        
    except Exception as e:
        return JsonResponse({'status': 'failed', 'msg': 'Exception occurred while deploying packages'})     
    
    
def getDeployInfo(request):    
    
    '''
    env_id = request.GET.get('envid')
    session_id = request.GET.get('sessid')     
    resp =m_utils.get_session_deatils(env_id, session_id) 
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': resp['state']})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    '''
    env_id = request.GET.get('envid')
    
    resp = m_utils.get_deployment_status(env_id)
    
    #print resp
    
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': str(resp['status'])})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    
def test_fn(request):
    
    import requests
    import json
    import datetime
    
    ip = 'controller-demodevstack-xppgiav6.srv.ravcloud.com'
    ###Creating auth_token
    data = {"auth": {"tenantName": "demo", "passwordCredentials": {"username": "demo", "password": "demo"}}}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data_json = json.dumps(data)
    response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #print(response.text)
    response = response.json()
    auth_token = response["access"]["token"]["id"]
    print auth_token
    
    #env_id ='5ffbea6d511e46fe985fa789ab649745'
    env_id ='1a5cb9ba73a94c95af20bd2f4d5d6c9a'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    resp_config = requests.get('http://' + ip + ':8082/v1/environments/' + env_id , headers=headers)
    print resp_config
    resp_config = resp_config.json()
    
    print resp_config
   
    
    
    return HttpResponse("Done")
    
    
    
    ip = 'controller-multinodetacker-yrcntlzg.srv.ravcloud.com'
    ###Creating auth_token
    data = {"auth": {"tenantName": "demo", "passwordCredentials": {"username": "demo", "password": "demo"}}}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data_json = json.dumps(data)
    response = requests.post('http://' + ip + ':35357/v2.0/tokens', data=data_json, headers=headers)
    #print(response.text)
    response = response.json()
    auth_token = response["access"]["token"]["id"]
    print auth_token
    
    ###Creating a template
    utc_datetime = datetime.datetime.utcnow()
    formated_string = utc_datetime.strftime("%Y-%m-%d-%H%M%SZ")
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    payload = {'name': 'temp_name_1' + str(formated_string)}
    resp_temp = requests.post('http://' + ip + ':8082/v1/templates', data=json.dumps(payload), headers=headers)
    resp_temp = resp_temp.json()
    # environment Id
    temp_id = resp_temp["id"]
    print temp_id
    
    
    instance_json = {
      "instance": {
        "flavor": "m1.small",
        "keyname": "key_tacker",
        "assignFloatingIp": "true",
        "image": "debian-8-m-agent.qcow2",
        "?": {
          "type": "io.murano.resources.Instance",
          "id": "b49352b8-95cf-4d63-a60b-61c8c8ea88a9"
        }
      },
      "name": "PostgreSQL",
      "?": {
       
        "type": "io.murano.databases.PostgreSql",
        "id": "fdba9ef8710b4a4b907c6ce48d350a84"
      }
    }   
    
    
    package_name = 'io.murano.databases.PostgreSql'      
    repo_url = settings.MURANO_PACKAGE_REPO_URL  
        
        #import package
    app_info = m_utils.import_application_package(repo_url, package_name)
    
    
    
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    resp_app = requests.post('http://' + ip + ':8082/v1/templates/' + temp_id + '/services',
                            data=json.dumps(instance_json), headers=headers)
    resp_app = resp_app.json()
    # environment Id
    app_id = resp_app["instance"]
    print app_id
    
    
    ###Creating environmetn template in template
    headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': auth_token}
    payload = {'name': 'env_name_11' + str(formated_string)}
    resp_env = requests.post('http://' + ip + ':8082/v1/templates/' + temp_id + '/create-environment', data=json.dumps(payload), headers=headers)
    resp_env = resp_env.json()
    # environment Id
    env_id = resp_env["environment_id"]
    session_id = resp_env["session_id"]
    print env_id
    print session_id
    
    ###Session id
    resp_config = requests.get('http://' + ip + ':8082/v1/environments/' + env_id + '/sessions/' + session_id, headers=headers)
    resp_config = resp_config.json()
    instance_state = resp_config["state"]
    print instance_state
    
    ###deploy a session
    headers = {'Content-type': 'application/json','Accept':'application/json','X-Auth-Token': auth_token,'X-Configuration-Session':session_id}
    resp_session = requests.post('http://' + ip + ':8082/v1/environments/' + env_id + '/sessions/' + session_id + '/deploy' , headers=headers)
    print resp_session.status_code
    
    
    return HttpResponse(resp_session.status_code)
    
    
          
    
    #time.sleep(2)    
    

    