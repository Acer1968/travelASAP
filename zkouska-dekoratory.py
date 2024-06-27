# %%
 
funkce = []


def pridej_funkci(func):
    funkce.append(func)
    return funkce

@pridej_funkci
def ahoj():
    print("Ahoj...")

@pridej_funkci
def nazdar():
    print("Nazdar...")

@pridej_funkci
def dobry_den():
    print("Dobry Den...")


if __name__ == "__main__":
    for f in funkce:
        f()

# %%
def co_se_deje(func):
    print("Aplikuji dekorátor")
    return func

@co_se_deje
def fib(x):
    """
    Spočítá x-té číslo ve Fibonacciho posloupnosti.
    """
    if x <= 1:
        return x
    print(x)
    return fib(x - 1) + fib(x - 2)

print(fib(7))
# %%
