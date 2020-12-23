# coding: utf8

from tkinter import *
from tkinter.filedialog import *
import os


class parseur:
    def __init__(self, code):
        self.memory = [0]*50000
        self.code_raw = code
        self.code = []
        self.output = ""
        self.input = ""

    def getoutput(self):
        return self.output

    def setinput(self, val):
        self.input = val

    def clearify(self): #supprime l'inutile du code
        self.code = [""]
        i = 0
        while i<len(self.code_raw):
            char = self.code_raw[i]
            if char == "#": #on est sur un commentaire
                try:
                    i += self.code_raw[i:].index("\n")-1 #on se met en fin de ligne et on laisse l'autre tour de boucle gerer le retour à la ligne
                except ValueError:
                    break
            elif char == "\n": #retour à la ligne
                 if self.code[-1] != "": #si la dernière ligne créée est pas vide, on en recree une
                    self.code.append("")
                #sinon on continue à remplir la meme ligne
            elif not char in [" ","\t"]: #sinon, si le caractère n'est pas un espace ou un tab on l'enregistre
                self.code[-1] += char
            i += 1
        
    def parsenum(self, ligne, posdeb): #retourne la valeur de l'expression entre parentheses (première parenthèse à l'index posdeb) ou la valeur du nombre si pas de parenthèses et la position du pointeur à prendre pour etre juste après la parenthèse

        premchar = ligne[posdeb]

        if premchar in ["0","1","2","3","4","5","6","7","8","9"]: #on ne parse qu'un simple nombre, on recherche jusqu'à la fin
            val = 0
            i = posdeb
            while i < len(ligne):
                temp = ligne[i]
                if temp in ["0","1","2","3","4","5","6","7","8","9"]:
                    val = val*10+int(temp)
                else:
                    break
                i += 1
            return val, i #la position prochaine renvoyée est égale à len(ligne) si on a fini la ligne

        
        elif premchar in ["m","g","h"]: #on parse une entrée ou une accession mémoire
            temp,foo = self.parsenum(ligne, posdeb+1)
            if premchar == "m":
                return self.memory[temp], foo
            elif premchar == "g":
                temp = self.input[0]
                self.input = self.input[1:] #on supprime la première entrée
                return int(temp)
            elif premchar == "h":
                temp = self.input[0]
                self.input = self.input[1:] #on supprime la première entrée
                return ord(temp)
            
        elif premchar == "(": #on parse une expression
        
            lignebis = ""
            i = posdeb + 1
            #on remplace toutes les parenthèses de plus bas niveau par leur valeurs par récursivité en construisant une nouvelle ligne appelée lignebis en enlevant le superflu
            #ex: "g(1*(3+4)+(3*4))" ---> "1*7+12"
            while True:
                try:
                    char = ligne[i]
                except IndexError:
                    raise SyntaxError("""A ")" is missing""")
                if char == "(":
                    temp,i = self.parsenum(ligne,i)
                    lignebis += str(temp)
                elif char == ")":
                    break
                else:
                    lignebis += char
                    i+=1
            posfin = i+1 #on récupère la valeur de la position finale de l'expression (position juste après la parenthèse)
            #on détache un a un les nombres que l'on enregistre dans l'ordre dans "nombres"
            #on enregistre dans "operations" la position des "+","-","*","/" dans l'ordre dans lequel ils viennent dans le calcul
            #(les "-" sont enregistrés comme des + et rendent les nombre suivant négatif (on enregistre l'index dans "nombres" du nombre de gauche))
            #ex: "-1+3*4-81" ---> operations = ["+","*","+"] ; nombres = [-1,3,4,-81] ; opeprio = 1
            nombres = []
            operations = []
            opeprio = [] #liste des emplacements des opérations prioritaires dans "operations"
            nextisnegative = False #booléen qui indique si il faut enregistrer l'opposé du prochain nombre ou tel quel
            i = 0 #pointeur dans la ligne
            while i<len(lignebis):
                char = lignebis[i]
                if char in ["0","1","2","3","4","5","6","7","8","9","m","g","h"]: #on capture un nombre
                    temp, i = self.parsenum(lignebis,i)
                    if nextisnegative:
                        nombres.append(-temp)
                        nextisnegative = False
                    else:
                        nombres.append(temp)
                elif i != 0: #dans ce cas on n'a normalement que des opérations, on ne s'y intéresse que si on n'est pas au tout début
                    if char in ["*","/"]:
                        operations.append(char)
                        opeprio.append(len(nombres)-1)
                    elif char == "+":
                        operations.append("+")
                    elif char == "-":
                        nextisnegative = True
                        operations.append("+")
                    else:
                        raise SyntaxError("Unvalid character "+char) 
                    i += 1
                elif char == "-": #cas ou le premier caractère est un moins
                    nextisnegative = True
                    i += 1
                    
            #on fait les multiplication et division en premier
            for foo,ope in enumerate(opeprio):
                #l'opeprio se situe en i = ope-foo car foo est le nombre d'ope deja faites et elles sont faites de la gauche vers la droite, et à chaque fois on retire un élément de nombre
                #et puisque c'est fait de la gauche vers la droite, alors c'est à gauche de i que l'on avait supprimé des éléments, d'où le -foo
                i = ope-foo
                char = operations[i]
                if char == "*":
                    nombres[i] = nombres[i]*nombres[i+1]
                elif char == "/":
                    nombres[i] = nombres[i]//nombres[i+1]
                else: #ce cas n'est pas censé arriver
                    raise SystemError("Internal Error")
                del nombres[i+1]
                del operations[i]
            #il ne reste que des additions
            res = sum(nombres)
            return res, posfin


        else:
            SyntaxError("Number parsing ignited on a incorrect value "+ premchar)

    def readl(self, exp):
        premchar = exp[0]
        if premchar == "i": #on est dans le cas d'un if
            num1,i = self.parsenum(exp,1)
            cond = exp[i]
            num2,i = self.parsenum(exp,i+1)
            if not exp[i] == ":":
                raise SyntaxError("""":" awaited in a if structure""")
            if cond == "<":
                if num1<num2: #soit la condition est vérifiée et on s'occupe de ce qu'il y a après le :
                    self.readl(exp[i+1:])
                else: #soit on passe à la ligne suivante
                    self.memory[0] += 1
            elif cond == ">":
                if num1>num2: #soit la condition est vérifiée et on s'occupe de ce qu'il y a après le :
                    self.readl(exp[i+1:])
                else: #soit on passe à la ligne suivante
                    self.memory[0] += 1
            elif cond == "=":
                if num1==num2: #soit la condition est vérifiée et on s'occupe de ce qu'il y a après le :
                    self.readl(exp[i+1:])
                else: #soit on passe à la ligne suivante
                    self.memory[0] += 1
            else:
                SyntaxError("""Bad control structure :""" + cond)
        elif premchar == "j":
            self.memory[0] = self.parsenum(exp,1)[0]
        elif premchar == "p":
            temp = self.parsenum(exp,1)[0]
            self.output += str(temp)
            self.memory[0] += 1
        elif premchar == "q":
            temp = self.parsenum(exp,1)[0]
            self.output += str(chr(temp))
            self.memory[0] += 1
        elif premchar in ["0","1","2","3","4","5","6","7","8","9","m","g","h","("]: #on est sur une affectation
            val1,i = self.parsenum(exp,0)
            if not exp[i] == "t":
                raise SyntaxError("Affectation structure awaiten")
            val2,i = self.parsenum(exp,i+1)
            self.memory[val2] = val1
            self.memory[0] += 1

    def runprgm(self):
        if self.code == []:
            self.clearify() #on enlève le superflu du programme
        while self.memory[0] < len(self.code):
            self.readl(self.code[self.memory[0]])

    def __repr__(self):
        return str(self.memory[:10])


class prgm():    
    def __init__(self):
        self.reset = False
        self.filepath = ""
        self.erroroccured = False #mis à True si une erreur survient pour stopper le programme


        #général
        self.fenetre = Tk()
        self.fenetre.title("Torus Interpreter 1.0 - untitled.to")

        self.fenetre.bind("<F1>", lambda event: self.bfall())
        self.fenetre.bind("<F2>", lambda event: self.havereset())

        ##framecode
        framecode = LabelFrame(self.fenetre, text = "Code")
        framecode.pack(fill = BOTH)

        #framecode1
        framecode1 = Frame(framecode)
        framecode1.pack(side = TOP, fill = BOTH)

        scroller = Scrollbar(framecode1)
        scroller.pack(side = RIGHT, fill = Y)
        self.code = Text(framecode1, height = 44)
        scroller.config(command=self.code.yview)
        self.code.config(yscrollcommand=scroller.set)
        self.code.pack(fill = BOTH)
        self.code.tag_configure('big', font=('DejaVu Sans Mono', 10, 'bold'), foreground = "red", underline = True) #forme de l'élément lu

        #framecode2
        framecode2 = Frame(framecode)
        framecode2.pack(side = TOP, fill = BOTH)

        Button(framecode2, text = "RUN CODE (F1)", command = self.bfall).pack(fill = BOTH)


        ##frameIO
        frameIO = LabelFrame(self.fenetre, text = "Input/Output")
        frameIO.pack(fill = BOTH)

        #frameIO1

        frameIO1 = Frame(frameIO)
        frameIO1.pack(side = TOP, fill = BOTH)

        Label(frameIO1, text = """Input:   """).pack(side = LEFT)

        self.entrevar = StringVar()
        Entry(frameIO1, textvariable = self.entrevar).pack(fill = BOTH)

        #frameIO2

        frameIO2 = Frame(frameIO)
        frameIO2.pack(fill = BOTH)

        Label(frameIO2, text = """Output: """).pack(side = LEFT)

        self.sortievar = StringVar()
        Entry(frameIO2, textvariable = self.sortievar).pack(fill = BOTH)

        ##menu
        menubar = Menu(self.fenetre)
        
        menu1 = Menu(menubar, tearoff=0)

        menu1.add_command(label="New File", command=self.newfile)
        menu1.add_command(label="Open", command=self.openfile)
        menu1.add_command(label="Save", command=self.savefile)
        menu1.add_command(label="Save As", command=self.savefileas)
        menubar.add_cascade(label="Fichier", menu=menu1)

        self.fenetre.config(menu=menubar)

        ##launch
        self.iptr = parseur("") #on initialise l'interpreteur avec un code vide
        self.fenetre.mainloop()

    
    def resetvariables(self):
        self.iptr.__init__(self.code.get("1.0", "end-1c"))
        self.iptr.setinput(self.entrevar.get())
        self.stepbystepon = False
        self.reset = False
        self.setdisplay()
        self.erroroccured = False
        
    def setdisplay(self):
        self.sortievar.set(self.iptr.output)

    def bfall(self):
        self.resetvariables()
        self.iptr.runprgm()
        self.setdisplay()

    def refreshtitle(self): #permet d'écrire le titre de la fenetre en fonction du nom du fichier
        foo = -(self.filepath[::-1].index("/"))
        self.fenetre.title("TORUS Interpreter 1.0 - " + self.filepath[foo:])

    def newfile(self):
        self.filepath = ""
        self.code.delete(1.0, END)
        self.refreshtitle("/untitled.to")
        self.havereset()

    def openfile(self):
        self.filepath = askopenfilename(initialfile = os.getcwd(), title="Open",filetypes=[('torus files', '.to'),('all files','.*')])
        if self.filepath != '':
            f = open(self.filepath, 'r')
            self.code.delete(1.0, END)
            for l in f:
                self.code.insert(END, l)
            f.close()
        self.refreshtitle()

    def savefileas(self):
        self.filepath = asksaveasfilename(initialfile = os.getcwd(), title= "Save Under", filetypes=[('torus files', '.to'),('all files','.*')])
        f = open(self.filepath, 'w')
        f.write(self.code.get("1.0", "end-1c"))
        f.close()
        self.refreshtitle()

    def savefile(self):
        if self.filepath == '':
            self.savefileas()
        else:
            f = open(self.filepath, 'w')
            f.write(self.code.get("1.0", "end-1c"))
            f.close()
            
app = prgm()


