**References**

>[1] Althoff, Paulo E. e Faleiros, Thiago P.; Efeitos do coarsening na classificação de grafos k-partidos

```
Aviso
-------
A implementação relativa aos resultados encontrados no documento referenciado está na branch `dissertacao`
A versão na branch `master` possui evoluções e está em desenvolvimento
```

Como reproduzir os resultados do documento de dissertação
Como realizar seus próprios experimentos com esta ferramenta
Como estender este código

A ideia central do algoritmo consiste em, dada uma partição a qual se deseja classificar, utilizar dados de rótulos conhecidos nesta partição para guiar a redução da quantidade de vértices e conexões. Como os métodos de classificação em grafos possuem complexidade normalmente associada ao número de vértices e arestas, a intenção deste procedimento é reduzir o tempo de execução da classificação, e assim poder averiguar os impactos na qualidade dos resultados.

## Sumário
##### Sumário
[Preparação](#preparacao)  
[Uso](#uso) 

Optionally, include a table of contents in order to allow other people to quickly navigate especially long or detailed READMEs.

## Preparação
### Pré-requisitos

- Python `3.9.7`
- Anaconda `3-2011.11-Linux-x86_64`
- Projetos clonados:
  - [Este projeto](https://github.com/pealthoff/CoarseKlass)
  - [BNOC](https://github.com/alanvalejo/bnoc)
  - [pynetviewer](https://github.com/alanvalejo/pynetviewer)


### Instalação

- A lista de pacotes python utilizada está no arquivo `requiremets.txt`, na raiz deste projeto
- Recomenda-se o uso da ferramenta Anaconda para gerenciamento dos mesmos.
  - O ambiente pode ser recriado usando o `Anaconda3-2011.11-Linux-x86_64` com o comando:
    - `conda create --name <env> --file requirements.txt` 
  - O código também foi testado em máquinas Windows instalando-se pacote a pacote descrito no mencionado arquivo.

### Configuração

- Os 3 projetos listados em [Pré-requisitos]() devem ser clonados em uma mesma pasta
- O ambiente descrito em [Instalação]() adiciona todos os pacotes necessários para os 3 projetos
- 3 diretórios devem ser adicionados na mesma pasta para onde os projetos foram clonados
  - input - É o diretório que irá conter os descritores das configurações de grafos
  - graphs - É o diretório que irá conter os arquivos dos grafos já gerados, com seus nós, arestas e classificações "corretas"
  - output - Neste diretório as métricas das classificações serão salvas, além dos gráficos gerados

## Uso

### Geração de grafos

### Coarsening + Classificação

### Experimentos

#### Geração dos descritores

#### Geração dos grafos

### Exemplos

#### Exemplo básico

#### Experimento 1 da dissertação
#### Experimento 2 da dissertação
#### Experimento com dados do DBLP

### Versionamento

Hoje o projeto contém duas versões:
  - a tag `dissertacao` corresponde a exata versão usada em [1], para replicação dos resultados
  - a branch `master` contém o código mais atual conforme os procedimentos são otimizados e está em desenvolvimento


## Bugs

- Se forem encontrados problemas na execução dos procedimentos aqui descritos ou na instalação do ambiente, por favor contate o autor:
- **Contato**:
  - Paulo Eduardo Althoff
  - pealthoff@gmail.com

## Créditos e Licenças

- Caso use este código, por favor referencie o trabalho referenciado [1]
- [Licença Pública Geral GNU v3.0](https://www.gnu.org/licenses/gpl-3.0.pt-br.html)


<div class="footer"> &copy; Copyright (C) 2022 Paulo Eduardo Althoff &lt;pealthoff@gmail.com&gt; All rights reserved.</div>
