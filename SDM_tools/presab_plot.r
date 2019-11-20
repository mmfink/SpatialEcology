#############################################################################
# Create violin plots shaded by quartile to compare prediction values of
# presence and absence points used in a randomForest (or similar) inductive
# model.
# ** Requires violinplot.r **
#
# Michelle M. Fink, michelle.fink@colostate.edu
# Colorado Natural Heritage Program, Colorado State University
# Code Last Modified 11/20/2019.
#
# Adapted from:
# https://www.shinyapps.org/apps/RGraphCompendium/index.php
#         #reproducibility-project-the-layered-violin-graph
# Which was created by [Fred Hasselman](https://osf.io/ujgs6/)
#
# Code licensed under the GNU General Public License version 3.
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/
#############################################################################

setwd("C:/Path/To/Project")
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
  expand_limits(y = c(0,0.8)) + scale_y_continuous(expand = c(0,0)) +
  theme(legend.position=c(0.1,0.8), legend.text=element_text(size=10),
  legend.title=element_text(size=14), axis.text.x=element_text(size=14),
  axis.text.y=element_text(size=14), axis.title.y=element_text(size=14, vjust=2.6),
  title=element_text(size=14))

g.pv1
