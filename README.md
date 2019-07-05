# Azure and LISP for Workload Migration 


Lab it up:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMicrosoft%2FAzure-LISP%2Fmaster%2Flisp_lab_iterate_through_vnet.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

Remember to deploy IOS configs to each CSR, and update x.x.x.x within configs referencing neighboring public IP of CSR.


![alt text](https://github.com/jgmitter/images/blob/master/LISP%20Lab%20Diagram.png)

The image below represents the LISP Mapping Server highlight that 10.100.100.10 is behind LISP RLOC 192.168.100.100 and 10.100.100.20 is behind LSIP RLOC 192.168.200.200.  We have stretched/split a subnet between on-premises and Azure.  

![alt text](https://github.com/jgmitter/images/blob/master/Annotation%202019-06-11%20152917.png)

## Azure and LISP for Workload Migration 

Workload migrations to a public cloud such as Azure involve careful planning and coordination between multiple teams, including application, server, network, and storage teams.  
One of the challenges the teams face is dealing with IP address changes.  An IP address change to an application can cause unnecessary complexity and delay to the project. For example, some applications, have IP addresses hard-coded, therefore, introduces risk with having to rewrite an application.  What if you could migrate workloads to Azure with IP mobility keeping the original IP address without network constraints?  IP mobility allows you to separate the workload migration from network limitations.  For instance, if the team can’t migrate all workloads within a subnet during a change window than the subnet can co-exist in your data center and Azure during the migration.   A migration team can migrate workloads in small groupings, enabling even a single-server migration. 

This blog describes a solution for data center migration to Azure using Locator/ID Separation Protocol (LISP) technology [RFC 6830](https://tools.ietf.org/html/rfc6830)

## LISP 
The Locator Identity Separation Protocol (LISP) is a routing architecture that creates a new paradigm by splitting the device identity, known as an Endpoint Identifier (EID), and its location, known as its Routing Locator (RLOC), into two different numbering spaces. This capability brings scale and flexibility to the network in a single protocol, enabling the areas of mobility, scalability, and security. For enterprises moving to Azure, LISP provides key benefits such as IP Mobility for Public IP Address Portability, Split Subnets during Data Center Migration, Geographic Dispersion of Data Centers and Disaster Recovery. This document focuses on LISP use cases addressing today’s enterprise data center use-cases when migrating to Azure.  Workload virtualization requires location independence for server resources and requires the flexibility to move these server resources from one data center to another to meet increasing workloads and to support disaster recovery. This brings the challenge of route optimization when the Virtual Servers move to route traffic to its current location. It also to keep the server’s identity (IP address) the same across moves, so the clients can continue to send traffic regardless of the server’s current location. The LISP VM-Mobility solution addresses this issue seamlessly by enabling IP end-points to change location while keeping their assigned IP addresses. The Virtual Servers may move between different subnets or across different locations of a subnet that has been moved via Azure ARM or Azure Migration Tools.  In either case, the LISP VM-Mobility solution guarantees optimal routing between clients and the IP end-point that moved, regardless of its location. Also, LISP VM-Mobility does not require any change in the DNS infrastructure (since the mobile nodes preserve their original IP addressing), which overall reduces operating expenses for the data center administrator.
LISP is a routing architecture, not a feature; it gives IP a full set of capabilities that it does not natively have. LISP enables IP address portability, which can be seen in two ways. First, it allows the mobility of a host anywhere without changing the host IP address. Second, it allows defining an edge host IP address independently from the site IP structure it will reside on. The decoupling of the application definition from the network is critical for cloud flexibility.

## IP Mobility Requirements
The goal of IP mobility is to steer traffic to the valid location of the end-point. This aspect is generally addressed by providing some sort of re-direction mechanism to enhance the traffic steering already provided by basic routing. Redirection can be achieved by replacing the destination address with a surrogate address that is representative of the new location of the end-point. For instance, what VNET or Region does my workload currently reside in?  A goal of IP mobility is to provide a solution that is transparent to the applications and allows for the preservation of established sessions, as end-points move around the IP infrastructure.

## Terminology:
In traditional IP, the IP edge routing subnets are advertised all over the network using either an Interior Gateway Protocol (IGP) or an Exterior Gateway Protocol (EGP); it is very rare to advertise any host address (subnet mask /32). With LISP, such constraints disappear; LISP splits the host ID (EID) from the RLOC, allowing any host to move from location to location while keeping its unique identity. LISP architecture is composed of several elements, including the following:

Locator/ID Separation Protocol (LISP): A tunnel protocol that uses a central database in which endpoint location is registered. LISP enables an IP host-based mobility of endpoints.

LISP-enabled virtualized router: A virtual machine or appliance that supports routing and LISP functions, including host mobility.

Endpoint ID (EID):  IPv4 or IPv6 identifier of the devices connected at the edge of the network and used in the first (most inner) LISP header of a packet.

Routing Locator (RLOC): IPv4 or IPv6 addresses used to encapsulate and transport the flow between LISP nodes.   An RLOC is the output of an EID-to-RLOC mapping lookup.

Ingress tunnel router (ITR): A router that has two functions: it resolves the location of an EID by querying the database, and then it performs the encapsulation toward the remote RLOC.  Sends requests toward the map resolver.  Populates its local map cache with the learned association.  Responsible for performing the LISP encapsulation

Egress tunnel router (ETR): A router that has two functions: it registers the endpoint or location associated with the database, and then it decapsulates the LISP packet and forwards it to the right endpoint.  It registers the EID address space it is authorized for, and It is identified by one (or more) RLOCs

xTR: A generic name for a device performing both ITR and ERT functions.

Proxy-ITR (PITR): Acts like an ITR but does so on behalf of non-LISP sites that send packets to destinations at LISP sites.

Proxy-ETR (PETR): Acts like an ETR but does so on behalf of LISP sites that send packets to destinations at non‑LISP sites.

PxTR: The point of interconnection between an IP network and a LISP network, playing the role of ITR and ETR at this peering point.

Map-Server (MS): A MS is a LISP Infrastructure device that LISP site ETRs register to with their EID prefixes. The MS advertises aggregates for the registered EID prefixes into the LISP mapping system. All LISP sites use the LISP mapping system to resolve EID-to-RLOC mappings.  This server is the database where all EID and RLOC associations are stored.  It can be deployed simply on a pair of devices.  Or it can be a hierarchy of devices, organized like a DNS system for massive scale implementation.

Map-Resolver (MR): An MR is a LISP Infrastructure device to which LISP site ITRs send LISP Map-Request queries when resolving EID-to-RLOC mappings.  Receives the request and selects the appropriate map server

## LISP Use-Cases
Fast Bring-up of Disaster Recovery Facilities

DC Migration/Relocation of workloads to Azure without IP address change.

## DC Migration
This document is focused on DC Migration.  The concept of the solution is to use an Azure Availability Set of Cisco CSR 1000V virtual routers within an Azure VNET, and a LISP-enabled router pair (Cisco ASR 1000 Series Aggregation or Cisco CSR 1000V virtual routers) deployed in the enterprise data center with a LISP (encrypted optional) tunnel in between. LISP provides the mobility between the two or more sites, allowing you to stretch subnets from the enterprise to an Azure VNET.
Non-LISP-enabled sites communicate to the servers moved to Azure through the enterprise data center, where LISP is deployed.
The solution proposed in this paper does not require LISP to be enabled globally; it can be deployed by enabling LISP on just the enterprise data center and within Azure, with minimal impact on the operations of both the data center and Azure.
The optional deployment of LISP at individual user's sites provides data-path optimization because the LISP-encapsulated traffic is routed directly Azure or the data center, depending on the server location.
The LISP-enabled router deployed within the enterprise data center does not need to be the default gateway for the local servers (physical and virtual machines). The LISP enabled router is deployed “on a stick,” meaning that it does not need to be the default gateway, and its interaction with the local infrastructure is based on Proxy-ARP. The router has at least two interfaces facing the data center, one as the routed core interface and one for Layer 2 collection of VLANs. The stretched subnets are locally either connected using sub-interfaces.

The LISP CSRs in Azure is deployed with one interface facing the Internet or facing Gateway Subnet and the other interfaces facing the local Azure Subnets. The stretched subnets are connected by the interfaces that face the local Azure subnets.

The LISP-enabled Azure solution allows inter and intra-subnet communication regardless of the location of the server, meaning that communication between two endpoints located in different subnets can happen even when one endpoint is located at the enterprise, and another endpoint is located at Azure with a stretched subnet between enterprise and Azure. 

![alt text](https://github.com/jgmitter/images/blob/master/1stpic.png)


## Routing Considerations
In any case, DC Migration solution requires only that each CSR have one unique outside address; then an IPsec tunnel is built between these addresses, and the IPsec tunnel has a private address.
In the DC Migration solution, an OSPF peering is enabled over this GRE/IPsec tunnel. The objective is to announce to the other CSR the loopback address that is used as the LISP location (RLOC). Now, enabling a routing protocol could allow you to advertise some subnet of the cloud that does not need mobility and could not be subject to LISP handling.

The transport service in the WAN side is usually of two types. It could be a plain public Internet network, or it could be private peering over ExpressRoute. Both transport services are supported. With the Internet, an important consideration is the NAT service. NAT is sometimes used between Azure and the transport network, and most probably the same occurs on the enterprise side. Because IPsec supports NAT, the fact that this solution uses IPsec as a tunnel connection between the enterprise and Azure solves any NAT burden. In the IPsec tunnel, as well as in the cloud, the private enterprise addressing is used, and LISP operates over these private addresses. With the ExpressRoute option, because all addresses are in a private space, no NAT considerations are necessary.

## LISP Stretched Subnets Advertisement
The subnets that will be stretched from the enterprise to Azure already exist within the enterprise data center. Those subnets should already be advertised toward the enterprise WAN by the existing routing protocol to ensure that non-LISP remote sites have a route to the LISP-enabled subnets through the enterprise data center, where PxTR-1 attracts all the traffic directed to the subnets that have been "stretched" to Azure.

## Reference Topology
The reference topology has three environments: An enterprise branch office (remote site), an enterprise data center, and Azure.

The branch-office subnet where users connect is 10.0.100/24.  The users’ default gateway is the router (Router 1) with IP address 10.0.100.10. Router 1is connected to the Internet with a VPN to the enterprise DC or via a private WAN.  Router 1 does not run LISP, so the branch office is a non-LISP site. Branch-office users access servers located either at the enterprise data center or at Azure.
The enterprise data center is connected to the Internet or private WAN through the data center WAN edge routers (Router A & B) The default gateway for all the servers located in the enterprise data center is at the aggregation layer; on the diagram 10.0.5.0/24 is the only subnet represented for simplicity.  The Cisco CSR 1000V or Cisco ASR installed on the enterprise, PxTR-1, has two interfaces. The blue link is the connecting towards the Internet or WAN, and the black link is the PxTR-1 connection to the 10.0.5.0/24 subnet where mobility is required.
PxTR-1 is the only device within the enterprise data center running LISP, and it is configured as a LISP PxTR. PxTR-1 is also configured with a GRE/IPsec tunnel toward the Azure CSR. OSPF is enabled over the IPsec tunnel to advertise the IP address of the loopback interfaces of PxTR-1 and CSR that are used as the LISP RLOCs.

The (CSR) deployed on Azure has one public IP address, and one or more interfaces with private addresses, one interface configured with IP 10.1.50.x.  A virtual machine with IP address 10.0.5.253 has been moved to Azure; it uses the IP address 10.0.5.1 (Azure Fabric) as its default gateway.  The subnet has a UDR pointing to the CSR for subnets still within the Enterprise it needs to reach. 

CSR is the only device in the Azure running LISP, and it is configured as a LISP xTR. CSR is also configured with a GRE/IPsec tunnel toward PxTR-1, the enterprise data center CSR, and it has OSPF enabled over its IPsec tunnel to advertise its loopback interface address that is used as its RLOC. In the topology, the subnet 10.0.5.0/24 is stretched between the enterprise data center, Azure. The IPsec tunnel between the enterprise and cloud CSRs is used to secure communication between the enterprise and the cloud.


![alt text](https://github.com/jgmitter/images/blob/master/pic2.png)


## Implementation Details within Azure
The Azure CSR is configured as a LISP ITR and ETR node so that it can perform LISP encapsulation and de-encapsulation of the packets coming from or going to the virtual machines located within Azure. For traffic leaving Azure, whenever a route to the destination is not found on the CSR routing table, CSR must route that traffic through PxTR-1 at the enterprise data center. This function, known as use-petr, is useful to ensure that the traffic flow is symmetric between non-LISP-enabled sites and Azure, and it must be used when firewalls or other stateful devices are located at the enterprise data center.


## Packet Walk and Encapsulation Stack
This section explains the detailed communication flows referring to the diagram shown in Figure above earlier in this document. PxTR-1, at the enterprise data center, is placed on a stick. PxTR-1 proxy replies on behalf of all nonlocal servers, inserting its own MAC address for any EID that is not locally detected. PxTR-1 can be either a physical router (Cisco ASR 1000) or a virtual router (Cisco CSR 1000V). PxTR -1 is enabled as a LISP PiTR so you can manage both locally sourced traffic and traffic coming from the WAN. PxTR-1 is also set up as a LISP PeTR so you can receive traffic back from Azure and deliver it to the WAN.  At Azure, the CSR (xTR) is a standard LISP xTR for the locally attached subnets.  Azure CSR xTR plays the role of eTR for the flow coming from the enterprise site and acts as an iTR for the flow going back to the enterprise site. For any destination that is not known by the xTR, the iTR encapsulates the traffic to the RLOC of the PeTR specified, in this case, the PxTR-1 deployed at the enterprise site.

## Communication from Non-LISP-Enabled Remote Sites to Enterprise and Azure
Traffic from user PCs, which are located at a remote site that is not LISP-enabled, is naturally attracted toward the enterprise data center by IP routing. When it reaches the enterprise site, it crosses the site's security and other services to reach the local subnet that is supposed to host the destination server 10.0.5.253. When the local default gateway sends an ARP request to find .253, PxTR-1 responds to this ARP request using the Proxy-ARP function as described previously. Traffic is sent LISP-encapsulated to Azure, where it is delivered to CSR (xTR), which is the LISP gateway for (.253), handles the return traffic that is sent by .253. Because this traffic is intended for a non-LISP site, Azure CSR sends the traffic to the PeTR configured on it (PxTR-1).


![alt text](https://github.com/jgmitter/images/blob/master/pic3.png)



## Communication from Enterprise Local LISP-Enabled Subnet to the Azure LISP-Enabled Subnet
Traffic originated from a LISP-enabled subnet (non-10.0.5.0/24) intended for another LISP-enabled subnet and further extended to Azure (to .253) first reaches the local gateway and then will be routed locally to the extended subnet where PxTR-1 will respond to the ARP request. On the return path, the traffic will hit Azure CSR, which is the LISP gateway and then be routed by LISP toward the enterprise site.

## Communication from Enterprise Local Non-LISP-Enabled Subnet to Azure LISP-Enabled Subnet
In this case, traffic will first reach the default gateway, from which it will follow the same path as the traffic originated from a remote site. The PxTR function will be used in both directions.

## Communication from LISP-Enabled Subnets to Non-LISP-Enabled Subnets
Traffic sourced from a LISP-enabled subnet at the enterprise site toward a non-LISP-enabled subnet at Azure, standard routing will take effect.  Communication sourced from VMs in Azure will be LISP encapsulated to the PxTR in the Customer DC, and the the PxTR will follow standard routing.

## Communication between Non-LISP-Enabled Subnets
In this case, the traffic will be routed using plain IP routing, and LISP is not involved. The return traffic also uses plain IP routing, and LISP is not involved. Inter-Subnet

## Communication between Servers in Azure
In Azure itself, Azure fabric will route traffic between local subnets because it is the default gateway.  CSR can optionally route traffic between LISP enabled subnets because it is the Azure LISP gateway. 

## Communication from LISP-Enabled Remote Sites to Enterprise and Cloud
All previous considerations of traffic flows assume that the only LISP-enabled devices are PxTR-1 and xTR-2. If one remote site needs to access directly a non-LISP-enabled resource in Azure, meaning a subnet that is strictly local to Azure, then pure routing can be used. If a remote site needs path optimization to directly reach the servers that are part of a LISP stretched subnet at Azure, LISP can be enabled on this remote site. An xTR deployed on this remote site would consult the map server to receive the correct location of the server.  If Azure vWAN is used than a LISP-enabled branch would have an optimized path for LISP stretched subnets during DC migration. 

![alt text](https://github.com/jgmitter/images/blob/master/pic4.png)

## References:
https://www.lisp4.net/

<a id="stretched"></a> 
# Stretched Intra Subnet Routing
Currently, for intra-subnet routing from Azure to on-premises, additional configuration is required.  For the Azure fabric to forward a packet to the CSR to an IP back on-premises within the same stretched subnet, it requires a secondary IP on the NIC attached to the CSR interface attached to the stretched subnet for each IP within the same stretched subnet still on-premises.  This additional configuration is not required on-premises.  There is work being done to automate this via the LISP Map-Server to programmatically program Azure API to define secondary IPs based on what IPs are still on-premises within the stretched subnet.  

![alt text](https://github.com/jgmitter/images/blob/master/Secondaryip.png)

# Automation (this is beta - test that it works for your use case!)
For this to automatically work as new hosts are being moved around from on-premises to Azure, the secondary IPs that need to be added to the NIC in Azure as referred to in the section on [Stretched Intra Subnet Routing above](#stretched) can be done automatically by leveraging the Cisco Embedded Event Manager, guestshell (a Linux shell running on select Cisco devices, including the CSR), [Python](https://www.python.org/) and the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python).

## Concepts

### Embedded Event Manager
You will find more on [Cisco's](http://www.cisco.com) web site but the idea is that this is a trigger that can, based on events, or timers, fire something. This is what will be launching our Python script.

### Guestshell
Again on [Cisco's](http://www.cisco.com) web site, you will see more in-depth coverage on this. Cisco's guestshell is a linux subsystem that can run arbitrary things we need. Specifically in our case, we need to run Python code.

### [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
With Python at the core of this, we need to interact, using Python, with the Azure REST API to manage Azure. Specifically, we're trying to add on the NIC of the XTR that runs in Azure the IP addresses that exist on-premises. For this, a REST call is necessary, but it's much simpler to rather use the Python SDK for Azure. It has all the methods required to make this much simpler to do than handling REST calls directly.

## Script and dependencies
The Python script that we used is included [here](ipconfig-register.py), and there are two dependency files:
1. [site_configs.json](site_configs.json): Contain the configuration of the sites in this format : 
    ```jsonc
    {
        "site_name" : "DC1",
        "resource_group" : "lisp-labs",
        "csr_azure_intf_name" : "azure-pxtr1-nic2"
    }
    ```
    This file is referenced by the main [python script](ipconfig-register.py) so that it pulls the proper information out of the CSR router to update Azure. The `site_name` is used by other configuration elements in the CSRs to identify the site for LISP.
1. [secret.json](secrets.json): As the name suggests, this file contains the credentials to be able to communicate with Azure.
    ```jsonc
    {
        "sp_client_id": "<YOUR APP ID GUID>",
        "sp_secret" : "<YOUR SECRET ID GUID>",
        "sp_tenant_id" : "<YOUR AAD TENANT GUID>",
        "sub_id" : "<YOUR SUBSCRIPTION GUID>"
    }
    ````
    The `sp_client_id` and `sp_secret` can both be generated using the `az` command [`az ad sp create-for-rbac`](https://docs.microsoft.com/en-us/cli/azure/ad/sp?view=azure-cli-latest#az-ad-sp-create-for-rbac). Many variances of the command exist, and please note that by default, (other methods exist) this command will give contributor right to the newly created client/secret (think of them as a service account and password), access to all the Azure resources in this subscription. There are options to the command `az ad sp create-for-rbac` so this isn't the case. See the [documentation](https://docs.microsoft.com/en-us/cli/azure/ad/sp?view=azure-cli-latest#az-ad-sp-create-for-rbac) for more information.
    Both `sp_tenant_id` and `sub_id` can be retrived by running `az account list --output json` will yield something similar to this
    ```json
    {
        "cloudName": "AzureCloud",
        "id": "<SUBSCRIPTION ID>",
        "isDefault": true,
        "name": "subscription_name",
        "state": "Enabled",
        "tenantId": "<TENANT GUID>",
        "user": {
          "name": "user@company.com",
          "type": "user"
        }
    }
    ```
## IOS Configuration

### Upload files
In order for the CSR to be able to execute this script, the 3 files above need to be uploaded to the flash memory (bootflash) of the CSR so that the script is accessible from inside the guestshell.

### Configure Guestshell 
1. In order to activate the guestshell, you need to type, in exec mode :
    ```
    onprem-pxtr#guestshell enable
    ```
    This will enable the guestshell and then typing guestshell will get you in the shell environment :
    ```
    onprem-pxtr#guestshell
    [guestshell@guestshell ~]$
    ```
    where you can run arbitrairy commands, including running a Python script.
1. You will then need to install [Azure SDK for python](https://github.com/Azure/azure-sdk-for-python) by using the following commands:
    ```shell
    pip install azure
    ```
    This will install all required packages. To confirm that this works, type the following:
    ```shell
    [guestshell@guestshell ~]$ python
    Python 2.7.5 (default, Apr 11 2018, 07:36:10)
    [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import azure
    >>>
    ```
    If you are seeing something like this :
    ```shell
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ImportError: No module named azure
    ```
    it means something did not install properly. This needs to be addressed before moving on to the next step.
1. At this stage, you can try testing the script assuming the configuration files are working properly, that should confirm that the script runs smoothly by using the command :
    ```bash
    [guestshell@guestshell ~]$ python /bootflash/ipconfig-register.py
    2019-07-05 20:59:53,879:INFO:MainThread:b604d245-3f35-4826-a2e0-2a84dcea41b1 - TokenRequest:Getting token with client credentials.
    2019-07-05 20:59:54,174:INFO:MainThread:b604d245-3f35-4826-a2e0-2a84dcea41b1 - OAuth2Client:Get Token Server returned this correlation_id: b604d245-3f35-4826-a2e0-2a84dcea41b1
    2019-07-05 20:59:54,189:INFO:MainThread:0c6e7594-9740-4b15-885e-c6aa81ce729a - TokenRequest:Getting token with client credentials.
    2019-07-05 20:59:54,640:INFO:MainThread:IOS output of show =
    2019-07-05 20:59:54,640:INFO:MainThread:Running on IOS. Picking up IPs [''] in local database
    2019-07-05 20:59:54,641:INFO:MainThread:Adding primary IP 10.100.100.4 to the list (primary IP of CSR in Azure).
    2019-07-05 20:59:54,641:INFO:MainThread:Dropping the IP 10.100.100.20 from the current list
    2019-07-05 20:59:54,641:INFO:MainThread:Dropping the IP 10.100.100.6 from the current list
    2019-07-05 20:59:54,641:INFO:MainThread:Adding the IP  to the list
    2019-07-05 20:59:54,642:INFO:MainThread:Triggering the update of the ipconfig in Azure to include the following list : [u'10.100.100.4', '']
    2019-07-05 20:59:54,645:INFO:MainThread:4fb0e271-99ac-4db1-9ea7-e9f8a4c9767e - TokenRequest:Getting token with client credentials.
    2019-07-05 20:59:55,108:INFO:MainThread:Exception : Private IP address is required when privateIPAllocationMethod is Static in IP configuration /subscriptions/321cae6f-e4d3-40bf-824f-c07493a62af5/resourceGroups/lisp-labs/providers/Microsoft.Network/networkInterfaces/azure-pxtr1-nic2/ipConfigurations/ipconfig_remote_.  2019-07-05 20:59:55,109:INFO:MainThread:Done.
    ```
    If you see an output similar to the above, you can validate in the Azure portal that the IP addresses are properly configured on the Azure side.
    
### Configure Event Manager
There are likely multiple ways to launch the script, we chose to run it every 60 seconds. Running it more frequently will result in API calls likely returning that the resource is busy, processing the previous updates. Moreover, we don't think that in general, VMs will be migrating at a pace that would require to run the script several times per minute. The following commands were added in configuration mode on the Cisco device.
```
event manager applet azure_update_ipconfigs
 event timer watchdog time 60
 action 1.0 cli command "en"
 action 2.0 cli command "guestshell run python /bootflash/ipconfig-register.py"
```

## Testing
In order to test that the following works, you can try the following steps :
    1. create a new virtual machine on the on-premises side of the network
    1. ping the IP of the VMs from the local XTR (or vice-versa)
    1. wait for 60 seconds to see if the new IP of this newly created machine is reacheable from Azure

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

# Legal Notices

Microsoft and any contributors grant you a license to the Microsoft documentation and other content
in this repository under the [Creative Commons Attribution 4.0 International Public License](https://creativecommons.org/licenses/by/4.0/legalcode),
see the [LICENSE](LICENSE) file, and grant you a license to any code in the repository under the [MIT License](https://opensource.org/licenses/MIT), see the
[LICENSE-CODE](LICENSE-CODE) file.

Microsoft, Windows, Microsoft Azure and/or other Microsoft products and services referenced in the documentation
may be either trademarks or registered trademarks of Microsoft in the United States and/or other countries.
The licenses for this project do not grant you rights to use any Microsoft names, logos, or trademarks.
Microsoft's general trademark guidelines can be found at http://go.microsoft.com/fwlink/?LinkID=254653.

Privacy information can be found at https://privacy.microsoft.com/en-us/

Microsoft and any contributors reserve all others rights, whether under their respective copyrights, patents,
or trademarks, whether by implication, estoppel or otherwise.
