# Com apenas um caminho
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import heapq
import time
import tracemalloc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    print(f"--------------{funcao.__name__} -------------------")
    print(f"Tempo para {funcao.__name__}: {tempo_decorrido:.12f} segundos")
    print(f"Memória atual usada por {funcao.__name__}: {memoria_atual_kb:.2f} KB")
    print(f"Memória pico usada por {funcao.__name__}: {memoria_pico_kb:.2f} KB")
    print("---------------------------------------------")
    
    return resultado

# Busca em largura
def bfs(adj_matrix, vertices, origem, destino):
    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    visitados = [False] * len(vertices)
    fila = [(origem_idx, [origem])]

    while fila:
        atual, caminho = fila.pop(0)
        if atual == destino_idx:
            return caminho

        visitados[atual] = True
        for i, peso in enumerate(adj_matrix[atual]):
            if peso < float('inf') and not visitados[i]:
                fila.append((i, caminho + [vertices[i]]))

    return None

# Busca em profundidade
def dfs(adj_matrix, vertices, origem, destino):
    origem_idx, destino_idx = vertices.index(origem), vertices.index(destino)
    visitados = [False] * len(vertices)
    caminho = []

    def dfs_visit(atual):
        if visitados[atual]:
            return False
        visitados[atual] = True
        caminho.append(vertices[atual])
        
        if atual == destino_idx:
            return True

        for i, peso in enumerate(adj_matrix[atual]):
            if peso < float('inf') and not visitados[i]:
                if dfs_visit(i): 
                    return True

        caminho.pop()  
        return False

    dfs_visit(origem_idx)
    return caminho if caminho and caminho[-1] == destino else None

# Algoritmo de Dijkstra
def dijkstra(adj_matrix, vertices, origem, destino):
    origem_idx = vertices.index(origem)
    destino_idx = vertices.index(destino)
    num_vertices = len(vertices)
    
    distancias = [float('inf')] * num_vertices
    distancias[origem_idx] = 0
    antecessores = [None] * num_vertices
    fila_prioridade = [(0, origem_idx)]  
    
    while fila_prioridade:
        distancia_atual, atual = heapq.heappop(fila_prioridade)
    
        if atual == destino_idx:
            break

        for i in range(num_vertices):
            peso = adj_matrix[atual][i]
            if peso < float('inf'): 
                nova_distancia = distancia_atual + peso
                if nova_distancia < distancias[i]:
                    distancias[i] = nova_distancia
                    antecessores[i] = atual
                    heapq.heappush(fila_prioridade, (nova_distancia, i))
    caminho = []
    atual = destino_idx
    while atual is not None:
        caminho.insert(0, vertices[atual])
        atual = antecessores[atual]

    return caminho if caminho and caminho[0] == origem else None

# Algoritmo de Floyd-Warshall
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
        return None 
    
    caminho = []
    atual = origem_idx
    while atual != destino_idx:
        caminho.append(vertices[atual])
        atual = next_vertex[atual][destino_idx]
    caminho.append(vertices[destino_idx])

    return caminho

# Algoritmo de bellman-ford
def bellman_ford(adj_matrix, vertices, origem, destino):
    origem_idx = vertices.index(origem)
    destino_idx = vertices.index(destino)
    num_vertices = len(vertices)
    
    distancias = [float('inf')] * num_vertices
    distancias[origem_idx] = 0
    antecessores = [None] * num_vertices

    for _ in range(num_vertices - 1):
        for i in range(num_vertices):
            for j in range(num_vertices):
                peso = adj_matrix[i][j]
                if peso < float('inf') and distancias[i] != float('inf') and distancias[i] + peso < distancias[j]:
                    distancias[j] = distancias[i] + peso
                    antecessores[j] = i
    for i in range(num_vertices):
        for j in range(num_vertices):
            peso = adj_matrix[i][j]
            if peso < float('inf') and distancias[i] != float('inf') and distancias[i] + peso < distancias[j]:
                messagebox.showerror("Erro", "O grafo contém um ciclo de peso negativo.")
                return []

    caminho = []
    atual = destino_idx
    while atual is not None:
        caminho.insert(0, vertices[atual])
        atual = antecessores[atual]
        
    if caminho and caminho[0] == origem:
        return caminho
    else:
        return None

# Função verifica o caminho
def show_search_path(path):
    travel_info_text.delete(1.0, tk.END)
    if path:
        travel_info_text.insert(tk.END, " -> ".join(path))
    else:
        travel_info_text.insert(tk.END, "Não há caminho entre os vértices informados.")

# Função caminhos
def find_path():
    origin = origin_var.get()
    destination = destination_var.get()
    algorithm = algorithm_var.get()

    if origin and destination and algorithm:
        if algorithm == "Busca em Largura":
            path = medir_tempo(bfs, adj_matrix, vertices, origin, destination)
        elif algorithm == "Busca em Profundidade":
            path = medir_tempo(dfs, adj_matrix, vertices, origin, destination)
        elif algorithm == "Dijkstra":
            path = medir_tempo(dijkstra, adj_matrix, vertices, origin, destination)
        elif algorithm == "Floyd-Warshall":
            path = medir_tempo(floyd_warshall, adj_matrix, vertices, origin, destination)
        elif algorithm == "Bellman-Ford":
            path = medir_tempo(bellman_ford, adj_matrix, vertices, origin, destination)
        else:
            messagebox.showerror("Erro", "Algoritmo inválido")
            return

        # Mostra o caminho encontrado e desenha o grafo atualizado
        show_search_path(path)
        plot_graph(vertices, adj_matrix, path)
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
