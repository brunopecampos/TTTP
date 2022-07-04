#!/bin/Rscript
png('cpu-client2.png', width=500, height=500)
a <- read.csv('./cpu-client1.csv')
plot(a)
dev.off()
