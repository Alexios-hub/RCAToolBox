from base.base_runner import BaseRunner
from data_reader.standard_data_reader import StandardDataReader
from data_loader.standard_data_loader import StandardDataLoader
from pre_processor.sock_shop_pre_processor import SockShopPreProcessor
from ad_model.n_sigma_ad_model import NSigmaADModel
from utils.ad_utils import ADUtils
from rca_model.cloud_ranger_rca_model import CloudRangerModel
from localization.random_walk_localization import RandomWalkLocalization
import os
import json
from utils.config_handler import config_loader


class CloudRangerRunner(BaseRunner):
    """
    CloudRanger框架runner(整合整个根因分析过程).

    Attributes:
        config_dict: 异常检测、根因分析、定位的参数配置.
    """

    def __init__(self):
        super().__init__()
        self.config_dict = config_loader('cloud_ranger_runner_config.json')
        self.ad_model = NSigmaADModel()

    def run(self):
        # 构建data_loader
        standard_data_reader = StandardDataReader()
        demo_pre_processor = SockShopPreProcessor()
        self.data_loader = StandardDataLoader(standard_data_reader, demo_pre_processor)
        self.data_loader.load_data(rca_model_name='rca_model_name', dataset='sock-shop')

        # 训练集异常检测与预处理
        self.data_loader.train_data = self.data_preparation(self.data_loader.train_data)

        # RCA模型搭建（有监督的根据训练数据搭建，无监督的训练集等于测试集，因此搭建的就是测试集的模型）
        cloud_ranger_rca_model = CloudRangerModel()
        self.rca_model = cloud_ranger_rca_model.build(self.data_loader.train_data, self.config_dict['rca_model'])

    def test(self):
        # 测试集异常检测与预处理
        self.data_loader.test_data = self.data_preparation(self.data_loader.test_data)
        # 在测试集上进行根因定位
        cloud_ranger_localization = RandomWalkLocalization(order=2)
        result_dict = cloud_ranger_localization.localize(rca_model=self.rca_model,
                                                         data=self.data_loader.test_data,
                                                         config=self.config_dict['localization'])
        # base_dir = str(os.path.dirname(os.path.dirname(__file__))) + '/saved/model/cloud_ranger_runner/alpha_0_05' \
        #                                                              '/score_ranking_list/ '
        # experiment_list = list(result_dict.keys())
        # experiment_list.sort()
        # filename = f'{experiment_list[0]}.json'
        # with open(base_dir + filename, 'w') as json_file:
        #     json_file.write(json.dumps(result_dict))
        return result_dict

    def data_preparation(self, raw_data):
        """
        训练集、验证集、测试集可能需要统一地处理，归类到这里.

        :param raw_data: 训练集、验证集或测试集数据.
        :return: dict，包含data和entry_metric_name两个key，data为处理好的数据，entry_metric_name记录了开始分析的入口点.
        """
        result_dict = {
            'data': dict(),
            'entry_metric_name': dict()
        }

        for experiment_id, data in raw_data.items():
            forward_interval = self.config_dict['ad_model']['forward_interval']
            backward_interval = self.config_dict['ad_model']['backward_interval']

            for metric in data['metric']:
                self.ad_model.build_anomaly_model(metric, experiment_id)

            detect_metric_list = []
            for metric in data['metric']:
                if ('service' in metric.name and 'qps' in metric.name) or (
                        'node' in metric.name and 'System Load' in metric.name):
                    detect_metric_list.append(metric)
            first_timestamp_info = ADUtils.ad_metric_find_first_timestamp(ad_model=self.ad_model,
                                                                          metric_list=detect_metric_list,
                                                                          experiment_id=experiment_id)

            if len(first_timestamp_info) > 0:
                first_timestamp = first_timestamp_info[0][0]
                result_dict['entry_metric_name'][experiment_id] = first_timestamp_info[0][1]
            else:
                # TODO: 日志记录下这里存在问题
                print('No anomaly timestamp detected!: ', experiment_id)
                raw_data[experiment_id]['metric'] = []
                continue
            filtered_data = ADUtils.ad_metric_filter(ad_model=self.ad_model,
                                                     metric_list=data['metric'],
                                                     start_timestamp=first_timestamp - forward_interval,
                                                     end_timestamp=first_timestamp + backward_interval,
                                                     experiment_id=experiment_id)
            raw_data[experiment_id]['metric'] = filtered_data
            break
        result_dict['data'] = raw_data
        return result_dict

    def evaluation(self):
        pass


if __name__ == '__main__':
    cloud_ranger_runner = CloudRangerRunner()
    cloud_ranger_runner.run()
    print([i.name for i in cloud_ranger_runner.data_loader.train_data['data']['20210718_123000_SockShopPerformance']['metric']])
    final_result = cloud_ranger_runner.test()
    print(final_result)
    ...
