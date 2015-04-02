__author__ = 'Andre Kuck, Jan Philipp Harries'

#Litte Law Finder Alpha 0.1

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_rawdata(endogen,exogen):
    zwi=pd.DataFrame({'exo':exogen,'endo':endogen}).dropna()
    zwi=zwi.sort(columns='exo')
    zwi.index=zwi['exo']
    return zwi['endo']

def berechne_step(rawdata, lag, stype="increase"):
    rollrendite=pd.rolling_sum(rawdata,lag)
    #rollrendite=pd.rolling_sum(rawdata,lag, min_periods=0)
    if stype=="increase":
        rollrendite=rollrendite-rollrendite.shift(lag)
    rollrendite_no=pd.Series(index=np.arange(len(rollrendite)))
    rollrendite_no[(rollrendite_no.index%lag)==0]=rollrendite.reset_index()[0]
    rollrendite_no.index=rollrendite.index
    return rollrendite, rollrendite_no

def create_lawplot(fig,rollrendite,rollrendite_no,lag, min_emergenz, max_emergenz, emergenz_ueberl):
    plt.clf()
    plt.figure(fig.number)
    emergenz="  ja" if min_emergenz else "nein"
    emergenz_ueberl="  ja" if emergenz_ueberl else "nein"
    t_wahr="{0:5d}".format(min_emergenz) if emergenz=="  ja" else "  n/a"
    t_wahr_max="{0:5d}".format(max_emergenz) if max_emergenz else "  n/a"
    fenster="{0:5.1f}".format((len(rollrendite)-lag)/float(lag))
    grad_best="{0:5.1f}".format((len(rollrendite)-min_emergenz)/float(min_emergenz)) if emergenz=="  ja" else "  n/a"

    #fig=plt.figure(figsize=(12,8))
    ax=fig.add_subplot(1,1,1)
    ax.set_title('Little Law Finder', fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Summe ueber Lag')
    rollrendite.plot(label='Summe ueber T Messzeitpunkte')
    rollrendite_no.plot(marker='o', color='red', markersize=10.0, label='Summe ueber T nicht ueberlappende Messzeitpunkte')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25,
                     box.width, box.height * 0.75])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
              fancybox=True, shadow=True, ncol=5)

    #ax.set_xlim([rollrendite[~np.isnan(rollrendite)].index[0]-100,rollrendite.index[-1]])
    #todo debug
    try:
        ax.set_xlim([rollrendite[~np.isnan(rollrendite)].index[0],rollrendite.index[-1]]) #todo TEST raus
    except IndexError:
        import pdb
        pdb.set_trace()

    limits=ax.axis()
    text1x=limits[0]
    text1y=limits[2]-(limits[3]-limits[2])/2.05
    text1text=("Relation: Summe(np.log1p(data.CLOSE.pct_change()),T)>0\n"
               "Ordnung: DATE\n"
               "Wahr fuer T (min) = {}\n"
               "Wahr fuer alle T ueber = {}\n"
               "Grad induktiver Bestaetigung: {}   ( Fenster: {} )").format(t_wahr, t_wahr_max, grad_best, fenster)

    text1=ax.text(text1x,text1y,text1text, bbox=dict(facecolor='white', alpha=0.1), fontsize=12)

    text2x=limits[0]+(limits[1]-limits[0])/3*2
    text2text=("T = {}\n"
               "Emergenz erreicht: {}\n"
               "Emergenz in nicht\n"
               "ueberlappenden Sequenzen: {}\n").format(lag,emergenz,emergenz_ueberl)
    text1=ax.text(text2x,text1y,text2text, bbox=dict(facecolor='white', alpha=0.1), fontsize=12)


def find_laws(endogen, exogen,lag_step=250, stype="level", graphic=True):
    rawdata=create_rawdata(endogen,exogen)
    lag=lag_step
    rollrendite, rollrendite_no=berechne_step(rawdata,lag, stype=stype)
    i=0
    min_emergenz=0
    max_emergenz=0
    next_max=False
    emergenz_ueberl=0
    fig=plt.figure(figsize=(12,9))
    while lag<(len(rollrendite)/2)-lag_step:
        i+=1
        lag+=lag_step
        rollrendite,rollrendite_no=berechne_step(rawdata,lag, stype=stype)

        if round(rollrendite.min(),4)>=0:
            if not min_emergenz:
                min_emergenz=lag
                max_emergenz=lag
            if next_max:
                max_emergenz=lag
                next_max=False
        else:
            if min_emergenz:
                next_max=True

        if round(rollrendite_no.min(),4)>=0:
            if not emergenz_ueberl:
                emergenz_ueberl=lag

        create_lawplot(fig,rollrendite,rollrendite_no,lag, min_emergenz, max_emergenz, emergenz_ueberl)
        number=str(10000+i)
        #plt.savefig('E:\\Dev\\lawfinder_python\\filme\\'+number+'.png')
        fig.canvas.draw()
        plt.show(block=False)
        #break #todo DEBUG raus

    rollrendite,rollrendite_no=berechne_step(rawdata,min_emergenz, stype=stype)
    create_lawplot(fig,rollrendite,rollrendite_no,min_emergenz, min_emergenz, max_emergenz, emergenz_ueberl)
    plt.show()


if __name__=="__main__":
    data=pd.read_csv('E:\\Dev\\lawfinder_python\\beispiele\\close_spy.csv', delimiter=";")
    #data=data.set_index(pd.to_datetime(data.DATE))
    #data=data.drop(['DATE'],axis=1)
    data.DATE=pd.to_datetime(data.DATE)
    #Vars
    endogen=np.log1p(data.CLOSE.pct_change())#.shift(-1)
    exogen=data.DATE
    #exogen=np.log1p(data.CLOSE.pct_change())
    relation='groessergleich'
    stype='niveau' #niveau/steigung
    zwischenschritte=False
    xachse_zeitlich=False
    lag=250
    min=-1
    find_laws(endogen,exogen, stype=stype)