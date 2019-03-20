import re
import random
import itertools

from Destiny.Clustering_Incarnations import Clustering_Incarnations
from Destiny.Evaluateur_Precision import Evaluateur_Precision
from Nature2 import Genome
from Nature2 import Fabriquant as fb
import time
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

class Nature:
    Pstop=0.4
    maxA = 3
    maxH = 5
    maxP = 500
    maxS = 10
    strat = []
    population = []
    actualalpha = None
    DM=None
    Tol=3
    population_clusterised = {}
    alphas_locaux = []
    alpha_global = []
    modele = DecisionTreeClassifier()
    actual_precision=0

    @classmethod
    def csm(cls,G0I,G0A,Strat):
        st=""
        exp="\d[H\d]+/"
        gi=re.findall(exp,G0I)
        ga=re.findall(exp,G0A)
        for s,s2 in itertools.zip_longest(gi,ga):
            if(s!=None):
                p = random.random()
                if(p<Strat[0]):
                    st=st+"S"
                else:
                    if(p<Strat[1]):
                        pp=random.random()
                        if(pp<Strat[2]):
                            st=st+"MI"
                        else:
                            st=st+"MO"
                    else:
                        if(s2 != None):
                            if(s[0]==s2[0]):
                                pp = random.random()
                                if (pp < Strat[3]):
                                    st = st + "CI"
                                else:
                                    st = st + "CO"
                            else:
                                st=st+"CO"
                        else:
                            st = st + "MO"
        return st

    @classmethod
    def Grand(cls, G=None):
        st = ""
        if (G is None):
            n = random.randint(1,cls.maxA)
            st = st + str(n)
        else:
            st = st + G[0]
        k = random.randint(1, cls.maxH)
        st = st + "H" + str(k)
        while(random.random()<cls.Pstop):
            k = random.randint(1, cls.maxH)
            st = st + "H" + str(k)
        return st

    @classmethod
    def MergeH(cls,gi, ga):
        return gi + ga[1:]

    @classmethod
    def PseudoTransoducteur(cls, GOI, GOA, CSM):
        st = ""
        exp = "(\d[H\d]+)/"
        exp2 = "S|CI|CO|MI|MO"

        gi = re.findall(exp, GOI)
        ga = re.findall(exp, GOA)
        csm = re.findall(exp2, CSM)
        modif = itertools.zip_longest(gi, ga, csm)
        for i, a, c in modif:
            if(random.random()<0.72):
                if (gi != None):
                    if (c == "S"):
                        st = st + i + "/"
                    if (c == "MI"):
                        st = st + cls.Grand(i) + "/"
                    if (c == "MO"):
                        st = st + cls.Grand() + "/"
                    if (c == "CI"):
                        st = st + cls.MergeH(i, a) + "/"
                    if (c == "CO"):
                        st = st + a + "/"
        return st

    @classmethod
    def validate(cls, G):
        if (len(G.identity) == 0):
            ppp = random.randint(0, 1)
            if (ppp == 1):
                G.identity = cls.PseudoTransoducteur("1H1/2H3/1H2/2H5/1H6/2H2", "", "MOMOMOMOMOMOMOMO")
            else:
                G.identity = cls.PseudoTransoducteur("1H2H3/2H3/1H4/2H1H4/2H1", "", "MOMOMOMOMOMOMO")
        fab = fb.Fabriquant(G, cls.DM)
        VG = fab.genome
        return VG

    @classmethod
    def monoevolv(cls, VGOI, VGOA, strat):
        st = cls.csm(VGOI.identity, VGOA.identity, strat)
        GN = Genome.Genome()
        GN.identity = cls.PseudoTransoducteur(VGOI.identity, VGOA.identity, st)
        VGN = cls.validate(GN)
        return VGN

    @classmethod
    def eludeAlpha(cls):
        P = []
        for i in cls.population:
            P.append(i.resultat)
        CI = Clustering_Incarnations()
        CI.setDestiny(Nature.DM)
        CI.ajouter_population(P)
        CI.projeter()
        CI.clusteriser()
        Nature.population_clusterised = CI.clusters
        Nature.alphas_locaux = CI.alphas_locaux
        E = Evaluateur_Precision(Nature.DM.getDataset()[0],Nature.DM.getDataset()[1])
        E.train(Nature.modele)
        alpha_global = None
        max=0
        for i in Nature.alphas_locaux:
            c=E.Evaluer(i)
            if c > max:
                max = c
                alpha_global = i
        Nature.alpha_global = alpha_global
        lesalpha=cls.alphas_locaux
        cls.alphas_locaux=[]
        for k in lesalpha:
            kk=0
            while(kk<len(cls.population)):
                if(cls.population[kk].resultat == list(k)):
                    cls.alphas_locaux.append(cls.population[kk])
                    kk=len(cls.population)+1
                kk=kk+1
        ll=0
        if(cls.actual_precision<max):
            cls.actual_precision=max
            while(ll<len(cls.population)):
                if (cls.population[ll].resultat == list(cls.alpha_global)):
                    cls.actualalpha=cls.population[ll]
                    ll=len(cls.population)+1
                ll=ll+1





    @classmethod
    def init(cls,D):
        cls.DM=D
        cls.strat=[[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],
               [0.2, 0.6, 0.5, 0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8],[0.2,0.6,0.5,0.8]]
        cls.population=[]
        VNG=Genome.Genome()
        for i in range(cls.maxP):
            cls.population.append(cls.monoevolv(VNG,VNG,cls.strat[random.randint(0,cls.maxS-1)]))
        cls.eludeAlpha()

    @classmethod
    def evolve(cls):
        for i in range(cls.maxP):
            cls.population[i]=cls.monoevolv(cls.population[i],cls.alphas_locaux[cls.getcluster(cls.population[i])],cls.strat[random.randint(0, cls.maxS - 1)])
            cls.population[i] = cls.monoevolv(cls.population[i], cls.actualalpha, cls.strat[random.randint(0, cls.maxS - 1)])
        cls.eludeAlpha()

    @classmethod
    def getcluster(cls,G):
        cpt=0
        trouve=False
        while(cpt<len(cls.population_clusterised)):
            cpt2=0
            while(cpt2<len(cls.population_clusterised[cpt])):
                if(G.resultat == list(cls.population_clusterised[cpt][cpt2])):
                    return cpt
                    cpt2=len(cls.population_clusterised[cpt])+1
                    trouve=True
                cpt2=cpt2+1
            if(trouve):
                cpt = len(cls.population_clusterised) + 1
            cpt=cpt+1


        return -1




