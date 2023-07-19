# python app that pushes docker stats infos as prometheus metrics
# docker stats -> prometheus client on port 8080

import prometheus_client
import time
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
import psutil


UPDATE_PERIOD = 2

RAM_USAGE = prometheus_client.Gauge('ram_usage', 'RAM usage')

CPU_USAGE_ONE = prometheus_client.Gauge('cpu_usage_one', 'CPU usage 1')
CPU_USAGE_TWO = prometheus_client.Gauge('cpu_usage_two', 'CPU usage 2')
CPU_USAGE_THREE = prometheus_client.Gauge('cpu_usage_three', 'CPU usage 3')
CPU_USAGE_FOUR = prometheus_client.Gauge('cpu_usage_four', 'CPU usage 4')

BATTERY_PERCENTAGE = prometheus_client.Gauge('battery_percentage', 'Battery percentage')

registry = None

if __name__ == '__main__':
    prometheus_client.start_http_server (9999)

    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    # Unlike process and platform_collector gc_collector registers itself as three different collectors that have no corresponding public named variable. 
    REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])


while True:
    cpu_usages = []
    per_cpu = psutil.cpu_percent(percpu=True)
    for idx, usage in enumerate(per_cpu):
        cpu_usages.append(usage)

    RAM_USAGE.set(psutil.virtual_memory().percent)

    CPU_USAGE_ONE.set(cpu_usages[0])
    CPU_USAGE_TWO.set(cpu_usages[1])
    CPU_USAGE_THREE.set(cpu_usages[2])
    CPU_USAGE_FOUR.set(cpu_usages[3])

    BATTERY_PERCENTAGE.set(psutil.sensors_battery().percent)

    # gives an object with many fields
    psutil.virtual_memory()
    # you can convert that object to a dictionary 
    dict(psutil.virtual_memory()._asdict())
   # print(psutil.virtual_memory().percent)


    time.sleep(UPDATE_PERIOD)
