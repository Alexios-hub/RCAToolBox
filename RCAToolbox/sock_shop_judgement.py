import os
import json


class SockShopJudgement:
    def __init__(self):
        super().__init__()
        self.saved_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'saved', 'model')
        label_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'sock-shop')
        with open(os.path.join(label_path, 'label.json')) as f:
            self.label_dict = json.load(f)
        self.experiment_result_dict = dict()

    def load_experiment_result(self, model, alpha):
        self.experiment_result_dict = dict()
        saved_base_path = os.path.join(self.saved_path, model, 'sock_shop', 'alpha_' + str(alpha).replace('.', '_'), 'score_ranking_list')
        for root, dirs, files in os.walk(saved_base_path):
            for file in files:
                with open(os.path.join(saved_base_path, file)) as f:
                    temp_dict = json.load(f)
                    self.experiment_result_dict.update(temp_dict)
        pass

    def judge(self):
        total = 0
        ac = [0, 0, 0, 0, 0]
        for experiment_id, experiment_result in self.experiment_result_dict.items():
            if len(experiment_result) == 0:
                continue
            elif experiment_id in self.label_dict.keys():
                total += 1
                label = self.label_dict[experiment_id]
                if 'node-cpu' in label['type']:
                    for i in range(min(5, len(experiment_result))):
                        if 'service' in experiment_result[i][0]:
                            i -= 1
                            continue
                        if label['position'] in experiment_result[i][0] and 'CPU' in experiment_result[i][0]:
                            for j in range(i, 5):
                                ac[j] += 1
                            break
                if 'node-network' in label['type']:
                    for i in range(min(5, len(experiment_result))):
                        if 'service' in experiment_result[i][0]:
                            i -= 1
                            continue
                        if label['position'] in experiment_result[i][0] and 'Network' in experiment_result[i][0]:
                            for j in range(i, 5):
                                ac[j] += 1
                            break
                if 'pod-pod' in label['type']:
                    for i in range(min(5, len(experiment_result))):
                        if label['position'] in experiment_result[i][0]:
                            for j in range(i, 5):
                                ac[j] += 1
                            break
        avg = 0
        for j in range(0, 5):
            ac[j] /= total
            avg += ac[j]
        avg /= 5
        print(f'ac@1: {ac[0]}, ac@3: {ac[2]}, ac@5: {ac[4]}, avg@5: {avg}')


if __name__ == '__main__':
    sock_shop_judgement = SockShopJudgement()
    for i in [0.05, 0.1, 0.15]:
        sock_shop_judgement.load_experiment_result('cloud_ranger_runner', i)
        sock_shop_judgement.judge()
