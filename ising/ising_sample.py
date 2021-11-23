import random
import numpy as np
import matplotlib.pyplot as plt
import openjij as oj
import neal
import time

# 問題設定
N = 30
h = {0: -10}
J = {(i, i+1): 1 for i in range(N-1)}

# モデル・最適解
def create_correct_state():

    correct_state = [(-1)**i for i in range(N)]
    bqm = oj.BinaryQuadraticModel.from_ising(h, J)
    minimum_energy = bqm.energy(correct_state)

    return minimum_energy

# TTS
def calc_tts(tau, vaild, num_reads):
    tts = 0
    pR = 0.99
    ps = vaild
    if vaild == 1:
        tts = tau
    elif vaild == 0:
        tts = 9999
    else:
        tts = tau*(np.log(1-pR)/np.log(1-ps))
    return tts

# サンプラー情報
jij_sasampler_info = "openjij.sampler.sa_sampler.SASampler"
dwave_neal_info = "neal.sampler.SimulatedAnnealingSampler"

# アニーリング用パラメータ
def annealing_param(sampler):
    annealing_param = {}
    annealing_param["num_reads"] = 100
    annealing_param["num_sweeps"] = 100
    if jij_sasampler_info in str(sampler):
        annealing_param["beta_min"] = 0.1
        annealing_param["beta_max"] = 10.0     
    elif dwave_neal_info in str(sampler):
        annealing_param["beta_range"] = [0.1, 10.0]
        
    return annealing_param

# 実行
def exe():
    correct_state = create_correct_state()
    sampler_list = [oj.SASampler(), neal.SimulatedAnnealingSampler()]
    
    for sampler in sampler_list:
        print(sampler)
        param = annealing_param(sampler)
        chk_time = time.time()
        response = sampler.sample_ising(h, J, **param)
        annealing_time = time.time() - chk_time
    
        correct_answer = 0
        if jij_sasampler_info in str(sampler):
            tau = response.info['execution_time'] / 1000000
            energies = response.energies
            for e in energies:
                if e <= correct_state:
                    correct_answer+=1
        elif dwave_neal_info in str(sampler):
            tau = annealing_time
            for s, e, n in response.data(["sample", "energy", "num_occurrences"]):
                if e <= correct_state:
                    correct_answer+=1

        vaild = correct_answer / param["num_reads"]
        tts = calc_tts(tau, vaild, param["num_reads"])

        print("calc_time      = ", tau, "[sec]", )
        print("correct_answer = ", correct_answer, "/", param["num_reads"])
        print("tts            = ", tts, "[sec]")
        print("")

exe()
