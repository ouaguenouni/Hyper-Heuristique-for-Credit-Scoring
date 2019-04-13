import operator
from Nature2 import Nature as nat
from Nature2 import Genome as gn
import time
import re
import random
from Destiny import Destin as dest
class Fabriquant:
    def __init__(self,GN,DM):

        self.dm=DM
        self.listbuffer=[]
        exp = "(\d[H\d]+)/"
        self.attlen= GN.identity[0]
        self.recette=re.findall(exp,GN.identity)
        self.genome=gn.Genome()
        self.incarnation=[]
        self.listbuffer=[]
        exp2="H\d+"
        cpt=0
        for stg in self.recette:
            self.attlen=stg[0]
            gene = re.findall(exp2, stg)
            condidats=set()
            for mesure in gene:
                dictt=DM.getMegaHeuristique([mesure],int(self.attlen))
                hierlist = dictt[list(dictt.keys())[0]]
                latol=0
                cpt1=0
                while(cpt1<len(hierlist) and latol!=nat.Nature.Tol):
                    trock=set(self.listbuffer)
                    if(intersect(trock,set(list(hierlist[cpt1][0])))==[]):
                        a=tuple(hierlist[cpt1][0])
                        condidats.add(a)
                        latol=latol+1
                    cpt1=cpt1+1
            tournoit=[]
            for joueur in list(condidats):
                score=0
                adversaires=list(condidats)
                adversaires.remove(joueur)
                for adversaire in adversaires:
                    for j in range(nat.Nature.maxH):
                        dicttt = DM.getMegaHeuristique([mesure], int(self.attlen))
                        hierlistx = dicttt[list(dicttt.keys())[0]]
                        kk=0
                        while(kk<len(hierlistx)):
                            if(hierlistx[kk][0]==joueur):
                                kk=len(hierlistx)+1
                                score=score+1
                            else:
                                if(hierlistx[kk][0]==adversaire):
                                    kk=len(hierlistx)+1
                                    score=score-1
                            kk=kk+1
                tournoit.append((joueur,score))
            tournoit=sorted(tournoit,key=operator.itemgetter(1),reverse=True)
            if(tournoit!=[]):
                self.incarnation.append((stg,tournoit[0][0],1))
                for i in tournoit[0][0]:
                    self.listbuffer.append(i)
        #        print(self.listbuffer)

        self.bourrage2()
       # print(self.listbuffer)
        ch=""
        for m in self.recette:
            ch=ch+m+"/"
        self.genome.identity=ch
        self.genome.incarnation=self.incarnation
        self.genome.isvalide=1
        self.genome.resultat=sorted(self.listbuffer)



    def getgenome(self):
        return self.genome



    def bourrage2(self):
        Vincanration = []
        bourlist = []
        k = 0
        while (k < len(self.incarnation)):
            if (int(self.incarnation[k][2]) > 0):
                lalist=[]
                for l in self.incarnation[k][1]:
                    lalist.append(l)
                bourlist.extend(lalist)
                Vincanration.append(self.incarnation[k])
            k = k + 1
        self.incarnation=Vincanration
        self.listbuffer=bourlist
        #print("ici",self.listbuffer)
        k = random.randint(len(self.dm.inter),len(self.dm.union))
        for j in range(k):
            fait=0
            while(fait==0):
                p=random.randint(1,nat.Nature.maxH)
                gjj = self.dm.getMegaHeuristique(["H" + str(p)], 1)
                hierlist3 = gjj[list(gjj.keys())[0]]
                hh=0
                while(hh<len(hierlist3)):
                    if(intersect(self.listbuffer,list(hierlist3[hh][0]))==[] and hierlist3[hh][1]>0):
                        self.listbuffer = self.listbuffer + list(hierlist3[hh][0])
                        gene = "1H" + str(p)
                        self.recette.append(gene)
                        self.incarnation.append((gene, hierlist3[hh][0], hierlist3[hh][1]))
                        hh = len(hierlist3) + 1
                        fait=1
                    else:hh=hh+1



def intersect(a, b):
    return list(set(a) & set(b))
