data = read.csv("C:\\Users\\liu.6544\\Documents\\GitHub\\CoronavirusTransit\\doc\\excels\\correlation.csv")
wfh_pop_rate = data$Work.from.home.populuation.ratio
all_working_pop = data$All.working.population
transit_pop_rate = data$Transit.commuting.population.ratio
google_trend = data$X..Unique.users
social_rate = data$social_rate
net_post_per_capita = data$net_post_per_capita
B = data$B
pop = data$pop
pp55 = data$pp55
pp65 = data$pp65
pp75 = data$pp75
pp85 = data$pp85

fit <- lm(B ~ Work.from.home.populuation.ratio +  black_ratio + pp45 + google_trend_Coronavirus, data=data)
summary(fit)  # show results
car::vif(fit)

fit <- lm(B ~ black_ratio + pp45 + google_trend_Coronavirus, data=data)
summary(fit)  # show results
car::vif(fit)

fit <- lm(B ~ Work.from.home.populuation.ratio +  pp45 + google_trend_Coronavirus, data=data)
summary(fit)  # show results
car::vif(fit)

fit <- lm(B ~ Work.from.home.populuation.ratio +  black_ratio + google_trend_Coronavirus, data=data)
summary(fit)  # show results
car::vif(fit)

fit <- lm(B ~ Work.from.home.populuation.ratio +  black_ratio + pp45, data=data)
summary(fit)  # show results
car::vif(fit)


cor.test(data$B, data$vehicle0_renter)
cor.test(data$Work.from.home.populuation.ratio, data$google_trend_Coronavirus)

cor.test(data$Work.from.home.populuation.ratio, data$hispanic_ratio)
cor.test(data$pp45, data$all_post_per_capita)
cor.test(data$Work.from.home.populuation.ratio, data$vehicle0_house_rate)
cor.test(data$Work.from.home.populuation.ratio, data$transit_pop_rate)
cor.test(data$median_income, data$female_ratio)
cor.test(data$black_ratio, data$median_income)
cor.test(data$black_ratio, data$vehicle0_house_rate)
cor.test(data$B, data$black_ratio)
cor.test(data$divergent_point, data$convergent_point)

residual = resid(fit)

par(mfrow=c(2,2))
plot(fit)
