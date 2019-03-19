from itertools import combinations

import numpy as np
from sklearn.datasets import make_classification

from Destiny.RankingFunctions.Final.Mesure import Mesure


class MesureDeConsistance(Mesure):
    seuil_max = 4

    def __init__(self):
        super().__init__()
        self.__data = None
        self._liste_mesures = ['FCC']
        self.__target = None
        self.feature_score= {}

    def getscore(self):
        return self.feature_score

    def fit(self,data,target):
        super().fit(data,target)
        self.__data = data
        self.__target = target


    def ranking_function_constructor(self,motclef):
        return self.fcc

    def rank_with(self,lmotclef = None,n = 1):
        if not n in self._calculated_measures.keys():
            self._calculated_measures[n] = {}
        if(lmotclef == None):
            lmotclef = self._liste_mesures
        for mc in lmotclef:
            if not (mc in self._calculated_measures[n].keys()):
                self._calculated_measures[n]["FCC"] = self.rank(n)
        return self._calculated_measures

    def rank(self,n):
        if (n > MesureDeConsistance.seuil_max):
            return None
        if not (n in self.feature_score):
            L = list(range(0, len(self.__data[0]) - 1))
            for i in combinations(L, n):
                KK = []
                for j in i:
                    KK.append(j)
                self.fcc(KK)
            self.feature_score[n] = sorted(self.feature_score[n].items(), key=lambda x: x[1], reverse=True)
        return self.feature_score[n]

    def fcc(self,x):
        if not (len (x) in self.feature_score.keys()):
            self.feature_score[len(x)] = {}
        if not tuple(x) in self.feature_score[len(x)].keys():
            a=[]
            dat=np.transpose(self.__data)
            for i in range(len(x)):
                a.append(dat[x][i])
            patterns=[]
            b=np.transpose(a)
            for j in b:
                patterns.append(tuple(j))
            setpatterns=set(patterns)
            s=0
            for pat in setpatterns:
                npp=0
                c1=0
                c2=0
                for val in range(len(patterns)):
                    if(pat==patterns[val]):
                        npp=npp+1
                        if(self.__target[val]==1):
                            c1=c1+1
                        else: c2=c2+1
                c1=max(c1,c2)
                s=s+npp-c1
            if(1-float(s)/len(patterns) >= self._liste_thresholds[0]):
                self.feature_score[len(x)][tuple(x)] = 1-float(s)/len(patterns)
                print(1-float(s)/len(patterns))
            else:
                self.feature_score[len (x)][tuple (x)] = -1
        return self.feature_score[len(x)][tuple(x)]

from Destiny.DataSets import german_dataset
data, target = make_classification(n_samples=300, n_features=25, n_informative=5,
                           n_redundant=3, n_repeated=2, n_classes=2,
                           n_clusters_per_class=1, random_state=0)
data,target = german_dataset.load_german_dataset()
M = MesureDeConsistance()
M.fit(data,target)
M.setThresholdsAutomatiquement()
print(M.rank_with(n=1))
