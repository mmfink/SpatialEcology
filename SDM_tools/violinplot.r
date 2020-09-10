#############################################################################
# Functions used in presab_plot.r
#
# Michelle M. Fink, michelle.fink@colostate.edu
# Colorado Natural Heritage Program, Colorado State University
# Code Last Modified 09/10/2020.
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

# Theme function -----------------------------------
gg.theme <- function(type=c("clean","noax")[1],useArial = F){
  # Last changed 11/20/2019 [MMF] -
  # Removed code to force fonts on Mac and tweaked Windows font handling
  require(ggplot2)
  if(useArial){
    bf_font=windowsFonts("sans")
  } else {bf_font=windowsFonts("serif")}

  switch(type,
         clean = theme_bw(base_size = 16, base_family=bf_font) +
           theme(axis.text.x     = element_text(size = 14),
                 axis.title.y    = element_text(vjust = +1.5),
                 panel.grid.major  = element_blank(),
                 panel.grid.minor  = element_blank(),
                 legend.background = element_blank(),
                 legend.key = element_blank(),
                 panel.border = element_blank(),
                 panel.background = element_blank(),
                 axis.line  = element_line(colour = "black")),

         noax = theme(line = element_blank(),
                      text  = element_blank(),
                      title = element_blank(),
                      plot.background = element_blank(),
                      panel.border = element_blank(),
                      panel.background = element_blank())
  )
}

#function to create geom_polygon calls
fill_viol<-function(gr.df,gr,qtile=NULL,probs){
  # SETUP VIOLIN QUANTILE PLOTS -----------------------------------
  # This is adapted from: http://stackoverflow.com/questions/22278951/combining-violin-plot-with-box-plot
  # Changed 05/30/2018 [MMF] -
  # - filter out NA values that are generated when populations are not the same size
  # 11/20/2019 [MMF] - improve quantile handling
  ifelse(is.null(qtile),{
    cuts <- cut(gr.df$y, breaks = quantile(gr.df$y, probs, na.rm=T, type=3, include.lowest = T, right = T), na.rm=T)},{
      cuts <- cut(gr.df$y, breaks = qtile, na.rm=T)
    }
  )
  quants <- dplyr::mutate(gr.df,
                   x.l=x-violinwidth/2,
                   x.r=x+violinwidth/2,
                   cuts=cuts)

  quants <- dplyr::filter(quants, !is.na(cuts))

  plotquants <- data.frame(x=c(quants$x.l,rev(quants$x.r)),
                           y=c(quants$y,rev(quants$y)),
                           id=c(quants$cuts,rev(quants$cuts)))

  #cut by quantile to create polygon id
  geom <- geom_polygon(aes(x=x,y=y,fill=factor(id)),data=plotquants,na.rm=T)

  return(list(quants=quants,plotquants=plotquants,geom=geom))
}

vioQtile <- function(gg=NULL,qtiles=NULL,probs=seq(0,1,.25),labels=paste(probs[-1]*100),withData=F,usecol=F){
  require(ggplot2)
  # SETUP VIOLIN QUANTILE PLOTS -----------------------------------
  # This is adapted from: http://stackoverflow.com/questions/22278951/combining-violin-plot-with-box-plot
  #
  # Changed:
  # - Deal with 'empty' quantile groups
  # - Deal with original data
  # - More input, more output
  # Changed 05/30/2018 [MMF] - minor aesthetic tweaks
  # 11/20/2019 [MMF] - improve quantile handling
  g.df <- ggplot_build(gg)$data[[1]]    # use ggbuild to get the outline co-ords

  ifelse(is.null(qtiles),{
    gg <- gg + lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x, ],x,NULL,probs)$geom)},{
      gg <- gg + lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x, ],x,qtiles[x, ],probs)$geom)}
  )

  ifelse(usecol,{
    gg <- gg +
      scale_fill_hue(name="Quantile",labels=labels,guide=guide_legend(reverse=T,label.position="right"),h=c(250,300)) +
      stat_summary(fun.y=mean, geom="point", size=5, color="grey50", shape=22, fill="red")},{
        gg <- gg +
          scale_fill_grey(name="Quantile",labels=labels,guide=guide_legend(reverse=T,label.position="right")) +
          stat_summary(fun.y=mean, geom="point", size=3.5, color="grey50", shape=22, fill="white")
      })

  if(withData){
    ifelse(is.null(qtiles),{
      ggData <- lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x,],x,NULL,probs))},{
        ggData <- lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x,],x,qtiles[x,],probs))
      }
    )
    return(list(ggGraph=gg,ggData=ggData))
  } else {
    return(gg)
  }
}

# MULTIPLOT FUNCTION ------------------------------------------------------------------------------------------------------------------
#
# [copied from http://www.cookbook-r.com/Graphs/Multiple_graphs_on_one_page_(ggplot2)/ ]
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multi.PLOT <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  require(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }

  if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))

      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}