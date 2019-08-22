from sdmdl.sdmdl.import_variable_list import import_variable_list
from sklearn.metrics.ranking import roc_auc_score, roc_curve
from sdmdl.sdmdl.load_taxa_list import load_taxa_list
from sklearn.model_selection import train_test_split
from keras.layers import Dense, Dropout, Activation
from imblearn.keras import balanced_batch_generator
from imblearn.under_sampling import NearMiss
from keras.models import Sequential
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tqdm
import shap
import os

def train_model (path,verbose = True):
    
    np.random.seed(42)
    
    if not os.path.isdir(path+'/results/_DNN_performance'):
        os.makedirs(path+'/results/_DNN_performance')
    
    #create text file to store results in and close again:
    with open(path+'/results/_DNN_performance/DNN_eval.txt','w+') as file:
        file.write("Species"+"\t"+"Test_loss"+"\t"+"Test_acc"+"\t"+"Test_tpr"+"\t"+"Test_AUC"+"\t"+"Test_LCI95%"+"\t"+"Test_UCI95%"+"\t"+"occ_samples"+"\t"+"abs_samples"+"\n")
        file.close()
        
    #access file with list of taxa names
    taxa, _ = load_taxa_list(path)
    
    ###column variable names
    var_names, _, _ = import_variable_list(path)
        
    for species in tqdm.tqdm(taxa["taxon"][:],desc = 'training models' + (35 * ' ')) if verbose else taxa["taxon"][:]:
        
        #open dataframe and rename columns
        spec = species
        variables=var_names.copy()
        variables.remove("%s_presence_map"%spec) #drop species own occurrences from from variable list
    
        table = pd.read_csv(path +"/data/spec_ppa_env/%s_env_dataframe.csv"%spec)
        table=  table.drop('%s_presence_map'%spec,axis=1) #drop species own occurrences from features
    
        ####################################
        #  filter dataframe for training   #
        ####################################
        
        # drop any row with no-data values
        table = table.dropna(axis=0, how="any")
    
    
        # make feature vector
        band_columns = [column for column in table.columns[1:len(var_names)]]
    
        X = []
        y = []
    
        for _, row in table.iterrows():
            x = row[band_columns].values
            x = x.tolist()
            x.append(row["present/pseudo_absent"])
            X.append(x)
    
        df = pd.DataFrame(data=X, columns=band_columns + ["presence"])
        df.to_csv(path + "/data/filtered.csv", index=None)
    
        # extract n. of occ. and abs. samples
        occ_len=int(len(df[df["presence" ]==1]))
        abs_len=int(len(df[df["presence" ]==0]))
    
    
        ####################################
        #  Numpy feature and target array  #
        ####################################
        
        X = []
        y = []
    
        band_columns = [column for column in df.columns[:-1]]
    
        for _, row in df.iterrows():
            X.append(row[band_columns].values.tolist())
            y.append([1 - row["presence"], row["presence"]])
    
        X = np.vstack(X)
        y = np.vstack(y)
    
        ####################################
        #    Split training and test set   #
        ####################################
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, stratify=y,random_state=42)
    
    
        test_set=pd.DataFrame(X_test)
        test_set.rename(columns=dict(zip(test_set.columns[0:len(var_names)-1], variables)),inplace=True)
    
        shuffled_X_train=X_train.copy()
        np.random.shuffle(shuffled_X_train)
        shuffled_X_train=shuffled_X_train[:1000] # random subsample from test set for feature importance
    
        shuffled_X_test=X_test.copy()
        np.random.shuffle(shuffled_X_test)
        shuffled_X_test=shuffled_X_test[:1000] # random subsample from test set for feature importance
        
        ####################################
        #      Training and testing        #
        ####################################
        
        # prepare metrics
        test_loss=[]
        test_acc=[]
        test_AUC=[]
        test_tpr=[]
        test_uci=[]
        test_lci=[]
    
        Best_model_AUC=[0]
        
        # Five repetitions
        for i in (tqdm.tqdm(range(1,6),desc = '%s' % spec + ((50-len(spec)) * ' ')) if verbose else range(1,6)):
            btchs = 75
            num_classes = 2
            epch = 150
    
            num_inputs = X.shape[1]  # number of features
    
    
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
    
            model.compile(loss="categorical_crossentropy",
                        optimizer=Adam(lr=0.001),
                        metrics =['accuracy'])
           
            ###############
            # Train model #
            ###############
            training_generator,steps_per_epoch = balanced_batch_generator(X_train, y_train, sampler=NearMiss(), batch_size=btchs, random_state=42)
            model.fit_generator(generator=training_generator, steps_per_epoch=steps_per_epoch, epochs=epch, verbose=0)
    
            ##############
            # Test model #
            ##############
            score = model.evaluate(X_test, y_test, verbose=0)
            predictions = model.predict(X_test)
            fpr, tpr, thresholds = roc_curve(y_test[:, 1], predictions[:, 1])
            len_tpr=int(len(tpr)/2)
    
            #################
            # Append scores #
            #################
            test_loss.append(score[0])
            test_acc.append(score[1])
            test_AUC.append(roc_auc_score(y_test[:, 1], predictions[:, 1]))
            test_tpr.append(tpr[len_tpr])
            AUC = roc_auc_score(y_test[:, 1], predictions[:, 1])
    
            ###############################
            # Create confidence intervals #
            ###############################
            n_bootstraps=1000
            y_pred=predictions[:,1]
            y_true=y_test[:,1]
            rng_seed=42
            bootstrapped_scores =[]
    
    
            rng=np.random.RandomState(rng_seed)
    
            for i in range (n_bootstraps):
                #bootstrap by sampling with replacement on prediction indices
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
    
            
            ##############################################################
            # Selection of best model across runs and feature importance #
            ##############################################################
    
            #determine whether new model AUC is higher
            if AUC > Best_model_AUC[0]:
                
                if not os.path.isdir(path+'/results/%s'%spec):
                    os.makedirs(path+'/results/%s'%spec,exist_ok=True)
                
                # if yes save model to disk / overwrite previous model
                Best_model_AUC[0]=AUC
                model_json=model.to_json()
                with open (path+'/results/{}/{}_model.json'.format(spec,spec),'w') as json_file:
                    json_file.write(model_json)
                model.save_weights(path+'/results/{}/{}_model.h5'.format(spec,spec))
                #if yes, save a figure of shap feature value impact    
    
                if int(len(X_train)) > 5000:           
                    explainer=shap.DeepExplainer(model,shuffled_X_train)
                    test_set=pd.DataFrame(shuffled_X_test)
                    test_set.rename(columns=dict(zip(test_set.columns[0:len(var_names)-1], variables)),inplace=True)
    
                    shap_values=explainer.shap_values(shuffled_X_test)
                    shap.summary_plot(shap_values[1],test_set,show=False)
                    plt.savefig(path+'/results/{}/{}_feature_impact'.format(spec,spec),bbox_inches="tight")
                    plt.close()
    
                else:
                    explainer=shap.DeepExplainer(model,X_train)
                    shap_values=explainer.shap_values(X_test)
                    shap.summary_plot(shap_values[1],test_set,show=False)
                    plt.savefig(path+'/results/{}/{}_feature_impact'.format(spec,spec),bbox_inches="tight")
                    plt.close()
        
        # Model output metrics averaged across five runs to be written to file
        avg_loss= sum(test_loss)/len(test_loss)
        avg_acc = sum(test_acc)/len(test_acc)
        avg_AUC = sum(test_AUC)/len(test_AUC)
        avg_tpr = sum(test_tpr)/len(test_tpr)
        avg_lci = sum(test_lci)/len(test_lci)
        avg_uci = sum(test_uci)/len(test_uci)
    
        # Write to file
        with open(path+'/results/_DNN_performance/DNN_eval.txt','a') as file:
            file.write(spec+"\t"+str(avg_loss)+"\t"+str(avg_acc)+"\t"+str(avg_tpr)+"\t"+str(avg_AUC)+"\t"+str(avg_lci)+"\t"+str(avg_uci)+"\t"+str(occ_len)+"\t"+str(abs_len)+"\n")       