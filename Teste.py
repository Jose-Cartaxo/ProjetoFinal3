from Main import main
import pandas as pd

# Caminho para o arquivo Excel existente
caminho_arquivo = 'ResultadosCU.xlsx'


    # 1 - K-NearestNeighbors 1.0
    # 2 - K-NearestNeighbors 2.0
    # 3 - K-NearestNeighbors com DBSCANS
    # 4 - DBSCANS
    # 5 - Central

def knnn():
    # 1 - K-NearestNeighbors 1.0
    metodoCluster = 1

    dbscan_min = -1
    dbscan_max = -1
    dbscan_ite = -1

    lista_knn_ite = [2,3,4,5,6,7,8,9,10,11,12]
    tempo_dep = 60
    tempo_ant = 30

    for knn_ite in lista_knn_ite:
        res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
        Percent_Atividades = res[0]
        Quant_Pdd = res[1]
        Quant_No = res[2]

        novos_dados = {
            'metodoClustering': metodoCluster,
            'dbscan_min': dbscan_min,
            'dbscan_max': dbscan_max,
            'dbscan_ite': dbscan_ite,
            'knn_ite': knn_ite,
            'tempo_dep': tempo_dep,
            'tempo_ant': tempo_ant,
            'Percent Atividades': Percent_Atividades,
            'Quant Pdd': Quant_Pdd,
            'Quant No': Quant_No
        }


        # Carregar o arquivo Excel existente
        df = pd.read_excel(caminho_arquivo)

        # Criar um DataFrame com a nova linha
        df_novos_dados = pd.DataFrame([novos_dados])

        # Concatenar o DataFrame existente com o DataFrame da nova linha
        df = pd.concat([df, df_novos_dados], ignore_index=True)

        # Salvar o arquivo Excel
        df.to_excel(caminho_arquivo, index=False)







def knna():
    # 2 - K-NearestNeighbors 2.0
    metodoCluster = 2

    dbscan_min = -1
    dbscan_max = -1
    dbscan_ite = -1

    lista_knn_ite = [2,3,4,5,6,7,8,9,10,11,12]
    tempo_dep = 60
    tempo_ant = 30

    for knn_ite in lista_knn_ite:
        res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
        Percent_Atividades = res[0]
        Quant_Pdd = res[1]
        Quant_No = res[2]

        novos_dados = {
            'metodoClustering': metodoCluster,
            'dbscan_min': dbscan_min,
            'dbscan_max': dbscan_max,
            'dbscan_ite': dbscan_ite,
            'knn_ite': knn_ite,
            'tempo_dep': tempo_dep,
            'tempo_ant': tempo_ant,
            'Percent Atividades': Percent_Atividades,
            'Quant Pdd': Quant_Pdd,
            'Quant No': Quant_No
        }


        # Carregar o arquivo Excel existente
        df = pd.read_excel(caminho_arquivo)

        # Criar um DataFrame com a nova linha
        df_novos_dados = pd.DataFrame([novos_dados])

        # Concatenar o DataFrame existente com o DataFrame da nova linha
        df = pd.concat([df, df_novos_dados], ignore_index=True)

        # Salvar o arquivo Excel
        df.to_excel(caminho_arquivo, index=False)







def knndbscan():
    # 3 - K-NearestNeighbors com DBSCANS
    metodoCluster = 3

    lista_dbscan_min = [1,2,3,4,5]
    lista_dbscan_max = [10,15,20,25,30,35,40]
    lista_dbscan_ite = [1,2,3,4,5]

    lista_knn_ite = [12]
    tempo_dep = 60
    tempo_ant = 30

    for knn_ite in lista_knn_ite:
        for dbscan_min in lista_dbscan_min:
            for dbscan_max in lista_dbscan_max:
                for dbscan_ite in lista_dbscan_ite:
                    res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
                    Percent_Atividades = res[0]
                    Quant_Pdd = res[1]
                    Quant_No = res[2]

                    novos_dados = {
                        'metodoClustering': metodoCluster,
                        'dbscan_min': dbscan_min,
                        'dbscan_max': dbscan_max,
                        'dbscan_ite': dbscan_ite,
                        'knn_ite': knn_ite,
                        'tempo_dep': tempo_dep,
                        'tempo_ant': tempo_ant,
                        'Percent Atividades': Percent_Atividades,
                        'Quant Pdd': Quant_Pdd,
                        'Quant No': Quant_No
                    }


                    # Carregar o arquivo Excel existente
                    df = pd.read_excel(caminho_arquivo)

                    # Criar um DataFrame com a nova linha
                    df_novos_dados = pd.DataFrame([novos_dados])

                    # Concatenar o DataFrame existente com o DataFrame da nova linha
                    df = pd.concat([df, df_novos_dados], ignore_index=True)

                    # Salvar o arquivo Excel
                    df.to_excel(caminho_arquivo, index=False)







def dbscan():
    # 4 - DBSCANS
    metodoCluster = 4

    lista_dbscan_min = [1,2,3,4,5]
    lista_dbscan_max = [10,15,20,25,30,35,40]
    lista_dbscan_ite = [1,2,3,4,5]

    knn_ite = -1
    tempo_dep = 60
    tempo_ant = 30

    for dbscan_min in lista_dbscan_min:
        for dbscan_max in lista_dbscan_max:
            for dbscan_ite in lista_dbscan_ite:
                res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
                Percent_Atividades = res[0]
                Quant_Pdd = res[1]
                Quant_No = res[2]

                novos_dados = {
                    'metodoClustering': metodoCluster,
                    'dbscan_min': dbscan_min,
                    'dbscan_max': dbscan_max,
                    'dbscan_ite': dbscan_ite,
                    'knn_ite': knn_ite,
                    'tempo_dep': tempo_dep,
                    'tempo_ant': tempo_ant,
                    'Percent Atividades': Percent_Atividades,
                    'Quant Pdd': Quant_Pdd,
                    'Quant No': Quant_No
                }


                # Carregar o arquivo Excel existente
                df = pd.read_excel(caminho_arquivo)

                # Criar um DataFrame com a nova linha
                df_novos_dados = pd.DataFrame([novos_dados])

                # Concatenar o DataFrame existente com o DataFrame da nova linha
                df = pd.concat([df, df_novos_dados], ignore_index=True)

                # Salvar o arquivo Excel
                df.to_excel(caminho_arquivo, index=False)







def central():
    # 5 - Central
    metodoCluster = 5

    dbscan_min = -1
    dbscan_max = -1
    dbscan_ite = -1

    lista_knn_ite = [2,3,4,5,6,7,8,9,10,11,12]
    tempo_dep = 60
    tempo_ant = 30

    for knn_ite in lista_knn_ite:
        res = main(metodoCluster, dbscan_min, dbscan_max, dbscan_ite, knn_ite, tempo_dep, tempo_ant)
        Percent_Atividades = res[0]
        Quant_Pdd = res[1]
        Quant_No = res[2]

        novos_dados = {
            'metodoClustering': metodoCluster,
            'dbscan_min': dbscan_min,
            'dbscan_max': dbscan_max,
            'dbscan_ite': dbscan_ite,
            'knn_ite': knn_ite,
            'tempo_dep': tempo_dep,
            'tempo_ant': tempo_ant,
            'Percent Atividades': Percent_Atividades,
            'Quant Pdd': Quant_Pdd,
            'Quant No': Quant_No
        }


        # Carregar o arquivo Excel existente
        df = pd.read_excel(caminho_arquivo)

        # Criar um DataFrame com a nova linha
        df_novos_dados = pd.DataFrame([novos_dados])

        # Concatenar o DataFrame existente com o DataFrame da nova linha
        df = pd.concat([df, df_novos_dados], ignore_index=True)

        # Salvar o arquivo Excel
        df.to_excel(caminho_arquivo, index=False)







knnn()
knna()
# knndbscan()
# dbscan()
# central()