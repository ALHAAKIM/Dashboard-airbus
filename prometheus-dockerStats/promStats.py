# python app that pushes docker stats infos as prometheus metrics
# docker stats -> prometheus client on port 8080

import prometheus_client
import docker
import time


UPDATE_PERIOD = 10

client = docker.from_env()
registry = prometheus_client.CollectorRegistry()

# Create a Prometheus gauge for each container, with the container ID and name as a label
CONTAINER_STATUS = prometheus_client.Gauge('container_status', 'Status of the container (0 = exited, 1 = running)', ['container_name','container_id'])
CONTAINER_CPU = prometheus_client.Gauge('container_cpu_percent', 'CPU percent usage by the container in %', ['container_name', 'container_id'])
CONTAINER_MEM = prometheus_client.Gauge('container_memory_usage', 'Memory usage by the container in MiB', ['container_name', 'container_id'])
CONTAINER_MEM_LIM = prometheus_client.Gauge('container_memory_limit', 'Memory limit of the container in MiB', ['container_name', 'container_id'])
CONTAINER_MEM_PER = prometheus_client.Gauge('container_memory_percent', 'Memory usage by the container in %', ['container_name', 'container_id'])

CONTAINER_NETWORK_IN = prometheus_client.Gauge('container_network_input', 'Input of the container over the network in kB', ['container_name', 'container_id'])
CONTAINER_NETWORK_OUT = prometheus_client.Gauge('container_network_output', 'Output of the container over the network in kB', ['container_name', 'container_id'])
CONTAINER_PIDS = prometheus_client.Gauge('container_pids', 'Number of PIDs of the container', ['container_name', 'container_id'])



if __name__ == '__main__':
    prometheus_client.start_http_server (8080)

while True:
    # loop through all containers
    for container in client.containers.list(all=True):
        # extract the wole docker stats stream
        stats = container.stats(stream=False)

        # generall infos about the container
        name = container.name
        id = container.short_id
        status = container.status
        status_boal = 1 if container.status == 'running' else 0
        
        #initialize the values about the CPU, memory & network with 0
        cpu_percent = 0.0
        mem_usage = 0.0
        mem_percent = 0.0
        networks_I = 0
        networks_O = 0
        pids = 0
        
        if status == 'running':
            # extrac values from the stream, if the container is running
            try:
                # infos about CPU & memory
                cpu_percent = stats ['cpu_stats']['cpu_usage']['total_usage'] / stats ['cpu_stats']['system_cpu_usage'] * 100
                mem_usage = stats ['memory_stats']['usage'] / 2**20         #in MiB
                mem_limit = stats ['memory_stats']['limit'] / 2**20         #in MiB
                mem_percent = (mem_usage / mem_limit) * 100

                # infos about the network & PIDs
                networks = stats ['networks']['eth0']
                networks_I = networks ['rx_bytes'] / 2**10                  #in kB
                networks_O = networks['tx_bytes'] / 2**10                   #in kB
                pids = stats ['pids_stats']['current']
            
            except KeyError:
                # Handle the error by printing an error message
                print("Warning: A key value was not found in stats_dict")

        
        # set infos & values to the prometheus metrics
        CONTAINER_STATUS.labels(container_name=name, container_id=id).set(status_boal)
        CONTAINER_CPU.labels(container_name=name, container_id=id).set(cpu_percent)
        CONTAINER_MEM.labels(container_name=name, container_id=id).set(mem_usage)
        CONTAINER_MEM_LIM.labels(container_name=name, container_id=id).set(mem_limit)
        CONTAINER_MEM_PER.labels(container_name=name, container_id=id).set(mem_percent)

        CONTAINER_NETWORK_IN.labels(container_name=name, container_id=id).set(networks_I)
        CONTAINER_NETWORK_OUT.labels(container_name=name, container_id=id).set(networks_O)
        CONTAINER_PIDS.labels(container_name=name, container_id=id).set(pids)
        
        prometheus_client.push_to_gateway('localhost:8080', job='my_job', registry=registry)
        
    time.sleep(UPDATE_PERIOD)


