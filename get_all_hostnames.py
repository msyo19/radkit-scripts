# Script to be executed either from the radkit-client directly
# (copy paste inside radkit-client), OR called as such:
# radkit-client script snmp_example.py

# User login and service connection

def parse_sys_services(value: int) -> str:
    capas = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
    binario = f"{int(value):07b}"[::-1]  # Invertimos para alinear con el orden L1 a L7
    activas = [capas[i] for i in range(7) if binario[i] == '1']
    return ",".join(activas)

user_id = input("Enter your CCO user id: ")
service_id = input("Enter your RADKit service id: ")
client = sso_login(user_id)
service = client.service(service_id).wait()

device_data = []

for dev in service.inventory.values():
    if dev.attributes.internal["snmp_config"]:
        print(f"{dev.name} supports SNMP")

        sys_name = service.inventory[dev.name].snmp.get("1.3.6.1.2.1.1.5.0").wait()
        hostname = str(sys_name.result[(1, 3, 6, 1, 2, 1, 1, 5, 0)].value)

        sys_services = service.inventory[dev.name].snmp.get("1.3.6.1.2.1.1.7.0").wait()
        services_value = int(sys_services.result[(1, 3, 6, 1, 2, 1, 1, 7, 0)].value)
        services_human = parse_sys_services(services_value)

        sys_descr = service.inventory[dev.name].snmp.get("1.3.6.1.2.1.1.1.0").wait()
        descr = str(sys_descr.result[(1, 3, 6, 1, 2, 1, 1, 1, 0)].value)

        ip = service.inventory[dev.name].attributes.internal["host"]

        print(f"Device: {hostname}, IP: {ip}, Services: {services_human}")
        print(f"Description: {descr}")

        device_data.append((hostname, ip, services_human, descr))

with open("hostnames.csv", "w", encoding="utf-8") as f:
    f.write("hostname,ip,sysServices,sysDescr\n")
    for hostname, ip, services, descr in device_data:
        descr_clean = descr.replace('"', '""').replace('\n', ' ').replace('\r', ' ')
        f.write(f"{hostname},{ip},{services},\"{descr_clean}\"\n")
