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

class train_handler():
    
    '''train_handler object that manages model training. '''
    
    def __init__(self,occurrence_handler,gis_handler,config_handler,verbose):
        
        '''train_handler object initiation'''
        
        self.oh = occurrence_handler
        self.gh = gis_handler
        self.ch = config_handler
        self.verbose = verbose
        
    def train_model(self):
        
        '''train_model function, responsible for training the deep learning models and writing the resulting models to file.'''
        
        np.random.seed(42)    
        if not os.path.isdir(self.ch.result_path + '/_DNN_performance'):
            os.makedirs(self.ch.result_path + '/_DNN_performance')
        with open(self.ch.result_path + '/_DNN_performance/DNN_eval.txt','w+') as file:
            file.write("Species"+"\t"+"Test_loss"+"\t"+"Test_acc"+"\t"+"Test_tpr"+"\t"+"Test_AUC"+"\t"+"Test_LCI95%"+"\t"+"Test_UCI95%"+"\t"+"occ_samples"+"\t"+"abs_samples"+"\n")
            file.close()            
        for species in tqdm.tqdm(self.oh.name,desc = 'training models' + (35 * ' ')) if self.verbose else self.oh.name:
            spec = species
            variables=self.gh.names.copy()
            variables.remove("%s_presence_map"%spec)        
            table = pd.read_csv(self.gh.spec_ppa_env + '/%s_env_dataframe.csv'%spec)
            table=  table.drop('%s_presence_map'%spec,axis=1)
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
            occ_len=int(len(df[df["presence" ]==1]))
            abs_len=int(len(df[df["presence" ]==0]))
            X = []
            y = []        
            band_columns = [column for column in df.columns[:-1]]        
            for _, row in df.iterrows():
                X.append(row[band_columns].values.tolist())
                y.append([1 - row["presence"], row["presence"]])        
            X = np.vstack(X)
            y = np.vstack(y)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, stratify=y,random_state=42)       
            test_set=pd.DataFrame(X_test)
            test_set.rename(columns=dict(zip(test_set.columns[0:len(self.gh.names)-1], variables)),inplace=True)        
            shuffled_X_train=X_train.copy()
            np.random.shuffle(shuffled_X_train)
            shuffled_X_train=shuffled_X_train[:1000]        
            shuffled_X_test=X_test.copy()
            np.random.shuffle(shuffled_X_test)
            shuffled_X_test=shuffled_X_test[:1000]
            test_loss=[]
            test_acc=[]
            test_AUC=[]
            test_tpr=[]
            test_uci=[]
            test_lci=[]        
            Best_model_AUC=[0]
            for i in (tqdm.tqdm(range(1,6),desc = '%s' % spec + ((50-len(spec)) * ' ')) if self.verbose else range(1,6)):
                btchs = 75
                num_classes = 2
                epch = 150        
                num_inputs = X.shape[1]        
                model = Sequential()
                layer_1 = Dense(250, activation='relu', input_shape=(num_inputs,))#, kernel_regularizer=regularizers.l2(0.000001))
                layer_2 = Dense(200, activation='relu', input_shape=(num_inputs,))#, kernel_regularizer=regularizers.l2(0.000001))
                layer_3 = Dense(150, activation='relu', input_shape=(num_inputs,))#, kernel_regularizer=regularizers.l2(0.0000001))
                layer_4 = Dense(100, activation='relu', input_shape=(num_inputs,))#, kernel_regularizer=regularizers.l2(0.00000001))        
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
                model.compile(loss="categorical_crossentropy",optimizer=Adam(lr=0.001),metrics =['accuracy'])
                training_generator,steps_per_epoch = balanced_batch_generator(X_train, y_train, sampler=NearMiss(), batch_size=btchs, random_state=42)
                model.fit_generator(generator=training_generator, steps_per_epoch=steps_per_epoch, epochs=epch, verbose=0)
                score = model.evaluate(X_test, y_test, verbose=0)
                predictions = model.predict(X_test)
                fpr, tpr, thresholds = roc_curve(y_test[:, 1], predictions[:, 1])
                len_tpr=int(len(tpr)/2)
                test_loss.append(score[0])
                test_acc.append(score[1])
                test_AUC.append(roc_auc_score(y_test[:, 1], predictions[:, 1]))
                test_tpr.append(tpr[len_tpr])
                AUC = roc_auc_score(y_test[:, 1], predictions[:, 1])
                n_bootstraps=1000
                y_pred=predictions[:,1]
                y_true=y_test[:,1]
                rng_seed=42
                bootstrapped_scores =[]       
                rng=np.random.RandomState(rng_seed)        
                for i in range (n_bootstraps):
                    indices = rng.randint(0,len(y_pred)-1,len(y_pred))
                    if len (np.unique(y_true[indices])) <2:
                        continue        
                    score = roc_auc_score(y_true[indices],y_pred[indices])
                    bootstrapped_scores.append(score)        
                sorted_scores=np.array(bootstrapped_scores)
                sorted_scores.sort()        
                ci_lower=sorted_scores[int(0.05*len(sorted_scores))]
                ci_upper=sorted_scores[int(0.95*len(sorted_scores))]        
                test_lci.append(ci_lower)
                test_uci.append(ci_upper)     
                if AUC > Best_model_AUC[0]:                    
                    if not os.path.isdir(self.ch.result_path + '/%s'%spec):
                        os.makedirs(self.ch.result_path + '/%s'%spec,exist_ok=True)
                    Best_model_AUC[0]=AUC
                    model_json=model.to_json()
                    with open (self.ch.result_path + '/{}/{}_model.json'.format(spec,spec),'w') as json_file:
                        json_file.write(model_json)
                    model.save_weights(self.ch.result_path + '/{}/{}_model.h5'.format(spec,spec))
                    if int(len(X_train)) > 5000:           
                        explainer=shap.DeepExplainer(model,shuffled_X_train)
                        test_set=pd.DataFrame(shuffled_X_test)
                        test_set.rename(columns=dict(zip(test_set.columns[0:len(self.gh.names)-1], variables)),inplace=True)        
                        shap_values=explainer.shap_values(shuffled_X_test)
                        shap.summary_plot(shap_values[1],test_set,show=False)
                        plt.savefig(self.ch.result_path + '/{}/{}_feature_impact'.format(spec,spec),bbox_inches="tight")
                        plt.close()        
                    else:
                        explainer=shap.DeepExplainer(model,X_train)
                        shap_values=explainer.shap_values(X_test)
                        shap.summary_plot(shap_values[1],test_set,show=False)
                        plt.savefig(self.ch.result_path + '/{}/{}_feature_impact'.format(spec,spec),bbox_inches="tight")
                        plt.close()
            avg_loss= sum(test_loss)/len(test_loss)
            avg_acc = sum(test_acc)/len(test_acc)
            avg_AUC = sum(test_AUC)/len(test_AUC)
            avg_tpr = sum(test_tpr)/len(test_tpr)
            avg_lci = sum(test_lci)/len(test_lci)
            avg_uci = sum(test_uci)/len(test_uci)        
            with open(self.ch.result_path + '/_DNN_performance/DNN_eval.txt','a') as file:
                file.write(spec+"\t"+str(avg_loss)+"\t"+str(avg_acc)+"\t"+str(avg_tpr)+"\t"+str(avg_AUC)+"\t"+str(avg_lci)+"\t"+str(avg_uci)+"\t"+str(occ_len)+"\t"+str(abs_len)+"\n")       