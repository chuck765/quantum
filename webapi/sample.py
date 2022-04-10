from pyqubo import Array, Constraint, Placeholder
import client

# pyquboでquboデータ生成
NUM_VER = 6
vertices = list(range(NUM_VER))
edges = [(0,1), (0,4), (0,5), (1,2), (1,3), (3,4), (4,5)]

x = Array.create('x', shape=NUM_VER, vartype='BINARY')
H_cover = Constraint(sum((1-x[u])*(1-x[v]) for (u,v) in edges), "cover")
H_vertices = sum(x)
H = H_vertices + Placeholder("cover") * H_cover
model = H.compile()
feed_dict = {"cover": 1.0}
qubo, offset = model.to_qubo(feed_dict=feed_dict)

# 作ったAPI
sampler = client.TestHostSampler()
result = sampler.sample(qubo, num_reads=1, num_sweeps=200)
print(result)
