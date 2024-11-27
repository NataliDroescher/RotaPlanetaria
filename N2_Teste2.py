# Com varios caminhos
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import heapq
import time
import tracemalloc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

valid_planets = ["Mercúrio", "Vênus", "Terra", "Marte", "Júpiter", "Saturno", "Urano", "Netuno", "Estacao_Esp1", "Estacao_Esp2", "Estacao_Esp3"]

# Dicionario
distances = {
    ("Mercúrio", "Vênus"): 38,
    ("Mercúrio", "Terra"): 91,
    ("Mercúrio", "Marte"): 78,
    ("Mercúrio", "Júpiter"): 550,
    ("Mercúrio", "Saturno"): 1220,
    ("Mercúrio", "Urano"): 2600,
    ("Vênus", "Terra"): 42,
    ("Vênus", "Marte"): 61,
    ("Vênus", "Júpiter"): 520,
    ("Vênus", "Saturno"): 1130,
    ("Vênus", "Urano"): 2480,
    ("Terra", "Marte"): 78,
    ("Terra", "Júpiter"): 628,
    ("Terra", "Saturno"): 1270,
    ("Terra", "Urano"): 2720,
    ("Terra", "Netuno"): 4340,
    ("Marte", "Júpiter"): 558,
    ("Marte", "Saturno"): 1150,
    ("Marte", "Urano"): 2650,
    ("Júpiter", "Saturno"): 650,
    ("Júpiter", "Urano"): 1520,
    ("Júpiter", "Netuno"): 2380,
    ("Saturno", "Urano"): 870,
    ("Saturno", "Netuno"): 1420,
    ("Urano", "Netuno"): 2850,
    ("Estacao_Esp1", "Mercúrio"): 500,
    ("Estacao_Esp1", "Netuno"): 1000,
    ("Estacao_Esp2", "Marte"): 400,
    ("Estacao_Esp2", "Netuno"): 900,
    ("Estacao_Esp3", "Vênus"): 450,
    ("Estacao_Esp3", "Netuno"): 950,
}

planet_colors = {
    "Mercúrio": "#E1C699",
    "Vênus": "#F9E79F",
    "Terra": "#ADD8E6",
    "Marte": "#FFB6C1",
    "Júpiter": "#D2B48C",
    "Saturno": "#FDEBD0",
    "Urano": "#AFEEEE",
    "Netuno": "#87CEEB",
    "Estacao_Esp1": "#FFFFFF",
    "Estacao_Esp2": "#FFFFFF",
    "Estacao_Esp3": "#FFFFFF",
}

#Tamanho dos planetas
def get_node_sizes(vertices):
    node_sizes = []
    for vertex in vertices:
        if vertex in ["Mercúrio", "Vênus", "Terra", "Marte", "Júpiter", "Saturno", "Urano", "Netuno"]:
            node_sizes.append(6000) 
        else:
            node_sizes.append(4000) 
    return node_sizes

# Grafo como matriz
def initialize_adjacency_matrix(vertices):
    num_vertices = len(vertices)
    adj_matrix = np.full((num_vertices, num_vertices), float('inf')) 
    np.fill_diagonal(adj_matrix, 0) 
    return adj_matrix

def add_edge(adj_matrix, vertices, origem, destino, peso):
    i, j = vertices.index(origem), vertices.index(destino)
    adj_matrix[i][j] = peso
    adj_matrix[j][i] = peso
    
# Mostrar Matriz
def print_adjacency_matrix(adj_matrix, vertices):
   
    matrix_int = np.where(adj_matrix == float('inf'), 0, adj_matrix).astype(int)
    df = pd.DataFrame(matrix_int, index=vertices, columns=vertices)
    
    print("Matriz de adjacência ajustada:")
    print(df)

# Upload do CSV 
def upload_csv():
    global adj_matrix, vertices 
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path, delimiter=';')
            if 'Planeta' not in df.columns or 'Conexoes' not in df.columns:
                raise ValueError("O CSV deve conter as colunas: 'Planeta' e 'Conexoes'")   
           
            print("Dados lidos do CSV:\n", df.head())

            df.columns = ['Planeta', 'Conexoes']  
          
            vertices = list(set(df['Planeta'].tolist() + df['Conexoes'].tolist()))
            
            for planet in vertices:
                if planet not in valid_planets:
                    raise ValueError(f"Planeta inválido no CSV: {planet}")

            adj_matrix = initialize_adjacency_matrix(vertices)
           
            for index, row in df.iterrows():
                planet = row['Planeta']
                connections = row['Conexoes'].split(',')
                for connection in connections:
                    if connection in vertices:
                        if (planet, connection) in distances:
                            add_edge(adj_matrix, vertices, planet, connection, distances[(planet, connection)])
                        elif (connection, planet) in distances:
                            add_edge(adj_matrix, vertices, planet, connection, distances[(connection, planet)])

            print_adjacency_matrix(adj_matrix, vertices)

            populate_planet_options(vertices)
            
            plot_graph(vertices, adj_matrix)

            messagebox.showinfo("Sucesso", "Arquivo CSV carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo CSV: {str(e)}")

# Função para popular os planetas
def populate_planet_options(vertices):
    origin_menu['menu'].delete(0, 'end')
    destination_menu['menu'].delete(0, 'end')
    for planet in vertices:
        origin_menu['menu'].add_command(label=planet, command=tk._setit(origin_var, planet))
        destination_menu['menu'].add_command(label=planet, command=tk._setit(destination_var, planet))
    if vertices:
        origin_var.set(vertices[0])
        destination_var.set(vertices[0])

# Função para desenhar o grafo
def plot_graph(vertices, adj_matrix, path=None):
    fig.clear()
    fig.patch.set_visible(False)
    ax = fig.add_subplot(111, facecolor='#0d1b2a')    
    ax.axis('off')
    ax.grid(False)
    
    num_vertices = len(vertices)
    angle = np.linspace(0, 2 * np.pi, num_vertices, endpoint=False)
    positions = {vertices[i]: (np.cos(angle[i]), np.sin(angle[i])) for i in range(num_vertices)}
    
    node_colors = [planet_colors.get(vertex, "#FFFFFF") for vertex in vertices]  # Cor padrão branca
    node_sizes = get_node_sizes(vertices)

    for idx, (vertex, pos) in enumerate(positions.items()):
        ax.plot(pos[0], pos[1], 'o', markersize=node_sizes[idx] / 200, color=node_colors[idx])
        ax.text(pos[0], pos[1] + 0.1, vertex, fontsize=12, ha='center', color='white')
    
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if adj_matrix[i][j] < float('inf'): 
                x_values = [positions[vertices[i]][0], positions[vertices[j]][0]]
                y_values = [positions[vertices[i]][1], positions[vertices[j]][1]]
                
                ax.plot(x_values, y_values, 'gray', linestyle='-', linewidth=1.5)
                
                mid_x = (x_values[0] + x_values[1]) / 2
                mid_y = (y_values[0] + y_values[1]) / 2
                ax.text(mid_x, mid_y, str(int(adj_matrix[i][j])),  color="black", fontsize=10, ha='center',
                    bbox=dict(facecolor='gray', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'))
                
    if path:
        for k in range(len(path) - 1):
            origem = path[k]
            destino = path[k + 1]
            i, j = vertices.index(origem), vertices.index(destino)
            x_values = [positions[origem][0], positions[destino][0]]
            y_values = [positions[origem][1], positions[destino][1]]
            
            ax.plot(x_values, y_values, 'orange', linestyle='-', linewidth=3)
            
            ax.plot(positions[origem][0], positions[origem][1], 'o', markersize=18, color='orange')
            ax.plot(positions[destino][0], positions[destino][1], 'o', markersize=18, color='orange')
    
    canvas.draw()

#Função do tempo/Espaço
def medir_tempo(funcao, *args):
    tracemalloc.start() 
    inicio = time.time()
    
    resultado = funcao(*args)  
    
    fim = time.time()
    tempo_decorrido = fim - inicio
    
    memoria_atual, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    memoria_atual_kb = memoria_atual / 1024
    memoria_pico_kb = memoria_pico / 1024
    print(f"----------------{funcao.__name__} ---------------------")
    print(f"Tempo para {funcao.__name__}: {tempo_decorrido:.12f} segundos")
    print(f"Memória atual usada por {funcao.__name__}: {memoria_atual_kb:.2f} KB")
    print(f"Memória pico usada por {funcao.__name__}: {memoria_pico_kb:.2f} KB")
    print("-------------------------------------------")
    
    return resultado

def verificar_combustivel(caminhos, fuel_available):
    caminhos_viaveis = []
    mensagem_caminhos = []

    estacoes_espaciais = {"Estacao_Esp1", "Estacao_Esp2", "Estacao_Esp3"}  # Estações espaciais para reabastecimento

    for caminho, custo in caminhos:
        combustivel_restante = fuel_available
        estacoes_visitadas = set()

        for i in range(len(caminho) - 1):
            origem = caminho[i]
            destino = caminho[i + 1]
            peso = distances.get((origem, destino), distances.get((destino, origem), float('inf')))

           
            if origem in estacoes_espaciais and origem not in estacoes_visitadas:
                combustivel_restante += 1000  
                estacoes_visitadas.add(origem)
           
            combustivel_restante -= peso

            if combustivel_restante < 0:
                mensagem_caminhos.append(f"Caminho {' -> '.join(caminho)}: INVIÁVEL (Falta de combustível)")
                break
        else:
            mensagem_caminhos.append(f"Caminho {' -> '.join(caminho)}: Viável (Combustível restante: {combustivel_restante})")
            caminhos_viaveis.append((caminho, custo, combustivel_restante))  

    if not caminhos_viaveis:
        raise ValueError("Nenhum caminho viável devido à falta de combustível.")

    return caminhos_viaveis, mensagem_caminhos

# Busca em Largura
def bfs(adj_matrix, vertices, origem, destino):
    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    fila = deque([(origem_idx, [origem], 0)]) 
    caminhos = []

    while fila:
        atual, caminho, custo = fila.popleft()

        if atual == destino_idx:
            if (caminho, custo) not in caminhos: 
                caminhos.append((caminho, custo))
            continue

        for i, peso in enumerate(adj_matrix[atual]):
            if peso < float('inf') and vertices[i] not in caminho:
                fila.append((i, caminho + [vertices[i]], custo + peso))

    caminho_otimo = min(caminhos, key=lambda x: x[1])[0] if caminhos else None
    return caminhos, caminho_otimo

# Busca em Profundidade
def dfs(adj_matrix, vertices, origem, destino):
    origem_idx = vertices.index(origem)
    destino_idx = vertices.index(destino)
    caminhos = []

    def dfs_visit(atual, caminho, custo):
        if atual == destino_idx:
            if (caminho, custo) not in caminhos: 
                caminhos.append((caminho[:], custo))
            return

        for i, peso in enumerate(adj_matrix[atual]):
            if peso < float('inf') and vertices[i] not in caminho:
                dfs_visit(i, caminho + [vertices[i]], custo + peso)

    dfs_visit(origem_idx, [origem], 0)

    caminho_otimo = min(caminhos, key=lambda x: x[1])[0] if caminhos else None
    return caminhos, caminho_otimo

def dijkstra(adj_matrix, vertices, origem, destino):
    origem_idx = vertices.index(origem)
    destino_idx = vertices.index(destino)
    num_vertices = len(vertices)
    
    distancias = [float('inf')] * num_vertices
    distancias[origem_idx] = 0
    caminhos = {origem_idx: [[origem]]}
    fila_prioridade = [(0, origem_idx)]

    while fila_prioridade:
        distancia_atual, atual = heapq.heappop(fila_prioridade)

        for i in range(num_vertices):
            peso = adj_matrix[atual][i]
            if peso < float('inf'):  
                nova_distancia = distancia_atual + peso
                if nova_distancia < distancias[i]:
                    distancias[i] = nova_distancia
                    caminhos[i] = [caminho + [vertices[i]] for caminho in caminhos[atual]]
                    heapq.heappush(fila_prioridade, (nova_distancia, i))
                elif nova_distancia == distancias[i]:
                    novos_caminhos = [caminho + [vertices[i]] for caminho in caminhos[atual]]
                    
                    for novo_caminho in novos_caminhos:
                        if novo_caminho not in caminhos[i]:
                            caminhos[i].append(novo_caminho)

    caminhos_destino = [(caminho, distancias[destino_idx]) for caminho in caminhos.get(destino_idx, [])]
    caminho_otimo = min(caminhos_destino, key=lambda x: x[1])[0] if caminhos_destino else None

    return caminhos_destino, caminho_otimo

def floyd_warshall(adj_matrix, vertices, origem, destino):
    num_vertices = len(vertices)
    dist = np.array(adj_matrix)
    next_vertex = [[None if i == j or adj_matrix[i][j] == float('inf') else j for j in range(num_vertices)] for i in range(num_vertices)]

    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_vertex[i][j] = next_vertex[i][k]

    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    if next_vertex[origem_idx][destino_idx] is None:
        return [], None 

    def reconstruct_path(i, j):
        if next_vertex[i][j] is None:
            return None
        path = [vertices[i]]
        while i != j:
            i = next_vertex[i][j]
            path.append(vertices[i])
        return path

    caminho_otimo = reconstruct_path(origem_idx, destino_idx)
    caminhos = [(caminho_otimo, dist[origem_idx, destino_idx])] if caminho_otimo else []

    return caminhos, caminho_otimo

def bellman_ford(adj_matrix, vertices, origem, destino):
    origem_idx = vertices.index(origem)
    destino_idx = vertices.index(destino)
    num_vertices = len(vertices)

    distancias = [float('inf')] * num_vertices
    distancias[origem_idx] = 0
    caminhos = {origem_idx: [[origem]]}  

    for _ in range(num_vertices - 1):
        for i in range(num_vertices):
            for j in range(num_vertices):
                peso = adj_matrix[i][j]
                if peso < float('inf') and distancias[i] + peso < distancias[j]:
                    distancias[j] = distancias[i] + peso
                    caminhos[j] = [caminho + [vertices[j]] for caminho in caminhos[i]]
                elif peso < float('inf') and distancias[i] + peso == distancias[j]:
                    novos_caminhos = [caminho + [vertices[j]] for caminho in caminhos[i]]
                    
                    for novo_caminho in novos_caminhos:
                        if novo_caminho not in caminhos[j]:
                            caminhos[j].append(novo_caminho)

    for i in range(num_vertices):
        for j in range(num_vertices):
            peso = adj_matrix[i][j]
            if peso < float('inf') and distancias[i] + peso < distancias[j]:
                messagebox.showerror("Erro", "O grafo contém um ciclo de peso negativo.")
                return [], None

    caminhos_destino = [(caminho, distancias[destino_idx]) for caminho in caminhos.get(destino_idx, [])]
    caminho_otimo = min(caminhos_destino, key=lambda x: x[1])[0] if caminhos_destino else None

    return caminhos_destino, caminho_otimo

# Função verifica o caminho
def show_search_path(path):
    travel_info_text.delete(1.0, tk.END)
    if path:
        path_str = " -> ".join(map(str, path))
        travel_info_text.insert(tk.END, path_str)
    else:
        travel_info_text.insert(tk.END, "Não há caminho entre os vértices informados.")

def find_path():    

    origem = origin_var.get()
    destino = destination_var.get()
    algorithm = algorithm_var.get()
    month = month_var.get()
    
    try:
        fuel_available = float(fuel_var.get())  # Combustível inicial
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um valor válido de combustível.")
        return

    caminhos = []
    caminho_otimo = None

    if origem and destino and algorithm:
        if algorithm == "Busca em Largura":
            caminhos, caminho_otimo = medir_tempo(bfs, adj_matrix, vertices, origem, destino)
        elif algorithm == "Busca em Profundidade":
            caminhos, caminho_otimo = medir_tempo(dfs, adj_matrix, vertices, origem, destino)
        elif algorithm == "Dijkstra":
            caminhos, caminho_otimo = medir_tempo(dijkstra, adj_matrix, vertices, origem, destino)
        elif algorithm == "Floyd-Warshall":
            caminhos, caminho_otimo = medir_tempo(floyd_warshall, adj_matrix, vertices, origem, destino)
        elif algorithm == "Bellman-Ford":
            caminhos, caminho_otimo = medir_tempo(bellman_ford, adj_matrix, vertices, origem, destino)
        else:
            messagebox.showerror("Erro", "Algoritmo inválido")
            return
        
         # Aplicar as regras específicas
        if destino == "Vênus" and month == "dezembro":
            travel_info_text.insert(tk.END, "Viagem para Vênus cancelada devido a uma tempestade solar em dezembro.\n")
            
            plot_graph(vertices, adj_matrix)  # Desenha o grafo sem caminhos destacados
            return

        if destino == "Saturno" and month not in ["janeiro", "março", "junho"]:
            travel_info_text.insert(tk.END, "Atenção: Chuvas de meteoros esperadas em Saturno fora de janeiro, março e junho.\n")
            proceed = messagebox.askyesno("Aviso", "Deseja continuar a viagem?")
            if not proceed:
                travel_info_text.insert(tk.END, "Viagem cancelada pelo usuário devido às condições meteorológicas.\n")
                plot_graph(vertices, adj_matrix)
                return

        if destino == "Marte" and month in ["dezembro", "fevereiro", "agosto"]:
            travel_info_text.insert(tk.END, "Aviso: Tempestades de areia intensas esperadas em Marte nos meses de dezembro, fevereiro e agosto.\n")
            fuel_available -= 200  # Penalidade de combustível

        if origem == "Terra" and destino == "Júpiter" and month in ["maio", "junho", "outubro"]:
            travel_info_text.insert(tk.END, "Alinhamento planetário favorecido! Redução no consumo de combustível.\n")
            fuel_available += 30  # Bônus de combustível

        if destino == "Netuno" and month in ["janeiro", "abril"]:
            travel_info_text.insert(tk.END, "Viagem para Netuno cancelada devido aos ventos mais rápidos do sistema solar em janeiro e abril.\n")
            plot_graph(vertices, adj_matrix)
            return

        # Uso de slingshot
        if "Júpiter" in caminho_otimo or "Saturno" in caminho_otimo:
            travel_info_text.insert(tk.END, "Gravidade de Júpiter ou Saturno usada para slingshot! Combustível aumentado.\n")
            fuel_available += 300

        
        try:
            # Verificar os caminhos com base no combustível
            caminhos_viaveis, mensagem_caminhos = verificar_combustivel(caminhos, fuel_available)            

            # Exibe todos os caminhos no `textbox`
            travel_info_text.delete(1.0, tk.END)
            travel_info_text.insert(tk.END, "\n".join(mensagem_caminhos) + "\n")

            # Se houver caminhos viáveis, desenhar o caminho ótimo
            if caminhos_viaveis:
                melhor_caminho, custo_otimo, combustivel_restante = min(caminhos_viaveis, key=lambda x: x[1])
           
                travel_info_text.insert(tk.END, f"\nCaminho Ótimo: {' -> '.join(melhor_caminho)}\n")
                travel_info_text.insert(tk.END, f"Gasto Total de Combustível: {custo_otimo}\n")
                travel_info_text.insert(tk.END, f"Combustível Restante: {combustivel_restante}\n")
                plot_graph(vertices, adj_matrix, melhor_caminho)  # Desenhar apenas o ótimo
            else:
                # Se nenhum caminho viável, exibir alerta e não destacar caminhos no gráfico
                plot_graph(vertices, adj_matrix)  # Desenha o grafo sem caminhos destacados
                messagebox.showwarning("Atenção", "Nenhum caminho viável com o combustível disponível.")

        except ValueError as e:
            # Mostrar erro se nenhum caminho for possível
            travel_info_text.delete(1.0, tk.END)
            travel_info_text.insert(tk.END, str(e))
            plot_graph(vertices, adj_matrix)  # Desenha o grafo sem caminhos destacados
            messagebox.showerror("Erro", str(e))
    else:
        messagebox.showerror("Erro", "Por favor, selecione origem, destino e o algoritmo de busca.")


# Interface Tkinter
window = tk.Tk()
window.title("Planejamento de Rotas Interplanetárias")

origin_var = tk.StringVar(window)
destination_var = tk.StringVar(window)
algorithm_var = tk.StringVar(window)
fuel_var = tk.StringVar(window)
month_var = tk.StringVar(window)
month_var.set("janeiro")  # Valor padrão do mês

frame_top_controls = tk.Frame(window)
frame_top_controls.grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky='ew')

btn_upload = tk.Button(frame_top_controls, text="Carregar CSV", command=upload_csv)
btn_upload.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

fuel_label = tk.Label(frame_top_controls, text="Combustível disponível:")
fuel_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

fuel_entry = tk.Entry(frame_top_controls, textvariable=fuel_var)
fuel_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')

month_label = tk.Label(frame_top_controls, text="Mês da viagem:")
month_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')

month_menu = ttk.OptionMenu(frame_top_controls, month_var, "janeiro", 
                            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
                            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
month_menu.grid(row=0, column=4, padx=5, pady=5, sticky='w')

origin_label = tk.Label(frame_top_controls, text="Origem:")
origin_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')

origin_menu = ttk.OptionMenu(frame_top_controls, origin_var, "")
origin_menu.grid(row=0, column=6, padx=5, pady=5, sticky='w')

destination_label = tk.Label(frame_top_controls, text="Destino:")
destination_label.grid(row=0, column=7, padx=5, pady=5, sticky='w')

destination_menu = ttk.OptionMenu(frame_top_controls, destination_var, "")
destination_menu.grid(row=0, column=8, padx=5, pady=5, sticky='w')

algorithm_label = tk.Label(frame_top_controls, text="Algoritmo:")
algorithm_label.grid(row=0, column=9, padx=5, pady=5, sticky='w')

algorithm_menu = ttk.OptionMenu(frame_top_controls, algorithm_var, "Busca em Largura", 
                                "Busca em Largura", "Busca em Profundidade", 
                                "Dijkstra", "Floyd-Warshall", "Bellman-Ford")
algorithm_menu.grid(row=0, column=10, padx=5, pady=5, sticky='w')

btn_find_path = tk.Button(frame_top_controls, text="Encontrar Caminho", command=find_path)
btn_find_path.grid(row=0, column=11, padx=5, pady=5, sticky='ew')

travel_info_text = tk.Text(window, height=5, width=50)
travel_info_text.grid(row=2, column=0, columnspan=10, padx=10, pady=5, sticky='w')

frame_graph = tk.Frame(window)
frame_graph.grid(row=3, column=0, columnspan=10, padx=10, pady=10, sticky='nsew')

fig = plt.Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().config(bg='#0d1b2a') # Definir o fundo de onde aparece o grafo
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

window.mainloop()
