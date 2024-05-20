import matplotlib.pyplot as plt
import numpy as np

class Stats:
    def __init__(self, tipo):
        self.tipo = tipo
        self.active = 0
        self.total = 1
    
    def plusOneActive(self):
        self.active = self.active + 1
    
    def plusOne(self):
        self.total = self.total + 1

    def print(self):
        print('Tipo Atividade:',self.tipo)
        print('TOTAL: ', self.total, ' ATIVA: ', self.active,' PERCENT: ', (100/self.total * self.active),'\n')

    def __lt__(self, other):
        return self.tipo < other.tipo

class WorkBlockStats:
    workblockquantidade = 0
    workblockquantidademanha = 0
    workblockquantidadetarde = 0
    def __init__(self, tipo, quantidade):
        self.tipo = tipo
        self.quantidade = quantidade
        WorkBlockStats.workblockquantidade += 1
        if tipo == 'manha' :
            WorkBlockStats.workblockquantidademanha += 1
            self.id = WorkBlockStats.workblockquantidademanha
        else:
            WorkBlockStats.workblockquantidadetarde += 1
            self.id = WorkBlockStats.workblockquantidadetarde


def plot_scatter_with_trendline(dados):
    # Separando os dados em listas separadas para o eixo x e y
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for stat in dados:
        if stat.tipo == 'manha':
            x1.append(stat.id)
            y1.append(stat.quantidade)
        else:
            x2.append(stat.id)
            y2.append(stat.quantidade)

    # Função auxiliar para criar o gráfico de dispersão com linha de tendência
    def create_scatter_plot_with_trendline(x, y, title, filename):
        # Criando o gráfico de dispersão
        plt.scatter(x, y)

        # Calculando a linha de tendência
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        plt.plot(x, p(x), linestyle='-', color='r')

        # Adicionando rótulos aos eixos
        plt.xlabel('Eixo X')
        plt.ylabel('Eixo Y')

        # Adicionando título ao gráfico
        plt.title(title)

        # Exibindo e salvando o gráfico
        plt.grid(True)
        plt.savefig(filename)
        plt.show()

    # Criando o gráfico de dispersão com linha de tendência para a manhã
    create_scatter_plot_with_trendline(x1, y1, 'Gráfico de Dispersão com Linha de Tendência - Manhã', 'PNG_Graphics/PlotScatterTrendline_Manha.png')

    # Criando o gráfico de dispersão com linha de tendência para a tarde
    create_scatter_plot_with_trendline(x2, y2, 'Gráfico de Dispersão com Linha de Tendência - Tarde', 'PNG_Graphics/PlotScatterTrendline_Tarde.png')

def DataAnalyticsByHour(listActivities):
    statsList = []
    for activity in listActivities:
        found = False
        for stat in statsList:
            if stat.tipo == activity.appointment:
                found = True
                stat.plusOne()
                if activity.state == 1:
                    stat.plusOneActive()
                break
        if not found:
            new = Stats(activity.appointment)
            if activity.state == 1:
                new.plusOneActive()
            statsList.append(new)
    
    return statsList


def DataAnalyticsBySkill(listActivities):
    statsList = []
    for activity in listActivities:
        found = False
        for stat in statsList:
            if stat.tipo == activity.skill:
                found = True
                stat.plusOne()
                if activity.state == 1:
                    stat.plusOneActive()
                break
        if not found:
            new = Stats(activity.skill)
            if activity.state == 1:
                new.plusOneActive()
            statsList.append(new)
    
    return statsList