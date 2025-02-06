import json
import os
import gns3fy
import shutil

GNS3_SERVER_URL = "http://127.0.0.1:3080"
PROJECT_NAME = "projet gn3 tc v3"
PROJECT_PATH = "C:/Users/julie/GNS3/projects/projet gn3 tc v3"
gns3_server = gns3fy.Gns3Connector(GNS3_SERVER_URL)

json_file = "C:/Users/julie/GNS3/projects/projet gn3 tc v3/intent_file.json"
script_dir = os.path.dirname(os.path.abspath(__file__)) 
configs_dir = os.path.join(script_dir, "configs") 

with open(json_file, "r") as f:
    data = json.load(f)

for router, config in data["network"]["routers"].items():
    config_lines = []

    config_lines.append("!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!")
    config_lines.append("hostname "+router)
    config_lines.append("!\nboot-start-marker\nboot-end-marker\n!\n!\n!\nno aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n!\n!\n!\n!\n!")
    config_lines.append("no ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n!")
    config_lines.append("multilink bundle-name authenticated\n!\n!\n!\n!\n!\n!\n!\n!\n!\nip tcp synwait-time 5\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!")
    config_lines.append("interface Loopback0")
    config_lines.append(" no ip address")
    config_lines.append(" ipv6 address "+config['loopback'])
    config_lines.append(" ipv6 rip RIPNG enable" if config["igp"] == "RIPng" else " ipv6 ospf 1 area 0")
    config_lines.append("!")

    for intf, details in config["interfaces"].items():
        config_lines.append("interface "+intf)
        config_lines.append(" no ip address")
        config_lines.append(" negotiation auto")
        config_lines.append(" ipv6 address "+str(details['ip']))
        config_lines.append(" ipv6 rip RIPNG enable" if config["igp"] == "RIPng" else " ipv6 ospf 1 area 0")
        config_lines.append("!")

    router_number = int(router[1:])
    router_id = str(router_number)+"."+str(router_number)+"."+str(router_number)+"."+str(router_number)
    config_lines.append("router bgp "+str(config['as']))
    config_lines.append(" bgp router-id "+router_id)
    config_lines.append(" bgp log-neighbor-changes")
    
    for neighbor, details in config["ibgp_neighbors"].items():
        config_lines.append(" neighbor "+str(neighbor)+" remote-as "+ str(details['as']))
        config_lines.append(" neighbor "+neighbor+ " update-source Loopback0")
    
    if config.get("ebgp_neighbors"):
        
        for neighbor, details in config["ebgp_neighbors"].items():
            config_lines.append(" neighbor "+str(neighbor)+ " remote-as "+str(details['as']))

    config_lines.append("!")
    config_lines.append(" address-family ipv6")
    config_lines.append("  network "+config['loopback'])
    
    for intf, details in config["interfaces"].items():
        config_lines.append("  network "+details['ip'][:-4]+"/64")
    
    for neighbor, details in config["ibgp_neighbors"].items():
        config_lines.append("  neighbor "+neighbor+ " activate")
    
    if config.get("ebgp_neighbors"):
        
        for neighbor, details in config["ebgp_neighbors"].items():
            config_lines.append("  neighbor "+neighbor+" activate")
    
    config_lines.append(" exit-address-family")
    config_lines.append("!")
    config_lines.append("ip forward-protocol nd\n!\n!\nno ip http server\nno ip http secure-server\n!")
    if config["igp"]== "RIPng":
        config_lines.append("ipv6 router rip RIPNG")
    else:
        config_lines.append("ipv6 router ospf 1")
        config_lines.append(" router-id "+router_id)
    config_lines.append("!\n!\n!\n!\ncontrol-plane\n!\n!\nline con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n!\n!\nend")

    config_filename = os.path.join(configs_dir, "i"+router[1:]+"_startup-config.cfg")
    with open(config_filename, "w") as f:
        f.write("\n".join(config_lines))

    print("Configuration générée pour "+router+"→ "+config_filename)

project = gns3fy.Project(name=PROJECT_NAME, connector=gns3_server)
project.get()

for node in project.nodes:
    print("\nDéploiement de la configuration pour le routeur "+ node.name +" ...")
    node.stop()

    src = os.path.join(configs_dir, "i"+node.name[1:]+"_startup-config.cfg")
    dst = os.path.join(PROJECT_PATH, "project-files", "dynamips", node.node_id, "configs", "i"+node.name[1:]+"_startup-config.cfg")

    shutil.copy(src, dst)
    node.start()

print("\nDéploiement terminé ! Tous les routeurs sont configurés.")