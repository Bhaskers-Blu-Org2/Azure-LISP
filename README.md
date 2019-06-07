# Azure and LISP for Workload Migration 

Workload migrations to a public cloud such as Azure involve careful planning and coordination between multiple teams, including application, server, network, and storage teams.  
One of the challenges the teams face is dealing with IP address changes.  An IP address change to an application can cause unnecessary complexity and delay to the project. For example, some applications, have IP addresses hard-coded, therefore, introduces risk with having to rewrite an application.  What if you could migrate workloads to Azure with IP mobility keeping the original IP address without network constraints?  IP mobility allows you to separate the workload migration from network limitations.  For instance, if the team can’t migrate all workloads within a subnet during a change window than the subnet can co-exist in your data center and Azure during the migration.   A migration team can migrate workloads in small groupings, enabling even a single-server migration. 

This blog describes a solution for data center migration to Azure using Cisco® Locator/ID Separation Protocol (LISP) technology (RFC 6830).

# LISP 
The Locator Identity Separation Protocol (LISP) is a routing architecture that creates a new paradigm by splitting the device identity, known as an Endpoint Identifier (EID), and its location, known as its Routing Locator (RLOC), into two different numbering spaces. This capability brings scale and flexibility to the network in a single protocol, enabling the areas of mobility, scalability, and security. For enterprises moving to Azure, LISP provides key benefits such as IP Mobility for Public IP Address Portability, Split Subnets during Data Center Migration, Geographic Dispersion of Data Centers and Disaster Recovery. This document focuses on LISP use cases addressing today’s enterprise data center use-cases when migrating to Azure.  Workload virtualization requires location independence for server resources and requires the flexibility to move these server resources from one data center to another to meet increasing workloads and to support disaster recovery. This brings the challenge of route optimization when the Virtual Servers move to route traffic to its current location. It also to keep the server’s identity (IP address) the same across moves, so the clients can continue to send traffic regardless of the server’s current location. The LISP VM-Mobility solution addresses this issue seamlessly by enabling IP end-points to change location while keeping their assigned IP addresses. The Virtual Servers may move between different subnets or across different locations of a subnet that has been moved via Azure ARM or Azure Migration Tools.  In either case, the LISP VM-Mobility solution guarantees optimal routing between clients and the IP end-point that moved, regardless of its location. Also, LISP VM-Mobility does not require any change in the DNS infrastructure (since the mobile nodes preserve their original IP addressing), which overall reduces operating expenses for the data center administrator.
LISP is a routing architecture, not a feature; it gives IP a full set of capabilities that it does not natively have. LISP enables IP address portability, which can be seen in two ways. First, it allows the mobility of a host anywhere without changing the host IP address. Second, it allows defining an edge host IP address independently from the site IP structure it will reside on. The decoupling of the application definition from the network is critical for cloud flexibility.

IP Mobility Requirements
The goal of IP mobility is to steer traffic to the valid location of the end-point. This aspect is generally addressed by providing some sort of re-direction mechanism to enhance the traffic steering already provided by basic routing. Redirection can be achieved by replacing the destination address with a surrogate address that is representative of the new location of the end-point. For instance, what VNET or Region does my workload currently reside in?  A goal of IP mobility is to provide a solution that is transparent to the applications and allows for the preservation of established sessions, as end-points move around the IP infrastructure.

Terminology:
In traditional IP, the IP edge routing subnets are advertised all over the network using either an Interior Gateway Protocol (IGP) or an Exterior Gateway Protocol (EGP); it is very rare to advertise any host address (subnet mask /32). With LISP, such constraints disappear; LISP splits the host ID (EID) from the RLOC, allowing any host to move from location to location while keeping its unique identity. LISP architecture is composed of several elements, including the following:

Locator/ID Separation Protocol (LISP): A tunnel protocol that uses a central database in which endpoint location is registered. LISP enables an IP host-based mobility of endpoints.

LISP-enabled virtualized router: A virtual machine or appliance that supports routing and LISP functions, including host mobility.

Endpoint ID (EID): IPv4 or IPv6 identifier of the devices connected at the edge of the network and used in the first (most inner) LISP header of a packet.

Routing Locator (RLOC): IPv4 or IPv6 addresses used to encapsulate and transport the flow between LISP nodes.   An RLOC is the output of an EID-to-RLOC mapping lookup.

Ingress tunnel router (ITR): A router that has two functions: it resolves the location of an EID by querying the database, and then it performs the encapsulation toward the remote RLOC.  Sends requests toward the map resolver.  Populates its local map cache with the learned association.  Responsible for performing the LISP encapsulation

Egress tunnel router (ETR): A router that has two functions: it registers the endpoint or location associated with the database, and then it decapsulates the LISP packet and forwards it to the right endpoint.  It registers the EID address space it is authorized for, and It is identified by one (or more) RLOCs

xTR: A generic name for a device performing both ITR and ERT functions.

Proxy-ITR (PITR): Acts like an ITR but does so on behalf of non-LISP sites that send packets to destinations at LISP sites.

Proxy-ETR (PETR): Acts like an ETR but does so on behalf of LISP sites that send packets to destinations at non‑LISP sites.

PxTR: The point of interconnection between an IP network and a LISP network, playing the role of ITR and ETR at this peering point.

Map-Server (MS): A MS is a LISP Infrastructure device that LISP site ETRs register to with their EID prefixes. The MS advertises aggregates for the registered EID prefixes into the LISP mapping system. All LISP sites use the LISP mapping system to resolve EID-to-RLOC mappings.  This server is the database where all EID and RLOC associations are stored.  It can be deployed simply on a pair of devices.  Or it can be a hierarchy of devices, organized like a DNS system for massive scale implementation.

Map-Resolver (MR): An MR is a LISP Infrastructure device to which LISP site ITRs send LISP Map-Request queries when resolving EID-to-RLOC mappings.  Receives the request and selects the appropriate map server



<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMicrosoft%2FAzure-LISP%2Fmaster%2Flisp_lab_iterate_through_vnet.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>





![alt text](https://github.com/jgmitter/images/blob/master/Capture.PNG)








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
