def main():
    import getpass
    from Master_Parent1 import Client
    host = input("Enter the Fabric Controller IP/Hostname Ex:172.19.254.4 :")
    usr = input("Enter the Fabric username admin:")
    pwd = getpass.getpass(prompt="Enter the password:")
    #tn = input("Enter the Tenant Name:")
    tn = "Cloud1"
    vrf = input("Enter the VRF Name:")
    bd = vrf
    L3OUT_NAME = vrf+"_l3out"
    app =vrf
    epg =vrf
    L3OUT_DOMAIN = "GCP_l3dom"
    EXTERNAL_SUBNETS_NAME = L3OUT_NAME+"_Ntwk"
    Node_ID_1 = "101"
    Node_ID_2 = "103"
    PORT1 = "1/15"
    PORT2 = "1/36"
    ROUTER_ID_1 = "1.101.1.1"
    ROUTER_ID_2 = "3.103.3.3"
    MTU = "9000"
    REMOTE_ASN = "64513"
    LOCAL_ASN = "300"
    GCP_Import_subnet ="10.27.1.0/24"
    on_prem_subnet ="10.27.2.1/24"
    Export_Subnet ="172.16.0.0/12"
    SVI_VLAN = input("Enter the .1Q SVI_VLAN#:")
    SVI_PRI_IP = input("Enter the SVI Primary_IP address/Mask:")
    SVI_SEC_IP = input("Enter the SVI Secondary_IP address/Mask:")
    SVI_HSRP_IP=""
    BGP_Peer_IP = input("Enter the BGP_Neigbor_VM-PE_IP:")
    on_prem_subnet = input("Enter the on_prem_subnet:")
    GCP_Import_subnet = input("Enter the gcp_cloud_subnet:")
   
  

    ACTION = input("Are you sure you want to push the configuration (y/n): ")

    if ACTION in ("y","yes","Y","YES"): 
     FABRIC=Client(host, usr, pwd)
     print("Calling the Master function -> Authenticating into the Controller")
     FABRIC.login()
     t1=FABRIC.tenant(tn,vrf,bd)
     t2=FABRIC.bd_Subnet(tn,bd,on_prem_subnet)
     t3=FABRIC.app_profile(tn,app)
     t4=FABRIC.epg(tn,bd,app,epg)
     t20_0=FABRIC.L3OUT_BGPRAS(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,EXTERNAL_SUBNETS_NAME,Node_ID_1,PORT1,SVI_VLAN,SVI_PRI_IP,MTU,BGP_Peer_IP,ROUTER_ID_1,REMOTE_ASN)
     t20_1=FABRIC.L3OUT_BGPRAS(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,EXTERNAL_SUBNETS_NAME,Node_ID_1,PORT2,SVI_VLAN,SVI_PRI_IP,MTU,BGP_Peer_IP,ROUTER_ID_1,REMOTE_ASN)
     t20_2=FABRIC.L3OUT_BGPRAS(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,EXTERNAL_SUBNETS_NAME,Node_ID_2,PORT1,SVI_VLAN,SVI_SEC_IP,MTU,BGP_Peer_IP,ROUTER_ID_2,REMOTE_ASN)
     t20_3=FABRIC.L3OUT_BGPRAS(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,EXTERNAL_SUBNETS_NAME,Node_ID_2,PORT2,SVI_VLAN,SVI_SEC_IP,MTU,BGP_Peer_IP,ROUTER_ID_2,REMOTE_ASN)
     t21_0=FABRIC.L3OUT_BGPLAS(tn,L3OUT_NAME,Node_ID_1,PORT1,BGP_Peer_IP,LOCAL_ASN)
     t21_1=FABRIC.L3OUT_BGPLAS(tn,L3OUT_NAME,Node_ID_1,PORT2,BGP_Peer_IP,LOCAL_ASN)
     t21_2=FABRIC.L3OUT_BGPLAS(tn,L3OUT_NAME,Node_ID_2,PORT1,BGP_Peer_IP,LOCAL_ASN)
     t21_3=FABRIC.L3OUT_BGPLAS(tn,L3OUT_NAME,Node_ID_2,PORT2,BGP_Peer_IP,LOCAL_ASN)
     t21_3=FABRIC.L3OUT_EXPORT_Subnet(tn,L3OUT_NAME,EXTERNAL_SUBNETS_NAME,Export_Subnet)

     #t22=FABRIC.L3OUT_SEC_IP(tn,L3OUT_NAME,Node_ID,PORT,SVI_HSRP_IP) 
    elif ACTION in ("n","no","N","No"):
      print("Ending the script")
    else: 
      print("Please enter yes or no.")

 
if __name__ == '__main__':
    main()