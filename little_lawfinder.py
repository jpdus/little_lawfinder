__author__ = 'Andre Kuck, Jan Philipp Harries'


"""
Litte Law Finder Alpha 0.1

Finds empirical laws in arbitrary data

More information on www.updl.de
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_rawdata(endogen,exogen):
    """Takes two pandas series of the same length and
    returns one series, indexed by the other.

    :param endogen: pandas series for which emergent laws will be searched
    :param exogen: pandas series (must be of same length as endogen) which will be used as explanatory variable
    :return: pandas series of endogen, indexed by exogen
    """
    zwi=pd.DataFrame({'exo':exogen,'endo':endogen}).dropna()
    zwi=zwi.sort(columns='exo')
    zwi.index=zwi['exo']
    return zwi['endo']

def calc_step(rawdata, lag, stype="level"):
    """Takes a series of an endogen variable indexed by an exogen variable and a lag and calculates
    a moving sum over lag periods. If stype is "increase", will return the increase of the moving sum over lag
    periods.

    :param rawdata: pandas series of an endogen variable indexed by an exogen variable
    :param lag: lag for which the moving sum is calculated (int)
    :param stype: should be "level" or "increase" (optional, default is "level"
    :return: Tuple of (moving sum/increase of moving sum, moving sum every lag periods)
    """
    rollrendite=pd.rolling_sum(rawdata,lag)
    if stype=="increase":
        rollrendite=rollrendite-rollrendite.shift(lag)
    elif stype=="level":
        pass
    else:
        raise ValueError('wrong stype - use "level" or "increase"')
    rollrendite_no=pd.Series(index=np.arange(len(rollrendite)))
    rollrendite_no[(rollrendite_no.index%lag)==0]=rollrendite.reset_index()[0]
    rollrendite_no.index=rollrendite.index
    return rollrendite, rollrendite_no

def create_lawplot(fig,rollrendite,rollrendite_no,lag, min_emergenz, max_emergenz, emergenz_ueberl,
                   des_endogen="endogenous variable", des_exogen="exogenous variable"):
    """Creates a Plot visualising the results

    :param fig: Matplotlib figure on which the plot will be drawed (should be of size (12,9))
    :param rollrendite: moving sum/increase of moving sum for endogen/exogen, output of calc_step()
    :param rollrendite_no: moving sum/increase of moving sum every lag periods, output of calc_step()
    :param lag: lag for which the moving sum was calculated (int)
    :param min_emergenz: minimum emergence level found, int - 0 if no emergence reached
    :param max_emergenz: lag for which all greater lags have reached emergence, int - 0 if no emergence reached
    :param emergenz_ueberl: minimum emergence level found for non overlapping periods, int - 0 if no emergence reached
    :param des_endogen: description for endogenous variable
    :param des_exogen: description for exogenous variable
    :return: edited matplotlib figure
    """
    plt.clf()
    plt.figure(fig.number)
    emergenz="yes" if min_emergenz else " no"
    emergenz_ueberl="yes" if emergenz_ueberl else " no"
    t_wahr="{0:5d}".format(min_emergenz) if min_emergenz else "  n/a"
    t_wahr_max="{0:5d}".format(max_emergenz) if max_emergenz else "  n/a"
    fenster="{0:5.1f}".format((len(rollrendite)-lag)/float(lag))
    grad_best="{0:5.1f}".format((len(rollrendite)-min_emergenz)/float(min_emergenz)) if min_emergenz else "  n/a"

    ax=fig.add_subplot(1,1,1)
    ax.set_title('Little Law Finder', fontsize=16)
    ax.set_xlabel(des_exogen)
    ax.set_ylabel('Sum over lag')
    rollrendite.plot(label='Sum over T periods')
    rollrendite_no.plot(marker='o', color='red', markersize=10.0, label='Sum over T non-overlapping periods')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.25,
                     box.width, box.height * 0.75])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
              fancybox=True, shadow=True, ncol=5)
    ax.set_xlim([rollrendite[~np.isnan(rollrendite)].index[0],rollrendite.index[-1]])
    limits=ax.axis()
    text1x=limits[0]
    text1y=limits[2]-(limits[3]-limits[2])/2.05
    text1text=("Relation: {}\n"
               "Order: {}\n"
               "True for T (min) = {}\n"
               "True for all T above = {}\n"
               "Degree of inductive Verification: {}   ( Window: {} )").format(des_endogen, des_exogen, t_wahr, t_wahr_max, grad_best, fenster)

    text1=ax.text(text1x,text1y,text1text, bbox=dict(facecolor='white', alpha=0.1), fontsize=12)
    text2x=limits[0]+(limits[1]-limits[0])/3*2
    text2text=("T = {}\n"
               "Emergence reached: {}\n"
               "Emergence in non-overlapping\n"
               "sequences reached: {}\n").format(lag,emergenz,emergenz_ueberl)
    text1=ax.text(text2x,text1y,text2text, bbox=dict(facecolor='white', alpha=0.1), fontsize=12)
    return fig


def find_laws(endogen, exogen,lag_step=250, stype="level", plot_result=True, savepath="",
              des_endogen="endogenous variable", des_exogen="exogenous variable"):
    """Find empirical laws and calculate levels of Emergence

    :param endogen: Endogenous variable (pandas series)
    :param exogen:  Exogenous variable (pandas series - must have same length as endogen)
    :param lag_step: Min lag and step for lag increase (int, should be >len(endogen)/1000) - default 250
    :param stype: "level" for moving aggregation or "increase" for increase of aggregate sum - default level
    :param plot_result: True if result should be visualized, False for quiet mode - default True
    :param savepath: Path for plot images to be saved - empty string for no saving - default ""
    :return: Tuple of (Minimum level of Emergence, lag for which all greater lags have reached emergence,
             minimum emergence level found for non overlapping periods, Degree of inductive Verification)
    """
    rawdata=create_rawdata(endogen,exogen)
    lag=lag_step
    rollrendite, rollrendite_no=calc_step(rawdata,lag, stype=stype)
    i=0
    min_emergenz=0
    max_emergenz=0
    next_max=False
    emergenz_ueberl=0
    if plot_result:
        fig=plt.figure(figsize=(12,9))
    while lag<(len(rollrendite)/2)-lag_step:
        i+=1
        lag+=lag_step
        rollrendite,rollrendite_no=calc_step(rawdata,lag, stype=stype)

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

        if plot_result:
            create_lawplot(fig,rollrendite,rollrendite_no,lag, min_emergenz, max_emergenz, emergenz_ueberl,
                           des_endogen=des_endogen, des_exogen=des_exogen)
            if savepath:
                number=str(10000+i)
                plt.savefig(savepath+number+'.png')
            fig.canvas.draw()
            plt.show(block=False)

    div=(len(rollrendite)-min_emergenz)/float(min_emergenz)
    print "Emergence reached: {}".format("yes" if min_emergenz else " no")
    print "True for T (min): {0:5d}".format(min_emergenz)
    print "True for all T above: {0:5d}".format(max_emergenz)
    print "Degree of inductive Verification: {0:5.1f}".format(div)

    if plot_result:
        rollrendite,rollrendite_no=calc_step(rawdata,min_emergenz, stype=stype)
        create_lawplot(fig,rollrendite,rollrendite_no,min_emergenz, min_emergenz, max_emergenz, emergenz_ueberl,
                       des_endogen=des_endogen, des_exogen=des_exogen)
        plt.show()
    return min_emergenz,max_emergenz,emergenz_ueberl,div


if __name__=="__main__":
    #example data
    data=pd.read_csv('E:\\Dev\\lawfinder_python\\beispiele\\close_spy.csv', delimiter=";")
    data.DATE=pd.to_datetime(data.DATE)

    #define exogenous and endogenous variables
    endogen=np.log1p(data.CLOSE.pct_change()).shift(-1)
    exogen=data.DATE #select stype="level"
    #exogen=np.log1p(data.CLOSE.pct_change()) #select stype="increase"

    #find laws!
    find_laws(endogen,exogen, stype="level", des_endogen="SPY log return of next trading day", des_exogen="Date")