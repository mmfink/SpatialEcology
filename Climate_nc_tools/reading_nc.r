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
v1 <- nc$var[[1]]
lonsize <- v1$varsize[1] # X dimension
latsize <- v1$varsize[2] # Y dimension
endcount <- v1$varsize[3]
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