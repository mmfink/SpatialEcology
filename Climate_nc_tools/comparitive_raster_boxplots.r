library("raster")
setwd("Path/To/Geotiffs")
##The following is just a template. Obviously, change to suit the data.
eddi_hw <- raster("EDDI_2Freq_canesm2_rcp85.tif")
eddi_ff <- raster("EDDI_2Freq_cesm1_bgc_rcp85.tif")
eddi_ww <- raster("EDDI_2Freq_gfdl_esm2m_rcp45.tif")
eddi_hd <- raster("EDDI_2Freq_hadgem2_ao_rcp85.tif")

eddistack <- stack(eddi_hd, eddi_hw, eddi_ff, eddi_ww)
names(eddistack) <- c('HotDry', 'HotWet', 'FeastFamine', 'WarmWet')
boxplot(eddistack, main = 'Frequency of Extreme EDDI values over 2020-2050', ylim = c(0, 18))
