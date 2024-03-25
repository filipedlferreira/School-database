#School_database
import mysql.connector
import beaupy
import os
import datetime
import json

# Load table from database
def loadData(table_Name : str, BD_Name : str):
    # estabelecer a ligação
    try:
        conn = mysql.connector.connect(user='root', host='localhost', database=BD_Name, port=3306)
    except Exception as e:
        print(f"\nErro: {e.msg}")
        print("ligação à base de dados falhou!\n")
    else:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_Name}"
        try: #tenta injetar a query
            cursor.execute(query)
        except Exception as e:
            print(f"\nErro: {e.msg}\n")
        else:
            myResult = cursor.fetchall()
            conn.close()
            return myResult #retorna um cursor com a info
    return None

def GetBDConnection(BD_Name : str):
    # estabelecer a ligação
    try:
        conn = mysql.connector.connect(user='root', host='localhost', database=BD_Name, port=3306,autocommit=True)
    except Exception as e:
        print(f"\nErro: {e.msg}")
        print("ligação à base de dados falhou!\n")
        conn.close()
        return None
    else:
        return conn #retorna a conncção

def Send_Query_INSERT_INTO(BD_Conn,query,Data):
    try:
        cursor = BD_Conn.cursor()
        cursor.execute(query, Data) #Query e Dados
    except Exception as e:
        print(f"\nErro: {e.msg} !!")
        print("tentativa de inserção falhou!\n")
        return None
    else:
        return cursor._last_insert_id #retorna o id da linha inserida

def Check_IfExistsOnBD(BD_Conn,Table_Name,Col_Name,valueToCheck):
    #query = f"SELECT ID FROM {Table_Name} WHERE {Col_Name}=?"
    query=f"SELECT id FROM {Table_Name} WHERE EXISTS(SELECT * FROM {Table_Name} WHERE {Col_Name} = {valueToCheck})"
    try:
        cursor = BD_Conn.cursor()
        #cursor.execute(query, (valueToCheck,))
        cursor.execute(query)
    except Exception as e:
        print(f"\nErro: {e.msg} !!")
        print("Execução da query falhou!\n")
        return None
    else:
        data = cursor.fetchall()
        #for row in data:
        #    print(row)

        if len(data) == 0:
            return False
        else:
            return True

def GetColumnInBD(BD_Name,Table_Name,Col_Index): ##Return List
    BDList = loadData(Table_Name,BD_Name)
    ResultingList=None
    if BDList:      
        ResultingList=[]
        for col in BDList:
            ResultingList.append(col[Col_Index])
    return ResultingList

# Save to a Json file
def save(obj, filename : str):
    try:
        with open(filename, "w") as f:
            json.dump(obj,f, indent=4)
    except:
        return False
    else:
        return True

# Adicionar curso
def add_curso(BD_Name : str): #Retorna o Index do elemento intruduzido se sucesso
    """
    Adicionar 1 curso: Argumentos: database
    """
    nbr = None
    conn = GetBDConnection(BD_Name)
    if conn:
        nome = input("Qual o nome do curso? : ").title()
        #verificar se já existe
        Table_Name = "curso"
        column_bd = GetColumnInBD(BD_Name,Table_Name,1)
        if nome.title() not in column_bd:
            while True: #obtem a data de inicio
                data_inicio = add_date("Insira a data de início")
                if data_inicio>=datetime.date.today():
                    break
                print("\nERRO: A data que inseriou para o início do curso é anterior à data de hoje, por favor introduza novamente!\n")  

            while True: #obtem a data de fim
                data_fim = add_date("Insira a data de fim")
                if data_fim>= data_inicio:
                    break
                print("\nERRO: A data que inseriou para o fim do curso é anterior à data de início, por favor introduza novamente!\n")

            query = f"INSERT INTO {Table_Name} (nome, data_inicio, data_fim) VALUES (%s, %s, %s)"
            curso = (nome, data_inicio, data_fim)
            nbr = Send_Query_INSERT_INTO(conn,query,curso)
        else:
            print("O nome desse curso já existe na base de dados!!")
    else:
        pass #tratamento de erro feito na func GetBDConnection()
    conn.close()
    return nbr #se vazio falhou, se com valor tem o index da linha do dado inserido

def cursos_disponíveis(BD_Name : str):
    table_Name = "curso" #tabela onde estão guardados os cursos
    cursos_matric = loadData(table_Name,BD_Name)
    if not cursos_matric:
        return None
    else:
        cursos_disp =[]
        for curso in cursos_matric:
            if curso[2]>datetime.date.today():
                cursos_disp.append(curso)
        return cursos_disp

# Adicionar formando   ---------------WORK IN PROGRESS----------------------

def formandos_disponiveis(BD_Name):
    formandos_matriculados = loadData("formando",BD_Name)
    for formando in formandos_matriculados:
        print(f"ID:{formando[0]} - Nome: {formando[1]}, com o NIF: {formando[2]}")
    return formandos_matriculados

def lista_formandos(BD_Name):
    formandos_matriculados = loadData("formando",BD_Name)
    lista_formando = []
    for formando in formandos_matriculados:
        lista_formando.append(f"ID:{formando[0]} - Nome: {formando[1]}, com o NIF: {formando[2]}")
    return lista_formando,formandos_matriculados

def add_formando(BD_Name):
    """
    Adicionar 1 formando: Argumentos: database
    """
    nbr = None
    conn = GetBDConnection(BD_Name)
    if conn:
        #verifica se há cursos disponiveis paa inscrição
        cursos = cursos_disponíveis(BD_Name)
        if cursos:
            nome=""
            while len(nome)==0:
                nome = input("\nQual o nome do formando? ").title()
            while True:
                nif = get_number("\nInsira o NIF: ",0,999999999)
                if len(str(nif))!=9:
                    print("O NIF tem que conter 9 dígitos")
                else:
                    break
 
            if not Check_IfExistsOnBD(conn,"formando","nif",nif):
                query = "INSERT INTO formando (nome, nif) VALUES (%s, %s)" #Query
                formando = (nome, nif)                                     #Dados da Query
 
                nbr = Send_Query_INSERT_INTO(conn,query,formando)              
            else:
                print("O Nif inserido já exite na base de dados!!!")
        else:
            print("Não existem cursos disponíveis")
    else:
        pass #tratamento de erro feito na func GetBDConnection()
    conn.close()
    return nbr #se vazio falhou, se com valor tem o index da linha do dado inserido

def add_matricula(BD_Name): #### WORK IN PROGRESS
    """
    Adicionar 1 formando a um curso: Argumentos: database
    """
    nbr = None
    conn = GetBDConnection(BD_Name)
    if conn:
        formandos, formandos_bd = lista_formandos(BD_Name)      
        if formandos:
            Clear_Terminal()
            print("Selecione um formando:")
            formandos.insert(0,"Inserir novo formando")
            op_formando = beaupy.select(formandos, cursor="->", cursor_style="green", return_index=True)
            if op_formando==0:
                add_formando("ex_2")
                voltar_atras("Inserido Formando. Continuar.")
                add_matricula("ex_2")
                return
            else:
                formando_id = formandos_bd[op_formando-1][0] #obtem o ID da tabela formando.id selecionado
        else:
            print("Não existem formandos disponíveis")
 
        matricula_bd = loadData("matricula","ex_2")
        lista_cursos_matriculados = []
        for formando in matricula_bd:
            if formando_id == formando[1]:
                lista_cursos_matriculados.append(formando[2])
 
        cursos = [curso for curso in cursos_disponíveis("ex_2") if curso[0] not in lista_cursos_matriculados]
        cursos_formatado = []
        for curso in cursos:
            cursos_formatado.append(f"{curso[0]} - {curso[1]} - de {curso[2]} a {curso[3]}")
        if cursos:
            Clear_Terminal()
            print(f"\nSelecione o curso a atribuir ao formando: {formandos[op_formando]}\n")
            op_curso = beaupy.select(cursos_formatado, cursor="->", cursor_style="green", return_index=True) ### Trabalhar a apresentação deste beaupy
            curso_id = cursos[op_curso][0]
            matricula = (formando_id, curso_id)
            cursor = conn.cursor()
            query = "INSERT INTO matricula (formando_id, curso_id) VALUES (%s, %s)"
            cursor.execute(query, matricula)
            Clear_Terminal()        
            print(f"""
    Foi inserido o item {cursor._last_insert_id}:
    Formando: {formandos[op_formando]}
    Curso: {cursos_formatado[op_curso]}
                """)        
        else:
            print("Não existem cursos disponíveis")
            voltar_atras()
    else:
        pass #tratamento de erro feito na func GetBDConnection()
    conn.close()
    return nbr #se vazio falhou, se com valor tem o index da linha do dado inserido

#3 Pesquisar_Curso
def Perquisar_Cursos(BD_Name : str):
    table_Name = "curso" #tabela onde estão guardados os cursos
    cursos = loadData(table_Name,BD_Name)
    if not cursos:
        return None
    else:
        #questionar que curso pesquisar
        nome_a_pesquisar = input("Indique o nome do Curso a pesquisar: ").title()
        curso_id = None
        for values in cursos:
            if nome_a_pesquisar == values[1]:
                curso_id = values[0]
        if curso_id:
            matriculas_bd = loadData("matricula","ex_2")        
            lista_formando_id_matriculados = []
            for ids in matriculas_bd:
                if curso_id == ids[2]:
                    lista_formando_id_matriculados.append(ids[1])
            formandos_bd = loadData("formando","ex_2")
            lista_formandos_matriculados = []
            for formandos in formandos_bd:
                for ids in lista_formando_id_matriculados:
                    if formandos[0] == ids:
                        lista_formandos_matriculados.append(formandos[1])
            for curso in cursos:
                if curso_id == curso[0]:
                    texto_cursos = f"Curso: {curso[1]} de {curso[2]} a {curso[3]}"
            Clear_Terminal()
            print(texto_cursos)
            print("\nFormandos matriculados no curso:")
            for numero in range(len(lista_formandos_matriculados)):
                print(f"{numero+1} - {lista_formandos_matriculados[numero]}")
        else:
            print(f"\nO curso com o nome {nome_a_pesquisar} não existe na base de dados! ")
        return

#4 Pesquisa de formandos

def Perquisar_Formando(BD_Name : str):
    table_Name = "formando" #tabela onde estão guardados os cursos
    formandos = loadData(table_Name,BD_Name)
    if not formandos:
        return None
    else:
        #questionar que formando pesquisar
        nome_a_pesquisar = input("Indique o nome do Formando a pesquisar: ").title()
        formando_id = None
        for values in formandos:
            if nome_a_pesquisar == values[1]:
                formando_id = values[0]
        if formando_id:
            matriculas_bd = loadData("matricula","ex_2")        
            lista_cursos_id_matriculados = []
            for ids in matriculas_bd:
                if formando_id == ids[1]:
                    lista_cursos_id_matriculados.append(ids[2])
            if lista_cursos_id_matriculados:
                cursos_bd = loadData("curso","ex_2")
                lista_cursos_matriculados = []
                for cursos in cursos_bd:
                    for ids in lista_cursos_id_matriculados:
                        if cursos[0] == ids:
                            lista_cursos_matriculados.append(cursos[1])
                texto_cursos =[]
                for curso in cursos_bd:
                    if curso[0] in lista_cursos_id_matriculados:
                        texto_cursos.append(f"{curso[1]} de {curso[2]} a {curso[3]}")
                Clear_Terminal()
                print(f"\nFormando: {nome_a_pesquisar}\n\nMatriculado em:\n")
                for cursos_matriculados in texto_cursos:
                    print(cursos_matriculados)
            else:
                print("O formando não está matriculado em nenhum curso")
        else:
            print(f"\nO formando com o nome {nome_a_pesquisar} não existe na base de dados! ")
        return

# Adicionar data de início e fim para os cursos
def check_leap_year(year):
    """
    Check if the given year is a leap year or not.
    """
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return 29
            else:
                return 28
        else:
            return 29
    else:
        return 28

def get_number(msg1,min,max):
    while True:
        try:
            number = int(input(f'{msg1}'))
        except:
            print("\nERRO: Insira número inteiro")
        else:          
            if min>number or number>max:
                print(f"Erro: Insira valores entre {min} e {max}, tente novamente!")
            elif min <=number<=max:
                return number

def add_date(msg):
    year = get_number(msg + " -> ano: ",datetime.datetime.now().year,2030)
    month = get_number(msg + " -> mês: ",1,12)
    if month in [1,3,5,7,8,10,12]:
        end_day = 31
    elif month in [4,6,9,11]:
        end_day = 30
    elif month == 2:
        end_day = check_leap_year(year)
    day = get_number(msg + " -> dia: ",1,end_day)
    return datetime.date(year, month, day)

# Função para voltar atrás
def voltar_atras(msg="Voltar atrás"): #esta função suspende o programa até o operador clicar na mensagem
    print("")
    lista_sair = [msg]
    beaupy.select(lista_sair, cursor="->", cursor_style="blue")
    print("")

def Clear_Terminal():
    os.system("cls") #apaga a informação imprimida na consola

#1 - Gestão Cursos    ###########################################################
def Menu_Gestao_de_cursos(BD_Name : str):
    lista_gestao_cursos = ["a - Ver Cursos", "b - Inserir Curso", "c - Voltar ao menu"]
    while True:
        Clear_Terminal() ##apaga o menu de seleção
        print(" Gestão de Cursos:\n")
        op_1 = beaupy.select(lista_gestao_cursos, cursor="->", cursor_style="red", return_index=True)+1
        match op_1:
            case 1: #Ver Cursos
                Menu_Ver_Cursos(BD_Name)
            case 2: #Inserir Curso
                Menu_Inserir_Curso(BD_Name)
            case 3: #Voltar ao menu
                break
            case _:
                print("\nErro: opção inválida\n")

#1.a   #Ver Cursos
def Menu_Ver_Cursos(BD_Name : str):
    Clear_Terminal()
    cursos = loadData("curso",BD_Name)
    print("Lista de cursos:\n")
    for curso in cursos:
        print(f"{curso[0]} - {curso[1]} - de {curso[2]} a {curso[3]}")
    voltar_atras()

#1.b   #Inserir Curso
def Menu_Inserir_Curso(BD_Name : str):
    Clear_Terminal()
    print("Inserir curso\n")
    nbr = add_curso(BD_Name)
    if nbr:
        print(f"Foi inserido o registo nr. {nbr} !")
    voltar_atras()

#fim Gestão Cursos ##########################################################
#-----------------------------------------------------------------------------

#2 - Gestão Formandos   ##########################################################
def Menu_Gestao_de_Formadores(BD_Name : str):
    lista_gestao_formandos = ["a - Ver Formandos", "b - Inserir Formando","c - Matricular formando num curso", "d - Voltar ao menu"]
    while True:
        Clear_Terminal() ##apaga o menu de seleção
        print(" Gestão de Formandos:\n")      
        op_1 = beaupy.select(lista_gestao_formandos, cursor="->", cursor_style="green", return_index=True)+1
        match op_1:
            case 1: #a - Ver Formandos
                Menu_Ver_Formandos(BD_Name)
            case 2: #b - Inserir Formando
                Menu_Inserir_Formando(BD_Name)
            case 3: #c - Matricular formando num curso
                Menu_Matricular_formando_num_curso(BD_Name)              
            case 4: #d - Voltar ao menu
                return
            case _:
                print("\nErro: opção inválida\n")

#2 - Gestão Formandos
#   a - Ver Formandos
def Menu_Ver_Formandos(BD_Name : str):  
    Clear_Terminal()
    formandos = loadData("formando",BD_Name)
    print("Lista de formandos:\n")
    for formando in formandos:
        print(f"ID:{formando[0]} - Nome: {formando[1]}, com o NIF: {formando[2]}")
    voltar_atras()

#2 - Gestão Formandos
#   b - Inserir Formando
def Menu_Inserir_Formando(BD_Name : str):  
    cursos_disp = cursos_disponíveis(BD_Name)
    if cursos_disp:
        Clear_Terminal()
        print("Cursos disponíveis:\n")
        # mostra ao operador os cursos disponiveis
        for curso in cursos_disp:
            print(f"{curso[0]} - {curso[1]} - de {curso[2]} a {curso[3]}")
        # inicia o metodo de inserção de formandos
        nbr = add_formando(BD_Name)
        if nbr:
            print(f"Foi inserido o registo nr. {nbr} !")
    else:
        print("\nErro a obter cursos disponíveis ou Não há cursos!!\n")
    voltar_atras()

#2 - Gestão Formandos
#   c - Matricular formando num curso
def Menu_Matricular_formando_num_curso(BD_Name : str):
    add_matricula("ex_2")
    voltar_atras()
#fim Gestão Formandos ########################################################
#-----------------------------------------------------------------------------

#Pesquisa Cursos    ###########################################################
def Menu_Pesquisar_Cursos(BD_Name : str):
    Perquisar_Cursos(BD_Name)
    voltar_atras()
    #EM DESEMVOLVIMENTO ###########################################
    #No menu Pesquisar Curso deverá solicitar o nome do curso a pesquisar, e caso este seja encontrado devolver os
    #dados do curso seguidos da listagem de alunos inscritos no mesmo:      

#fim Pesquisa Cursos ##########################################################
#-----------------------------------------------------------------------------

#Pesquisa Formando    ###########################################################
def Menu_Pesquisar_Formando(BD_Name : str):
    Clear_Terminal()
    Perquisar_Formando(BD_Name)
    voltar_atras()

#fim Pesquisa Formando ##########################################################
#-----------------------------------------------------------------------------

# Criar Dicionários para o Json File
def criar_dict_bd(BD_Name, Table_Name):
    table_list = loadData(Table_Name, BD_Name)
    if Table_Name == "curso":
        for i in range(len(table_list)):
            item = list(table_list[i])  # Converter tuplo para lista de modificação
            item[2] = item[2].strftime('%Y-%m-%d')  # Formatar start date
            item[3] = item[3].strftime('%Y-%m-%d')  # Formatar end date
            table_list[i] = tuple(item)  # Convert para tuplo e fazer update na lista
    table_dict = {Table_Name: table_list}
    return table_dict

def Menu_Save_BD_to_JSON(BD_Name):
    Clear_Terminal()
    bd_dict= [criar_dict_bd(BD_Name,"curso"),criar_dict_bd(BD_Name,"formando"),criar_dict_bd(BD_Name,"matricula")]
    if bd_dict:
        status_func = save(bd_dict,"Json_file_ex_2.json")
        if status_func:
            print("Sucesso: O ficheiro Json foi gerado!")
        else:
            print("\nERRO: Houve um erro ao gerar o JSON File!")
    else:
        print("\nERRO: Menu save error!")
    voltar_atras("Sair do programa")
    return

#-----------------------------------------------------------------------------

# Execução do programa:
def main():
    BD_Name = "ex_2"
    menu_inicial = ["1 - Gestão de Cursos", "2 - Gestão de Formandos", "3 - Pesquisar Curso","4 - Pesquisar Formando", "5 - Sair"]
    while True:
        Clear_Terminal()
        print("Menu:\n")
        op = beaupy.select(menu_inicial, cursor="->", cursor_style="blue", return_index=True)+1
        match op:
            case 1: #Gestão de Cursos
                Menu_Gestao_de_cursos(BD_Name)
            case 2: #Gestão de Formadores
                Menu_Gestao_de_Formadores(BD_Name)
            case 3: #Pesquisar Cursos
                Menu_Pesquisar_Cursos(BD_Name)  
            case 4: #Pesquisar Formando
                Menu_Pesquisar_Formando(BD_Name)                              
            case 5: #Sair
                Menu_Save_BD_to_JSON(BD_Name)
                break
            case _:
                print("\nErro: opção inválida\n")

main()