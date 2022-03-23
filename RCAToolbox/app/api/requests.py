from werkzeug.utils import secure_filename
from flask import request

from runner.cloud_ranger_runner import CloudRangerRunner
from . import api
import os


@api.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print('POST detected!')
        file = request.files['file']
        if file is None:
            return "No file uploaded"
        file_path = os.path.join(os.getcwd(),
                                 f'saved/upload/{secure_filename(file.filename)}')
        file.save(file_path)
        return '<h1>Upload new File</h1>'


@api.route('/metric_list', methods=['GET'])
def get_metric_list():
    print('get metric list')
    cloud_ranger_runner = CloudRangerRunner()
    cloud_ranger_runner.run()
    return {'metric_list': [i.name for i in cloud_ranger_runner.data_loader.train_data['data']['20210718_123000_SockShopPerformance']['metric']]}


@api.route('/kpi/', methods=['GET'])
def get_kpi():
    print('get kpi')
    metric_name = request.args.get('name')
    print(metric_name)
    cloud_ranger_runner = CloudRangerRunner()
    cloud_ranger_runner.run()
    for i in cloud_ranger_runner.data_loader.train_data['data']['20210718_123000_SockShopPerformance']['metric']:
        if i.name == metric_name:
            return {'timestamp': [int(j) for j in i.sample['timestamp']], 'value': i.sample['value'].tolist()}
    return {'kpi': []}


@api.route('/run/cloud_ranger', methods=['GET'])
def run_cloud_ranger():
    print('run CloudRanger')
    cloud_ranger_runner = CloudRangerRunner()
    cloud_ranger_runner.run()
    final_result = cloud_ranger_runner.test()
    return {'score_list': final_result['20210718_123000_SockShopPerformance'],
            'url': '/Users/algiz/Desktop/Projects/Pycharm/RCAToolbox/saved/myplot.png'}
