print("oi")

g = "grafo"
s = {}
adicionados = {}
a = "partição alvo"
bfsList = [s[a]]
guia = {}
while len(bfsList) is not 0:
    v = bfsList.pop(0)
    for w in g[v]:
        if not adicionados[w]:
            adicionados[w] = True
            bfsList.append(w)
            guia[w] = v
