from Destiny.DataSets.german_dataset import load_german_dataset
from Destiny.Embedded_Thresholding import Embedded_Thresholding
from Destiny.Evaluateur_Precision import Evaluateur_Precision
from Destiny.RankingFunctions.Final.Distances_Measures import Distances_Measures

from Destiny.RankingFunctions.Final.Information_Measure import Information_Measure
from Destiny.RankingFunctions.Final.MesureDeConsistance import MesureDeConsistance
from Destiny.RankingFunctions.Final.MesureDeDependance import MesureDeDependance
from Destiny.RankingFunctions.Final.PrecisionClassification import PrecisionClassification
from sklearn.svm import SVC
from Destiny.Tresholding import Tresholding
import numpy as np



class Destiny:
    #C'est simple pour demander un ranking donné tu précise la lettre suivi de l'indice donc D0 pour Chi, I1 pour le gain d'information etc...
    #Sinon on peut indexer en utilisant H et un chiffre qui commence a 0
    mesures_distance = ["FScore","ReliefF","FCS"]
    mesures_information = [ 'GainInformation' , "GainRatio" , "SymetricalIncertitude" , "MutualInformation" , "UH" , "US" , "DML"]
    mesures_classification = ["RF",  "AdaBoost"]
    mesures_consistance = ['FCC']
    mesures_dependance = ["RST"]
    maxH = 13
    alpha=0.05
    #mesures_classification = ["BN","RF","LSVM","RBFSVM","GaussianProcess","AdaBoost","QDA","KNN","DTC","MLP"]

    def __init__(self):
        self.__data,self.__target = None,None
        self.__mesures = {}
        self.__max_iterations=2
        self.__Threshold = 0
        self.__nom_mesures = {}
        self.subsetgenerated = None
        self.__matrices_redondaces, self.__matrices_importances = {} , {}
        self.__mesures["D"],self.__nom_mesures["D"] = Distances_Measures(),Destiny.mesures_distance
        self.__mesures["I"],self.__nom_mesures["I"] = Information_Measure(),Destiny.mesures_information
        self.__mesures["C"],self.__nom_mesures["C"] = PrecisionClassification(),Destiny.mesures_classification
        self.__mesures["Co"],self.__nom_mesures["Co"] = MesureDeConsistance(),Destiny.mesures_consistance
        self.__mesures["De"],self.__nom_mesures["De"] = MesureDeDependance(),Destiny.mesures_dependance
        self.inter=set()
        self.union=set()



    def __copy__(self):
        D = Destiny()
        D.__mesures["D"] = self.__mesures["D"]
        D.__mesures["I"] = self.__mesures["I"]
        D.__mesures["C"] = self.__mesures["C"]
        D.__mesures["Co"] = self.__mesures["Co"]
        D.__mesures["De"] = self.__mesures["De"]

    #L est une liste de types de mesures par exemple ['C' ,'Ce', 'De']
    def GestionSubsets(self,L,Borne = None):
        for i in L:
            self.__mesures[i].CreateSubsets(Borne)

    def getDataset(self):
        return self.__data,self.__target

    def Projection(self,subset):
        #Ancienne projection :
        #D = self.__mesures["D"].ranking_function_constructor("FCS")(subset)
        #I = self.__mesures["I"].ranking_function_constructor("US")(subset)

        #Nouvelle Projection :
        D = self.MinimumRMaxS (subset,"Distance")
        I = self.MinimumRMaxS (subset , "Information")
        DE = self.__mesures["De"].dependence(subset)
        Co = self.__mesures["Co"].fcc(subset)
        return (D,I,DE,Co)

    def getMegaHeuristique(self,ids,nb):
        D = {}
        Lmotsclefs = []
        for id in ids:
            cpt = 0
            motclef = None
            tp = None
            for i in self.__nom_mesures.keys():
                cptlocal = 0
                for j in self.__nom_mesures[i]:
                    cptlocal = cptlocal + 1
                    if(id == str(i)+str(cptlocal) or id == "H"+str(cpt)):
                        motclef = j
                        tp = i
                        break
                    cpt = cpt + 1
                if(motclef != None):
                    break

            L = []
            L.append(motclef)
            Lmotsclefs.append(motclef)
            D.update(self.__mesures[tp].rank_with(L,n=nb))
        DDD = {}
        for i in D[nb]:
            if i in Lmotsclefs:
                DDD[i] = D[nb][i]
        return DDD


    def MinimumRMaxS(self,subset,mc):
        masque = self.__data.shape[1]*[0]
        for i in subset:
            masque[i] = 1
        masque = np.array(masque)
        return masque.transpose().dot(self.__matrices_redondaces[mc]).dot(masque)-masque.dot(self.__matrices_importances[mc])


    def setMatricesImportanceRedondance(self,data,target):
        self.__mesures["I"].fit (data , target)
        data = data.transpose ()
        d = list (data)
        d.append (target)
        d = np.array (d)
        #data = data.transpose ()
        c = np.corrcoef (d)
        c = c.transpose()
        self.__matrices_importances["Distance"] = c[-1]
        self.__matrices_redondaces["Distance"] = c[0:-1]
        self.__matrices_redondaces["Distance"] = self.__matrices_redondaces["Distance"].transpose()[:-1]
        self.__matrices_importances["Distance"] = self.__matrices_importances["Distance"].transpose ()[:-1]
        f = self.__mesures["I"]
        m = np.ones((len(data),len(data)))
        imp = np.ones((len(data)))
        for i in range(0,len(data)):
            C1 = f.getEntropy([i])
            for j in range(0,len(data)):
                C2 = f.getEntropy([j])
                C3 = f.getEntropySachant([j],[i])
                m[i][j] = C1 + C2 - C3
            C2 = f.getEntropy([-1])
            C3 = f.getEntropySachant([i],[-1])
            imp[i] = C1 + C2 - C3
        self.__matrices_redondaces["Information"] = m
        self.__matrices_importances["Information"] = imp
        unit = np.ones(self.__matrices_importances["Distance"].shape[0])
        for i in self.__matrices_importances:
            self.__matrices_importances[i] = unit - self.__matrices_importances[i]/self.__matrices_importances[i].sum()
        return self.__matrices_redondaces,self.__matrices_importances


    def ThresholdMeasures(self,seuil):
        cpt = 0
        for i in self.__mesures.keys():
            for j in range(0,len(self.__nom_mesures[i])):
                self.__mesures_anterieure.update(self.getMegaHeuristique(["H"+str(cpt)],1))
                cpt = cpt + 1
        self.attributs_qualitatifs(0.5)
        self.__Threshold = seuil
        for i in self.__mesures.keys():
            self.__mesures[i].setThresholdsAutomatiquement(self.__Threshold)


    def attributs_qualitatifs(self,seuil):
        nb = int(seuil * len(self.__data[0]))
        print("nb attributs = ",len(self.__data[0]))
        dict_listes = {}
        cpt = 0
        for i in self.__mesures_anterieure:
            L = []
            print("Je positionne le curseur sur ",i)
            for j in range(0,nb):
                L.append(self.__mesures_anterieure[i][j][0][0])
                print(self.__mesures_anterieure[i][j])
            print("L = ",L, " i= ",i)
            dict_listes[cpt] = L
            cpt = cpt + 1
        print(dict_listes)



    def fit(self,X,Y):
        self.__data ,self.__target = X, Y
        print("ici", X.shape,Y.shape )
        m1 , m2 = self.setMatricesImportanceRedondance(X,Y)
        for i in self.__mesures.keys():
            self.__mesures[i].fit (X , Y)
            print(i," fini")
            if(self.subsetgenerated == None):
                self.__mesures[i].setMatrix(m1,m2)
                self.subsetgenerated = self.__mesures[i].CreateSubsets(borne = 1000)
            else:
                self.__mesures[i].setSubsets(self.subsetgenerated)
        #T = Tresholding ()
        #T.fit (X , Y)
        #self.ThresholdMeasures(T.getTreshold(X,Y))
        self.activer_treshold()

    def getMatriceImportanceRedondance(self):
        return self.__matrices_redondaces,self.__matrices_importances

    def test(self):
        D = {}
        for i in self.__mesures.keys():
            print("Utilisation de ", i)
            self.__mesures[i].rank_with(n=1)
            self.__mesures[i].rank_with(n=2)
            print(self.__mesures[i].rank_with(n=3))

    def tresholder(self,t):
        self.nouvmesures=self.__mesures
        for i in self.__mesures.keys():
            self.nouvmesures[i].setThresholdsAutomatiquement(t)

    def union_intersection(self):
        for i in range(self.maxH):
            gj = self.getMegaHeuristique(["H" + str(i + 1)], 1)
            hierlist2 = gj[list(gj.keys())[0]]
            elus = set()
            #print('hierlist:',hierlist2)
            #print("___")
            for h in hierlist2:
                if (h[1] >= 0):
                    elus = elus.union(set(h[0]))
           # print("les elus",elus)
            if (len(self.inter) > 0):
                self.inter = self.inter.intersection(elus)
            else:
                self.inter = elus
            self.union = self.union.union(elus)

    def evaluer(self):
        E = Evaluateur_Precision(self.__data, self.__target)
        #print("target et data shape",self.__data.shape,self.__target.shape)
        E.train(SVC( ))
        if(len(self.inter)>0):
            return (self.reguler_par_complexote(E.Evaluer(list(self.inter)),len(self.inter))+self.reguler_par_complexote(E.Evaluer(list(self.union)),len(self.union)))/2
        else:
            return 0
    def criteron(self,t):
        self.tresholder(t)
        self.union_intersection()
        return self.evaluer()
    def activer_treshold(self):
        t=0.5
        alpha=0.4
        for i in range(self.__max_iterations):
            p1=t+alpha
            p2=t-alpha
            if(self.criteron((t+p1)/2)>self.criteron((t+p1)/2)):
                t=(p1+t)/2
            else:t=(p2+t)/2
            alpha=alpha/2
            print("----le treshold est:",t)
        self.tresholder(t)



    def reguler_par_complexote(self,val,taille):
        return (val *(1-self.alpha)/(taille)*self.alpha)