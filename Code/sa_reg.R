sa <- read.csv("./Data/SA_FA_Grants.csv", sep=",", strip.white = TRUE, na.strings = c("-"))

sa <- sa[1:68, ]

sa[is.na(sa)] <- 0

sa <- sa[-c(1, 3, 26:28)]

library(dplyr)

sa_ <- data.frame(lapply(sa, function(x) gsub(",", "", x)))

sa_ <- sa_ %>% mutate_if(is.character, as.numeric)

attach(sa_)

library(ggplot2)
library(reshape2)

cormat_ = cor(sa_)

cormat <- melt(cor(sa_))

ggplot(data = cormat, aes(x = Var1, y = Var2, fill=value)) + geom_tile()

mod <- lm(Adjustment ~ Total.Raw.Calc + Per.Capita.Applied.Amount + 
     Estimated.Grant..GPG. + Deficit + Minimum.Grant..PC.basis. + 
     Raw.Allocation + MGC + New.Grant)

summary(mod)
