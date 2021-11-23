#!/bin/python3

import os
import math
from pathlib import Path

home_dir        = Path.home()
run_case        = "test"
gem5_binary     = "build/X86_MESI_Two_Level/gem5.opt"
benchmark_dir   = os.path.join(home_dir, "benchmarks/rodinia_3.0/openmp/")
base_dir        = os.path.abspath(os.getcwd())
results_dir     = os.path.join(base_dir,
        os.path.join("isca_results",run_case))
bash_scripts_dir = os.path.join(base_dir,
        os.path.join("isca_scripts",run_case))
config_file     = os.path.join(base_dir, "configs/example/se.py")
pclist_dir      = os.path.join(base_dir, "pcs")

attack_rate     = [1]
policy          = ['policy_baseline', 'poilcy_jitter_all', 'policy_camouflage']
policy          = ['policy_baseline']
debug_flag_lists= ["JitterAllStats"]
debug_flags     = ','.join(map(str, debug_flag_lists))
debug_file      = "debug.out"

sim_cycles      = 1000000
max_hpc         = 3
lower_limit     = 20
upper_limit     = 80

n_cpus          = 64
n_dirs          = 64
n_l2caches      = 64
n_rows          = int(math.sqrt(n_dirs))

dest_list_all = ",".join([ str(i) for i in range(64) ])
attacker_node = dest_list_all
# attacker_node   = 0
destination_list= [dest_list_all]
target_latency  = 40

list_of_application = [
    'backprop',
    # 'b+tree',
    'heartwall',
    'kmeans',
    'lud',
    # 'nn',
    #'particlefilter',
    'srad_v1',
    'srad_v2',
    'bfs',
    'cfd',
    'hotspot',
    # 'lavaMD', #runtime error
    'myocyte',
    'nw',
    'pathfinder',
    'streamcluster',
    ]

# list_of_application = ['pathfinder']

application_cmd= {
    'kmeans'    : [benchmark_dir+"kmeans/kmeans_openmp/kmeans",
    "-n 64 -i "+benchmark_dir+"data/kmeans/kdd_cup"],
    'bfs'       :   [benchmark_dir+"bfs/bfs",
    "164 "+benchmark_dir+"data/bfs/graph1MW_6.txt"],
    'lavaMD'    :    [benchmark_dir+"lavaMD/lavaMD",
    "-cores 64 -boxes1d 10"],
    'lud'       :    [benchmark_dir+"lud/omp/lud_omp",
    "-n 64 -i "+benchmark_dir+"data/lud/512.dat"],
    'nn'        : [benchmark_dir+"nn/nn",
    "filelist_4 5 30 90"],
    'srad_v2'   :
        [benchmark_dir+"srad/srad_v2/srad",
    "2048 2048 0 127 0 127 64 0.5 2"],
    'srad_v1'   :
        [benchmark_dir+"srad/srad_v1/srad",
    "100 0.5 502 458 64"],
    'streamcluster' :
        [benchmark_dir+"streamcluster/sc_omp",
    "10 20 64 8192 8192 1000 none output.txt 64"],
    'nw'        : [benchmark_dir+"nw/needle",
    "2048 10 64"],
    'particlefilter' :
        [benchmark_dir+"particlefilter/particle_filter",
    "-x 128 -y 128 -z 10 -np 10000"],
    'cfd'       :
        [benchmark_dir+"cfd/euler3d_cpu",
    benchmark_dir+"data/cfd/fvcorr.down.097K"],
    'pathfinder':
        [benchmark_dir+"pathfinder/pathfinder",
    "100000 100 64"],
    'heartwall' :
        [benchmark_dir+"heartwall/heartwall",
    benchmark_dir+"data/heartwall/test.avi 20 64"],
    'backprop'  :
        [benchmark_dir+"backprop/backprop",
    "65536 64"],
    'b+tree'    :
        [benchmark_dir+"b+tree/b+tree.out",
    "core 64 file "+benchmark_dir+"data/b+tree/mil.txt command "
    +benchmark_dir+"data/b+tree/command.txt"],
    'hotspot'   :
        [benchmark_dir+"hotspot/hotspot",
    "512 512 2 64 "+benchmark_dir+"data/hotspot/temp_512  "
    +benchmark_dir+"data/hotspot/power_512"],
    'myocyte'   :
        [benchmark_dir+"myocyte/myocyte.out","100 1 0 64"]
}



def get_test_case(a,p):
    return "{}-{}".format(a,p)

def get_out_dir(dir_name, a,p):
    test_case = os.path.join(dir_name,get_test_case(a,p))
    #print(test_case)
    if not os.path.exists(test_case):
        try:
            os.makedirs(test_case)
        except(Exception):
            pass
            # print(Exception)
    return test_case




def get_gem5_command(a, p):
    outdir = get_out_dir(results_dir, a, p)
    s = os.path.join(base_dir,gem5_binary)
    #s += " --debug-flags={} ".format(debug_flags)
    #s += " --debug-file={} ".format(os.path.join(outdir,debug_file))
    s += " --outdir={} ".format(outdir)
    s += " --redirect-stdout "
    s += " --redirect-stderr "
    s += " --stdout-file={} ".format(os.path.join(outdir,"stdout.log"))
    s += " --stderr-file={} ".format(os.path.join(outdir,"stderr.log"))

    s += " {} ".format(config_file)

    s += "--num-cpus={} ".format(n_cpus)
    s += "--num-dirs={} ".format(n_dirs)
    s += "--network=garnet "
    s += "--topology=Mesh_XY "
    s += "--mesh-row={} ".format(n_rows)
    s += "--maxinsts={} ".format(sim_cycles)

    s += "--ruby "
    s += "--caches "
    s += "--l2cache "
    s += "--num-l2caches={} ".format(n_cpus)
    s += "--fast-forward=9223372036854775807 "
    s += "--policy={} ".format(p)
    s += "--attack-enabled "
    s += "--attack-node={} ".format(attacker_node)
    # s += "--max-hpc={} ".format(max_hpc)
    # s += "--lower-limit={} ".format(lower_limit)
    # s += "--upper-limit={} ".format(upper_limit)
    s += "--cmd={} ".format(application_cmd[a][0])
    s += "--options=\"{}\" ".format(application_cmd[a][1])
    s += "--destination-list={} ".format(destination_list[0])
    s += "--target-latency={} ".format(target_latency)
    s += "--attack-rate={} ".format(attack_rate[0])

    s += "--read_pc_list_from_file "
    s += "--pc_list_filename={}.txt ".format(os.path.join(pclist_dir, a))
    return s

def create_bash_script():
    try:
        os.makedirs(bash_scripts_dir)
        print("Created dir {}".format(bash_script_dir))
    except(Exception):
        pass

    for a in list_of_application:
        for p in policy:
            gem5_command = get_gem5_command(a,p)
            bash_script_filename = "{}.sh".format(get_test_case(a,p))
            # get_out_dir(bash_scripts_dir, a,p)
            bash_script_file = os.path.join(bash_scripts_dir,
                    bash_script_filename)
            print(gem5_command)
            with open(bash_script_file, "w") as f:
                print("#!/bin/bash", file=f)
                print("#SBATCH --exclude=compute012,compute013,compute014",
                        file=f)

                print("source ~/.bashrc", file=f)
                print("mkdir -p {}".format(os.path.join(results_dir,
                    get_test_case(a,p))),
                    file=f)
                print("{}".format(gem5_command), file=f)

def create_slurm_job():
    with open("{}.sh".format(run_case), "w") as f:
        print("#!/bin/bash",file=f)
        for a in list_of_application:
            for p in policy:
                bash_script_filename = "{}.sh".format(get_test_case(a,p))
                bash_script_file = os.path.join(bash_scripts_dir,
                        bash_script_filename)
                print("chmod +x {} &&".format(bash_script_file), file=f)
                print("sbatch {}".format(bash_script_file), file=f)


#print(get_out_dir(results_dir, "bfs","bypass_none"))
create_bash_script()
create_slurm_job()
