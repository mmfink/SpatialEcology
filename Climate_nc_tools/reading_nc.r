## These are snippets (separated by '-----------') that have been adapted
## from various sources that I failed to keep track of at the time.
## Therefore I (Michelle Fink) do not claim any authorship or license to
## this particular code.

library(ncdf4)
inpath <- "Path/To/file.nc"

## Quick and dirty graphing version:
## Plots the entire dataset, which can be very large!
##-----------
nc <- nc_open(inpath)
# look at metadata
nc
# what to label our graphs
varname <- "testing"
vaxis <- "ppt (mm)"
v1 <- nc$var[[1]]  #This assumes first variable is one of interest (which to use will be in metadata)
v1data <- ncvar_get(nc, v1)
hist(v1data, col = "gray", main = varname, xlab = vaxis)
qqnorm(v1data, main = varname)
qqline(v1data)
nc_close(nc)
##-----------

## Subsetting version:
## Assumes full timeperiod of interest (historic and future) in same file.
##-----------
nc <- nc_open(inpath)
nc  #pay attention to order of dimensions, and repeat them exactly in 'start' and 'count' below
v1 <- nc$var[[1]]
lonsize <- v1$varsize[1] # X dimension
latsize <- v1$varsize[2] # Y dimension
#endcount <- v1$varsize[3] # use instead of endh or endf if you want to go all the way to end
starth <- 1 #starting time index for historic data
endh <- 30  #count of historic data slice (i.e., years)
startf <- 70 #starting time index for future data
endf <- 30  #count of future data slice (i.e., years)
datahistoric <- ncvar_get(nc, v1, start = c(1, 1, starth), count = c(lonsize, latsize, endh))
datafuture <- ncvar_get(nc, v1, start = c(1, 1, startf), count = c(lonsize, latsize, endf))
varname <- "testing"
vaxis <- "tasmin"
hist(datahistoric, col = "gray", main = varname, xlab = vaxis)
hist(datafuture, col = "gray", main = varname, xlab = vaxis)
nc_close(nc)
##-----------
## Single timeslice:
library(raster)
nc <- nc_open(inpath)
nc #pay attention to order of dimensions, and repeat them exactly in 'start' and 'count' below
v1 <- nc$var[[1]]
lonsize <- v1$varsize[1]
latsize <- v1$varsize[2]
timeidx <- 42 # the index of the time (year) you want
dataslice <- ncvar_get(nc, v1, start = c(1, 1, timeidx), count = c(lonsize, latsize, 1))
ras <- raster(dataslice)
plot(ras) #odds are, this will not be facing north = up
#try transposing
rast <- t(ras)
plot(rast)
#or rotating
rasr <- rotate(ras)
plot(rasr)
#or flipping
rasf <- flip(ras, 'y')
plot(rasf)
nc_close(nc)