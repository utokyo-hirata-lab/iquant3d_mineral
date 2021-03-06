import glob
import os
import os.path
import sys
import csv
import warnings
import itertools
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import matplotlib as mpl
from matplotlib.ticker import ScalarFormatter
import plotly.offline
import plotly.graph_objects as go
import plotly.figure_factory as ff

class iq3t_m():
    def __init__(self, folder, filelist=[], elements=[], data=[],std_element = "29Si", offset = 3, length = 122,nb_line = 17,washout = 30):
        self.folder = folder
        self.filelist = filelist
        self.elements = elements
        self.data = data
        self.offset = offset
        self.length = length
        self.nb_line = nb_line
        self.washout = washout
        self.std_element = std_element

    def csv_list(self, folder):
        filepath = glob.glob(folder + "/*.csv")
        filelist = sorted(s for s in filepath)
        return filelist

    def element_list(self, filelist):
        f = pd.read_csv(filelist[0], dtype="str", skiprows=[14], header=12, low_memory=False)[0:1]
        names = list(f.columns)
        elements = names[1:len(names)-1]
        self.elements = elements
        return elements

    def translate_data(self,file,std_element,elements,gasdata,stddata,concentration):
        df_gas = pd.read_csv(gasdata,skiprows=[14],header=12,dtype='float64',index_col = 0, low_memory=False)
        df_std = pd.read_csv(stddata,skiprows=[14],header=12,dtype='float64',index_col = 0, low_memory=False)
        df_intencity = pd.read_csv(concentration,header = 0,low_memory = False)
        std_intencity = df_std - df_gas.mean()
        mean_data = std_intencity.mean()
        new_file = file[elements]*(28*1000000/190)*(df_intencity[elements][0]/df_intencity[std_element][0])/(file[std_element]*(mean_data[elements]/mean_data[std_element]))
        return new_file



    def imaging(self, folder, file, element, offset, length, nb_line, washout):
        print("Analysis of " + file + "_" + element)
        df = pd.read_csv(file, dtype="float64", skiprows=[14], header=12, low_memory=False)
        #print(df.head(10))
        ts = offset
        line_num = 0
        merged_line = pd.DataFrame()
        fig = plt.figure(figsize=(15, 3))
        ax = fig.add_subplot(111)
        plt.rcParams['lines.linewidth'] = 0.3
        plt.plot(df['Time'], df[element], color='black', linewidth=0.3)

        for i in range(len(df[element])):
            line_num += 1
            y = df.query("@ts <Time< (@ts + @length)")[element]
            merged_line['line'+str(line_num)] = pd.Series(list(y))
            ax.axvspan(df.iloc[y.index[0]]["Time"], df.iloc[y.index[-1]]["Time"], color="lightgray")
            line_length = length + washout
            ts += line_length
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
        sns.heatmap(merged_line.T, cmap='jet', xticklabels=False, yticklabels=False, ax=ax, cbar=True, robust=True)
        plt.tight_layout()
        outname = file.split('.')[0]+'_'+element+'_mapping.png'
        plt.savefig(outname)
        plt.style.use('default')
        plt.close()

    def imaging_quantum(self, folder, file, element, offset, length, nb_line, washout,gasdata,stddata,concentration, std_element = "29Si"):
        print("Analysis of " + file + "_" + element)
        row_data = pd.read_csv(file, dtype="float64", skiprows=[14], header=12,low_memory=False)
        data = self.translate_data(row_data,std_element,element,gasdata,stddata,concentration)
        data.index = row_data["Time"]
        df = data.reset_index()
        df.columns = ["Time",element]
        #print(df.head(10))
        ts = offset
        line_num = 0
        merged_line = pd.DataFrame()
        fig = plt.figure(figsize=(15, 3))
        ax = fig.add_subplot(111)
        plt.rcParams['lines.linewidth'] = 0.3
        plt.plot(df["Time"], df[element], color='black', linewidth=0.3)

        for i in range(len(df[element])):
            line_num += 1
            y = df.query("@ts <Time < (@ts + @length)")[element]
            merged_line['line'+str(line_num)] = pd.Series(list(y))
            ax.axvspan(df.iloc[y.index[0]]["Time"], df.iloc[y.index[-1]]["Time"], color="lightgray")
            line_length = length + washout
            ts += line_length
            if line_num == nb_line:
                break

        outname = file.split('.')[0]+'_'+element+'_q_signal.pdf'
        plt.savefig(outname)
        plt.close()

        outname = file.split('.')[0]+'_'+element+'_q.xlsx'
        merged_line.T.to_excel(outname, sheet_name=element)

        sns.set()
        plt.style.use('dark_background')
        plt.figure()
        ax = plt.subplot(111)
        sns.heatmap(merged_line.T, cmap='jet', xticklabels=False, yticklabels=False, ax=ax, cbar=True, robust=True)
        plt.tight_layout()
        outname = file.split('.')[0]+'_'+element+'_q_mapping.png'
        plt.savefig(outname)
        plt.style.use('default')
        plt.close()


    def moving(self, folder):
        dirname = self.folder+'/result'
        if os.path.isdir(dirname) is False:
            os.mkdir(dirname)
        os.system('mv '+self.folder+'/*.xlsx '+self.folder+'/result')

        dirname = self.folder+'/signal'
        if os.path.isdir(dirname) is False:
            os.mkdir(dirname)
        os.system('mv '+self.folder+'/*signal.pdf '+self.folder+'/signal')

        dirname = self.folder+'/mapping'
        if os.path.isdir(dirname) is False:
            os.mkdir(dirname)
        os.system('mv '+self.folder+'/*mapping.png '+self.folder+'/mapping')
        print("Complite!")


    def ccf(self, file, element_a, element_b, std, threshold):
        data = pd.read_csv(file, dtype="float64", skiprows=[14], header=12, low_memory=False)
        df = data[data[std] > threshold]
        sig_a = (df[element_a] - df[element_a].mean())/(df[element_a].std(ddof = 0)*len(df[element_a]))
        sig_b = (df[element_b] - df[element_b].mean())/df[element_b].std(ddof = 0)
        corr = np.correlate(list(sig_a), list(sig_b))
        return np.round(corr,decimals = 3)[0]

    def ccf_table(self,file,elements, std, threshold):
        list = []
        ind, col = elements, elements
        x = len(elements)
        ccf_element = [np.nan]*x
        for p in itertools.product(range(x), repeat=2):#デカルト積
            ccf_element[p[1]] = self.ccf(file,elements[p[0]],elements[p[1]], std, threshold)
            print(ccf_element[p[1]])
            list.append(ccf_element[p[1]])

        new_list = np.array(list).reshape(x,x).tolist()

        """
        2重ループ
        for i in range(len(elements)):
            ccf_element = [np.nan]*len(elements)
            for j in range(i,len(elements)):
                ccf_element[j] = self.ccf(file,elements[i],elements[j], std, threshold)
        """
        df = pd.DataFrame(new_list,index = ind, columns = col)
        return df.T

    def execlusion(self, offset, length, nb_line, washout):
        l = self.csv_list(self.folder)
        print(l)
        elements = self.element_list(l)
        [[self.imaging(self.folder, file, i, offset, length, nb_line, washout) for i in elements] for file in l]
        self.moving(self.folder)
        # offset=5, length=103, nb_line=17, washout=20がデフォルト

    def execlusion_quantum(self, offset, length, nb_line, washout,std_element = "29Si"):
        l = self.csv_list(self.folder)

        for file in l:
            print(file)
            gasdata = input('Enter gasblank data:')
            stddata = input('Enter std data:')
            concentration = input("Enter intencity data:")
            elements = self.element_list(l)
            [self.imaging_quantum(self.folder, file, i, offset, length, nb_line, washout,gasdata,stddata,concentration,std_element = "29Si") for i in elements]
        self.moving(self.folder)

    def normalize(self, element, base):
        intmin,intmax,frag = float(),float(),0
        base_list = glob.glob(self.folder +'/result/*'+base+'_q.xlsx')
        element_list = glob.glob(self.folder +'/result/*'+element+'_q.xlsx')
        print(base_list)
        print(element_list)

        print("normalizing")
        for i in range(len(base_list)):
            base_data = pd.read_excel(base_list[i], index_col = 0)
            element_data = pd.read_excel(element_list[i],index_col = 0)
            nimage = element_data/base_data
            if frag == 0:
                    intmin = nimage.min().min()
                    intmax = nimage[int(len(nimage)/2)][int(len(nimage[0])/2)]
                    print(intmax,intmin)
                    frag = 1
            outname = self.folder+'/mapping/'+base_list[i].split('/')[-1].split('_')[0]+'_'+element+'_per'+base+'.png'
                #outname = datalist_c[i].split('/')[-1].split('_')[0] + '_' + outname
            print(outname)
            sns.set()
            plt.style.use('dark_background')
            sns.heatmap(nimage,cmap='jet',vmin=intmin,vmax=intmax,xticklabels=False,yticklabels=False,cbar=True)
            plt.tight_layout()
            plt.savefig(outname)
            plt.close('all')
        print("Complete!")

    def print_ccf(self, std, threshold):
        warnings.filterwarnings('ignore')
        l = self.csv_list(self.folder)
        elements = self.element_list(l)
        print(elements)
        for file in l:

            #plotlyを使う
            df = self.ccf_table(file, elements, std, threshold)
            #print(df)
            fig = ff.create_annotated_heatmap(z = df.values.tolist(),x = list(df.columns),y = list(df.index),colorscale = "oranges")
            outname = file.split('.')[0]+"_correelation_coeeficient.html"
            fig.write_html(outname, auto_open=False)
            fig.show()

            #matplotlib(普通の)

            #seabornをつかう

            """
            fig = go.Figure(data = [go.Table(header = dict(values = df.columns,align = "center",font_size = 10),cells = dict(values = df.values,align = "center",font_size = 10))])
            fig.show()
            """

            """
            重い&色の変更がうまくいかないのでボツ
            df = self.ccf_table(file,elements)
            cm = sns.light_palette("green", as_cmap=True)
            df_ccf = df.corr().style.background_gradient(cmap = cm).render()
            outname = file.split('.')[0]+'_ccc.html'
            testname = file.split('.')[0]+"_"+"test.html"
            df.to_html(testname)
            with open(outname,"w") as file:
                file.write(df_ccf)
            """
