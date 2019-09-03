from sklearn.metrics.ranking import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from keras.layers import Dense, Dropout, Activation
from imblearn.keras import balanced_batch_generator
from imblearn.under_sampling import NearMiss
from keras.models import Sequential
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shap
import tqdm
import os

# I want to be called Trainer and I need real documentation
class train_handler():
    """train_handler object that manages model training. """

    # These constructors must not be like this. They all look the same,
    # with the same object fields. Clearly they must inherit from a
    # base class. However, I really doubt they all must hold references
    # to oh, gh, ch. 
    def __init__(self, oh, gh, ch, verbose):

        """train_handler object initiation"""

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

        self.variables = self.gh.names.copy()

        self.spec = ''

        self.test_loss = []
        self.test_acc = []
        self.test_AUC = []
        self.test_tpr = []
        self.test_uci = []
        self.test_lci = []
        self.best_model_auc = [0]

        self.occ_len = 0
        self.abs_len = 0

        np_random = 42  # change later (e.g. self.ch.np_r)
        np.random.seed(np_random)

        self.btchs = 75  # change later (e.g. self.ch.batch)

        self.epoch = 150  # change later (e.g. self.ch.epoch)

    def create_eval(self):

        if not os.path.isdir(self.ch.result_path + '/_DNN_performance'):
            os.makedirs(self.ch.result_path + '/_DNN_performance')
        with open(self.ch.result_path + '/_DNN_performance/DNN_eval.txt', 'w+') as file:
            file.write(
                "Species" + "\t" + "Test_loss" + "\t" + "Test_acc" + "\t" + "Test_tpr" + "\t" + "Test_AUC" + "\t" + "Test_LCI95%" + "\t" + "Test_UCI95%" + "\t" + "occ_samples" + "\t" + "abs_samples" + "\n")
            file.close()

    def create_input_data(self):

        self.variables.remove("%s_presence_map" % self.spec)
        table = pd.read_csv(self.gh.spec_ppa_env + '/%s_env_dataframe.csv' % self.spec)
        table = table.drop('%s_presence_map' % self.spec, axis=1)
        table = table.dropna(axis=0, how="any")
        band_columns = [column for column in table.columns[1:len(self.gh.names)]]
        X = []
        y = []
        for _, row in table.iterrows():
            x = row[band_columns].values
            x = x.tolist()
            x.append(row["present/pseudo_absent"])
            X.append(x)
        df = pd.DataFrame(data=X, columns=band_columns + ["presence"])
        df.to_csv(self.gh.root + '/filtered.csv', index=None)
        self.occ_len = int(len(df[df["presence"] == 1]))
        self.abs_len = int(len(df[df["presence"] == 0]))
        X = []
        y = []
        band_columns = [column for column in df.columns[:-1]]
        for _, row in df.iterrows():
            X.append(row[band_columns].values.tolist())
            y.append([1 - row["presence"], row["presence"]])
        X = np.vstack(X)
        y = np.vstack(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=42)
        test_set = pd.DataFrame(X_test)
        test_set.rename(columns=dict(zip(test_set.columns[0:len(self.gh.names) - 1], self.variables)), inplace=True)
        shuffled_X_train = X_train.copy()
        np.random.shuffle(shuffled_X_train)
        shuffled_X_train = shuffled_X_train[:1000]
        shuffled_X_test = X_test.copy()
        np.random.shuffle(shuffled_X_test)
        shuffled_X_test = shuffled_X_test[:1000]
        return X, X_train, X_test, y_train, y_test, test_set, shuffled_X_train, shuffled_X_test

    def create_model_architecture(self, X):

        num_classes = 2
        num_inputs = X.shape[1]
        model = Sequential()
        layer_1 = Dense(250, activation='relu', input_shape=(num_inputs,))
        layer_2 = Dense(200, activation='relu', input_shape=(num_inputs,))
        layer_3 = Dense(150, activation='relu', input_shape=(num_inputs,))
        layer_4 = Dense(100, activation='relu', input_shape=(num_inputs,))  # kernel_regularizer
        model.add(layer_1)
        model.add(Dropout(0.3))
        model.add(layer_2)
        model.add(Dropout(0.5))
        model.add(layer_3)
        model.add(Dropout(0.3))
        model.add(layer_4)
        model.add(Dropout(0.5))
        out_layer = Dense(num_classes, activation=None)
        model.add(out_layer)
        model.add(Activation("softmax"))
        model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=0.001), metrics=['accuracy'])
        return model

    def train_model(self, model, X_train, X_test, y_train, y_test):

        training_generator, steps_per_epoch = balanced_batch_generator(X_train, y_train, sampler=NearMiss(),
                                                                       batch_size=self.btchs, random_state=42)
        model.fit_generator(generator=training_generator, steps_per_epoch=steps_per_epoch, epochs=self.epoch,
                            verbose=0)
        score = model.evaluate(X_test, y_test, verbose=0)
        predictions = model.predict(X_test)
        fpr, tpr, thresholds = roc_curve(y_test[:, 1], predictions[:, 1])
        len_tpr = int(len(tpr) / 2)
        self.test_loss.append(score[0])
        self.test_acc.append(score[1])
        self.test_AUC.append(roc_auc_score(y_test[:, 1], predictions[:, 1]))
        self.test_tpr.append(tpr[len_tpr])
        AUC = roc_auc_score(y_test[:, 1], predictions[:, 1])
        n_bootstraps = 1000
        y_pred = predictions[:, 1]
        y_true = y_test[:, 1]
        rng_seed = 42
        bootstrapped_scores = []
        rng = np.random.RandomState(rng_seed)
        for i in range(n_bootstraps):
            indices = rng.randint(0, len(y_pred) - 1, len(y_pred))
            if len(np.unique(y_true[indices])) < 2:
                continue
            score = roc_auc_score(y_true[indices], y_pred[indices])
            bootstrapped_scores.append(score)
        sorted_scores = np.array(bootstrapped_scores)
        sorted_scores.sort()
        ci_lower = sorted_scores[int(0.05 * len(sorted_scores))]
        ci_upper = sorted_scores[int(0.95 * len(sorted_scores))]
        self.test_lci.append(ci_lower)
        self.test_uci.append(ci_upper)
        return AUC, model

    def validate_model(self, model, AUC, X_train, X_test, shuffled_X_train, shuffled_X_test, test_set):

        if AUC > self.best_model_auc[0]:
            if not os.path.isdir(self.ch.result_path + '/%s' % self.spec):
                os.makedirs(self.ch.result_path + '/%s' % self.spec, exist_ok=True)
            self.best_model_auc[0] = AUC
            model_json = model.to_json()
            with open(self.ch.result_path + '/{}/{}_model.json'.format(self.spec, self.spec), 'w') as json_file:
                json_file.write(model_json)
            model.save_weights(self.ch.result_path + '/{}/{}_model.h5'.format(self.spec, self.spec))
            if int(len(X_train)) > 5000:
                explainer = shap.DeepExplainer(model, shuffled_X_train)
                test_set = pd.DataFrame(shuffled_X_test)
                test_set.rename(columns=dict(zip(test_set.columns[0:len(self.gh.names) - 1], self.variables)),
                                inplace=True)
                shap_values = explainer.shap_values(shuffled_X_test)
                shap.summary_plot(shap_values[1], test_set, show=False)
                plt.savefig(self.ch.result_path + '/{}/{}_feature_impact'.format(self.spec, self.spec),
                            bbox_inches="tight")
                plt.close()
            else:
                explainer = shap.DeepExplainer(model, X_train)
                shap_values = explainer.shap_values(X_test)
                shap.summary_plot(shap_values[1], test_set, show=False)
                plt.savefig(self.ch.result_path + '/{}/{}_feature_impact'.format(self.spec, self.spec),
                            bbox_inches="tight")
                plt.close()

    def update_performance_metrics(self):
        avg_loss = sum(self.test_loss) / len(self.test_loss)
        avg_acc = sum(self.test_acc) / len(self.test_acc)
        avg_AUC = sum(self.test_AUC) / len(self.test_AUC)
        avg_tpr = sum(self.test_tpr) / len(self.test_tpr)
        avg_lci = sum(self.test_lci) / len(self.test_lci)
        avg_uci = sum(self.test_uci) / len(self.test_uci)
        with open(self.ch.result_path + '/_DNN_performance/DNN_eval.txt', 'a') as file:
            file.write(self.spec + "\t" + str(avg_loss) + "\t" + str(avg_acc) + "\t" + str(avg_tpr) + "\t" + str(
                avg_AUC) + "\t" + str(avg_lci) + "\t" + str(avg_uci) + "\t" + str(self.occ_len) + "\t" + str(
                self.abs_len) + "\n")

    def train(self):
        self.create_eval()
        for self.spec in tqdm.tqdm(self.oh.name, desc='training models' + (35 * ' ')) if self.verbose else self.oh.name:
            X, X_train, X_test, y_train, y_test, test_set, shuffled_X_train, shuffled_X_test = self.create_input_data()
            self.best_model_auc = [0]
            for i in (tqdm.tqdm(range(1, 6), desc='%s' % self.spec + ((50 - len(self.spec)) * ' ')) if self.verbose else range(1, 6)):
                model = self.create_model_architecture(X)
                AUC, model = self.train_model(model, X_train, X_test, y_train, y_test)
                self.validate_model(model, AUC, X_train, X_test, shuffled_X_train, shuffled_X_test, test_set)
                self.update_performance_metrics()
