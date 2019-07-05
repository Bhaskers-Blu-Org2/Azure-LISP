""" Prep steps
az login
az account set --subscription 'your-sub-id'
az ad sp create-for-rbac --name lisp-csr
Extract to variable below:
 appid = sp_client_id
 password = sp_secret
 tenant = sp_tenant_id
Navigate to portal (or automate) giving rights to that service principal over the resource group.
"""
import logging
import os
import json
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(threadName)s:%(message)s')
log = logging.getLogger(__name__)
import sys
from azure.mgmt.network import NetworkManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network.v2018_12_01.models.network_interface_ip_configuration import NetworkInterfaceIPConfiguration

# If running on cisco IOS...
try:
    from cli import execute
    config_dir = '/bootflash'
except:
    log.info('Not running on IOS, will use test IPs.')
    config_dir = '.'

site_config_file = os.path.join(config_dir, 'site_configs.json')
secret_config_file = os.path.join(config_dir, 'secret.json')

# Initialize some variables from json file
with open(site_config_file) as json_data:
    config_data = json.load(json_data)
resource_group = config_data['resource_group']
csr_azure_intf_name = config_data['csr_azure_intf_name']
site_name = config_data['site_name']

# Read secrets from json file
with open(secret_config_file, mode = 'rt') as json_data:
    secret_data = json.load(json_data)
sp_client_id = secret_data['sp_client_id']
sp_secret = secret_data['sp_secret']
sp_tenant_id = secret_data['sp_tenant_id']
sub_id = secret_data['sub_id']

def get_credentials():
    global sp_client_id,sp_secret,sp_tenant_id
    credentials = ServicePrincipalCredentials(
        client_id = sp_client_id,
        secret = sp_secret,
        tenant = sp_tenant_id
    )
    return credentials

def get_onprem_ips():
    if 'cli' not in sys.modules:
        # Testing without IOS
        on_prem_ips = [u'10.100.100.20'] #, u'10.100.100.5']
        log.info('Using test IPs {} for testing as this does not run on IOS'.format(on_prem_ips))
        # on_prem_ips = [u'10.100.100.20', u'10.100.100.30', u'10.100.100.31', u'10.100.100.32', u'10.100.100.33']
        ## will use REST for LIPS on IOSXR but for now testing it out...
    else:
        ios_lisp_show_output = execute('show ip lisp database eid-table default | inc {}'.format(site_name))
        log.info('IOS output of show = {}'.format(ios_lisp_show_output))
        on_prem_ips = [ip.split('/')[0] for ip in ios_lisp_show_output.split('\n')]
        log.info('Running on IOS. Picking up IPs {} in local database'.format(on_prem_ips))
    return on_prem_ips

if __name__ == "__main__":
    try:
        # Obtain credentials
        creds = get_credentials()
        # Network API client
        network_client = NetworkManagementClient(credentials = creds, subscription_id=sub_id)
        # Obtain CSR interface object
        csr_intf = network_client.network_interfaces.get(resource_group_name=resource_group,
                                            network_interface_name=csr_azure_intf_name)
        # Pick the subnet of the first ipconfig
        csr_intf_subnet = csr_intf.ip_configurations[0].subnet
        
        # Compare to onprem list of IPs
        new_onprem_ips = get_onprem_ips()

        # Remove the no longer valid ipconfigs (the hosts onprem that went away for instance - migrated to Azure for example)
        new_ip_config_list = []
        for idx, ipconfig in enumerate(csr_intf.ip_configurations):
            if ipconfig.primary:
                log.info("Adding primary IP {} to the list (primary IP of CSR in Azure).".format(ipconfig.private_ip_address))
                new_ip_config_list.append(ipconfig)
            else:
                if ipconfig.private_ip_address in new_onprem_ips:
                    log.info("Keeping the IP {} in the list".format(ipconfig.private_ip_address))
                    new_ip_config_list.append(ipconfig)
                else:
                    log.info("Dropping the IP {} from the current list".format(ipconfig.private_ip_address))

        # Adding new current onprem IPs
        new_ip_addresses_ip_config = [ipconfig.private_ip_address for ipconfig in new_ip_config_list]
        for idx, ip in enumerate(new_onprem_ips):
            # Add the new IP to the ipconfig list if it's not already there
            if ip not in new_ip_addresses_ip_config:
                ipconfig = NetworkInterfaceIPConfiguration(name = 'ipconfig_remote_{}'.format(ip),
                                                       private_ip_address = ip,
                                                       private_ip_allocation_method = u'Static',
                                                       subnet = csr_intf_subnet)
                log.info("Adding the IP {} to the list".format(ipconfig.private_ip_address))
                new_ip_config_list.append(ipconfig)

        try:
            # Trigger actual NIC udpdate
            csr_intf.ip_configurations = new_ip_config_list
            log.info("Triggering the update of the ipconfig in Azure to include the following list : {}".format([ipconfig.private_ip_address for ipconfig in new_ip_config_list]))
            update_result = network_client.network_interfaces.create_or_update(
                                    resource_group,
                                    csr_azure_intf_name,
                                    csr_intf)
            update_result.wait()
            log.info("Update completed.")
        except Exception as ex:
            log.info("Exception : {}".format(ex.message))
    except Exception as ex:
        log.info("Exception : {}".format(ex.message))
    log.info("Done.")
