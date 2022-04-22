import csv

import seaborn as sns

import pandas
import matplotlib.pyplot as plt

pandas.options.mode.chained_assignment = None

# name = 's1'
# name = 's1-900'
name = 'hier-3000-x'
# comp = True
comp = False
std_red = False

coarsening_directory = "C:/Users/Paulo Eduardo/mestrado/coarsening/"
df_control = pandas.read_csv(coarsening_directory + 'output/metrics/metrics-control.csv')

df_c1 = df_control.loc[df_control['graph'] == 1]
df_c2 = df_c1.loc[df_control['metric'] == 1]
# df_c2['v']=df_c2['v']/16
# df['v']=df['v']/16
df_c3 = df_c2.groupby(['c'], as_index=False).sum()

# df = pandas.read_csv(coarsening_directory + 'output/metrics/all-metrics-norm-complete.csv')
# df = pandas.read_csv(coarsening_directory + 'output/metrics/hier-metrics.csv')
df = pandas.read_csv(coarsening_directory + 'output/metrics/' + name + '-metrics.csv')
# df = pandas.read_csv(coarsening_directory + 'output/metrics/APCT-norm-complete.csv')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.loc[df['Amostragem'] != '--']
# df = df.loc[df['Amostragem'] >= 0.1]
# df = df.loc[df['Reduction'] != 0.67]
# df = df.loc[df['Reduction'] != 0.74]
df = df.loc[df['Reduction'] != 0.8]
# df = df.loc[df['Reduction'] == 0.0]

df['Amostragem'] = df['Amostragem'] * 100
df['Reduction'] = df['Reduction'] * 100
if name == 'hier-3000-x':
    df['Vertices'] = df['Vertices'] * 1.5

if comp:
    df = df.loc[df['Vertices'] < 15000]


###############################



filters = {
        # 'Noise': 0.1,
        # 'Dispersion': 0.4,
        # 'Communities': 5,
        # 'Vertices': 1600,
        # 'Amostragem': 0.01,
        # 'Schema': 'h1',
        # 'Reduction': 0.2
}

df_filtered = df
for metric in filters:
    df_filtered = df_filtered.loc[df_filtered[metric] == filters[metric]]
    # df_filtered = df_filtered.loc[df_filtered['Vertices'] < 24000]
    # df_filtered = df_filtered.loc[df['Reduction'] < 0.5]
# df_filtered = df_filtered.loc[df_filtered['Precision (macro)'] > 0.6]

df_filtered = df_filtered.rename(columns={"Amostragem": "% rótulos inicial",
                        "Dispersion": "Dispersão",
                        "Noise": "Ruído",
                        "Vertices": "# de vértices",
                        "Reduction": "% de redução",
                        "Communities": "# de classes",
                        "F-score (micro)": "Accuracy",
                        "F-score (micro) N": "Accuracy N",
                        })

for ya in [
    "Accuracy",
    'F-score (macro)',
    'Precision (macro)',
    'Recall (macro)'
]:
    y = ya + ' N'
    df_filtered = df_filtered.rename(columns={y: ya + ' relativa'})

df_filtered = df_filtered.loc[df_filtered['% de redução'] != 65]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 66]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 69]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 70]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 71]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 72]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 73]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 75]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 76]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 77]
df_filtered = df_filtered.loc[df_filtered['% de redução'] != 78]

def plot():

    for ya in [
        'Accuracy',
        'F-score (macro)',
        'Precision (macro)',
        'Recall (macro)'
    ]:
        for y in [
                  ya + ' relativa',
                  ya
        ]:
            for x in [
                # 'Ruído',
                # 'Dispersão',
                '% rótulos inicial',
                # '# de vértices',
                # '# de classes'
            ]:
                x_name = x.replace(" ", "-").replace("%", "pct").replace("#", "n")
                y_name = y.replace(" ", "-").replace("%", "pct").replace("#", "n")
                print(coarsening_directory + 'output/images/seaborn/' + name + '/' + 'pct_de_reducao' + '_x_' + y_name + '_hue=' + x_name + '.png')


                if name == 'hier-3000-x':
                    if comp:
                        sns.lineplot(x=x, y=y, data=df_filtered, hue='% de redução', palette=sns.color_palette("viridis", as_cmap=True), ci=50)
                        plt.savefig(coarsening_directory + 'output/images/seaborn/' + name + '-comp/comp-' + x_name + '_x_' + y_name + '_hue=' + 'pct_de_reducao' + '.png')
                        plt.show()
                    else:
                        if std_red:
                            #100000
                            sns.lineplot(x=x, y=y, data=df_filtered, hue='% de redução', palette=sns.color_palette("viridis", as_cmap=True), ci=50)
                            plt.savefig(coarsening_directory + 'output/images/seaborn/' + name + '-100000/100000-' + x_name + '_x_' + y_name + '_hue=' + 'pct_de_reducao' + '.png')
                            plt.show()
                        else:


                            sns.lineplot(x='% de redução', y=y, data=df_filtered, hue=x, palette=sns.color_palette("viridis", as_cmap=True))
                            plt.savefig(coarsening_directory + 'output/images/seaborn/' + name + '/' + 'pct_de_reducao' + '_x_' + y_name + '_hue=' + x_name + '.png')
                            plt.show()

                            sns.lineplot(x=x, y=y, data=df_filtered, hue='% de redução',
                                         palette=sns.color_palette("viridis", as_cmap=True))
                            plt.savefig(
                                coarsening_directory + 'output/images/seaborn/' + name + '/' + x_name + '_x_' + y_name + '_hue=' + 'pct_de_reducao' + '.png')
                            plt.show()
                else:
                    # sns.lineplot(x='% de redução', y=y, data=df_filtered, hue=x, palette=sns.color_palette("viridis", as_cmap=True))
                    # plt.savefig(coarsening_directory + 'output/images/seaborn/' + name + '/' + 'pct_de_reducao' + '_x_' + y_name + '_hue=' + x_name + '.png')
                    # plt.show()

                    sns.lineplot(x=x, y=y, data=df_filtered, hue='% de redução', palette=sns.color_palette("viridis", as_cmap=True))
                    plt.savefig(
                        coarsening_directory + 'output/images/seaborn/' + name + '/' + x_name + '_x_' + y_name + '_hue=' + 'pct_de_reducao' + '.png')
                    plt.show()

# sns.lineplot(x=x, y=y, data=df_filtered, hue='# de vértices',palette=sns.color_palette("viridis", as_cmap=True))
# plt.savefig(coarsening_directory + 'output/images/seaborn/' + name + '/' + x_name + '_x_' + y_name + '_hue=' + 'n_de_vértices' + '.png')
# plt.show()


# plot()


def gen_table_red(df_filtered):
    df_red = df_filtered.groupby("% de redução").mean()
    df_red_m = df_red[['Precision (macro) relativa', 'Recall (macro) relativa', 'Accuracy relativa', 'F-score (macro) relativa']]
    df_red_m = df_red_m.apply(lambda x: 100*abs(1-x))

    df_red_s = df_filtered.groupby("% de redução").std()

    df_red_s = df_red_s[['Precision (macro) relativa', 'Recall (macro) relativa', 'Accuracy relativa', 'F-score (macro) relativa']]

    df_red_s = df_red_s.rename(columns={
        'Precision (macro) relativa': 'Precision (macro) relativa std',
    'Recall (macro) relativa': 'Recall (macro) relativa std',
    'Accuracy relativa': 'Accuracy relativa std',
    'F-score (macro) relativa': 'F-score (macro) relativa std'})

    df_red_s = df_red_s.apply(lambda x: 10*x)

    df_red_ms = pandas.concat([df_red_m, df_red_s], axis=1)

    columns = []

    for ya in [
        'Accuracy',
        'F-score (macro)',
        'Precision (macro)',
        'Recall (macro)'
    ]:
        for y in [
            ya + ' relativa',
        ]:
            columns.append(y + ' tb')
            df_red_ms[y + ' tb'] = ""
            for index, row in df_red_ms.iterrows():
                df_red_ms[y + ' tb'][index] = str("{:.2f}".format(df_red_ms[y][index])) + '+-' + str(
                    "{:.2f}".format(df_red_ms[y + ' std'][index])) + "% "
    return df_red_ms[columns]



# , 66, 69, 70, 71, 72, 73, 75, 76, 77, 78]]
df_filtered_a = df_filtered
df_filtered_noise_01 = df_filtered
df_filtered_noise_04 = df_filtered
df_filtered_noise_01 = df_filtered_noise_01.loc[df_filtered_noise_01['Ruído'] == 0.1]
df_filtered_noise_04 = df_filtered_noise_04.loc[df_filtered_noise_04['Ruído'] == 0.4]
df_filtered_vertices_min = df_filtered
df_filtered_vertices_max = df_filtered
#s1_900
min = 2400
max = 19200
#hier 1500 1.5
min = 3150
max = 12600
#hier 100000 1.5
min = 3150
max = 94500
df_filtered_vertices_min = df_filtered_vertices_min.loc[df_filtered_vertices_min['# de vértices'] == min]
df_filtered_vertices_max = df_filtered_vertices_max.loc[df_filtered_vertices_max['# de vértices'] == max]

table_noise_a = gen_table_red(df_filtered_a)
table_noise_01 = gen_table_red(df_filtered_noise_01)
table_noise_04 = gen_table_red(df_filtered_noise_04)
table_noise_vertices_min = gen_table_red(df_filtered_vertices_min)
table_noise_vertices_max = gen_table_red(df_filtered_vertices_max)

print('ok')
