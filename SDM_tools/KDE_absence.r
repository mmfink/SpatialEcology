library(spatstat)
library(ks)
library(raster)
library(rgdal)
library(sp)

setwd("D:/GIS/Projects/WYNDD")
dat<-read.csv("input_training_pts.csv") # All input points with obs quality rank as field 'responseCount' (absence pts = 0)
#shapefile of absence points that we are selecting from:
abs_shp<-readOGR("D:/GIS/Projects/WYNDD/Final_inputs/Absence_pts_train_1km.shp", layer="Absence_pts_train_1km")
outname<-"prob_selected_abspts.csv"
N<-1000 #number of points to return

#Get XY coordinates of both inputs
xy_in<-data.frame(cbind(as.numeric(as.character(dat$X)), as.numeric(as.character(dat$Y))))
xy_out<-coordinates(abs_shp)

#Create Kernel Density surface using 'responseCount' as weight
Hpi = Hpi(xy_in, binned = TRUE, bgridsize = rep(500, times = 2))
a<-kde(xy_in, H = Hpi, eval.points = xy_out, w = dat$responseCount)

#Get the probability of being selected for each absence point
probpts<-data.frame(cbind(a$eval.points, a$estimate))
probpts$P<-(probpts$V3/sum(probpts$V3))

#Select our desired number of absence points based on their probability
d = sample(as.numeric(row.names(probpts)), size = N, replace = FALSE, prob = probpts$P)
out<-probpts[d, 1:2]

#Export CSV with point ID, X, Y
write.csv(out, file = outname)
