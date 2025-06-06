'''

    We tried to use the LSTM model (RNN-based model for time series forecasting), but it did not perform well.
    We tried to use the ARIMA model, no results were obtained.
    We are working with sunspot data, which is not linear and has a complex seasonality and trend.

'''

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import numpy as np
import statsmodels.api as sm

'''

    === COLUMNS IN SUNSPOT DAILY TOTAL DATA ===

    year
    month
    day
    date_in_fraction (e.g. 2023-01-01 is 2023.0, 2023-01-02 is 2023.003, etc.)
    total_sunspots
    deviation
    number_of_observations
    definitive/provisional

    === COLUMNS IN SUNSPOT MONTLY TOTAL DATA ===

    year
    month
    date_in_fraction (e.g. 2023-01-01 is 2023.0, 2023-01-02 is 2023.003, etc.)
    total_sunspots
    deviation 
    number_of_observations 
    definitive/provisional 

    === COLUMNS IN SUNSPOT MONTHY SMOOTHED DATA ===

    (identical to the monthly total data, but with a 13-month moving average applied)

    === COLUMNS IN HEMISPHERIC MONTHLY TOTAL DATA ===

    year
    month
    date_in_fraction
    north+south (total sunspots in both hemispheres)
    north (total sunspots in northern hemisphere)
    south (total sunspots in southern hemisphere)
    deviation 
    deviation_north 
    deviation_south 
    observations 
    observations_north 
    observations_south 
    definitive/provisional 

    === COLUMNS IN HEMISPHERIC MONTHLY SMOOTHED DATA: ===

    (identical to the monthly total data, but with a 13-month moving average applied)

    WE HAVE DATA FROM JULY 1st 1749 TO OCTOBER 1st 2024 (AFTER REMOVING FIRST AND LAST 6)
    FIRST AND LAST 6 MONTHS OF DATA IN SMOOTHED ARE MISSING (-1 in column indicates missing data) 

    WE HAVE HEMISPHERIC DATA FROM JANARY 1992 TO APRIL 2025


'''

# Plotting 4 graphs in one figure, one above the other
# monthly total data, monthly smoothed data, hemispheric monthly total data, hemispheric monthly smoothed data
# where in hemispheric data we plot 2 lines, one for north and one for south
# There are no labels (no header) in the data,
# so we will access the columns by their index

def load_data():
    cols_monthly = ['year', 'month', 'date_in_fraction', 'total_sunspots', 'deviation', 'number_of_observations', 'definitive_provisional']
    cols_hemispheric = ['year', 'month', 'date_in_fraction', 'north_south', 'north', 'south', 'deviation', 'deviation_north', 'deviation_south', 'observations', 'observations_north', 'observations_south', 'definitive_provisional']

    df_monthly = pd.read_csv('data/SN_m_tot_V2.0.csv', header=None, names=cols_monthly, sep=';')
    df_monthly_smooth = pd.read_csv('data/SN_ms_tot_V2.0.csv', header=None, names=cols_monthly, sep=';')
    df_hemispheric = pd.read_csv('data/SN_m_hem_V2.0.csv', header=None, names=cols_hemispheric, sep=';')
    df_hemispheric_smooth = pd.read_csv('data/SN_ms_hem_V2.0.csv', header=None, names=cols_hemispheric, sep=';')

    # Convert date_in_fraction to datetime
    # Date in fraction looks like e.g. 2023.453, 2022.123, etc.

    df_monthly['date'] = pd.to_datetime(df_monthly['date_in_fraction'].apply(lambda x: f"{int(x)}-{int((x - int(x)) * 12 + 1):02d}-01"))
    df_monthly_smooth['date'] = pd.to_datetime(df_monthly_smooth['date_in_fraction'].apply(lambda x: f"{int(x)}-{int((x - int(x)) * 12 + 1):02d}-01"))
    df_hemispheric['date'] = pd.to_datetime(df_hemispheric['date_in_fraction'].apply(lambda x: f"{int(x)}-{int((x - int(x)) * 12 + 1):02d}-01"))
    df_hemispheric_smooth['date'] = pd.to_datetime(df_hemispheric_smooth['date_in_fraction'].apply(lambda x: f"{int(x)}-{int((x - int(x)) * 12 + 1):02d}-01"))

    # Set date as index
    df_monthly.set_index('date', inplace=True)
    df_monthly_smooth.set_index('date', inplace=True)
    df_hemispheric.set_index('date', inplace=True)
    df_hemispheric_smooth.set_index('date', inplace=True)

    # Drop unnecessary rows in total_sunspots data (e.g. rows with -1 in total_sunspots)
    df_monthly = df_monthly[df_monthly['total_sunspots'] != -1]
    df_monthly_smooth = df_monthly_smooth[df_monthly_smooth['total_sunspots'] != -1]
    df_hemispheric = df_hemispheric[df_hemispheric['north_south'] != -1]
    df_hemispheric_smooth = df_hemispheric_smooth[df_hemispheric_smooth['north_south'] != -1]

    # Remove forst and last 6 rows in df_monthly to have equal length of data in smoothed and non-smoothed data
    df_monthly = df_monthly.iloc[6:-6]

    # using only monthly data from > 1960 since there is a lot of unreliable data before that
    df_monthly = df_monthly[df_monthly.index >= '1800-01-01']
    df_monthly_smooth = df_monthly_smooth[df_monthly_smooth.index >= '1800-01-01']

    return df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth

def plot_data(df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth):
    plt.figure(figsize=(15, 20))

    # Monthly total data
    plt.subplot(4, 1, 1)
    plt.plot(df_monthly.index, df_monthly['total_sunspots'], label='Monthly Total Sunspots', color='blue')
    plt.grid()
    plt.legend()

    # Monthly smoothed data
    plt.subplot(4, 1, 2)
    plt.plot(df_monthly_smooth.index, df_monthly_smooth['total_sunspots'], label='Monthly Smoothed Sunspots', color='orange')
    plt.grid()
    plt.legend()
    # Hemispheric monthly total data
    plt.subplot(4, 1, 3)
    plt.plot(df_hemispheric.index, df_hemispheric['north'], label='Northern Hemisphere', color='red')
    plt.plot(df_hemispheric.index, df_hemispheric['south'], label='Southern Hemisphere', color='green')
    plt.grid()
    plt.legend()
    # Hemispheric monthly smoothed data
    plt.subplot(4, 1, 4)
    plt.plot(df_hemispheric_smooth.index, df_hemispheric_smooth['north'], label='Northern Hemisphere', color='red')
    plt.plot(df_hemispheric_smooth.index, df_hemispheric_smooth['south'], label='Southern Hemisphere', color='green')
    plt.grid()
    plt.legend()
    plt.tight_layout()  
    plt.show()

def plot_acf_data(df_monthly):

    from statsmodels.graphics.tsaplots import plot_acf

    fig, ax = plt.subplots(figsize=(15, 6))
    plot_acf(df_monthly['total_sunspots'], lags=50, ax=ax)
    ax.set_title('Autocorrelation Function of Monthly Total Sunspots')
    ax.set_xlabel('Lags')
    ax.set_ylabel('Autocorrelation')
    plt.grid()
    plt.show()

def plot_pacf_data(df_monthly):

    from statsmodels.graphics.tsaplots import plot_pacf

    fig, ax = plt.subplots(figsize=(15, 6))
    plot_pacf(df_monthly['total_sunspots'], lags=50, ax=ax)
    ax.set_title('Partial Autocorrelation Function of Monthly Total Sunspots')
    ax.set_xlabel('Lags')
    ax.set_ylabel('Partial Autocorrelation')
    plt.grid()
    plt.show()

def plot_stl_decomposition(df_monthly):

    from statsmodels.tsa.seasonal import STL

    stl = STL(df_monthly['total_sunspots'])  # Using additive model and 13-month seasonality
    result = stl.fit()

    fig = result.plot()  # bez ax argumenta
    fig.set_size_inches(20, 10)
    plt.suptitle('STL Decomposition of Monthly Total Sunspots')
    plt.tight_layout()
    plt.show()

def adf_test_stationarity(series):
    from statsmodels.tsa.stattools import adfuller

    # first we difference the series to make it stationary
    diff_series = series.diff().dropna()
    result = adfuller(diff_series)
    print('ADF Statistic:', result[0])
    print('p-value:', result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'  {key}: {value}')
    if result[1] < 0.05:
        print("The series is stationary (reject H0)")
    else:
        print("The series is non-stationary (fail to reject H0)")

def plot_normalized_data(df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth):
    plt.figure(figsize=(15, 20))

    # Normalized Monthly total data
    plt.subplot(4, 1, 1)
    plt.plot(df_monthly.index, df_monthly['total_sunspots_scaled'], label='Normalized Monthly Total Sunspots', color='blue')
    plt.grid()
    plt.legend()

    # Normalized Monthly smoothed data
    plt.subplot(4, 1, 2)
    plt.plot(df_monthly_smooth.index, df_monthly_smooth['total_sunspots_scaled'], label='Normalized Monthly Smoothed Sunspots', color='orange')
    plt.grid()
    plt.legend()

    # Normalized Hemispheric monthly total data
    plt.subplot(4, 1, 3)
    plt.plot(df_hemispheric.index, df_hemispheric['north_scaled'], label='Normalized Northern Hemisphere', color='red')
    plt.plot(df_hemispheric.index, df_hemispheric['south_scaled'], label='Normalized Southern Hemisphere', color='green')
    plt.grid()
    plt.legend()

    # Normalized Hemispheric monthly smoothed data
    plt.subplot(4, 1, 4)
    plt.plot(df_hemispheric_smooth.index, df_hemispheric_smooth['north_scaled'], label='Normalized Northern Hemisphere', color='red')
    plt.plot(df_hemispheric_smooth.index, df_hemispheric_smooth['south_scaled'], label='Normalized Southern Hemisphere', color='green')
    plt.grid()
    plt.legend()

    plt.tight_layout()  
    plt.show()

def main():
    df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth = load_data()

    #plot_data(df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth)
    #plot_acf_data(df_monthly_smooth) 
    #plot_pacf_data(df_monthly_smooth) # not same for stationary and non-stationary data

    # WE USED pacf for analysis of non-stationary data (great choice)

    """

        Why is sunspot data not stationary?

        Sunspot data is not stationary because it exhibits trends and seasonality.
        Stationarity means that the statistical properties of a time series do not change over time. (check)

        Additive or multiplicative model?

        Additive model would be more appropriate for sunspot data... (not sure, but we will use it for now)

        Trend and seasonality in sunspot data?

        Sunspot data has a long-term trend (increasing/decreasing) and seasonal patterns (e.g. more sunspots during certain months).
        The trend is not linear, but it can be captured by the model.
        Seasonality is complex and not constant over time, so it is not easy to capture with simple models.
        We will use STL decomposition to analyze the data and capture the trend and seasonality.
        Just for the sake of it...


    """

    plot_stl_decomposition(df_monthly)
    #adf_test_stationarity(df_monthly['total_sunspots']) # not sure... (says stationary 100%, but we know it is not)

    
    # Normalize data using Min-Max scaler 

    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    df_monthly['total_sunspots_scaled'] = scaler.fit_transform(df_monthly[['total_sunspots']])
    df_monthly_smooth['total_sunspots_scaled'] = scaler.fit_transform(df_monthly_smooth[['total_sunspots']])
    df_hemispheric['north_scaled'] = scaler.fit_transform(df_hemispheric[['north']])
    df_hemispheric['south_scaled'] = scaler.fit_transform(df_hemispheric[['south']])
    df_hemispheric_smooth['north_scaled'] = scaler.fit_transform(df_hemispheric_smooth[['north']])
    df_hemispheric_smooth['south_scaled'] = scaler.fit_transform(df_hemispheric_smooth[['south']])

    # Plot normalized data
    plot_normalized_data(df_monthly, df_monthly_smooth, df_hemispheric, df_hemispheric_smooth)

    """
    
        This project was orriginally intended to use Informer model for time series forecasting, 
        but for me it is not clear how to use it for sunspot data.

        For now we will stick to SARIMA model, which is a good choice for time series forecasting.

        Why SARIMA model and not ARIMA model?

        SARIMA (Seasonal Autoregressive Integrated Moving Average) is an extension of ARIMA that supports seasonality.
        It is a good choice for time series data with seasonal patterns, like sunspot data.
        ARIMA (Autoregressive Integrated Moving Average) is a good choice for time series data without seasonality.

    """

    ################################################### DAILY DATA ANALYSIS 

    



if __name__ == "__main__":
    main()  
