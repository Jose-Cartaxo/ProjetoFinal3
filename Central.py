from numpy import double
from typing import List, Dict, Any, Tuple
from datetime import datetime, time

from KNearest_Neighbors import KNearest_Neighbors_Normal
from Helper import activitiesToState1, Distance_Calculator
from Optimization import Greedy
from Workers import Worker, WorkBlock, Find_Worker_By_Id
from Ploting import plot_activities_by_order, plot_scatter_with_trendline
from Activity import Activity
from Stats import WorkBlockStats


class Elemento_Lista_Grupos_Central:
    """É cada elemento da lista de atividades separadas por Central
    """
    def __init__(self, atividade):
        self.centro = [0,0]
        self.lista_atividades = [atividade]

    def AdicionarAtividade(self, atividade: Activity):
        """Adiciona a atividade recebida à "lista"

        Args:
            atividade (Activity): Atividade a adicionar
        """
        self.lista_atividades.append(atividade)

    def CalcularCentro(self):
        """Calcula o centro, através da média de todas as atividades pertencentes, e passa a ver o centro desta "central"
        """
        x_total = 0
        y_total = 0
        for atividade in self.lista_atividades:
            x_total += atividade.x
            y_total += atividade.y

        x_medio = x_total / len(self.lista_atividades)
        y_medio = y_total / len(self.lista_atividades)
        self.centro = [x_medio, y_medio]



class Lista_Grupos_Central:
    """Dicionário com o id da central e a lista de atividades que pertencem a essa central.
    """
    quantidadeGrupos = 0

    def __init__(self):
        self.lista_grupos_atividades: dict = {}

    def PesquisarPorId(self, idCentral: str)-> list[Activity]:
        """Perquisa a Central pelo seu Id

        Args:
            idCentral (str): id da central procurada

        Returns:
            list[Activity]: lista de todas as atividades pertencentes a essa central
        """
        return self.lista_grupos_atividades.get(idCentral, None).lista_atividades
    
    def AdicionarGrupoId(self, idCentral: str, atividade: Activity):
        """Adiciona a atividade ao seu grupo de acordo com o id da sua central

        Args:
            idCentral (str): id da central da atividade
            atividade (Activity): atividade a ser adicionada
        """
        if idCentral in self.lista_grupos_atividades:
            self.lista_grupos_atividades[idCentral].AdicionarAtividade(atividade)
        else:
            self.lista_grupos_atividades[idCentral] = Elemento_Lista_Grupos_Central(atividade)
            Lista_Grupos_Central.quantidadeGrupos += 1
        
    def CalcularTodosCentros(self):
        """Calcula todos os centros de todas as centrais
        """
        for elemento in self.lista_grupos_atividades.values():
            elemento.CalcularCentro()



def CentralMaisProxima(listaGruposCentral: Lista_Grupos_Central, competencias: list[str], lat: float, lon: float, listaCentraisExistentes: list[str], k: int) -> list[Activity]:
    """Adiciona recursivamente atividades ao cluster, até atingir a quantidade de atividades definidas

    Args:
        listaGruposCentral (Lista_Grupos_Central): lista com todas as atividades separadas por central
        competencias (list[str]): competencias do trabalhador
        lat (float): latitude do trabalhador
        lon (float): longitude do trabalhador
        central (list[str]): lista com os ids das centrais que já foram adicionadas
        k (int): quantidade de atividades

    Returns:
        list[Activity]: lista de atividades encontradas
    """

    if len(listaCentraisExistentes) < k:

        # lista de distancias vazia
        lista_distancias = []

        # percorrer o dicionário da classe
        for id, elemento in listaGruposCentral.lista_grupos_atividades.items():
            # se o id não estiver na lista das centrais  que já foram adicionadas
            if id not in listaCentraisExistentes: 
                distancia = Distance_Calculator(elemento.centro[0], elemento.centro[1], lat, lon)
                lista_distancias.append([id, distancia])
        
        # organiza a lista por ordem crescente (do menor para o maior) de acordo com a distancia
        lista_distancias = sorted(lista_distancias, key=lambda x: x[1])

        # id da central mais próxima
        primeiro_elemento = lista_distancias.pop(0)

        # lista de atividades da central mais próxima 
        lista = listaGruposCentral.PesquisarPorId(primeiro_elemento[0])

        # atividades da lsita com o state == 0 
        lista_atividades_estado_zero = [atividade for atividade in lista if atividade.state == 0 and atividade.competencia in competencias]
        # todo #1 

        if len(lista_atividades_estado_zero) < k:
            lista_atividades_estado_zero.extend(CentralMaisProxima(listaGruposCentral, lat, lon, central.append(primeiro_elemento[0]), k - len(lista_atividades_estado_zero))) # type: ignore
        
        return lista_atividades_estado_zero
    return []


def Opcao_Agrupamento_Por_Central(listaAtividades: list[Activity], listaTrabalhadores: list[Worker], listaBlocoTrabalho: list[WorkBlock], k_nearest_neighbors: int, dicionario_distancias: dict, competencias_dict: dict, valores_dict: dict, considerarAgendamento: bool, considerarPrioridade: bool, gmaps):
    """Faz a ateribuição de atividades por central

    Args:
        listaAtividades (list[Activity]): lista de todas as atividades
        listaTrabalhadores (list[Worker]): lista de todos os trabalhadores
        listaBlocoTrabalho (list[WorkBlock]): lista de todos os blocos de trabalho
        k_nearest_neighbors (int): quantidade de atividades para o clustering
        dicionario_distancias (dict): dicionário com os tempos de viagem já calculadas
        competencias_dict (dict): dicionário com as competencias, e o tempo de realização das atividades
        valores_dict (dict): dicionário com os valores de configuração
        considerarAgendamento (bool): bool com a opção de considerar tipo agendamento
        considerarPrioridade (bool): bool com a opção de considerar prioridade
        gmaps (_type_): _description_
    """

    # Print básico com a informação
    print('Quantidade Atividades:', len(listaAtividades), 'Trabalhadores:', len(listaTrabalhadores), 'BlocoTrabalho:', len(listaBlocoTrabalho), 'K_NEAREST_NEIGHBORS:', int(valores_dict['K_NEAREST_NEIGHBORS']))


    # Agrupa atividades por central
    listaGruposCentral = preencherListaCentral(listaAtividades)

    '''
        Fazer a atribuição para cada um dos blocos de trabalho
    '''

    for blocoTrabalho in listaBlocoTrabalho:

        # trabalhador do bloco de trabalho a ser atribuido
        trabalhador: Worker = Find_Worker_By_Id(listaTrabalhadores, blocoTrabalho.idWorker)
        
        # competencias do trabalhador
        competencias: list[str] = trabalhador.competencia
        
        # central do trabalhador
        central: str = trabalhador.idCentral

        # lista de atividades da central do trabalhador
        listaAtividadesGrupoCentral = listaGruposCentral.PesquisarPorId(central)

        # lista de atividades da central do trabalhador com o state == 0, e com uma competencia possuida pelo trabalhador
        atividades_estado_zero = [atividade for atividade in listaAtividadesGrupoCentral if atividade.state == 0 and atividade.competencia in competencias]


        if len(atividades_estado_zero) > k_nearest_neighbors:
            '''
                Se entrou aqui é porque na Central dele existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja não precisa de ir a outra central buscar mais atividades para complementar
            '''

            cluster = KNearest_Neighbors_Normal(atividades_estado_zero, competencias, blocoTrabalho, k_nearest_neighbors)



        else:
            '''
                Se entrou aqui é porque na Central dele não existem mais atividades do que as defenidas pelo utilizador para fazer a atribuição, ou seja precisa de ir a outra central buscar mais atividades para complementar
            '''
            
            # quantidade de atividades que lhe faltam
            k: int = k_nearest_neighbors - len(atividades_estado_zero)

            # vai buscar mais atividades a central mais próxima
            lista_extend = CentralMaisProxima(listaGruposCentral, competencias, blocoTrabalho.latitude, blocoTrabalho.longitude, [central], k)

            # junta as atividades encontradas as atividades que já tinhas
            atividades_estado_zero.extend(lista_extend)
            
            # como as atividades de cada central são todas adicionadas, pode acontecer de serem demasiadas, então tem de se diminuir, aqui usa se o KNN normal.
            cluster = KNearest_Neighbors_Normal(atividades_estado_zero, competencias, blocoTrabalho, k_nearest_neighbors)

        # chama o metodo de atribuição
        nodes = Greedy(cluster, listaTrabalhadores, blocoTrabalho, dicionario_distancias, competencias_dict, valores_dict, considerarAgendamento, considerarPrioridade, gmaps)

        # altera o estado das atividades para 1 (atribuidas)
        activitiesToState1(nodes, listaAtividades)

        # colocar todas as atividades que não têm o state igual a 1 a 0
        for activity in listaAtividades:
            activity.resetStateToZeroIfNotOne()
            
    return

def preencherListaCentral(listaAtividades: list[Activity]) -> Lista_Grupos_Central:
    """Agrupa as atividades por central

    Args:
        listaAtividades (list[Activity]): lista das atividades a serem agrupadas

    Returns:
        Lista_Grupos_Central: lista com as atividades já agrupadas
    """
    listaGruposCentral = Lista_Grupos_Central()
    for atividade in listaAtividades:
        listaGruposCentral.AdicionarGrupoId(atividade.idCentral, atividade)
    return listaGruposCentral