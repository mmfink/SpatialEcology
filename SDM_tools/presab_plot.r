# Michelle M. Fink, May, 2018. Adapted from:
#https://www.shinyapps.org/apps/RGraphCompendium/index.php#reproducibility-project-the-layered-violin-graph
# Requires violinplot.r
setwd("D:/GIS/Projects/YourProject")
library(readr)
library(plyr)
library(dplyr)
library(ggplot2)

Model_Results <- read_csv("Model_Results.csv") #input data to graph
# Change all instances of 'Pres_Abs' and SPIDIL_MeanModel' to your x and y variables, respectively
attach(Model_Results)
source('violinplot.r')
mytheme <- gg.theme("clean", useArial=T)
probs <- seq(0,1,.25)
qtiles <- ldply(unique(Pres_Abs),function(gr) quantile(SPIDIL_MeanModel[Pres_Abs==gr],probs,na.rm=T,type=3,include.lowest=T))

g.pv <- ggplot(Model_Results,aes(x=Pres_Abs,y=SPIDIL_MeanModel)) + 
  geom_violin(aes(group=Pres_Abs),scale="width",color="grey80",fill="grey80",trim=T, adjust=0.8)

g.pv0 <- vioQtile(g.pv,qtiles=qtiles,probs,withData=T)

g.pv1 <- g.pv0$ggGraph + ggtitle("Probability value at each [A]bsence and [P]resence point") + xlab("") +
  ylab("random forest output") + mytheme +
  theme(legend.position=c(0.1,0.8), legend.text=element_text(size=10),
  legend.title=element_text(size=14), axis.text.x=element_text(size=14),
  axis.text.y=element_text(size=14), axis.title.y=element_text(size=14, vjust=2.6),
  title=element_text(size=14))

g.pv1
