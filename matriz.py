import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Planetas e Estações Válidas
valid_planets = ["Mercúrio", "Vênus", "Terra", "Marte", "Júpiter", "Saturno", "Urano", "Netuno", "Estacao_Esp1", "Estacao_Esp2", "Estacao_Esp3"]

meses_do_ano = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

# Distâncias predefinidas entre planetas e estações espaciais
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

# Inicializando grafo vazio com NetworkX
G = nx.Graph()

# Função para inicializar a matriz de adjacência
def initialize_adjacency_matrix(vertices):
    num_vertices = len(vertices)
    adj_matrix = np.zeros((num_vertices, num_vertices))
    return adj_matrix

# Função para garantir que a matriz tenha no mínimo 20% de preenchimento
def ensure_20_percent_fill(adj_matrix):
    num_vertices = adj_matrix.shape[0]
    total_possible_edges = num_vertices * (num_vertices - 1) / 2  # A matriz é simétrica
    min_edges = int(0.2 * total_possible_edges)  # Pelo menos 20% de preenchimento
    filled_edges = np.count_nonzero(adj_matrix) / 2  # Contar arestas diferentes de zero (a matriz é simétrica)

    if filled_edges < min_edges:
        while filled_edges < min_edges:
            u, v = np.random.choice(num_vertices, size=2, replace=False)
            if adj_matrix[u, v] == 0:
                adj_matrix[u, v] = np.random.randint(1, 100)  # Peso maior que zero
                adj_matrix[v, u] = adj_matrix[u, v]  # Simetria
                filled_edges += 1

# Função para carregar o CSV e criar a matriz de adjacência
def upload_csv():
    global adj_matrix, vertices  # Tornar as variáveis globais para uso em outras funções
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path, delimiter=';')
            if 'Planeta' not in df.columns or 'Conexoes' not in df.columns:
                raise ValueError("O CSV deve conter as colunas: 'Planeta' e 'Conexoes'")
            
            df.columns = ['Planeta', 'Conexoes']  # Renomear as colunas para o formato esperado

            vertices = list(set(df['Planeta'].tolist() + df['Conexoes'].tolist()))  # Usar planetas e conexões como vértices únicos
            
            # Verificar se todos os planetas são válidos
            for planet in vertices:
                if planet not in valid_planets:
                    raise ValueError(f"Planeta inválido no CSV: {planet}")
            
            adj_matrix = initialize_adjacency_matrix(vertices)
            
            for index, row in df.iterrows():
                planet = row['Planeta']
                connections = row['Conexoes'].split(',')
                planet_idx = vertices.index(planet)
                for connection in connections:
                    if connection in valid_planets:
                        connection_idx = vertices.index(connection)
                        if planet_idx < len(vertices) and connection_idx < len(vertices):
                            # Atualizar matriz de adjacência com as distâncias predefinidas
                            if (planet, connection) in distances:
                                adj_matrix[planet_idx, connection_idx] = distances[(planet, connection)]
                                adj_matrix[connection_idx, planet_idx] = distances[(planet, connection)]  # Garantir simetria
                            elif (connection, planet) in distances:
                                adj_matrix[planet_idx, connection_idx] = distances[(connection, planet)]
                                adj_matrix[connection_idx, planet_idx] = distances[(connection, planet)]  # Garantir simetria
            
            ensure_20_percent_fill(adj_matrix)   # Garantir 20% de preenchimento da matriz

            # Atualizar o grafo com a matriz de adjacência preenchida
            update_graph(adj_matrix, vertices)
            populate_planet_options(vertices)
            print(f"Planeta: {planet}, Conexoes: {connections}")
            print(f"Matriz de adjacência atual: \n{adj_matrix}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo CSV: {str(e)}")
            print(f"Planeta: {planet}, Conexoes: {connections}")
            print(f"Matriz de adjacência atual: \n{adj_matrix}")

# Função para calcular as posições normalizadas dos planetas
def calculate_positions(vertices):
    pos = nx.spring_layout(G, seed=42, k=5, iterations=50) 
    central_planet = "Terra"  # Colocar a Terra no centro
    if central_planet in vertices:
        pos[central_planet] = np.array([0, 0])

    scale = 1.5  # Aumente o fator de escala para mais espaçamento
    angle_step = 2 * np.pi / len(vertices)  # Dividir 360 graus entre os planetas
    angle = 0

    for planet in vertices:
        if planet == central_planet:
            continue
        
        distance = None
        if (central_planet, planet) in distances:
            distance = distances[(central_planet, planet)]
        elif (planet, central_planet) in distances:
            distance = distances[(planet, central_planet)]

        if distance is not None:
            normalized_distance = np.log1p(distance)
            pos[planet] = np.array([np.cos(angle), np.sin(angle)]) * normalized_distance * scale
            angle += angle_step * 1.5
    
    # Posições manuais das estações espaciais se elas estiverem na lista de vértices
    if "Estacao_Esp1" in vertices:
        pos["Estacao_Esp1"] = np.array([3.2, -5])
    if "Estacao_Esp2" in vertices:
        pos["Estacao_Esp2"] = np.array([2.5, -2])
    if "Estacao_Esp3" in vertices:
        pos["Estacao_Esp3"] = np.array([4.5, -2])

    return pos

# Função para definir o tamanho dos nós (planetas maiores, estações menores)
def get_node_sizes(vertices):
    node_sizes = []
    for node in vertices:
        if node in ["Mercúrio", "Vênus", "Terra", "Marte", "Júpiter", "Saturno", "Urano", "Netuno"]:
            node_sizes.append(2000)  # Planetas maiores
        else:
            node_sizes.append(1000)  # Estações menores
    return node_sizes

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

# Função para atualizar o grafo visualmente com base na matriz de adjacência
def update_graph(adj_matrix, vertices):
    fig.clear()
    
    fig.patch.set_visible(False)  # Remover borda externa
    ax = fig.add_subplot(111, facecolor='#0d1b2a')  # Fundo escuro
    
    ax.grid(False)
    
    G.clear()  # Limpar grafo atual
    G.add_nodes_from(vertices)  # Adicionar vértices do CSV

    # Adicionar arestas e pesos do CSV a partir da matriz de adjacência
    for i, planet1 in enumerate(vertices):
        for j, planet2 in enumerate(vertices):
            if adj_matrix[i, j] > 0:
                G.add_edge(planet1, planet2, weight=adj_matrix[i, j])

    pos = calculate_positions(vertices)  # Calcular as posições
    node_colors = [planet_colors.get(node, "#FFFFFF") for node in vertices]  # Cores dos planetas
    node_sizes = get_node_sizes(vertices)  # Tamanhos dos nós

    # Desenhar grafo com as novas posições, cores e tamanhos
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes, edge_color='gray', ax=ax, font_size=10, font_color='black')
    
    # Desenhar pesos das arestas
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v}" for k, v in labels.items()}, ax=ax, font_color='gray')

    canvas.draw()

# Função para popular as opções de planetas
def populate_planet_options(vertices):
    if not vertices:
        vertices = ["Nenhuma"]
    stopover_planet_list = ["Nenhuma"] + vertices
    
    origin_menu['menu'].delete(0, 'end')
    destination_menu['menu'].delete(0, 'end')
    stopover_menu['menu'].delete(0, 'end')
    
    for planet in vertices:
        origin_menu['menu'].add_command(label=planet, command=tk._setit(origin_var, planet))
        destination_menu['menu'].add_command(label=planet, command=tk._setit(destination_var, planet))
    
    for planet in stopover_planet_list:
        stopover_menu['menu'].add_command(label=planet, command=tk._setit(stopover_var, planet))
    
    if vertices[0] != "Nenhuma":
        origin_var.set(vertices[0])
        destination_var.set(vertices[0])
        stopover_var.set("Nenhuma")
    else:
        origin_var.set("")
        destination_var.set("")
        stopover_var.set("Nenhuma")

# Função para calcular o caminho mais curto (baseada na matriz de adjacência)
def show_shortest_path():
    origin = origin_var.get()
    destination = destination_var.get()
    stopover = stopover_var.get()  
    fuel_available = fuel_var.get()  
    month = month_var.get()  

    travel_info_text.delete(1.0, tk.END)

    try:
        fuel_available = float(fuel_available)  
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira uma quantidade válida de combustível.")
        return

    # Verificação se a origem, destino, e mês são válidos
    if origin and destination and origin in G and destination in G and month in meses_do_ano:
        try:
            update_graph(adj_matrix, vertices)

            # Regra para cancelar a viagem se o destino for Vênus em dezembro
            if destination == "Vênus" and month == "dezembro":
                travel_info_text.insert(tk.END, "Devido a uma tempestade solar prevista para Dezembro, a viagem para Vênus foi adiada para evitar danos à nave.\n")
                return  # Interrompe a viagem, não prossegue

         
           # Regra 1: Viagens para Vênus (Chuvas de meteoros ocorrem fora messes em janeiro, março, junho)
            if destination == "Saturno" and month not in ["janeiro", "março", "junho"]:
                
                proceed = messagebox.askyesno("Aviso", "Viagens para Vênus fora de janeiro, março ou junho podem sofrer chuvas de meteoros.\nDeseja continuar com a viagem?")
                travel_info_text.insert(tk.END, "Ops parece que você escolheu viajar da mesmo com chuva de meteoros, você perder 150 de combustivel.\n")
                fuel_available -= 150 
                if not proceed:
                    travel_info_text.insert(tk.END, "Viagem cancelada devido às condições meteorológicas em Saturno.\n")
                    return  

            # Regra 2: Evitar viagens para Marte em dezembro, fevereiro, agosto
            if destination == "Marte" and month in ["dezembro", "fevereiro", "agosto"]:
                messagebox.showwarning("Aviso", "Viagens para Marte em dezembro, fevereiro ou agosto podem enfrentar tempestades de areia, podendo reduzir drasticamente a visibilidade e afetar operações de pouso.")
                travel_info_text.insert(tk.END, "Ops parece que você escolheu viajar da mesmo com a tempestade você vai perder 200 de combustivel, pois a tempestade foi intensa.\n")
                fuel_available -= 200  
                if not proceed:
                   
                    travel_info_text.insert(tk.END, "Viagem cancelada devido às condições meteorológicas em Marte.\n")
                    return  
                                
            # Regra 3: Alinhamento planetário entre Terra e Júpiter (menor consumo de combustível em maio, junho, outubro)
            if origin == "Terra" and destination == "Júpiter" and month in ["maio", "junho", "outubro"]:
                travel_info_text.insert(tk.END, "Viagem facilitada pelo alinhamento planetário! Menor consumo de combustível.\n")
                fuel_available += 30 
            
             # Regra 4: Viagens a Netuno nos messes de janeiro a abril, não podem ocorrer)
            if destination == "Netuno" and month in ["janeiro", "abril"]:
                messagebox.showwarning("Aviso", "Viagens para Neturno em jeneiro e Abril podem enfrentar fortes ventos, são os ventos mais rapidos do sistema solar! Por tanto não pode ocorrer.")
                travel_info_text.insert(tk.END, "Viagem cancelada devido às condições meteorológicas em Neturno.\n")
                return 

            # Regra 5: Verificar se há parada em Júpiter ou Saturno para aplicar "slingshot"
            if stopover == "Júpiter" or stopover == "Saturno":
                travel_info_text.insert(tk.END, "Usar a gravidade de Júpiter ou Saturno para um 'slingshot', diminuindo o consumo de combustível.\n")
                fuel_available += 300              

           
            if stopover and stopover != "Nenhuma" and stopover in G:
                
                path1 = nx.shortest_path(G, source=origin, target=stopover, weight='weight')
                path2 = nx.shortest_path(G, source=stopover, target=destination, weight='weight')
                full_path = path1[:-1] + path2 
            else:
              
                full_path = nx.shortest_path(G, source=origin, target=destination, weight='weight')

            full_path_edges = list(zip(full_path, full_path[1:]))

            total_distance = 0  

            
            travel_info_text.insert(tk.END, f"Viagem de {origin} para {destination}:\n")
            travel_info_text.insert(tk.END, f"Combustível inicial: {fuel_available} unidades\n")
            
            estacoes_espaciais = {"Estacao_Esp1", "Estacao_Esp2", "Estacao_Esp3"}
            estacoes_visitadas = set() 

            for edge in full_path_edges:
                # Verificar se o caminho passa por uma estação espacial e se ela já não foi visitada
                if (edge[0] in estacoes_espaciais and edge[0] not in estacoes_visitadas) or \
                (edge[1] in estacoes_espaciais and edge[1] not in estacoes_visitadas):
                    estacao_espacial = edge[0] if edge[0] in estacoes_espaciais else edge[1]
                    fuel_available += 1000  # Recarregar combustível ao passar pela estação espacial
                    estacoes_visitadas.add(estacao_espacial)  # Marcar a estação espacial como visitada
                    travel_info_text.insert(tk.END, f"Reabastecimento em estação espacial: {estacao_espacial}. Novo combustível: {fuel_available}\n")

                # Calcular a distância para a próxima etapa
                distance = distances.get(edge, distances.get((edge[1], edge[0]), 0))
                total_distance += distance
                fuel_available -= distance  # Reduzir o combustível disponível com base na distância percorrida

                # Mostrar a etapa atual no campo de texto
                travel_info_text.insert(tk.END, f"De {edge[0]} para {edge[1]}: {distance} km. Combustível restante: {fuel_available} unidades\n")

                # Verificar se o combustível é suficiente para a próxima etapa
                if fuel_available < 0:
                    messagebox.showerror("Erro", f"Não é possível completar a viagem. Combustível insuficiente após {edge[0]} ou {edge[1]}.")
                    travel_info_text.insert(tk.END, "Viagem interrompida por falta de combustível.\n")
                    return

            pos = calculate_positions(vertices)  # Posições recalculadas
            nx.draw_networkx_edges(G, pos, edgelist=full_path_edges, edge_color='red', width=3, ax=fig.axes[0])

            # Exibir a distância total percorrida e combustível final
            travel_info_text.insert(tk.END, f"Viagem concluída!\nDistância total: {total_distance} km\nCombustível restante: {fuel_available} unidades\n")
            travel_info_text.insert(tk.END, f"-------------------------------------------------")

            # Atualizar o canvas com o caminho destacado
            canvas.draw()
          
        except nx.NetworkXNoPath:
            messagebox.showerror("Erro", f"Não há caminho entre {origin} e {destination}")
    else:
        messagebox.showerror("Erro", "Por favor, selecione uma origem, destino válidos e insira um mês válido.")

# Função para resetar os campos e limpar o grafo
def reset_fields():
    fuel_var.set('')  # Limpar o campo de combustível
    origin_var.set('')  # Resetar origem
    destination_var.set('')  # Resetar destino
    stopover_var.set('Nenhuma')  # Resetar a parada intermediária para 'Nenhuma'
    month_var.set(meses_do_ano[0])  # Resetar o mês para 'janeiro'
    
    travel_info_text.delete(1.0, tk.END)  # Limpar o campo de texto com informações da viagem
   
    G.clear()  # Remove todos os nós e arestas do grafo
    
    # Atualizar visualmente o grafo (para refletir o reset)
    update_graph()

    # Atualizar os menus de planetas para refletir o grafo vazio
    populate_planet_options([])

# Interface Tkinter
window = tk.Tk()
window.title("Planejamento de Rotas Interplanetárias")

# Definir variáveis globais
fuel_var = tk.StringVar(window)
origin_var = tk.StringVar(window)
destination_var = tk.StringVar(window)
stopover_var = tk.StringVar(window)
month_var = tk.StringVar(window)
missing_planet_var = tk.StringVar(window)
delete_planet_var = tk.StringVar(window)

month_var.set(meses_do_ano[0])
month_var.set("janeiro")

# Configuração dos frames e widgets da interface gráfica
frame_top_controls = tk.Frame(window)
frame_top_controls.grid(row=0, column=0, columnspan=10, padx=10, pady=5, sticky='ew')

btn_upload = tk.Button(frame_top_controls, text="Carregar CSV", command=upload_csv)
btn_upload.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

fuel_label = tk.Label(frame_top_controls, text="Combustível disponível:")
fuel_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

fuel_entry = tk.Entry(frame_top_controls, textvariable=fuel_var)
fuel_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')

origin_label = tk.Label(frame_top_controls, text="Origem:")
origin_label.grid(row=0, column=3, padx=5, pady=5, sticky='w')

origin_menu = ttk.OptionMenu(frame_top_controls, origin_var, "", *valid_planets)
origin_menu.grid(row=0, column=4, padx=5, pady=5, sticky='w')

destination_label = tk.Label(frame_top_controls, text="Destino:")
destination_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')

destination_menu = ttk.OptionMenu(frame_top_controls, destination_var, "", *valid_planets)
destination_menu.grid(row=0, column=6, padx=5, pady=5, sticky='w')

stopover_label = tk.Label(frame_top_controls, text="Parada (Opcional):")
stopover_label.grid(row=0, column=7, padx=5, pady=5, sticky='w')

stopover_menu = ttk.OptionMenu(frame_top_controls, stopover_var, "", "", *valid_planets)
stopover_menu.grid(row=0, column=8, padx=5, pady=5, sticky='w')

# Botão para calcular caminho
btn_shortest_path = tk.Button(frame_top_controls, text="Caminho Mais Curto", command=show_shortest_path)
btn_shortest_path.grid(row=0, column=9, padx=5, pady=5, sticky='ew')

month_label = tk.Label(frame_top_controls, text="Mês da viagem:")
month_label.grid(row=1, column=1, padx=5, pady=5, sticky='e')

month_menu = ttk.OptionMenu(frame_top_controls, month_var, *meses_do_ano)
month_menu.grid(row=1, column=2, padx=5, pady=5, sticky='w')

# Campo de texto para exibir a viagem e o combustível
travel_info_text = tk.Text(window, height=5, width=50)
travel_info_text.grid(row=2, column=6, columnspan=10, padx=10, pady=5, sticky='w')

# Frame para a visualização do grafo
frame_graph = tk.Frame(window)
frame_graph.grid(row=3, column=0, columnspan=10, padx=10, pady=10, sticky='nsew')

fig = plt.Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.get_tk_widget().config(bg='#0d1b2a')  # Fundo azul claro para o widget Tkinter
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Loop principal da interface
window.mainloop()
