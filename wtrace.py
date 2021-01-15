from subprocess import PIPE, run
from concurrent.futures import ThreadPoolExecutor
import re

glinux_host = "higcp.bej.corp.google.com"
destination_URL_01 = "http://domain-01/"
destination_URL_02 = "http://domian-02/"
endpoint_list_file = "endpoints_list.data"
max_worker_num = 30
wtrace_reports = []
KV_01 = {}
KV_02 = {}

def run_wtrace(agent_ip, dest_url, kv):
    wtrace_cmd = "/google/data/ro/teams/internetto/wtrace --nowait --agent=" + agent_ip + " " + dest_url
#    cmd = 'ssh ' + glinux_host + ' "' + wtrace_cmd + '"' + '|grep "Response code\|Time elapsed"'
    cmd = 'ssh ' + glinux_host + ' "' + wtrace_cmd + '"' + '|grep "Time elapsed"'
    print(cmd)
    ret = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    #    print(ret.stdout)
    kv[agent_ip] = ret
    wtrace_reports.append([agent_ip, ret])
    return ret


def start_wtrace_thread_pool(list_file, max_worker, dest_url, kv):
    pool = ThreadPoolExecutor(max_workers=max_worker, thread_name_prefix="wtrace_")

    with open(list_file, 'r') as f:
        for line in f:
            ip = line.strip('\n')
            pool.submit(run_wtrace, ip, dest_url, kv)

    pool.shutdown(wait=True)
    print('threadPool shutdown')


def print_reports():
    index = 0
    with open(endpoint_list_file, 'r') as f:
        for line in f:
            index += 1
            ip = line.strip('\n')
            print("index: " + str(index))
            print(ip)
            print(re.findall(r'\d+', KV_01.get(ip).stdout))
            print(re.findall(r'\d+', KV_02.get(ip).stdout))


def print_reports_plant():
    index = 0
    with open(endpoint_list_file, 'r') as f:
        for line in f:
            index += 1
            ip = line.strip('\n')
            if((len(re.findall(r'\d+', KV_01.get(ip).stdout)) == 3) and (len(re.findall(r'\d+', KV_02.get(ip).stdout)) == 3)):
                prtstr = ip + ',' \
                         + re.findall(r'\d+', KV_01.get(ip).stdout)[0] \
                         + ',' + re.findall(r'\d+', KV_01.get(ip).stdout)[1]\
                         + ',' + re.findall(r'\d+', KV_01.get(ip).stdout)[2] \
                         + ',' + re.findall(r'\d+', KV_02.get(ip).stdout)[0] \
                         + ',' + re.findall(r'\d+', KV_02.get(ip).stdout)[1] \
                         + ',' + re.findall(r'\d+', KV_02.get(ip).stdout)[2]
            else:
                prtstr = ip

            print(prtstr)
#            print(re.findall(r'\d+', KV_01.get(ip).stdout))
#            print(re.findall(r'\d+', KV_02.get(ip).stdout))


start_wtrace_thread_pool(endpoint_list_file, max_worker_num, destination_URL_01, KV_01)
start_wtrace_thread_pool(endpoint_list_file, max_worker_num, destination_URL_02, KV_02)
print_reports_plant()
print('main finished')
