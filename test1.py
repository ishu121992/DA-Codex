import pandas as pd
import matplotlib.pyplot as plt



def plot_histogram(df):
    df.hist(column='Amount', by='Card_Type')
    plt.show()

df = pd.read_csv('tempDir/credit_spend.csv')
plot_histogram(df)
