"""This file will be removed.
"""

# import numpy as np
# import pandas as pd

# ##### LOOKUP TABLES #####
# _stats_ = {
#     'mae': "Mean Absolute Error",
#     'mape': "Mean Absolute Percentage Error",
#     'mbe': "Mean Bias Error",
#     'rmse': "Root Mean Squared Error",
#     'mdae': "Median Absolute Error",
#     'r2_score': "R2 Score"
# }


# _pollutants_ = {
#     'co': "Carbon Monoxide (CO)",
#     'pb': "Lead (Pb)",
#     'no2': r"Nitrogen Dioxide ($NO_2$)",
#     'o3': r"Ozone ($O_3$)",
#     'so2': r"Sulphur Dioxide ($SO_2$)",
#     'pm25': r"Particulate Matter smaller than 2.5 $\mu$m",
#     'pm10': r"Particulate Matter smaller than 10 $\mu$m",
# }

# _units_ = {
#     'co': "ppm",
#     'pb': r"$\frac{\mu g}{m^3}$",
#     'no2': "ppb",
#     'o3': "ppm",
#     'so2': "ppb",
#     'pm25': r"$\frac{\mu g}{m^3}$",
#     'pm10': r"$\frac{\mu g}{m^3}$",
# }

# ###################################
# ###### PREDICTIVE REGRESSION ######
# ###################################


# ##### ERROR METRICS FUNCTIONS #####

# EPSILON = 1e-10

# def percentage_error(y_true, y_pred):
#     """
#     Percentage error
#     Note: result is NOT multiplied by 100
#     """
#     return (y_true - y_pred) / (y_true + EPSILON)

# def mean_abs_pct_error(y_true, y_pred):
#     """
#     Mean Absolute Percentage Error
#     Note: result is NOT multiplied by 100
#     """
#     return np.mean(np.abs(percentage_error(y_true, y_pred)))

# def mean_abs_error(y_true, y_pred):
#     """
#     Mean absolute error
    
#     """
#     return np.mean(np.abs(y_true - y_pred))

# def mean_bias_error(y_true, y_pred):
#     """
#     Mean absolute error
    
#     """
#     return np.mean(y_true - y_pred)

# def mean_squared_error(y_true, y_pred):
#     """ 
#     Mean squared error
#     """
#     return np.mean(np.square(y_true - y_pred))

# def root_mean_squared_error(y_true, y_pred):
#     """
#     Root mean squared error
#     """
#     return np.sqrt(mean_squared_error(y_true, y_pred))

# def median_absolute_error(y_true, y_pred):
#     """ 
#     Median Absolute Error
#     """
#     return np.median(np.abs(y_true - y_pred))

# def r2_score(y_true, y_pred):
#     """
#     R^2 score -- adapted from sklearn documentation
#     """
#     numerator = ((y_true - y_pred) ** 2).sum(axis=0)
#     denominator = ((y_true - np.average(y_true, axis=0)) ** 2).sum(axis=0) 
    
#     nonzero_denominator = denominator != 0
#     nonzero_numerator = numerator != 0
    
#     valid_score = nonzero_denominator & nonzero_numerator
#     output_scores = np.ones(y_true.shape)
    
#     output_scores[valid_score] = 1 - (numerator[valid_score] /
#                                       denominator[valid_score])
    
#     return np.average(output_scores)

# ##### COMPUTING PREDICTIVE REGRESSION STATS #####

# METRICS = {
#     'mae': ("Mean Absolute Error", mean_abs_error),
#     'mape': ("Mean Absolute Percentage Error", mean_abs_pct_error),
#     'mbe': ("Mean Bias Error", mean_bias_error),
#     'rmse': ("Root Mean Squared Error", root_mean_squared_error),
#     'mdae': ("Median Absolute Error", median_absolute_error),
#     'r2_score': ("R-squared", r2_score),
# }

# def evaluate(y_true, y_pred, metrics=['mae', 'mape', 'mbe', 'rmse', 'mdae', 'r2_score']):
#     results = {}
#     for name in metrics:
#         if name.lower() in METRICS.keys():
#             label, f = METRICS.get(name.lower())
#             results[name.lower()] = f(y_true, y_pred) 
#         # later on, add logging for values not in the dict
        
#     return results


# def stats(**kwargs):
#     """
#     Calculate statistics between two lists of data

#     Accepts either a dataframe and column names, or two arrays
    
#     Returns a dictionary of computed statistics

#     kwargs
#     ------
#         :param data: dataframe containing atmospheric chemistry data to be compared
#         :type data: pandas Dataframe
#         :param x: column name within data, or array-like data input
#         :type x: str or array-like 
#         :param y: column name within data, or array-like data input
#         :type y: str or array-like 
#         :param metrics: list of metrics to be computed between x and y data
#                         default options = ['mae', 'mbe', 'rmse', 'mdae', 'r2score']
#         :type metrics: list 
        
#     Returns
#     -------
#         z : dictionary of statistics
        
    
#     References
#     ----------
    
#     """
#     x = kwargs.pop("x")
#     y = kwargs.pop("y")
#     data = kwargs.pop("data", None)
    
#     if data is not None:
#         #dataframe and column names
#         y_true = data[x]
#         y_pred = data[y]
#     elif isinstance(x, pd.Series) or isinstance(y, pd.Series):
#         #Series inputs
#         y_true = x.values
#         y_pred = y.values
#     else:
#         #array-like inputs
#         y_true = np.asarray(x)
#         y_pred = np.asarray(y)
    
#     #same length error
#     if len(y_true) != len(y_pred):
#         raise ValueError("Inputs must have the same length")
    
#     #remove nans -- do we want to do this? and if so, is this the best way?
#     clean_y_true = y_true[(np.isnan(y_true)==False) & (np.isnan(y_pred)==False)]
#     clean_y_pred = y_pred[(np.isnan(y_true)==False) & (np.isnan(y_pred)==False)]
    
    
#     return evaluate(clean_y_true, clean_y_pred)



# def statstable(stats):
#     """
#     Print calculated stats in an aesthetic table
    
#     Inputs
#     ------
#     :param stats: Statistical data calculated using the stats function
#     :type stats: dictionary
    
#     Returns
#     -------
#     None --> prints a table of statistics
#     ::
#     """
#     s = ' '
#     print(13*s+"Error Statistics"+13*s)
#     print(42*'-')
    
#     for key, value in stats.items():
#         l = len(key)
#         print(_stats_[key]+s*(30 - len(_stats_[key]))+' = %#8.3f' % value)


# ###################################
# ######### EPA STATISTICS ##########
# ###################################


# ##### SPECIAL EPA PREFERRED STATS #####

# def find_max_n(data, n):
#     """
#     Find the n largest values in an array
#     """
#     output = data.nlargest(n)
        
#     return output


# def days_max_gt_std(data, std):
#     """
#     Find the number of days where the maximum daily measurement is
#     above the standard used by the EPA
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should already be resampled to appropriate timebase
#         :type data: pd.DataFrame or pd.Series
#         :param std: standard value used by EPA
#         :type std: float
    
#     Returns
#     -------
#         count: the number of days where the max value surpassed the standard
#     """
    
#     daily_max = data.groupby(data.index.floor('d')).max()
    
#     count = daily_max[daily_max > std].count()
    
#     return count


# def days_avg_gt_std(data, std):
#     """
#     Find the number of days where the maximum hourly measurement is
#     above the 1-hour standard used by the EPA
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should already be resampled to appropriate timebase
#         :type data: pd.DataFrame or pd.Series
#         :param std: standard value used by EPA
#         :type std: float
    
#     Returns
#     -------
#         count: the number of days where the average value surpassed the standard
#     """
    
#     daily_avg = data.groupby(data.index.floor('d')).mean()
    
#     count = daily_avg[daily_avg > std].count()
    
#     return count


# def percentile_of_daily_max(data, pct):
#     """
#     Find the nth percentile of daily maximum values for time-series data.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should already be resampled to appropriate timebase
#         :type data: pd.DataFrame or pd.Series
#         :param pct: percentile to be calculated
#         :type std: float
        
#     Returns
#     -------
#         value: percentile value
#     """
    
#     daily_max = data.groupby(data.index.floor('d')).max()
    
#     value = np.nanpercentile(daily_max, pct)
    
#     return value


# ##### POLLUTANT SPECIFIC REPORTS #####

# def co_stats(data):
#     """
#     Compute the EPA monitoring report values for CO. Data should be in ppm.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
#     # 1 hour statistics
    
#     #Highest and second-highest daily max 1-hour values
#     max12_1h = find_max_n(data, 2)
    
#     #Number of daily max 1-hour values that exceeded the level of the 1-hour standard
#     days_gt_std_1h = days_max_gt_std(data, 35)
    
#     # 8 hour statistics
#     mean_8h = data.resample('8h').mean()
    
#     #Highest and second-highest daily max 8-hour values
#     max12_8h = find_max_n(mean_8h, 2)
    
#     #Number of daily max 1-hour values that exceeded the level of the 8-hour standard
#     days_gt_std_8h = days_max_gt_std(mean_8h, 9)
    
#     stats = {
#         "co" : {
#             "1h" : {
#                 "mean": np.nanmean(data),
#                 "min": np.nanmin(data),
#                 "max_1": max12_1h[0],
#                 "max_2": max12_1h[1],
#                 "pct_25": np.nanpercentile(data, 25),
#                 "pct_75": np.nanpercentile(data, 75),
#                 "pct_98": np.nanpercentile(data, 98),
#                 "days_max_gt_std": days_gt_std_1h,
#             },
#             "8h" : {
#                 "mean": np.nanmean(mean_8h),
#                 "min": np.nanmin(mean_8h),
#                 "max_1": max12_8h[0],
#                 "max_2": max12_8h[1],
#                 "pct_25": np.nanpercentile(mean_8h, 25),
#                 "pct_75": np.nanpercentile(mean_8h, 75),
#                 "pct_98": np.nanpercentile(mean_8h, 98),
#                 "days_max_gt_std": days_gt_std_8h,
#             }
#         }
#     }
    
#     return stats
    

# def no2_stats(data):
#     """
#     Compute the EPA monitoring report values for NO2. Data should be in ppb.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
    
#     # 1 hour statistics
    
#     #Highest and second-highest daily max 1-hour values
#     max12_1h = find_max_n(data, 2)
    
#     # 98th percentile of daily max 1hr values
#     pct_98_daily_max = percentile_of_daily_max(data, 98)
    
#     stats = {
#         "no2": {
#             "1h": {
#                 "mean": np.nanmean(data),
#                 "min": np.nanmin(data),
#                 "max_1": max12_1h[0],
#                 "max_2": max12_1h[1],
#                 "pct_25": np.nanpercentile(data, 25),
#                 "pct_75": np.nanpercentile(data, 75),
#                 "pct_98": np.nanpercentile(data, 98),
#                 "pct_98_daily_max": pct_98_daily_max,
#             }
#         }
#     }
    
#     return stats


# def pb_stats(data):
#     """
#     Compute the EPA monitoring report values for Pb. Data should be in micrograms per
#     cubic meter.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
#     # 24 hour statistics
#     mean_24h = data.resample('24h').mean()
    
#     #Highest, second-highest, third-highest, and fourth-highest daily max 24-hour values
#     max1234 = find_max_n(data, 4)
    
#     stats = {
#         "pb": {
#             "24h": {
#                 "mean": np.nanmean(mean_24h),
#                 "min": np.nanmin(mean_24h),
#                 "max_1": max1234[0],
#                 "max_2": max1234[1],
#                 "max_3": max1234[2],
#                 "max_4": max1234[3],
#                 "pct_25": np.nanpercentile(mean_24h, 25),
#                 "pct_75": np.nanpercentile(mean_24h, 75),
#                 "pct_98": np.nanpercentile(mean_24h, 98),
#             }
#         }
#     }
    
#     return stats


# def o3_stats(data):
#     """
#     Compute the EPA monitoring report values for Pb. Data should be in ppm.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
    
#     # 1 hour statistics
    
#     #Highest, second-highest, third-highest, and fourth-highest daily max 1-hour values
#     max1234_1h = find_max_n(data, 4)
    
#     #Number of daily max 1-hour values that exceeded the level of the 1-hour standard
#     days_gt_std_1h = days_max_gt_std(data, 0.12)
    
#     # 8 hour statistics
#     mean_8h = data.resample('8h').mean()
    
#     #Highest, second-highest, third-highest, and fourth-highest daily max 8-hour values
#     max1234_8h = find_max_n(mean_8h, 4)
    
#     #Number of daily max 1-hour values that exceeded the level of the 8-hour standard
#     days_gt_std_8h = days_max_gt_std(mean_8h, 0.07)
    
    
#     stats = {
#         "o3" : {
#             "1h" : {
#                 "mean": np.nanmean(data),
#                 "min": np.nanmin(data),
#                 "max_1": max1234_1h[0],
#                 "max_2": max1234_1h[1],
#                 "max_3": max1234_1h[2],
#                 "max_4": max1234_1h[3],
#                 "pct_25": np.nanpercentile(data, 25),
#                 "pct_75": np.nanpercentile(data, 75),
#                 "pct_98": np.nanpercentile(data, 98),
#                 "days_max_gt_std": days_gt_std_1h,
#             },
#             "8h" : {
#                 "mean": np.nanmean(mean_8h),
#                 "min": np.nanmin(mean_8h),
#                 "max_1": max1234_8h[0],
#                 "max_2": max1234_8h[1],
#                 "max_3": max1234_8h[2],
#                 "max_4": max1234_8h[3],
#                 "pct_25": np.nanpercentile(mean_8h, 25),
#                 "pct_75": np.nanpercentile(mean_8h, 75),
#                 "pct_98": np.nanpercentile(mean_8h, 98),
#                 "days_max_gt_std": days_gt_std_8h,
#             }
#         }
#     }
    
#     return stats
    

# def so2_stats(data):
#     """
#     Compute the EPA monitoring report values for SO2. Data should be in ppm.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
    
#     # 1 hour statistics
    
#     #Highest and second-highest daily max 1-hour values
#     max12_1h = find_max_n(data, 2)
    
#     # 99th percentile of daily max 1hr values
#     pct_99_daily_max = percentile_of_daily_max(data, 99)
    
#     #Number of daily max 1-hour values that exceeded the level of the 1-hour standard
#     days_gt_std_1h = days_max_gt_std(data, 0.075)
    
    
#     #24 hour statistics
#     mean_24h = data.resample('24h').mean()
    
#     #Highest and second-highest daily max 24-hour values
#     max12_24h = find_max_n(mean_24h, 2)
    
#     #Number of daily max 24-hour values that exceeded the level of the 24-hour standard
#     days_gt_std_24h = days_max_gt_std(mean_24h, 0.14)
    
    
#     stats = {
#         "so2" : {
#             "1h" : {
#                 "mean": np.nanmean(data),
#                 "min": np.nanmin(data),
#                 "max_1": max12_1h[0],
#                 "max_2": max12_1h[1],
#                 "pct_25": np.nanpercentile(data, 25),
#                 "pct_75": np.nanpercentile(data, 75),
#                 "pct_98": np.nanpercentile(data, 98),
#                 "pct_99_daily_max": pct_99_daily_max,
#                 "days_max_gt_std": days_gt_std_1h,
#             },
#             "24h" : {
#                 "mean": np.nanmean(mean_24h),
#                 "min": np.nanmin(mean_24h),
#                 "max_1": max12_24h[0],
#                 "max_2": max12_24h[1],
#                 "pct_25": np.nanpercentile(mean_24h, 25),
#                 "pct_75": np.nanpercentile(mean_24h, 75),
#                 "pct_98": np.nanpercentile(mean_24h, 98),
#                 "days_max_gt_std": days_gt_std_24h,
#             }
#         }
#     }
    
#     return stats
    

# def pm25_stats(data):
#     """
#     Compute the EPA monitoring report values for PM 2.5. Data should be in micrograms per
#     cubic meter.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
    
#     #24 hour statistics
#     mean_24h = data.resample('24h').mean()
    
#     #Highest, second-highest, third-highest, and fourth-highest daily max 1-hour values
#     max1234_24h = find_max_n(mean_24h, 4)
    
#     stats = {
#         "pm25": {
#             "24h": {
#                 "mean": np.nanmean(mean_24h),
#                 "min": np.nanmin(mean_24h),
#                 "max_1": max1234_24h[0],
#                 "max_2": max1234_24h[1],
#                 "max_3": max1234_24h[2],
#                 "max_4": max1234_24h[3],
#                 "pct_25": np.nanpercentile(mean_24h, 25),
#                 "pct_75": np.nanpercentile(mean_24h, 75),
#                 "pct_98": np.nanpercentile(mean_24h, 98),
#             }
#         }
#     }
    
#     return stats


# def pm10_stats(data):
#     """
#     Compute the EPA monitoring report values for PM 10. Data should be in micrograms per
#     cubic meter.
    
#     Inputs
#     ------
#         :param data: dataframe or Series with timestamp index and pollution data column.
#                     should be resampled to 1h timebase
#         :type data: pd.DataFrame or pd.Series
        
#     Returns
#     -------
#         stats: dictionary of statistics
#     """
    
#     #24 hour statistics
#     mean_24h = data.resample('24h').mean()
    
#     #Highest and second-highest daily max 1-hour values
#     max12_24h = find_max_n(mean_24h, 2)
    
#     #Number of daily max 24-hour values that exceeded the level of the 24-hour standard
#     days_gt_std_24h = days_max_gt_std(mean_24h, 150)
    
#     stats = {
#         "pm10": {
#             "24h": {
#                 "mean": np.nanmean(mean_24h),
#                 "min": np.nanmin(mean_24h),
#                 "max_1": max12_24h[0],
#                 "max_2": max12_24h[1],
#                 "pct_25": np.nanpercentile(mean_24h, 25),
#                 "pct_75": np.nanpercentile(mean_24h, 75),
#                 "pct_98": np.nanpercentile(mean_24h, 98),
#                 "days_max_gt_std": days_gt_std_24h,
#             }
#         }
#     }
    
#     return stats

# ##### COMPUTING EPA CHOSEN STATS #####

# POLLUTANTS = {
#     'co': co_stats,
#     'pb': pb_stats,
#     'no2': no2_stats,
#     'o3': o3_stats,
#     'so2': so2_stats,
#     'pm25': pm25_stats,
#     'pm10': pm10_stats
# }


# def EPAstats(df, col, pollutants=['co', 'no2', 'o3', 'pm10', 'pm25', 'so2'], tscol=None):
#     """
#     Compute the EPA monitoring report statistics for chosen pollutants with any appropriate 
#     time-series data. 
#     EPA recognized pollutants:
#         CO, Pb, NO2, O3, SO2, PM2.5, PM10
    
#     Inputs
#     ------
#         :param df: dataframe containing time series pollution data
#         :type data: pandas Dataframe
#         :param col: column name(s) within df that correspond(s) to chosen pollutants
#         :type col: str or list of str
        
#     Optional Inputs
#     ---------------
#     :param pollutants: list of pollutants to be computed 
#                         default options = ['co', 'no2', 'o3', 'pm10', 'pm25', 'so2']
#     :type pollutants: str or list of str 
#     :param tscol: column name within df that is the timestamp column. Must be pd.Datetime Series
#                     If left as None, then timestamp is assumed to be df.index
#     :type tscol: str
    
#     Returns
#     -------
#         z : dictionary of statistics
        
    
#     References
#     ----------
#     EPA monitoring report statistics:
#     https://www.epa.gov/outdoor-air-quality-data/about-air-data-reports#con
    
#     EPA Standard Pollution Levels:
#     https://www.epa.gov/criteria-air-pollutants/naaqs-table
    
#     """
#     if isinstance(col, str):
#         col = list(col)
    
#     # If timestamp column isn't given, we assume the index to be DatetimeIndex
#     if tscol is None:
#         data = df[col].copy(deep=True)
#     else:
#         tscol = list(tscol)
#         data = df[tscol+col].copy(deep=True)
#         data.set_index(tscol, inplace=True)
    
#     data.index = pd.DatetimeIndex(data.index)
#     data = data.resample('1h').mean()

#     stats = {}
#     for i,p in enumerate(col):
#         temp = data[col[i]]
#         stats.update(POLLUTANTS[p](temp))
    
#     reform = {(outerKey, innerKey): values for outerKey, innerDict in stats.items() for innerKey, values in innerDict.items()}

#     return reform
