import random
import numpy as np
import matplotlib.pyplot as plt
import openjij as oj

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

# アニーリング用パラメータ
def annealing_param():
    annealing_param = {} 
    annealing_param["num_reads"] = 1000
    annealing_param["beta_min"] = 0.1
    annealing_param["beta_max"] = 10.0
    annealing_param["num_sweeps"] = 100
    return annealing_param

# 実行
def exe():

    param = annealing_param()
    correct_state = create_correct_state()

    sampler = oj.SASampler()
    response = sampler.sample_ising(h, J, **param)
    tau = response.info['execution_time']
    energies = response.energies

    correct_answer = 0
    for e in energies:
        if e <= correct_state:
            correct_answer+=1

    vaild = correct_answer / param["num_reads"]
    tts = calc_tts(tau, vaild, param["num_reads"])

    print("calc_time      = ", tau, "[sec]", )
    print("correct_answer = ", correct_answer, "/", param["num_reads"])
    print("tts            = ", tts, "[sec]")

exe()
