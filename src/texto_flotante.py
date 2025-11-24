import pygame
class TextoFlotante:
    #el constructor
    def __init__(self, texto, x, y, color=(255, 255, 255)):
        
        #guardo la fuente que usare 
        self.fuente = pygame.font.Font(None, 50)#fuente pequeña para el daño
        
        #renderizo el texto (se crea la imagen del numero)
        self.imagen = self.fuente.render(str(texto), True, color)
        
        #guardo la posicion con floats, para moverlo suave
        self.x_float = float(x)
        self.y_float = float(y)
        
        self.velocidad_y = -0.5 #velocidad hacia arriba (negativo es para arriba)
        self.duracion = 60 # tiempo de vida en frames 60 frames= 1 seg
        
    #el update 
    #aca se llama en cada frame de la batalla
    def update(self):
        #el texto se mueve para arriba
        self.y_float += self.velocidad_y
        #le resto 1 a su vida
        self.duracion -= 1
    def esta_muerto(self):
        #si la duracion llega a 0 se muere
        return self.duracion <= 0
    
    #aca va el draw
    #esto se encarga de dibujar en la pantalla
    def draw(self, pantalla):
        #se dibuja la imagen del texto en la posicion  (se redondea a entero)
        pantalla.blit(self.imagen, (int(self.x_float), int(self.y_float)))