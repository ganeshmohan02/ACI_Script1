import requests
import json
from string import Template
requests.urllib3.disable_warnings()
import urllib3
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
"""
Author: Ganesh Mohan
Date: 12/23/2020
Purpose: Send API calls to APIC and print status 
Version: 1.3
"""

class AuthenticationError(Exception):
    pass
class Client:
    def __init__(self, host, usr, pwd):
        #self.jar = requests.cookies.RequestsCookieJar()
        self.host = host
        self.usr = usr
        self.pwd = pwd
        self.client = requests.Session() 
#Pushing the configuration in the APIC controller   
    def POST(self, url, data,Role):
        response= self.client.post('https://%s%s' % (self.host, url),data=json.dumps(data),timeout=5,verify=False)
        resp=response.text
        if 'error' in resp:
          print("\n!!!!{}: Config already exist or config issue..Code{}\n".format(Role,response))
          print("!!!!Error code:{}\n".format(resp))
          #raise AuthenticationError
        else:
          print(">>>>{}:>>>>>Done # Status Code>{}".format(Role,response))
        return response
#Login into APIC using static Credentials.
    def login(self):
        data = {"aaaUser": {"attributes": {"name": self.usr, "pwd": self.pwd}}}
        res= self.client.post('https://%s/api/aaaLogin.json' % (self.host),data=json.dumps(data),timeout=5,verify=False)
        print(res)
        if res.status_code != 200 or 'error' in res.json()['imdata'][0]:
            raise AuthenticationError


#T1:Create Tenant,VRF and L3 BD.
    def tenant(self,Tname,VRF,BD):
        Role='T1:tenant:{},VRF:{},L3_BD:{}'.format(Tname,VRF,BD)
        print("\nCreating the tenant:{}\n".format(Tname))
        data = { "fvTenant":{"attributes":{"dn":"uni/tn-"+Tname,"status":"created,modified"},"children":[
               {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","name":BD+"_bd","arpFlood":"true","unicastRoute":"true","rn":"BD-"+BD+"_bd","status":"created,modified"},
               "children":[{"fvRsCtx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]   }}]}},
               {"fvCtx":{"attributes":{"dn":"uni/tn-"+Tname+"/ctx-"+VRF+"_vrf","name": VRF+"_vrf","rn":"ctx-"+VRF+"_vrf","status":"created,modified"},"children":[]
              }}]}}
        return self.POST('/api/mo/uni/tn-{}.json'.format(Tname), data,Role)
#T2:Create L3 BD,Subnet and Scope of the subnet.
    def bd_Subnet(self,Tname,BD,Subnet):
        Role='T2: Creating the L3 BD:{} with Anycast GW:{}'.format(BD,Subnet)
        data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]","scope":"public,shared", "status": "created,modified"},"children": [] } }
        return self.POST('/api/node/mo/uni/tn-{}/BD-{}_bd/subnet-[{}].json'.format(Tname,BD,Subnet), data,Role)

#T3:Create APP policy.    
    def app_profile(self,Tname,APP):
        Role="T3:{}-Application profile:".format(APP)
        data = {"fvAp":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap","name":APP+"_ap","rn":"ap-"+APP+"_ap","status":"created,modified"},"children":[] }}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)        

#T4:Create EPG and assoicate the BD. 
    def epg(self,Tname,BD,APP,EPG):
        Role="T4:EPG:{}".format(EPG)
        data = {"fvAEPg":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap/epg-"+EPG+"_epg","name":EPG+"_epg","rn":"epg-"+EPG+"_epg","status":"created,modified"},
        "children":[{"fvRsBd":{"attributes":{"tnFvBDName":BD+"_bd","status":"created,modified"},"children":[] }}]}}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)

#T20 Create L3OUT BGP and Remote AS.
    def L3OUT_BGPRAS(self,Tname,VRF,L3OUT_NAME,L3OUT_DOMAIN,L3OUT_SUBNETS,Node_ID,PORT,SVI_VLAN,SVI_PRI_IP,MTU,BGP_Peer_IP,ROUTER_ID,REMOTE_ASN):
        Role="T20:{}-L3 domain_BGP Configure Remote AS:".format(L3OUT_NAME)
        data = {"l3extOut":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME,"name":L3OUT_NAME,"rn":"out-"+L3OUT_NAME,"status":"created,modified"},
               "children":[
               {"bgpExtP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/bgpExtP","rn":"bgpExtP","status":"created,modified"},"children":[]}},
               {"l3extInstP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS,"name":L3OUT_SUBNETS,"rn":"instP-"+L3OUT_SUBNETS,"status":"created,modified"},
               "children":[{"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-[10.24.192.0/19]","ip":"10.24.192.0/19","scope":"export-rtctrl","aggregate":"","rn":"extsubnet-[10.24.192.0/19]","status":"created,modified"},"children":[]}}]}},
               {"l3extLNodeP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile","name":L3OUT_NAME+"_nodeProfile","status":"created,modified"},
               "children":[{"l3extLIfP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile","name":L3OUT_NAME+"_interfaceProfile","status":"created,modified"},
               "children":[{"l3extRsPathL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]","tDn":"topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]","addr":SVI_PRI_IP,"ifInstT":"ext-svi","mtu":MTU,"encap":"vlan-"+SVI_VLAN,"status":"created","rn":"rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]","encapScope":"ctx"},
               "children":[{"bgpPeerP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]","addr":BGP_Peer_IP,"status":"created,modified"},
               "children":[{"bgpAsP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]/as","asn":REMOTE_ASN,"status":"created,modified"},
               "children":[]  }}]}}]}}]}},
               {"l3extRsNodeL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-"+Node_ID+"]","tDn":"topology/pod-1/node-"+Node_ID,"rtrId":ROUTER_ID,"rtrIdLoopBack":"false","status":"created,modified"},"children":[]}}]}},
               {"l3extRsEctx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]}},{"l3extRsL3DomAtt":{"attributes":{"tDn":"uni/l3dom-"+L3OUT_DOMAIN,"status":"created,modified"},"children":[]}}]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}.json'.format(Tname,L3OUT_NAME), data,Role)

#T21 Create L3OUT BGP Configure Local AS..
    def L3OUT_BGPLAS(self,Tname,L3OUT_NAME,Node_ID,PORT,BGP_Peer_IP,LOCAL_ASN):
        Role="T21:{}-L3OUT_BGP Configure Local AS:".format(L3OUT_NAME)
        data = {"bgpLocalAsnP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]/localasn","rn":"localasn","localAsn":LOCAL_ASN,"status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/lifp-{}_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-{}/pathep-[eth{}]]/peerP-[{}]/localasn.json'.format(Tname,L3OUT_NAME,L3OUT_NAME,L3OUT_NAME,Node_ID,PORT,BGP_Peer_IP),data,Role),

#T22 Create L3OUT HSRP IP address..  
    def L3OUT_SEC_IP(self,Tname,L3OUT_NAME,Node_ID,PORT,SVI_HSRP_IP):
        Role="T22:{}-L3OUT_Configure the secondary IP:".format(L3OUT_NAME)
        data = {"l3extIp":{"attributes":{"addr":SVI_HSRP_IP,"status":"created"},"children":[]}}  
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/lifp-{}_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-{}/pathep-[eth{}]].json'.format(Tname,L3OUT_NAME,L3OUT_NAME,L3OUT_NAME,Node_ID,PORT),data,Role)

 
  #T22 Create L3OUT Export subnets to GCP..  
    def L3OUT_EXPORT_Subnet(self,Tname,L3OUT_NAME,L3OUT_SUBNETS,Export_Subnet):
        Role="T22:L3OUT_Configure the Export subnet to GCP {}:".format(Export_Subnet)
        data = {"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-["+Export_Subnet+"]","ip":Export_Subnet,"scope":"export-rtctrl","aggregate":"","rn":"extsubnet-["+Export_Subnet+"]","status":"created"},"children":[]}} 
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/instP-{}/extsubnet-[{}].json'.format(Tname,L3OUT_NAME,L3OUT_SUBNETS,Export_Subnet),data,Role)

        




def main():
    print("\n Authenication in to the controller: {}\n".format(cfg.host))
    client.login()

if __name__ == '__main__':
    main()
