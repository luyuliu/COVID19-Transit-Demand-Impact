# Codes
This folder contains the necessary codes to reproduce the results. The codes are based on python and MongoDB. Please make sure you set up the environment before running the code. All codes are under the MIT license.

## daily_analysis
This folder contains the codes to conduct the daily analysis based on daily analysis.

### fit_exponential.py
This code will fit the logistic function based on daily transit demand data and generate the key parameters in the model. It also generates the date of first confirmed case. The results will be inserted in a mongodb database. 

### fit_k_and_cliff/base_point.py
These two codes generates the Fig 7.

### time_lag.py
This code calculate and print the response intervals for different incubation lag.

### qq_plot.py
This code generates the qq plots of the logistic function curve fitting.

## data_pipeline
This folder contains different codes that we used to collect the raw data.

## hourly_analysis
This folder contains two codes we used to conduct hourly analysis and procrustes analysis.

### calculate_similarity.py
This code contains methods of the procrustes analysis and Fig 10.

### calculate_similarity_weekdaysandweekends.py
This code contains the procrustes analysis between 

## correlation.r
The R code that conducts regression and correlation analyses between factors calculated from the raw data.