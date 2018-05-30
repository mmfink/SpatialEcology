# Michelle M. Fink, May, 2018. Adapted from:
#https://www.shinyapps.org/apps/RGraphCompendium/index.php#reproducibility-project-the-layered-violin-graph

# Theme function -----------------------------------
gg.theme <- function(type=c("clean","noax")[1],useArial = F){
  # Changed 05/30/2018 [MMF] -
  # Original had code to force fonts on Mac
  # I don't think my tweaks quite work (on Windows) yet, but it doesn't break anything.
  require(ggplot2)
  if(useArial){
    bf_font="Sans"
  } else {bf_font="Serif"}
  
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
fill_viol<-function(gr.df,gr,qtile,probs){
  # SETUP VIOLIN QUANTILE PLOTS -----------------------------------
  # This is adapted from: http://stackoverflow.com/questions/22278951/combining-violin-plot-with-box-plot
  # Changed 05/30/2018 [MMF] - 
  # - filter out NA values that are generated when populations are not the same size
  ifelse(is.null(qtile),{
    cuts <- cut(gr.df$y, breaks = quantile(gr.df$y, probs, na.rm=T, type=3, include.lowest = T, right = T), na.rm=T)},{
      cuts <- cut(gr.df$y, breaks = qtile, na.rm=T)
    }
  )
  quants <- mutate(gr.df,
                   x.l=x-violinwidth/2,
                   x.r=x+violinwidth/2,
                   cuts=cuts)
  
  quants <- filter(quants, !is.na(cuts))
  
  plotquants <- data.frame(x=c(quants$x.l,rev(quants$x.r)),
                           y=c(quants$y,rev(quants$y)),
                           id=c(quants$cuts,rev(quants$cuts)))
  
  plotquants <- filter(plotquants, !is.na(id))
  
  #cut by quantile to create polygon id
  geom <- geom_polygon(aes(x=x,y=y,fill=factor(id)),data=plotquants,alpha=1,na.rm = T)
  
  return(list(quants=quants,plotquants=plotquants,geom=geom))
}

vioQtile <- function(gg=NULL,qtiles=NULL,probs=seq(0,1,.25),labels=paste(probs[-1]*100),withData=FALSE){
  require(ggplot2)
  # SETUP VIOLIN QUANTILE PLOTS -----------------------------------
  # This is adapted from: http://stackoverflow.com/questions/22278951/combining-violin-plot-with-box-plot
  #
  # Changed:
  # - Deal with 'empty' quantile groups
  # - Deal with original data
  # - More input, more output
  # Changed 05/30/2018 [MMF] - minor aesthetic tweaks
  g.df <- ggplot_build(gg)$data[[1]]    # use ggbuild to get the outline co-ords
  
  ifelse(is.null(qtiles),{
    gg <- gg + lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x, ],x,NULL,probs)$geom)},{
      gg <- gg + lapply(unique(g.df$group), function(x) fill_viol(g.df[g.df$group==x, ],x,qtiles[x, ],probs)$geom)}
  )
  
  gg <- gg + geom_hline(aes(yintercept=0)) +
    scale_fill_grey(name="Quantile\n",labels=labels,guide=guide_legend(reverse=T,label.position="right")) +
    stat_summary(fun.y=median, geom="point", size=4, color="grey50", shape=22, fill="white")
  
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