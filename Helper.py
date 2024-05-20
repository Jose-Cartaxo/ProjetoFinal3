import matplotlib.pyplot as plt

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

            
def plot_line_graph(dados):
    # Separando os dados em listas separadas para o eixo x e y
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    for stat in dados:
        if stat.tipo == 'manha':
            x1.append(stat.id)
            y1.append(stat.quantidade)
        else:
            x2.append(stat.id)
            y2.append(stat.quantidade)

     # Criando o gráfico de linhas para a manhã
    plt.plot(x1, y1, marker='o', linestyle='-')

    # Adicionando rótulos aos eixos
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')

    # Adicionando título ao gráfico
    plt.title('Gráfico de Linhas - Manhã')

    # Exibindo o gráfico
    plt.savefig('PNG_Graphics/PlotLineGraphState_Manha.png')
    plt.grid(True)
    plt.show()

    # Criando o gráfico de linhas para a tarde
    plt.plot(x2, y2, marker='o', linestyle='-')

    # Adicionando rótulos aos eixos
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')

    # Adicionando título ao gráfico
    plt.title('Gráfico de Linhas - Tarde')

    # Exibindo o gráfico
    plt.savefig('PNG_Graphics/PlotLineGraphState_Tarde.png')
    plt.grid(True)
    plt.show()

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