## Descrição

Este repositório possui a implementação de minha dissertação de Mestrado em Informática (Inteligência Artificial) pela Universidade de Brasília, realizado em 2019-2022, sobre o tópico **Efeitos do coarsening na classificação de grafos k-partidos**.
A branch `dissertacao` contém o exato código ao final do trabalho, e a branch `master` a versão mais atual com posteriores evoluções.
O objetivo deste repositório é, além de servir como histórico do trabalho, permitir que:
  - Os resultados encontrados sejam reproduzidos
  - Novos resultados sejam extraídos da ferramenta, permitindo que os resultados sejam extendidos para diferentes configurações de problemas reais
  - Servir como base para futuros trabalhos na área de Coarsening em Grafos K-Partidos

Para isso, abaixo estão apresentados os passos de instalação e uso do código.

A ideia central do algoritmo consiste em, dado um grafo k-partido onde se possui uma partição a qual se deseja classificar, utilizar dados de rótulos conhecidos nesta partição para guiar a redução, por coarsening, da quantidade de vértices e conexões. Como os métodos de classificação em grafos possuem complexidade normalmente associada ao número de vértices e arestas, a intenção deste procedimento é reduzir a necessidade de memória para armazenar as representações dos grafos e ainda possibilitar a redução no tempo de execução da classificação, e assim poder averiguar os impactos na qualidade dos resultados.


## Referência

>[1] Texto da dissertação: Althoff, Paulo E. e Faleiros, Thiago P.; Efeitos do coarsening na classificação de grafos k-partidos, Universidade de Brasília (UnB), 2022

>[2] Vídeo da defesa: _____


```
Aviso
-------
A implementação relativa aos resultados encontrados no documento referenciado está na branch `dissertacao`
A versão na branch `master` possui evoluções e está em desenvolvimento
```


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

A geração de grafos é realizada usando a ferramenta BNOC `([1] Valejo, Alan and Goes, F. and Romanetto, L. M. and Oliveira, Maria C. F. and Lopes, A. A., A benchmarking tool for the generation of bipartite network models with overlapping communities, in Knowledge and information systems, vol. 62, p. 1641-1669, 2019, doi: https://doi.org/10.1007/s10115-019-01411-9)` os parâmetros possíveis são descritos no repositório[BNOC](https://github.com/alanvalejo/bnoc),

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
  - a tag `dissertacao` corresponde a exata versão usada em [1](https://github.com/pealthoff/CoarseKlass/edit/master/README.md#refer%C3%AAncia), para replicação dos resultados
  - a branch `master` contém o código mais atual conforme os procedimentos são otimizados e está em desenvolvimento


## Bugs

- Se forem encontrados problemas na execução dos procedimentos aqui descritos ou na instalação do ambiente, por favor contate o autor:
- **Contato**:
  - Paulo Eduardo Althoff
  - pealthoff@gmail.com

## Créditos e Licenças

- Caso use este código, por favor referencie o trabalho referenciado [1](https://github.com/pealthoff/CoarseKlass/edit/master/README.md#refer%C3%AAncia)
- [Licença Pública Geral GNU v3.0](https://www.gnu.org/licenses/gpl-3.0.pt-br.html)


<div class="footer"> &copy; Copyright (C) 2022 Paulo Eduardo Althoff &lt;pealthoff@gmail.com&gt; All rights reserved.</div>
