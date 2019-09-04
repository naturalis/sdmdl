from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.trainer import Trainer
import unittest
import pandas as pd
import numpy as np
import keras
import os
import tensorflow as tf


class TrainerTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.oh = Occurrences(self.root + '/root')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.ch = Config(self.root, self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False
        self.t = Trainer(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):
        self.assertEqual(self.t.oh, self.oh)
        self.assertEqual(self.t.gh, self.gh)
        self.assertEqual(self.t.ch, self.ch)
        self.assertEqual(self.t.verbose, self.verbose)
        self.assertEqual(self.t.spec, '')
        self.assertEqual(self.t.variables, [])
        self.assertEqual(self.t.test_loss, [])
        self.assertEqual(self.t.test_acc, [])
        self.assertEqual(self.t.test_AUC, [])
        self.assertEqual(self.t.test_tpr, [])
        self.assertEqual(self.t.test_uci, [])
        self.assertEqual(self.t.test_lci, [])
        self.assertEqual(self.t.best_model_auc, [0])
        self.assertEqual(self.t.occ_len, 0)
        self.assertEqual(self.t.abs_len, 0)
        self.assertEqual(self.t.np_random, 42)
        self.assertEqual(self.t.btchs, 75)
        self.assertEqual(self.t.epoch, 150)

    def test_create_eval(self):
        os.remove(self.root + '/root/results/_DNN_performance/DNN_eval.txt')
        self.assertFalse(os.path.isfile(self.root + '/root/results/_DNN_performance/DNN_eval.txt'))
        self.t.create_eval()
        self.assertTrue(os.path.isfile(self.root + '/root/results/_DNN_performance/DNN_eval.txt'))
        dnn_eval = pd.read_csv(self.root + '/root/results/_DNN_performance/DNN_eval.txt', delimiter='\t')
        dnn_eval_truth = pd.read_csv(self.root + '/trainer/create_eval.txt', delimiter='\t')
        self.assertEqual(dnn_eval.to_numpy().tolist(), dnn_eval_truth.to_numpy().tolist())

    def test_create_input_data(self):
        self.t.spec = self.oh.name[0]
        X, X_train, X_test, y_train, y_test, test_set, shuffled_X_train, shuffled_X_test = self.t.create_input_data()
        X_truth = np.load(self.root + '/trainer/X.npy')
        X_train_truth = np.load(self.root + '/trainer/X_train.npy')
        X_test_truth = np.load(self.root + '/trainer/X_test.npy')
        y_train_truth = np.load(self.root + '/trainer/y_train.npy')
        y_test_truth = np.load(self.root + '/trainer/y_test.npy')
        test_set_truth = np.load(self.root + '/trainer/test_set.npy')
        shuffled_X_train_truth = np.load(self.root + '/trainer/shuffled_X_train.npy')
        shuffled_X_test_truth = np.load(self.root + '/trainer/shuffled_X_test.npy')
        self.assertEqual(X.tolist(), X_truth.tolist())
        self.assertEqual(X_train.tolist(), X_train_truth.tolist())
        self.assertEqual(X_test.tolist(), X_test_truth.tolist())
        self.assertEqual(y_train.tolist(), y_train_truth.tolist())
        self.assertEqual(y_test.tolist(), y_test_truth.tolist())
        self.assertEqual(test_set.to_numpy().tolist(), test_set_truth.tolist())
        self.assertEqual(shuffled_X_train.tolist(), shuffled_X_train_truth.tolist())
        self.assertEqual(shuffled_X_test.tolist(), shuffled_X_test_truth.tolist())

    def test_create_model_architecture(self):
        self.t.spec = self.oh.name[0]
        X, _, _, _, _, _, _, _ = self.t.create_input_data()
        model = self.t.create_model_architecture(X)
        model_truth = keras.models.load_model(self.root + '/trainer/model.h5')
        self.assertEqual(model.get_config(), model_truth.get_config())
        weights = [x.tolist() for x in model.get_weights()]
        weights_truth = [x.tolist() for x in model_truth.get_weights()]
        self.assertEqual(weights, weights_truth)

    def notest_train_model(self):
        self.t.spec = self.oh.name[0]
        X, X_train, X_test, y_train, y_test, _, _, _ = self.t.create_input_data()
        model = self.t.create_model_architecture(X)
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        tf.Session(config=config)
        AUC, model = self.t.train_model(model, X_train, X_test, y_train, y_test)
        AUC_truth = 0.9930313588850174
        model_truth = keras.models.load_model(self.root + '/trainer/model_trained.h5')
        print(model.get_config())
        self.assertAlmostEqual(AUC, AUC_truth)
        #self.assertEqual(model.get_config(), model_truth.get_config()) ## look into this (it crashes when running the whole test suite but passes when only running this test)
        weights = [x.tolist() for x in model.get_weights()]
        weights_truth = [x.tolist() for x in model_truth.get_weights()]
        if len(weights) == len(weights_truth):
            for list in range(len(weights)):
                if len(weights[list]) == len(weights_truth[list]):
                    for lis in range(len(weights[list])):
                        np.testing.assert_almost_equal(weights[list][lis], weights_truth[list][lis], 6)

    def notest_update_performance_metrics(self):
        self.t.spec = self.oh.name[0]
        X, X_train, X_test, y_train, y_test, _, _, _ = self.t.create_input_data()
        model = self.t.create_model_architecture(X)
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        tf.Session(config=config)
        AUC, model = self.t.train_model(model, X_train, X_test, y_train, y_test)
        os.remove(self.root + '/root/results/_DNN_performance/DNN_eval.txt')
        self.assertFalse(os.path.isfile(self.root + '/root/results/_DNN_performance/DNN_eval.txt'))
        self.t.create_eval()
        self.t.update_performance_metrics()
        self.assertTrue(os.path.isfile(self.root + '/root/results/_DNN_performance/DNN_eval.txt'))
        dnn_eval = pd.read_csv(self.root + '/root/results/_DNN_performance/DNN_eval.txt', delimiter='\t')
        dnn_eval_truth = pd.read_csv(self.root + '/trainer/update_performance_metrics.txt', delimiter='\t')
        self.assertEqual(dnn_eval.to_numpy()[0][0],dnn_eval_truth.to_numpy()[0][0])
        np.testing.assert_almost_equal(dnn_eval.to_numpy()[0][1:], dnn_eval_truth.to_numpy()[0][1:],6)

if __name__ == '__main__':
    unittest.main()
