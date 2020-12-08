from subprocess import PIPE, run
from concurrent.futures import ThreadPoolExecutor

glinux_host = "your glinux host name"
destination_URL = "your destination url"
endpoint_list_file = "endpoints_list.data"
max_worker_num = 30
wtrace_reports = []


def run_wtrace(agent_ip):
    wtrace_cmd = "/google/data/ro/teams/internetto/wtrace --nowait --agent=" + agent_ip + " " + destination_URL
    cmd = 'ssh ' + glinux_host + ' "' + wtrace_cmd + '"' + '|grep "Response code\|Time elapsed"'
    print(cmd)
    ret = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    #    print(ret.stdout)
    wtrace_reports.append([agent_ip, ret])
    return ret


def start_wtrace_thread_pool(list_file, max_worker):
    pool = ThreadPoolExecutor(max_workers=max_worker, thread_name_prefix="wtrace_")

    with open(list_file, 'r') as f:
        for line in f:
            ip = line.strip('\n')
            pool.submit(run_wtrace, ip)

    pool.shutdown(wait=True)
    print('threadPool shutdown')


def print_reports():
    index = 0
    for report in wtrace_reports:
        index += 1
        print("index: " + str(index))
        print(report[0])
        print(report[1].stdout)


start_wtrace_thread_pool(endpoint_list_file, max_worker_num)
print_reports()
print('main finished')
