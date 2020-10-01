import glob
import os
import os.path
import sys
import csv
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import matplotlib as mpl
from matplotlib.ticker import ScalarFormatter

class iq3t_m():
    def __init__(self, folder, filelist=[], elements=[], data=[],offset = 3, length = 122,nb_line = 17,washout = 30):
        self.folder = folder
        self.filelist = filelist
        self.elements = elements
        self.data = data
        self.offset = offset
        self.length = length
        self.nb_line = nb_line
        self.washout = washout

    def csv_list(self, folder):
        filepath = glob.glob(folder + "/*.csv")
        filelist = sorted(s for s in filepath)
        return filelist

    def element_list(self,filelist):
        f = pd.read_csv(filelist[0],dtype = "str", skiprows = [14],header= 12 ,low_memory = False)[0:1]
        names = list(f.columns)
        elements = names[1:len(names)-1]
        self.elements = elements
        return elements

    def imaging(self,folder,file,element,offset,length, nb_line,washout):
        print("Analysis of " + file + "_" + element)
        df = pd.read_csv(file, dtype="float64", skiprows=[14], header=12, low_memory=False)
        ts = offset
        line_num = 0
        merged_line = pd.DataFrame()
        fig = plt.figure(figsize=(15,3))
        ax = fig.add_subplot(111)
        plt.rcParams['lines.linewidth'] = 0.3
        plt.plot(df['Time'],df[element],color='black',linewidth=0.3)

        for i in range(len(df[element])):
            line_num += 1
            y = df.query("@ts <Time< (@ts + @length)")[element]
            merged_line['line'+str(line_num)] = pd.Series(list(y))
            ax.axvspan(df.iloc[y.index[0]]["Time"],df.iloc[y.index[-1]]["Time"],color = "lightgray")
            l = length + washout
            ts += l
            if line_num == nb_line:
                break

        outname = file.split('.')[0]+'_'+element+'_signal.pdf'
        plt.savefig(outname)
        plt.close()

        outname = file.split('.')[0]+'_'+element+'.xlsx'
        merged_line.T.to_excel(outname, sheet_name=element)

        sns.set()
        plt.style.use('dark_background')
        plt.figure()
        ax = plt.subplot(111)
        sns.heatmap(merged_line.T,cmap='jet',xticklabels=False,yticklabels=False,ax=ax,cbar=False,robust=True)
        plt.tight_layout()
        outname = file.split('.')[0]+'_'+element+'_mapping.png'
        plt.savefig(outname)
        plt.style.use('default')
        plt.close()

    def moving(self,foler):
        dirname = self.folder+'/result'
        if os.path.isdir(dirname) == False:os.mkdir(dirname)
        os.system('mv '+self.folder+'/*.xlsx '+self.folder+'/result')

        dirname = self.folder+'/signal'
        if os.path.isdir(dirname) == False:os.mkdir(dirname)
        os.system('mv '+self.folder+'/*signal.pdf '+self.folder+'/signal')

        dirname = self.folder+'/mapping'
        if os.path.isdir(dirname) == False:os.mkdir(dirname)
        os.system('mv '+self.folder+'/*mapping.png '+self.folder+'/mapping')

    def execlusion(self,offset,length,nb_line,washout):
        l = self.csv_list(self.folder)
        elements = self.element_list(l)
        [[self.imaging(self.folder,file,i,offset = 5, length = 103,nb_line = 17,washout = 20) for i in elements] for file in l]
        self.moving(self.folder)
