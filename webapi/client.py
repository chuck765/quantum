import requests
import configparser
from pyqubo import Array, Constraint, Placeholder
import json
import bz2

class TestHostSampler():

    def __init__(self, num_reads=1, num_sweeps=200):
        self.num_reads = num_reads
        self.num_sweeps = num_sweeps


    def sample(self, qubo, *args, **kwargs):
        # quboデータをbz2形式で圧縮し出力
        with bz2.open('./qubo.txt.bz2', 'wb') as f:
            f.write(str(qubo).encode('utf-8'))
        f.close()

        # 設定ファイル読み込み
        config = configparser.ConfigParser()
        config.read('api.conf')
        token = config['BASE']['token']
        url = config['BASE']['endpoint']

        # 入力してリクエスト
        payload = {"num_reads": self.num_reads, "num_sweeps": self.num_sweeps}
        headers = {'Authorization': 'Bearer {}'.format(token)}
        res = requests.post(url, json=payload, headers=headers)

        return res.text

