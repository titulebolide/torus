class parseur:
    def __init__(self, code):
        self.memory = [0]*50000
        self.code_raw = code
        self.code = []

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
                pass #méthode pour capturer une entrée à définir
            elif premchar == "h":
                pass

            
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
                    readl(exp[i+1:])
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
        elif premchar == "g":
            self.memory[0] == self.parsenum(exp,1)
        elif premchar == "p":
            #definir la methode pour afficher entier
            self.memory[0] += 1
        elif premchar == "q":
            self.memory[0] += 1
            #idem avec ascii
        elif premchar in ["0","1","2","3","4","5","6","7","8","9","m","g","h","("]: #on est sur une affectation
            val1,i = self.parsenum(exp,0)
            if not exp[i] == "t":
                raise SyntaxError("Affectation structure awaiten " + exp)
            val2,i = self.parsenum(exp,i+1)
            self.memory[val2] = val1
            self.memory[0] += 1

    def runprgm(self):
        if self.code == []:
            self.clearify() #on enlève le superflu du programme
        while self.memory[0] < len(self.code):
            self.readl(self.code[self.memory[0]])
            print(self.memory[0])

    def __repr__(self):
        return str(self.memory[:10])

a = parseur(
"""(m2+43) t 2
(m1+42) t 1
(m1+m2) t 3
i m3=2 : 1t4
i m1=42 : 3t4""")
