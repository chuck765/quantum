from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPTokenAuth

import json
from datetime import datetime
import neal
import time
import bz2
import ast
import os

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

#トークン認証関数
@auth.verify_token
def verify_token(token):

    # トークンリストに含まれているかを判定。ない場合は401を返す
    tokens = ["test", "", ""]
    if token in tokens:
        return True
    abort(401)


# dwave-neal実行結果確認API
@app.route('/dwave', methods=['POST'])
@auth.login_required
def dwave():
    try:
        # bz2圧縮したquboをマルチストリーム展開
        with open("qubo.txt.bz2", "rb") as f:
            data = f.read()
        qubo = None
        while data:
            decompressor = bz2.BZ2Decompressor()
            bytes = decompressor.decompress(data)
            data  = decompressor.unused_data
            qubo = ''.join(bytes.decode("utf-8"))
        qubo = ast.literal_eval(qubo)
        os.remove("qubo.txt.bz2")        

        # POSTしたパラメータを設定
        param = {}
        if "num_reads" in request.json:
            num_reads = int(request.json["num_reads"])
            param["num_reads"] = num_reads
        if "num_sweeps" in request.json:
            num_sweeps = int(request.json["num_sweeps"])
            param["num_sweeps"] = num_sweeps

        solver = neal.SimulatedAnnealingSampler()
        chk_time = time.time()
        response = solver.sample_qubo(qubo, **param)
        exe_time = time.time() - chk_time

        spins = []
        energys = []
        num_ocs = []
        for s,e,n in response.data(['sample', 'energy', 'num_occurrences']):
            spins.append(s)
            energys.append(e)
            num_ocs.append(n)
        
        result = jsonify({'spin': str(spins), 
                          'energy': str(energys),
                          'num_occurrences': str(num_ocs),
                          'time': str(exe_time)})
        return result
    except Exception as e:
        abort(e.code)

# セッションAPI
@app.route('/test/<string:session_id>', methods=['GET'])
def get_sessionId(session_id):
    try:
       result = {'state': 'success', 'sessionId': session_id}
       return jsonify(result)
    except Exception as e:
       abort(e.code)


# 共通エラー関数
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
def error_handler(e):

    # 独自のエラーメッセージ
    errorCause = None
    if e.code == 400:
        errorCause = "error_message_400"
    elif e.code == 401 :
        errorCause = "error_message_401"
    elif e.code == 404:
        errorCause = "error_message_404"
    elif e.code == 405:
        errorCause = "error_message_405"

    return jsonify({"error": {"state": "Failed",
                    "timeStamp": datetime.now(),
                    "errorMessage": e.description, 
                    "errorCode": e.code, 
                    "errorCause": errorCause }})


if __name__=="__main__":
    app.run()
