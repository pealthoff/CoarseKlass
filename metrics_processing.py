import csv

import seaborn as sns

import numpy
import pandas
import matplotlib.pyplot as plt
pandas.options.mode.chained_assignment = None

coarsening_directory = "C:/Users/Paulo Eduardo/mestrado/coarsening/"
df = pandas.read_csv(coarsening_directory + 'output/metrics/all-metrics-norm-complete4.csv')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.loc[df['Amostragem'] != '--']
df = df.loc[df['Reduction'] != 0.67]
df = df.loc[df['Reduction'] != 0.74]
df = df.loc[df['Reduction'] != 0.8]
df = df.loc[df['Reduction'] != 0]
cols = df.columns.drop('Snippet')
df[cols] = df[cols].apply(pandas.to_numeric, errors='ignore')
df2 = df
# df2 = df2.loc[df['Reduction'] == 0.79]
# df2 = df2.loc[df['Noise'] == 0.4]
# df2 = df2.loc[df['Dispersion'] == 0.3]
# df2 = df2.loc[df['Amostragem'] == 0.5]
# df2 = df2.loc[df['Vertices'] == 14400]
x = 'Reduction'
x = 'Dispersion'
x = 'Vertices'
kind = 'line'
# kind = 'scatter'
# kind = 'box'
df3 = df2.groupby([x], as_index=False).mean()
for y in ['F-score (micro) N', 'F-score (macro) N']:
    # df2.plot(x=x, y=y, kind=kind)
    plt.plot(x, y, data=df3, marker='v', markerfacecolor='blue', markersize=12, color='skyblue',
             linewidth=4)

plt.legend()
plt.show()



# x = 'Reduction'
# # x = 'Dispersion'
# x = 'Vertices'
# kind = 'line'
# # kind = 'scatter'
# # kind = 'box'
# df3 = df2.groupby([x], as_index=False).mean()
# # plt.plot(x, 'Time class N', data=df3, marker='v', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
# plt.plot(x, 'Time with coarsening N', data=df3, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
#
#     # _ = sns.lmplot(x=x, y=y, data=df2, ci=None)
# plt.legend()
# plt.show()
print(df)

# file = open(coarsening_directory + 'output/metrics/v_100-s_s1-c_4-n_0.100-d0.400-itr_0-metrics.csv')
# csvreader = csv.reader(file)
# header = []
# header = next(csvreader)
# rows = []
# for row in csvreader:
#     rows.append(row)
# file.close()
#
# print(header)
# print(rows)
