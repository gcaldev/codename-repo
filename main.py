import gamelib
import random
import csv
import difflib

INOCENTE = 0
EQUIPO_ROJO = 1
EQUIPO_AZUL = 2
ASESINO = 3



def cantidad_jugadores():
    """
    Recibe la cantidad de jugadores que van a jugar al juego
    """
    players=gamelib.input("Ingrese la cantidad de jugadores")
    while not players or not players.isdigit() or players.isdigit() and int(players)%2!=0 or int(players) < 4:
        players=gamelib.input("El numero de jugadores debe ser entero y par(Mayor a 4)")
    return int(players)



def asignar_categoria(categorias):
    """Recibe un diccionario con los tipos de agentes y devuelve
    una categoria aleatoria"""
    if not any(list(categorias.values())):
        return None
    categoria_select=random.choice(list(categorias.keys()))
    while categorias[categoria_select] == 0:
        categoria_select=random.choice(list(categorias.keys()))
    categorias[categoria_select]=categorias[categoria_select] - 1 #Se resta la categoria seleccionada para que no se repita mas de lo permitido
    return categoria_select


def cargar_palabras():
    """
    Carga las palabras que van a ir en las tarjetas del tablero, desde una archivo
    """
    with open("dataset.txt",encoding="utf-8") as file:
        data = file.read().replace(" ","").split(",")
    palabras = list()
    for casillero in range(25):
        agregar_elemento(palabras,data)
    return palabras

def agregar_elemento(lista,data):
    """Recibe la lista de palabras, devuelve una
    palabra aleatoria y evita que se repitan"""
    eleccion=random.choice(data)
    while eleccion in lista:
        data.remove(eleccion)
        eleccion=random.choice(data)
    lista.append(eleccion)
    
def inicializar_equipos():
    """
    Funcion auxiliar para la creaacion de los equipos
    """
    jugadores = cantidad_jugadores() // 2
    team_blue=Equipo()
    team_red=Equipo()
    team_blue.cantidad_jugadores = team_red.cantidad_jugadores = jugadores
    return team_blue, team_red , jugadores

def dibujar_juego(juego,jugadores_por_equipo,team_blue,team_red,palabra,cantidad):
    """
    Contiene funciones relacionadas al dibujado de la partida y muestra en pantalla informacion de la misma
    """
    gamelib.draw_image("images/background.gif",0,0)
    if juego.terminado(jugadores_por_equipo):
        mostrar_resultado([team_blue, team_red])
        juego.turno[1] = False
    else:
        if not juego.turno[1]:
            gamelib.draw_image("images/boton.gif",660,620)
            gamelib.draw_text("PASAR",807,705,size=38,fill="Black")
        else:
            juego.generar_llave()
        juego.generar_tablero([team_blue, team_red])
        if juego.turno[0]:
            gamelib.draw_text("TURNO: AZUL",260,760,size=35,fill="Blue")
        else:
            gamelib.draw_text("TURNO: ROJO",260,760,size=35,fill="Red")
        gamelib.draw_text(f"PUNTUACION AZUL: {team_blue.puntaje_equipo}",350,700,size=35,fill="Blue")
        gamelib.draw_text(f"PUNTUACION ROJO: {team_red.puntaje_equipo}",1250,700,size=35,fill="Red")
        gamelib.draw_text(f"RONDA: {juego.ronda+1}",1105,745,size=35,fill="Yellow")
        dibujar_pista(palabra,cantidad)

def dibujar_pista(palabra,cantidad):
    """
    Muestra en pantalla la pista y la cantidad de agentes relacionados que ingreso el spymaster
    """
    if palabra and cantidad!=None:
        gamelib.draw_text(f"PISTA ACTUAL: {palabra}",255,808,size=25,fill="white")
        gamelib.draw_text(f"AGENTES",1073,787,size=25,fill="white")
        gamelib.draw_text(f"RELACIONADOS: {cantidad}",1140,820,size=25,fill="white")
    else:
        gamelib.draw_text(f"PISTA ACTUAL: N/A",255,808,size=25,fill="white")
        gamelib.draw_text(f"AGENTES",1073,787,size=25,fill="white")
        gamelib.draw_text(f"RELACIONADOS: N/A",1160,820,size=25,fill="white")

def main():
    juego = EstructuraDeJuego()
    team_blue, team_red, jugadores_por_equipo = inicializar_equipos()
    gamelib.resize(1600, 1000)
    palabra=None
    cantidad=None
    while gamelib.is_alive():
        gamelib.draw_begin()
        dibujar_juego(juego,jugadores_por_equipo,team_blue,team_red,palabra,cantidad)
        gamelib.draw_end()
        if juego.turno[1]:
            palabra , cantidad = juego.pedir_pista()
            if not juego.pista_es_valida(palabra):
                juego.penalizar([team_blue, team_red])
            else:
                juego.turno[1] = False
        ev = gamelib.wait()
        if not ev:
            break
        if ev.type == gamelib.EventType.KeyPress and ev.key == 'Escape':
            break
        if ev.type == gamelib.EventType.ButtonPress and not juego.terminado(jugadores_por_equipo):
            x, y = ev.x, ev.y
            juego.pedir_agente(x,y,[team_blue,team_red], cantidad)
            pasar_turno(juego, x, y)
        
        
class EstructuraDeJuego():
    def __init__(self):
        self.rondas = int()
        self.turno=[True,True]
        self.ancho=5
        self.alto=5
        self.ronda = 0
        self.categorias={INOCENTE:6,EQUIPO_ROJO:9,EQUIPO_AZUL:9,ASESINO:1} 
        self.tablero=self.crear_tablero() #Contiene todas las cartas

    
    def crear_tablero(self):
        """
        Devuelve una lista que contiene todas las cartas
        """
        palabras=cargar_palabras()
        lista_cartas=list()
        for y in range(self.ancho):
            for x in range(self.alto):
                categoria_ID=asignar_categoria(self.categorias)
                palabra_actual=palabras.pop(0)
                lista_cartas.append(Carta((260+(x*200),(y*120)),palabra_actual,categoria_ID))#Realiza los llamados con posiciones diferentes
        return lista_cartas
    
    
    def generar_tablero(self,equipos):
        """
        Dibuja las cartas dependiendo de su estado actual
        """
        equipo_azul,equipo_rojo=equipos
        for i in range(len(self.tablero)):

            if not self.tablero[i].levantada:

                gamelib.draw_image("images/carta2.gif",self.tablero[i].posicion[0],self.tablero[i].posicion[1])#recibe la posicion en x,y de cada carta

            else:

                if self.tablero[i].categoria==EQUIPO_ROJO:
                    gamelib.draw_image("images/agente_rojo_1.gif",self.tablero[i].posicion[0],self.tablero[i].posicion[1])

                if self.tablero[i].categoria==EQUIPO_AZUL:
                    gamelib.draw_image("images/agente_azul_1.gif",self.tablero[i].posicion[0],self.tablero[i].posicion[1])

                if self.tablero[i].categoria==ASESINO:
                    gamelib.draw_image("images/ASESINO.gif",self.tablero[i].posicion[0],self.tablero[i].posicion[1])

                if self.tablero[i].categoria==INOCENTE:
                    gamelib.draw_image("images/INOCENTE_1.gif",self.tablero[i].posicion[0],self.tablero[i].posicion[1])

            gamelib.draw_text(self.tablero[i].palabra,self.tablero[i].posicion[0]+147,self.tablero[i].posicion[1]+112,fill="black",size=18)#dibuja el texto basandose en la posicion de cada carta
        gamelib.draw_text(f"PUNTUACION AZUL: {equipo_azul.puntaje_equipo}",350,700,size=35,fill="Blue")
        gamelib.draw_text(f"PUNTUACION ROJO: {equipo_rojo.puntaje_equipo}",1250,700,size=35,fill="Red")
        if self.turno[0]:
            gamelib.draw_text("TURNO: AZUL",260,760,size=35,fill="Blue")
        else:
            gamelib.draw_text("TURNO: ROJO",260,760,size=35,fill="Red")
    
    def generar_llave(self):
        """
        Genera la llave que se mostrara a los SpyMasters
        """
        y=x=i=0
        if self.turno[1]:
            if self.turno[0]:
                gamelib.draw_image("images/llave azul.gif",650,650)
            else:
                gamelib.draw_image("images/llave rojo.gif",650,650)
            while y<self.alto:
                if self.tablero[i].categoria==ASESINO:
                    gamelib.draw_image("images/pieza_negra.gif",690+(x*45),685+(y*45))
                if self.tablero[i].categoria==INOCENTE:
                    gamelib.draw_image("images/pieza_amarillo.gif",690+(x*45),685+(y*45))
                if self.tablero[i].categoria==EQUIPO_AZUL:
                    gamelib.draw_image("images/pieza_azul.gif",690+(x*45),685+(y*45))
                if self.tablero[i].categoria==EQUIPO_ROJO:
                    gamelib.draw_image("images/pieza_rojo.gif",690+(x*45),685+(y*45))
                x+=1
                i+=1
                #El indice i recorre cada carta y x,y posicionan cada pieza
                if x==self.ancho:
                    x=0
                    y+=1
    

    def pedir_agente(self,x,y,equipos, cantidad):
        """
        Solicita que se seleccione a un agente
        """
        for i in range(len(self.tablero)):
               #Se recorre cada carta y se chequea que las x,y esten dentro de las dimensiones reales de la misma
            if self.tablero[i].dimensiones()[0][0]<x<self.tablero[i].dimensiones()[0][1] and self.tablero[i].dimensiones()[1][0]<y<self.tablero[i].dimensiones()[1][1]:
                if not self.tablero[i].levantada:
                    self.tablero[i].levantada=True
                    self.actualizar_estado_del_juego(equipos,i, cantidad)
                    if self.es_ronda_terminada(equipos,i):
                        self.ronda_terminada()
                    break
    
    def pedir_pista(self):
        """
        Recibe una palabra y un numero ingresada por el Spymaster
        """
        palabra=None
        cantidad_cartas=None

        while not palabra or not palabra.isalpha():
            palabra=gamelib.input("Ingrese una palabra de pista")

        while not cantidad_cartas or not cantidad_cartas.isdecimal() or int(cantidad_cartas)>25:
                cantidad_cartas=gamelib.input("Ingrese la cantidad de agentes que se relacionan a la pista")

        self.turno[1] = False
        return palabra,int(cantidad_cartas)

    def pista_es_valida(self, palabra):
        
        """Corrobora que el spymaster no haya ingresado una palabra similar
        a la de alguna de las cartas
        """
        palabra=palabra.lower()

        for carta in self.tablero:
            comparar=difflib.SequenceMatcher(a=palabra,b=carta.palabra)#la libreria difflib compara la cadena ingresada como pista con la cadena de cada carta y devuelve como resultado un valor entre 0 y 1 el cual se refiere a que tan similares son las cadenas ingresadas
            similitud=comparar.ratio()

            if similitud>=0.8:

                return False
        return True
    
    def penalizar(self,equipos):
        """
        Penaliza al SpyMaster al ingresar una pista invalida
        """
        equipo_azul, equipo_rojo = equipos

        if not self.turno[0]:
            for i in range(len(self.tablero)):
                if self.tablero[i].categoria == EQUIPO_AZUL and not self.tablero[i].levantada:
                    equipo_azul.puntaje_equipo += 1
                    equipo_azul.acierto += 1
                    self.tablero[i].levantada=True
                    break

        else:
            for i in range(len(self.tablero)):
                if self.tablero[i].categoria == EQUIPO_ROJO and not self.tablero[i].levantada:
                    equipo_rojo.puntaje_equipo += 1
                    equipo_rojo.acierto += 1
                    self.tablero[i].levantada=True
                    break

        self.cambiar_turno()

    def actualizar_estado_del_juego(self,equipos,i, cantidad_pista):
        """
        Actualiza el estado del juego dependiendo de lo que presione el usuario
        """
        equipo_azul, equipo_rojo = equipos

        if self.tablero[i].categoria == INOCENTE:
            if self.turno[0]:
                equipo_azul.puntaje_equipo -= 1
            else:
                equipo_rojo.puntaje_equipo -= 1

            self.reiniciar_aciertos_por_turno(equipos)
            self.cambiar_turno()

        if self.tablero[i].categoria == ASESINO:
            if self.turno[0]:
                equipo_azul.puntaje_equipo -= 5
            else:
                equipo_rojo.puntaje_equipo -= 5

            self.reiniciar_aciertos_por_turno(equipos)
            self.ronda_terminada()

        if self.tablero[i].categoria== EQUIPO_AZUL:
            equipo_azul.puntaje_equipo += 1
            equipo_azul.acierto += 1
            equipo_azul.acierto_por_turno += 1

           

            if not self.turno[0] or equipo_azul.acierto_por_turno == (cantidad_pista + 1):
                self.reiniciar_aciertos_por_turno(equipos)
                self.cambiar_turno()
                

        if self.tablero[i].categoria == EQUIPO_ROJO:

            equipo_rojo.puntaje_equipo += 1
            equipo_rojo.acierto += 1
            equipo_rojo.acierto_por_turno += 1



            if self.turno[0] or equipo_rojo.acierto_por_turno == (cantidad_pista + 1):
                self.reiniciar_aciertos_por_turno(equipos)
                self.cambiar_turno()
                
    
    def cambiar_turno(self):
        """
        Cambia el turno
        """
        self.turno[0] = not self.turno[0]
        self.turno[1] = True

    def es_ronda_terminada(self,equipos,i):
        """
        Determina si la ronda esta terminada o no 
        """
        equipo_azul,equipo_rojo=equipos
        return equipo_azul.acierto==9 or equipo_rojo.acierto==9 or self.tablero[i].categoria==ASESINO
    
    def ronda_terminada(self):
        """
        Se encarga de terminar la ronda 
        """
        self.ronda += 1
        self.categorias={INOCENTE:6,EQUIPO_ROJO:9,EQUIPO_AZUL:9,ASESINO:1}
        self.tablero=self.crear_tablero()
        self.cambiar_turno()

    def terminado(self,jugadores):
        """
        Si ya se jugo la misma cantidad de rondas que jugadores por equipo devuelve True
        """
        return self.ronda == jugadores

    def reiniciar_aciertos_por_turno(self, equipos):
        equipo_azul , equipo_rojo = equipos
        equipo_rojo.acierto_por_turno = 0
        equipo_azul.acierto_por_turno = 0
class Carta():

    def __init__(self,posicion,palabra,categoria,levantada=False):
        self.posicion=posicion
        self.palabra=palabra
        self.levantada=levantada
        self.categoria=categoria

    def dimensiones(self):
        """
        Devuelve el espacio en pixeles que ocupa la carta
        """
        carta_tamaño=((self.posicion[0]+52,self.posicion[0]+247),(self.posicion[1]+22,self.posicion[1]+140))#La tupla en i=0 contiene los bordes minimos y maximos de x,en i=1 lo mismo para y
        return carta_tamaño


class Equipo():

    def __init__(self):
        self.cantidad_jugadores = 0
        self.puntaje_equipo = 0
        self.acierto = 0
        self.acierto_por_turno = 0


def mostrar_resultado(equipos):
    """
    Muestra el resultado de la partida
    """
    equipo_azul, equipo_rojo = equipos

    if equipo_azul.puntaje_equipo > equipo_rojo.puntaje_equipo:
        gamelib.draw_text(f"GANADOR: AZUL {equipo_azul.puntaje_equipo} pts.",860,500,size=45,fill="Blue")
        gamelib.draw_text(f"Puntaje del equipo rojo {equipo_rojo.puntaje_equipo}",693,545,size=20,fill="Red")
    else:
        gamelib.draw_text(f"GANADOR: ROJO {equipo_rojo.puntaje_equipo} pts.",860,500,size=45,fill="Red")
        gamelib.draw_text(f"Puntaje del equipo azul {equipo_azul.puntaje_equipo}",693,545,size=20,fill="Blue")


def pasar_turno(juego,x, y):
    """
    Pasa el turno si el usuario presiona el boton de pasar turno
    """
    if 706 < x < 912 and 662 < y < 745:
        juego.turno[0]=not juego.turno[0]
        juego.turno[1]=True
        
gamelib.init(main)