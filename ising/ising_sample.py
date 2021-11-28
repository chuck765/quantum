import random
import numpy as np
import matplotlib.pyplot as plt
import openjij as oj
import neal
import dimod
import time

comp_flg = False # 比較モードフラグ

# モデル・最適解
def create_model():
    
    N = 30
    h = {0: -10}
    J = {(i, i+1): 1 for i in range(N-1)}
    correct_state = [(-1)**i for i in range(N)]
    bqm = oj.BinaryQuadraticModel.from_ising(h, J)
    minimum_energy = bqm.energy(correct_state)

    return h, J, minimum_energy

# TTS
def calc_tts(tau, ps):
    tts = 0
    pR = 0.99
    if ps == 1:
        tts = tau
    elif ps == 0:
        tts = 9999
    else:
        tts = tau*(np.log(1-pR)/np.log(1-ps))
    return tts

# サンプラー情報
jij_sasampler_info = "openjij.sampler.sa_sampler.SASampler"
dwave_neal_info = "neal"
dwave_dimod_info = "dimod"

# アニーリング用パラメータ
def annealing_param(sampler):
    annealing_param = {}
    annealing_param["num_reads"] = 100
    #annealing_param["num_sweeps"] = 50
    if jij_sasampler_info in str(sampler):
        annealing_param["beta_min"] = 0.1
        annealing_param["beta_max"] = 10.0     
    elif dwave_neal_info in str(sampler):
        annealing_param["beta_range"] = [0.1, 10.0]
    elif dwave_dimod_info in str(sampler):
        annealing_param["beta_range"] = [0.1, 10.0]
        
    return annealing_param

# 実行
def exe():
    h, J, correct_state = create_model()
    sampler_list = [oj.SASampler()]
    
    if comp_flg:
        sampler_list = [oj.SASampler(), neal.SimulatedAnnealingSampler(), dimod.SimulatedAnnealingSampler()]
    
    num_sweeps_list = [10, 30, 50, 70, 90]
    
    tts_list = []
    tau_list = []
    ps_list = []
    for num_sweeps in num_sweeps_list:
        for sampler in sampler_list:
            print(sampler, "num_sweeps = ", num_sweeps)
            param = annealing_param(sampler)
            param["num_sweeps"] = num_sweeps
            chk_time = time.time()
            response = sampler.sample_ising(h, J, **param)
            annealing_time = time.time() - chk_time
        
            correct_answer = 0
            if jij_sasampler_info in str(sampler):
                tau = response.info['execution_time'] / 1000000
                tau_list.append(tau)
                energies = response.energies
                for e in energies:
                    if e <= correct_state:
                        correct_answer+=1
            elif dwave_neal_info in str(sampler):
                tau = annealing_time
                tau_list.append(tau)
                for s, e, n in response.data(["sample", "energy", "num_occurrences"]):
                    if e <= correct_state:
                        correct_answer+=1

            ps = correct_answer / param["num_reads"]
            tts = calc_tts(tau, ps)
            
            if jij_sasampler_info in str(sampler):
                ps_list.append(ps)
                tts_list.append(tts)
            
        print("calc_time      = ", tau, "[sec]", )
        print("correct_answer = ", correct_answer, "/", param["num_reads"])
        print("tts            = ", tts, "[sec]")
        print("")
        
exe()
