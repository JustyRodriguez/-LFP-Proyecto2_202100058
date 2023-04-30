from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog as fd
from tkinter import ttk
import customtkinter
from tkdocviewer import *
import pymongo 
from pymongo import *

class objeto:
    #--------------Parametros de propiedades-------------------------------------------
    def __init__(self, identificador, tipo):
        self.identificador = identificador
        self.tipo = tipo
        self.propiedades = {}
        self.css = []
        self.contiene = []
        self.html = ""
#--------------Funcion creadora de de partes del HTML y asignacion de parametros a los mismos---------------------
    def crear_html(self):
        props = self.propiedades.keys()
        if "Texto" in props:
            Texto = self.propiedades["Texto"][1:-1]
        else:
            Texto = ""
            
        if "alineacion" in props:
            alineacion = self.propiedades["alineacion"]
        else:
            alineacion = "left"
            
        if "Marcado" in props:
            Marcado = self.propiedades["Marcado"]
        else:
            Marcado = "false"

        if "Grupò" in props:
            Grupò = self.propiedades["Grupò"]
        else:
            Grupò = ""
            
        if self.tipo == "Etiqueta":
            self.html = '<label id="'+self.identificador+'">'+Texto+"\n"
            for cont in self.contiene:
                if cont != None:
                    self.html+=cont.crear_html()
            self.html += '</label>\n'

        elif self.tipo == "Boton":
            self.html = '<input type="submit" id="'+self.identificador+'" value="'+Texto+'" style="text-align: '+alineacion+'"/>\n'

        elif self.tipo == "Check":
            self.html = '<input type="checkbox" id="'+self.identificador+'" value="'+Texto+'"'
            if Marcado == "true":
                self.html += " checked"
            self.html += '/>\n'
            
        elif self.tipo == "RadioBoton":
            self.html = '<input type="radio" id="'+self.identificador+'" name="'+Group+'" value="'+Texto+'"'
            if Marcado == "true":
                self.html += " checked"
            self.html += '/>\n'
            
        elif self.tipo == "Texto":
            self.html = '<input type="text" id="'+self.identificador+'" value="'+Texto+'" style="text-align: '+alineacion+'"/>\n'

        elif self.tipo == "AreaTexto":
            self.html = '<TEXTAREA id="'+self.identificador+'">'+Texto+"\n"
            for cont in self.contiene:
                if cont != None:
                    self.html+=cont.crear_html()
            self.html += '</TEXTAREA>\n'

        elif self.tipo == "Clave":
            self.html = '<input type="text" id="'+self.identificador+'" value="'+Texto+'"style="text-align: '+alineacion+'"/>\n'

        elif self.tipo == "Contenedor":
            self.html = '<div id="'+self.identificador+'">\n'
            for cont in self.contiene:
                if cont != None:
                    self.html+=cont.crear_html()
            self.html += '</div>\n'

        elif self.identificador == "this":
            for cont in self.contiene:
                if cont != None:
                    self.html+=cont.crear_html()
        
        return self.html
                
#--------------Definicion de caracteres que pertenecen al lenguaje------------------------------------
num = "0123456789"
alpha = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm_"
moreOless = "+-"
espacios = " \n\t();,."
archivo_abierto = None
t_global = []

#--------------Automata de comentacio linea------------------------------------
def afd_comentario(lexema):
    pat = "//.*"
    tabla = ""
    estado = 0
    aceptacion = [2]
    
    for char in lexema:
        if estado == 0:
            if char == "-":
                estado = 1
            else:
                estado = -5
        elif estado == 1:
            if char == "-":
                estado = 2
            else:
                estado = -5
        elif estado == 2:
            if char == "-":
                estado = 3
            else:
                estado = -5
        elif estado == 3:
            if char != "\n":
                estado = 3
            else:
                estado = -5
                
    if estado in aceptacion:
        return True
    else:
        return False

#--------------Automata de comentacio multilinea------------------------------------
def afd_cmultilinea(lexema):
    pat = "(/*) (.|\\n)* (*/) "
    estado = 0
    aceptacion = [4]
    
    if len(lexema) > 3:
        content = lexema[3:]
    else:
        content = ""
        
    if "/*" in content:
        estado == -1
    
    for char in lexema:   
            if estado == 0:
                if char == "/":
                    estado = 1
                else:
                    estado = -5
            elif estado == 1:
                if char == "*":
                    estado = 2
                else:
                    estado = -5
            elif estado == 2:
                if char == "*":
                    estado = 3
                elif char == "\n" or char != "\n" :
                    estado = 2
                else:
                    estado = -5
            elif estado == 3:
                if char == "/":
                    estado = 4
                else:
                    estado = -5
            elif estado == 4:
                if char == "/" or char != "/":
                    estado = -5

    if estado in aceptacion:
        return True
    else:
        return False

#--------------Automata de lectura de numeros------------------------------------
def afd_numero(lexema):
    pat = "[-+]?[0-9]+\.[0-9]+"
    estado = 0
    aceptacion = [2,4]

    for char in lexema:
        if estado == 0:
            if char in moreOless:
                estado = 1
            elif char in num:
                estado = 2
            else:
                estado = -5
        elif estado == 1:
            if char in num:
                estado = 2
            else:
                estado = -5
        elif estado == 2:
            if char in num:
                estado = 2
            elif char == ".":
                estado = 3
            else:
                estado = -5
        elif estado == 3:
            if char in num:
                estado = 4
            else:
                estado = -5
        elif estado == 4:
            if char in num:
                estado = 4
            else:
                estado = -5

    if estado in aceptacion:
        return True
    else:
        return False

#--------------Automata de lectura de identificadores------------------------------------
def afd_identificador(lexema):
    pat = "([A-Za-z_])([0-9A-Za-z_])*"
    estado=0
    aceptacion=[1]
	
    for char in lexema:
        if estado == 0:
            if char in alpha:
                estado = 1
            else:
                estado = -5
        elif estado == 1:
            if char in alpha or char in num:
                estado = 1
            else:
            	estado = -5

    if estado in aceptacion:
        return True 
    else:
        return False 

#--------------Automata de lectura de palabras------------------------------------
def afd_string(lexema):
    pat = '".*"'
    estado=0
    aceptacion=[2]
	
    for char in lexema:
        if estado == 0:
            if char == "\"":
                estado = 1
            else:
                estado = -5
        elif estado == 1:
            if char == "\"":
                estado = 2
            elif char != "\n":
                estado = 1
            else:
            	estado = -5
        elif estado == 2:
            if char == "\n" or char != "\n":
                estado = -5

    if estado in aceptacion:
        return True 
    else:
        return False 

#--------------Diccionario de tokens------------------------------------
tokens ={
    "tk_comentario": afd_comentario,
    "tk_cmultilinea": afd_cmultilinea,
    "tk_crear": "CrearBD",
    "tk_igual": "=",
    "tk_espacio": " ",
    "tk_nuevo": "nueva",
    "tk_ID": "ejemplo",
    "tk_crearcolec": "CrearColeccion",
    "tk_coleccion": "colec",
    "tk_eliminar": "EliminarBD",
    "tk_elimina": "elimina",
    "tk_puntoycoma": ";",
    "tk_pizq": "(",
    "tk_pder": ")",
    "tk_elicolec": "EliminarColeccion",
    "tk_elimco": "eliminacolec",
    "tk_insertaru": "InsertarUnico",
    "tk_doc": "insertadoc",
    "tk_llaveizq": "{",
    "tk_llaveder": "}",
    "tk_actualizaru": "ActualizarUnico",
    "tk_actdoc": "actualizadoc",
    "tk_eliminaru": "EliminarUnico",
    "tk_eliminardoc": "eliminadoc",
    "tk_string": afd_string,
    "tk_numero": afd_numero,
    "tk_identificador": afd_identificador
    }

controles = ["tk_Etiqueta","tk_Boton","tk_Check","tk_RadioBoton"
             ,"tk_Texto","tk_AreaTexto","tk_Clave","tk_Contenedor"]

propiedades = ["tk_crear",
    "tk_crearcolec",
    "tk_elicolec",
    "tk_insertaru",
    "tk_actualizaru",
    "tk_eliminaru",
    "tk_setAlto",
    "tk_setAncho"]

colocaciones = ["tk_add",
                "tk_setPosicion"]

comentarios = ["tk_comentario","tk_cmultilinea"]

##ELIMIAR TODA ESTA FUNCION
#--------------Creacion de propiedades------------------------------------
def crear_propiedad(i,propiedad,reconocidos,trabajando_con):
    nuevo_i = i+1
    error = []
    hay_error = False
    
    if propiedad[0] == "tk_setcolorLetra":
        color1 = reconocidos[i]
        color2 = reconocidos[i+1]
        color3 = reconocidos[i+2]
        if color1[0] != color2[0] or color1[0] != color3[0] or color3[0] != "tk_numero":
            hay_error = True
        else:
            trabajando_con.css.append("color: rgb("+str(color1[1])+","+str(color2[1])+","+str(color3[1])+");\n")
            nuevo_i = i+3
            
    elif propiedad[0] == "tk_setTexto":
        Texto = reconocidos[i]
        if Texto[0] != "tk_string":
            hay_error = True
        else:
            trabajando_con.propiedades["Texto"] = Texto[1]
            nuevo_i = i+1
            
    elif propiedad[0] == "tk_setAlineacion":
        alineacion = reconocidos[i]
        if alineacion[0] == "tk_centro":
            trabajando_con.propiedades["alineacion"] = "center"
        elif alineacion[0] == "tk_izq":
            trabajando_con.propiedades["alineacion"] = "left"
        elif alineacion[0] == "tk_der":
            trabajando_con.propiedades["alineacion"] = "right"
        else:
            hay_error = True
            nuevo_i = i-1
        nuevo_i = i+1

    elif propiedad[0] == "tk_setbgcolor":
        color1 = reconocidos[i]
        color2 = reconocidos[i+1]
        color3 = reconocidos[i+2]
        if color1[0] != color2[0] or color1[0] != color3[0] or color3[0] != "tk_numero":
            hay_error = True
        else:
            trabajando_con.css.append("background-color: rgb("+str(color1[1])+","+str(color2[1])+","+str(color3[1])+");\n")
            nuevo_i = i+3
            
    elif propiedad[0] == "tk_setMarcada":
        marcado = reconocidos[i]
        if marcado[0] != "tk_true" and marcado[0] != "tk_false":
            hay_error = True
        else:
            trabajando_con.propiedades["Marcado"] = marcado[1]
            nuevo_i = i+1
        
    elif propiedad[0] == "tk_setGrupo":
        grupo = reconocidos[i]
        if grupo[0] != "tk_identificador":
            hay_error = True
        else:
            trabajando_con.propiedades["Grupo"] = grupo[1]
            nuevo_i = i+1
            
    elif propiedad[0] == "tk_setAlto":
        alto = reconocidos[i]
        if alto[0] != "tk_numero":
            hay_error = True
        else:
            trabajando_con.css.append("height:"+str(alto[1])+";\n")
            nuevo_i = i+1
    
    elif propiedad[0] == "tk_setAncho":
        ancho = reconocidos[i]
        if ancho[0] != "tk_numero":
            hay_error = True
        else:
            trabajando_con.css.append("width:"+str(ancho[1])+";\n")
            nuevo_i = i+1        

    if hay_error:
        error.append(("Sintactico",propiedad[2], propiedad[3], propiedad[1], "Error sintactico en las propiedades de "+propiedad[1]))
        
    return (nuevo_i, error)

#ELIMINAR TODA ESTA FUNCION
#--------------Creacion de colocacion de objetos------------------------------------
def crear_colocacion(i,colocacion,reconocidos,trabajando_con,objetos_creados):
    nuevo_i = i+1
    error = []
    hay_error = False
            
    if colocacion[0] == "tk_add":
        id_buscar = reconocidos[i]
        if id_buscar[0] != "tk_identificador":
            hay_error = True
        else:
            poner = None
            for o in objetos_creados:
                if o.identificador == id_buscar[1]:
                    poner = o
                    break
            trabajando_con.contiene.append(poner)
            nuevo_i = i+1

    elif colocacion[0] == "tk_setPosicion":
        numero1 = reconocidos[i]
        numero2 = reconocidos[i+1]
        if numero1[0] != numero2[0] or numero2[0] != "tk_numero":
            hay_error = True
        else:
            trabajando_con.css.append("position: absolute;\n left: "+str(numero1[1])+"px;\n top: "+str(numero2[1])+"px;\n")
            nuevo_i = i+2

    if hay_error:
        error.append(("Sintactico",colocacion[2], colocacion[3], colocacion[1], "Error sintactico en la colocacion de "+id_buscar[1]))

    return (nuevo_i, error)

#--------------Analizador sintactico------------------------------------
def Analizador_sintactico(reconocidos):
    objetos_creados = [objeto("this", "")]
    i = 0
    errores = []
    while i < len(reconocidos):
        if reconocidos[i][0] == "tk_crear":
            client=MongoClient("mongodb://localhost", 27017)
            db=client["prueba"]
            coleccion=db["personas"]
            coleccion.insert_one({"name":"Justy", "password":123})
            print(client.list_database_names()) 
            i+=1
            salir = False
            while not salir and i < len(reconocidos):
                cont = reconocidos[i]
                if cont[0] == "tk_control_c":
                    i+=1
                    salir = True
                    break
                elif cont[0] in comentarios:
                    pass
                elif cont[0] in controles:
                    i+=1
                    obj = reconocidos[i]
                    if obj[0] != "tk_identificador":
                        errores.append(("Sintactico",obj[2], obj[3], obj[1], "Error sintactico, se esperaba tk_identificador, pero se recibio: "+obj[0]))
                        i-=1
                    else:
                        control = objeto(obj[1],cont[1])
                        if control.tipo == "Texto":
                            control.css.append("font-size: 12px;")
                        objetos_creados.append(control)
                else:
                    errores.append(("Sintactico",cont[2], cont[3], cont[1], "Error sintactico, se esperaba un Control, pero se recibio: "+cont[0]))
                i+=1
            i-=1
            
        elif reconocidos[i][0] == "tk_eliminar":
            i+=1
            salir = False
            while not salir  and i < len(reconocidos):
                cont = reconocidos[i]
                if cont[0] == "tk_props_c":
                    i+=1
                    salir = True
                    break
                elif cont[0] in comentarios:
                    i+=1
                elif cont[0] == "tk_identificador":
                    trabajando_con = None
                    for o in objetos_creados:
                        if o.identificador == cont[1]:
                            trabajando_con = o
                    if trabajando_con == None:
                        errores.append(("Sintactico",cont[2], cont[3], cont[1], "Error sintactico, no se encuentra el id: "+cont[1]))
                        i+=1
                        continue
                    i+=1
                    propiedad = reconocidos[i]
                    
                    if propiedad[0] not in propiedades:
                        errores.append(("Sintactico",propiedad[2], propiedad[3], propiedad[1], "Error sintactico, se esperaba Propiedad despues de "+cont[1]+", pero se recibio: "+propiedad[0]))
                        i+=1
                    else:
                        i+=1
                        i, err = crear_propiedad(i,propiedad,reconocidos, trabajando_con)
                        errores += err
                else:
                    errores.append(("Sintactico",cont[2], cont[3], cont[1], "Error sintactico, se esperaba tk_identificador, pero se recibió: "+cont[0]))
                    i+=1
                    
        if reconocidos[i][0] == "tk_coloca_a":
            i+=1
            salir = False
            while not salir  and i < len(reconocidos):
                cont = reconocidos[i]
                if cont[0] == "tk_coloca_c":
                    i+=1
                    salir = True
                    break
                elif cont[0] in comentarios:
                    i+=1
                elif cont[0] == "tk_identificador":
                    trabajando_con = None
                    for o in objetos_creados:
                        if o.identificador == cont[1]:
                            trabajando_con = o
                    if trabajando_con == None:
                        errores.append(("Sintactico",cont[2], cont[3], cont[1], "Error sintactico, no se encuentra el id: "+cont[1]))
                        i+=1
                        continue
                    i+=1
                    colocaciones = reconocidos[i]
                    
                    if colocaciones[0] not in colocaciones:
                        errores.append(("Sintactico",colocaciones[2], colocaciones[3], colocaciones[1], "Error sintactico, se esperaba Metodo de colocacion despues de "+cont[1]+", pero se recibio: "+colocaciones[0]))
                        i+=1
                    else:
                        i+=1
                        i, err = crear_colocacion(i, colocaciones, reconocidos, trabajando_con, objetos_creados)
                        errores += err
                else:
                    errores.append(("Sintactico",cont[2], cont[3], cont[1], "Error sintactico, se esperaba tk_identificador, pero se recibió: "+cont[0]))
                    i+=1
        i+=1

    if len(errores) > 0:
        messagebox.showwarning(message="Se encontraron errores, No se puede generar html", title="Analizar")
    else:
        messagebox.showinfo(message="Analisis Sintactico Realizado, Realizando la Pagina", title="Analizar")
        crear_Pagina(objetos_creados)
        
    return errores

#--------------Analizador lexico------------------------------------
def Analizador_lexico(entrada):
    linea, columna = 1, 0
    indice = 0
    reconocidos = []
    S_reconocidos = []
    S_errores = []
    error = False
    
    while indice < len(entrada):
        caracter = entrada[indice]
        reconocido = False

        columna+=1
        if caracter=="\n":
            linea+=1
            columna=0

        if caracter in espacios:
            indice += 1
            continue
        
        for token, patron in tokens.items():
            if type(patron) == str:
                if indice + len(patron) > len(entrada): continue

                lexema = entrada[indice : indice + len(patron)]
                
                if lexema == patron:
                    reconocido = True
                    reconocidos.append((token,lexema,linea,columna))
                    S_reconocidos.append((str(len(S_reconocidos)+1),str(linea),str(columna), token,lexema))
                    indice += len(patron)
                    columna += len(patron)-1
                    break

            else:
                indice_adelante = indice
                anterior_reconocido = False

                while indice_adelante <= len(entrada):
                    lexema = entrada[indice : indice_adelante]
                    reconocido = patron(lexema)

                    if not reconocido and anterior_reconocido:
                        lexema = entrada[indice : indice_adelante - 1]
                        reconocido = patron(lexema)
                        indice = indice_adelante - 1
                        break  

                    anterior_reconocido = reconocido
                    indice_adelante += 1

                if reconocido:
                    if "\n" in lexema:
                        for char in lexema:
                            columna +=1
                            if char == "\n":
                                linea +=1
                                columna = 0
                    else:
                        columna += indice_adelante - indice -1

                    lexema = lexema.replace("\n","\\n ")
                    reconocidos.append((token,lexema,linea,columna))
                    S_reconocidos.append((str(len(S_reconocidos)+1),str(linea),str(columna), token,lexema))
                    indice = indice_adelante - 1

            if reconocido: break

        if not reconocido:
            lexema = entrada[indice]
            indice += 1
            S_errores.append(("Lexico",str(linea), str(columna), lexema, "No se ha reconocido el lexema"))
            error = True

    messagebox.showinfo(message="Analisis lexico Realizado, continuando con analizador Sintactico", title="Analizar")
    err = Analizador_sintactico(reconocidos)
    S_errores += err
    return S_errores, S_reconocidos

#--------Ventana emergente para mostrar el manual de usuario---------------------------------------------------------
def Manual_user():
    root.withdraw()
    Ver_Manu_user = Toplevel()
    Ver_Manu_user.title("Manual de usuario")
    Ver_Manu_user.geometry("800x900")
    Ver_Manu_user.config(bg="green")

    btt_back = customtkinter.CTkButton(Ver_Manu_user,  text = "Regresar", command = lambda: Regresar(root, Ver_Manu_user),
        text_font=("Showcard Gothic", 15, "bold"), text_color="black", hover= True, hover_color= "#f2f2f2", height=30, width= 100,
        border_width=2, corner_radius=20, border_color= "#d3d3d3", bg_color="green", fg_color= "#fafafa")    
    btt_back.pack()

    ver_doc1 = DocViewer(Ver_Manu_user)
    ver_doc1.pack(side="top", expand=1, fill="both")
    ver_doc1.display_file("Manual de usuario de proyecto 2 LFP A+.pdf")

#-------Ventana emergente para mostrar el manual técnico------------------------------------------------
def Manual_Tec():
    root.withdraw()
    Ver_Manu_Tec = Toplevel()
    Ver_Manu_Tec.title("Manual Técnico")
    Ver_Manu_Tec.geometry("800x900")
    Ver_Manu_Tec.config(bg="green")
    
    btt_back = customtkinter.CTkButton(Ver_Manu_Tec,  text = "Regresar", command = lambda: Regresar(root, Ver_Manu_Tec),
        text_font=("Showcard Gothic", 15, "bold"), text_color="black", hover= True, hover_color= "#f2f2f2", height=30, width= 100,
        border_width=2, corner_radius=20, border_color= "#d3d3d3", bg_color="green", fg_color= "#fafafa")  
    btt_back.pack()

    ver_doc2 = DocViewer(Ver_Manu_Tec)
    ver_doc2.pack(side="top", expand=1, fill="both")
    ver_doc2.display_file("Manual Tecnico de proyecto 2 LFP A+.pdf")

#$CAMBIAR DATOS
#-----Funcion para mostrar los datos del creador------------------------------------------------
def Datos_user():
    messagebox.showinfo(message='''USAC, Facultad de Ingeniería, Escuela de Ciencias y Sistemas. Lenguajes Fomales y de Programación B+, 1er Semestre 2023

 
          DESARROLLADOR: Justy Sebastian Rodríguez del Cid


                        CARNET: 202100058''',
                        
                        title="Datos del creador")

#--------------Funcion para guardar un nuevo documento creado------------------------------------
def Nuevo(area_texto):
    global archivo_abierto
    seleccion = messagebox.askquestion(message="¿Desea guardar los cambios?", title="Nuevo")
    if seleccion == "yes":
        f = fd.asksaveasfile(mode='w', defaultextension=".gpw")
        if f is None:
            return
        guardar = str(area_texto.get(1.0, END)) 
        f.write(guardar)
        f.close()
    area_texto.delete(1.0, END)
    archivo_abierto=None

#--------------Funcion para abrir un archivo existente------------------------------------
def Abrir(area_texto):
    global archivo_abierto
    
    actual = str(area_texto.get(1.0, END)).strip()
    
    if len(actual) != 0:
        seleccion = messagebox.askquestion(message="¿Desea guardar los cambios?", title="Abrir")
        if seleccion == "yes":
            if archivo_abierto != None:
                open(archivo_abierto, "w").close()
                f = open(archivo_abierto, "w")
                guardar = str(area_texto.get(1.0, END)) 
                f.write(guardar)
                f.close()
            else:
                f = fd.asksaveasfile(mode='w', defaultextension=".gpw")
                if f != None:
                    guardar = str(area_texto.get(1.0, END)) 
                    f.write(guardar)
                    f.close()
                    
        area_texto.delete(1.0, END)

    f = fd.askopenfilename(filetypes=[("GPW files",".gpw")])
    if f == "":
        return
    archivo_abierto = f
    file = open(f,"r")
    leido = file.read()
    file.close()
    area_texto.insert(END, leido)

#--------------Funcion para guardar los cambios realizados a un archivo previamente cargado------------------------
def Guardar(area_texto):
    if archivo_abierto != None:
        open(archivo_abierto, "w").close()
        f = open(archivo_abierto, "w")
        guardar = str(area_texto.get(1.0, END)) 
        f.write(guardar)
        f.close()
        messagebox.showinfo(message="Se ha guardado el codigo", title="Guardar")
    else:
        messagebox.showwarning(message="No se ha seleccionado archivo de guardado", title="Guardar")
        GuardarC(area_texto)

#--------------Funcion para guardar un archivo nuevo editado------------------------------------
def GuardarC(area_texto):
    f = fd.asksaveasfile(mode='w', defaultextension=".gpw")
    if f is None:
        return
    guardar = str(area_texto.get(1.0, END))
    f.write(guardar)
    f.close()

#-----------Funcion para regresar a la ventana anterior---------------------------------------------------------------------
def Regresar(Padre, Hijo):
    Padre.deiconify()
    Hijo.destroy()

#--------------Funcion para salir de la aplicacion------------------------------------
def Salir(root):
    seleccion = messagebox.askquestion(message="¿Deseas salir de la aplicacion?", title="Salir")
    if seleccion == "yes":
        root.destroy()

#--------------Funcion para alanizar el archivo cargado------------------------------------
def Analizar(area_texto, T_errores):
    global t_global
    analizar = str(area_texto.get(1.0, END))
    err, tkns = Analizador_lexico(analizar)
    
    T_errores.delete(*T_errores.get_children())
    t_global = tkns
    for error in err:
        T_errores.insert("",tk.END,values=error)

#--------------Funcion para mostrar los tokens encontrados------------------------------------
def verTokens():
    global t_global
    toplevel = Toplevel()
    toplevel.config(borderwidth=20, bg="green")
    lbltokens = Label (toplevel, text="Reporte de tokens", font=("Showcard Gothic", 20, "bold"), bg = "green")
    lbltokens.pack()
    btn_Regresar = customtkinter.CTkButton(toplevel, text= "Regresar", command =lambda: Salir(toplevel))
    btn_Regresar.place(x=550, y=0)
    
    columnas1 = ("num","lin","col","token","lexema")
    T_tokens = ttk.Treeview(toplevel, columns=columnas1, show="headings")
    T_tokens.column("num", stretch=False, width=100)
    T_tokens.heading('num', text='Token No.')
    T_tokens.column("lin", stretch=False, width=100)
    T_tokens.heading('lin', text='Linea')
    T_tokens.column("col", stretch=False, width=100)
    T_tokens.heading('col', text='Posicion')
    T_tokens.column("token", stretch=False, width=150)
    T_tokens.heading('token', text='Token')
    T_tokens.column("lexema", stretch=False, width=250 )
    T_tokens.heading('lexema', text='Lexema')

    for token in t_global:
        T_tokens.insert("",tk.END,values=token)

    T_tokens.pack( fill = BOTH)

    toplevel.resizable(True, True)
    
#--------------Creacion de ventana principal------------------------------------
root = Tk()
root.title("LFP Proyecto 2: Analizador sintáctico")
root.geometry("1200x650")
root.config(borderwidth=20, bg="skyblue")
root.columnconfigure(0,weight=1)
root.columnconfigure(1,weight=3)
root.columnconfigure(2,weight=3)

root.rowconfigure(tuple(range(9)),weight=5)
root.rowconfigure(tuple(range(9,30)),weight=1)

lblcodigo = Label ( root, text="Escribe tu codigo en esta area", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblcodigo.grid(row=0,column=0)

lblopciones = Label ( root, text="Opciones", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblopciones.grid(row=0,column=1, columnspan=2)

T_codigo = Text(root, height = 35, width =65 , font=("Showcard Gothic", 10, "bold"), padx=7)
T_codigo.grid(row=1,column=0, rowspan= 25)

lblmenuArchivo = Label ( root, text="Archivo: ", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblmenuArchivo.grid(row=1,column=1, sticky="w")

btn_Nuevo = customtkinter.CTkButton(root, text= "Nuevo", command =lambda: Nuevo(T_codigo))
btn_Nuevo.grid(row=2,column=1, sticky="news", padx=10, pady=10)

btn_Abrir = customtkinter.CTkButton(root, text= "Abrir", command =lambda: Abrir(T_codigo))
btn_Abrir.grid(row=2,column=2, sticky="news", padx=10, pady=10)

btn_Guardar = customtkinter.CTkButton(root, text= "Guardar", command =lambda: Guardar(T_codigo))
btn_Guardar.grid(row=3,column=1, sticky="news", padx=10, pady=10)

btn_GuardarC = customtkinter.CTkButton(root, text= "Guardar Como", command =lambda: GuardarC(T_codigo))
btn_GuardarC.grid(row=3,column=2, sticky="news", padx=10, pady=10)

btn_Salir = customtkinter.CTkButton(root, text="Salir", command =lambda: Salir(root))
btn_Salir.place(x=700, y=190)

btn_Datos = customtkinter.CTkButton(root, text="Temas de ayuda", command =Datos_user)
btn_Datos.place(x=965, y=190)

lblmenuAnalisis = Label( root, text="Analisis: ", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblmenuAnalisis.grid(row=5,column=1, sticky="w")

lblmenuTokens = Label( root, text="Tokens: ", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblmenuTokens.grid(row=7,column=1, sticky="w")

btn_Manual_user = customtkinter.CTkButton(root, text="Manual de Usuario", command =Manual_user)
btn_Manual_user.place(x=965, y=240)

btn_Manual_Tec = customtkinter.CTkButton(root, text="Manual de Tecnico", command =Manual_Tec)
btn_Manual_Tec.place(x=965, y=295)

btn_Tokens = customtkinter.CTkButton(root, text="Ver Tokens", command =verTokens)
btn_Tokens.place(x=700, y=295)

lblerrores = Label( root, text="Area de Errores ", font=("Showcard Gothic", 10, "bold"), bg = "skyblue")
lblerrores.grid(row=9,column=1, sticky="w")

frame_error = Frame(root, height=265)
frame_error.grid(row=10, column=1, columnspan = 2, rowspan = 3, sticky="nsew", padx=15)
frame_error.columnconfigure(0, weight=1)
frame_error.grid_propagate(False)

columnas = ("tipo","lin","col","token","desc")
T_error = ttk.Treeview(frame_error, columns=columnas, show="headings")
T_error.column("tipo", stretch=False, width=100)
T_error.heading('tipo', text='Tipo de Error')
T_error.column("lin", stretch=False, width=100)
T_error.heading('lin', text='Linea')
T_error.column("col", stretch=False, width=100)
T_error.heading('col', text='Posicion')
T_error.column("token", stretch=False, width=150)
T_error.heading('token', text='Token/Componente')
T_error.column("desc", stretch=False, width=450 )
T_error.heading('desc', text='Descripcion')

scrollbarx = ttk.Scrollbar(frame_error, orient=tk.HORIZONTAL, command=T_error.xview)
scrollbary = ttk.Scrollbar(frame_error, orient=tk.VERTICAL, command=T_error.yview)
T_error.grid(row=0, column=0, sticky='nsew')
scrollbary.grid(row=0, column=1, sticky='ns')
scrollbarx.grid(row=1, column=0, sticky='ew', columnspan = 2)

btn_Generar = customtkinter.CTkButton(root, text="Analizar", command =lambda: Analizar(T_codigo,T_error))
btn_Generar.place(x=700, y=240)

root.resizable(False, False)

root.mainloop()
