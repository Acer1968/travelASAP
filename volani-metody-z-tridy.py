#%%
class Pokus():

    def vnitrniFunkce(self,c):
        self.c = c
        print("Po volání vnitřní funkce")
        print(self.c)
        return self.c

    def __init__(self,a,b):
        self.a = a
        self.b = b
        print("Před voláním vnitřní funkce")
        self.c = self.vnitrniFunkce(self.a + self.b)



#%%
prvni = Pokus(5,6)

# %%
