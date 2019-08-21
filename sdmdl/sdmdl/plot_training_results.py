import matplotlib.pyplot as plt
import pandas as pd
import math

def plot_training_results (path,verbose = True):
    
    if verbose:
        print('Plotting training results:', end = '')
    
    #Open the file with model performance metrics
    data=pd.read_csv(path+'/results/_DNN_performance/DNN_eval.txt',sep="\t")
    
    #set font size of axis
    plt.rcParams.update({'font.size': 15})
    
    #separate the metrics
    x=data["occ_samples"]
    x= [math.log10(i) for i in x]
    
    y1=data["Test_loss"]
    y2=data["Test_acc"]
    y3=data["Test_AUC"]
    #lci=data["Test_LCI95%"]
    #uci=data["Test_UCI95%"]
    wci=data["Test_UCI95%"]-data["Test_LCI95%"]
    
    #Plot loss
    fig,ax = plt.subplots()
    plt.scatter(x,y1,c="red")
    plt.xlabel("Occurrence samples",fontweight='bold')
    plt.ylabel("Test loss",fontweight='bold')
    labels=[item.get_text() for item in ax.get_xticklabels()]
    labels=['0','10','100','1000','10.000']
    ax.set_xticklabels(labels)
    fig.savefig(path+'/results/_DNN_performance/Test_loss.png', dpi=300,bbox_inches="tight")
    plt.show()
    
    #Plot accuracy
    fig,ax = plt.subplots()
    plt.scatter(x,y2,c="orange")
    plt.xlabel("Occurrence samples",fontweight='bold')
    plt.ylabel("Test accuracy",fontweight='bold')
    labels=[item.get_text() for item in ax.get_xticklabels()]
    labels=['0','10','100','1000','10.000']
    ax.set_xticklabels(labels)
    fig.savefig(path+'/results/_DNN_performance/Test_acc.png', dpi=300,bbox_inches='tight')
    plt.show()
    
    #Plot AUC
    fig,ax = plt.subplots()
    plt.scatter(x,y3)
    plt.xlabel("Occurrence samples",fontweight='bold')
    plt.ylabel("Test AUC",fontweight='bold')
    labels=[item.get_text() for item in ax.get_xticklabels()]
    labels=['0','10','100','1000','10.000']
    ax.set_xticklabels(labels)
    fig.savefig(path+'/results/_DNN_performance/Test_AUC.png', dpi=300,bbox_inches='tight')
    plt.show()
    
    #Plot confidence bands
    fig,ax = plt.subplots()
    points=plt.scatter(x,wci,c=y3,cmap="RdYlGn")
    cbar=plt.colorbar(points)
    cbar.set_label("AUC value")
    plt.xlabel("Occurrence samples",fontweight='bold')
    plt.ylabel("Confidence band width",fontweight='bold')
    labels=[item.get_text() for item in ax.get_xticklabels()]
    labels=['0','10','100','1000','10.000']
    ax.set_xticklabels(labels)
    fig.savefig(path+'/results/_DNN_performance/Confidence_width.png', dpi=300,bbox_inches='tight')
    plt.show()
    
    if verbose:
        print('Done!')