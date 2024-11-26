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

    for vertex, pos in positions.items():
        ax.plot(pos[0], pos[1], 'o', markersize=15, color='skyblue')
        ax.text(pos[0], pos[1], vertex, fontsize=12, ha='center', color='white')
    
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if adj_matrix[i][j] < float('inf'): 
                x_values = [positions[vertices[i]][0], positions[vertices[j]][0]]
                y_values = [positions[vertices[i]][1], positions[vertices[j]][1]]
                
                ax.plot(x_values, y_values, 'gray', linestyle='-', linewidth=1.5)
                
                mid_x = (x_values[0] + x_values[1]) / 2
                mid_y = (y_values[0] + y_values[1]) / 2
                ax.text(mid_x, mid_y, str(int(adj_matrix[i][j])), color="yellow", fontsize=10, ha='center')

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


# Busca em Largura
def bfs(adj_matrix, vertices, origem, destino):
    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    fila = deque([(origem_idx, [origem], 0)])  
    caminhos = []

    while fila:
        atual, caminho, custo = fila.popleft()

        if atual == destino_idx:
            caminhos.append((caminho, custo))
            continue

        for i, peso in enumerate(adj_matrix[atual]):
            if peso < float('inf') and vertices[i] not in caminho:
                fila.append((i, caminho + [vertices[i]], custo + peso))

    caminho_otimo = min(caminhos, key=lambda x: x[1])[0] if caminhos else None
    return caminhos, caminho_otimo  


def dfs(adj_matrix, vertices, origem, destino):
    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    caminhos = []

    def dfs_visit(atual, caminho, custo):
        if atual == destino_idx:
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
                    caminhos[i].extend([caminho + [vertices[i]] for caminho in caminhos[atual]])

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
                 
                    if j not in caminhos:
                        caminhos[j] = []
                    caminhos[j] = [caminho + [vertices[j]] for caminho in caminhos[i]]
                elif peso < float('inf') and distancias[i] + peso == distancias[j]:
                    if j not in caminhos:
                        caminhos[j] = []
                    caminhos[j].extend([caminho + [vertices[j]] for caminho in caminhos[i]])

    for i in range(num_vertices):
        for j in range(num_vertices):
            peso = adj_matrix[i][j]
            if peso < float('inf') and distancias[i] + peso < distancias[j]:
                messagebox.showerror("Erro", "O grafo contém um ciclo de peso negativo.")
                return [], None

    # Recupera todos os caminhos para o destino e identifica o caminho ótimo
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

        # Exibe todos os caminhos
        travel_info_text.delete(1.0, tk.END)
        if caminhos:
            for i, (path, custo) in enumerate(caminhos, 1):
                travel_info_text.insert(tk.END, f"Caminho {i}: {' -> '.join(path)} (Custo: {custo})\n")
            # Destaca o caminho ótimo
            travel_info_text.insert(tk.END, f"\nCaminho Ótimo: {' -> '.join(caminho_otimo)}\n")
            plot_graph(vertices, adj_matrix, caminho_otimo)
        else:
            travel_info_text.insert(tk.END, "Não há caminho entre os vértices informados.")
    else:
        messagebox.showerror("Erro", "Por favor, selecione origem, destino e o algoritmo de busca.")

# Interface Tkinter
window = tk.Tk()
window.title("Planejamento de Rotas Interplanetárias")

origin_var = tk.StringVar(window)
destination_var = tk.StringVar(window)
algorithm_var = tk.StringVar(window)

frame_top_controls = tk.Frame(window)
frame_top_controls.grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky='ew')

btn_upload = tk.Button(frame_top_controls, text="Carregar CSV", command=upload_csv)
btn_upload.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

origin_label = tk.Label(frame_top_controls, text="Origem:")
origin_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

origin_menu = ttk.OptionMenu(frame_top_controls, origin_var, "")
origin_menu.grid(row=0, column=2, padx=5, pady=5, sticky='w')

destination_label = tk.Label(frame_top_controls, text="Destino:")
destination_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')

destination_menu = ttk.OptionMenu(frame_top_controls, destination_var, "")
destination_menu.grid(row=0, column=4, padx=5, pady=5, sticky='w')

algorithm_label = tk.Label(frame_top_controls, text="Algoritmo:")
algorithm_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')

algorithm_menu = ttk.OptionMenu(frame_top_controls, algorithm_var, "Busca em Largura", 
                                "Busca em Largura", "Busca em Profundidade", 
                                "Dijkstra", "Floyd-Warshall", "Bellman-Ford")
algorithm_menu.grid(row=0, column=6, padx=5, pady=5, sticky='w')

btn_find_path = tk.Button(frame_top_controls, text="Encontrar Caminho", command=find_path)
btn_find_path.grid(row=0, column=7, padx=5, pady=5, sticky='ew')

travel_info_text = tk.Text(window, height=5, width=50)
travel_info_text.grid(row=2, column=0, columnspan=10, padx=10, pady=5, sticky='w')

frame_graph = tk.Frame(window)
frame_graph.grid(row=3, column=0, columnspan=10, padx=10, pady=10, sticky='nsew')

fig = plt.Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().config(bg='#0d1b2a') # Definir o fundo de onde aparece o grafo
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

window.mainloop()
