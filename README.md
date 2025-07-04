# Projet d'informatique : Mines Paris - PSL

**Groupe 1** : **_Analyse d’images pour le contrôle qualité des futurs modules du grand collisionneur de hadrons du CERN_**

Gabriel Vandersippe, Lucas Duhautois, Mathieu Jousson, Matthieu Benoit, Aurélien Bonin

**Pour utiliser le code** :

Aller dans le terminal (de préférence _Powershell_ pour avoir la progression du rendu affichée en temps réel), et entrer :

```
python check_wiring.py "ModulePictures/placeholder.jpg"
python absolute_coordinates.py "ModulePictures/placeholder.jpg"
```

En remplaçant `placeholder` par un fichier _câblé_ (contient "_Afterbonding_" ou "_Afterwirebonding_" dans son nom.) afin de compter les câbles sur un puce qui en contient. Certains fichiers sont volontairement choisis pour avoir des exemples d'images qui ne fonctionnent pas, et le ratio d'images avec un rendu inattendu est ainsi volontairement anormalement élevé.

**Contexte du projet** :

Dans le cadre du projet _ATLAS_ du CERN, le département de physique des particules (DPhP) de l'Institut de Recherche sur les lois Fondamentales de l'Univers (Irfu) du CEA Paris-Saclay travaille sur la construction d'un détecteur de très grande taille pour l'intégrer à un nouvel accélérateur de particules. Ce détecteur à pixels est constitué de modules, qui prennent la forme de cartes électroniques, et dont il faut vérifier avec précision la qualité de fabrication. En effet, il faut s'assurer que le câblage des modules est bien respecté, ce qui est très long et fastidieux à faire à la main (il y a environ 700 câbles par modules).

C'est ici qu'intervient notre projet, qui vise à apporter une aide au contrôle qualité des modules. Concrêtement notre objectif est d'aboutir à une fonction prenant en entrée le nom d'un fichier image contenant une photographie d'un module après câblage, et renvoyant des informations sur le module permetant d'accélerer et d'automatiser le processus de vérification (nombre de câbles attendus en fonction du numéro de série du module, nombre de câbles detectés, mise en évidence des câbles défectueux etc...).

**Répartition des tâches et déroulement du projet** :

Pendant la première partie du projet, le groupe s'est séparé en plusieurs sous groupes afin de travailler sur différents aspects du problème.

- Un premier groupe s'est occupé de mettre au point une fonction pouvant compter les câbles d'une image avec précision. Pour ce faire, on utilise le fait que les câbles sont très clairs par rapport au reste de l'image, il est ainsi possible de les détecter en analysant les variations de luminosité quand on parcours l'image de haut en bas. Cet aspect du problème est traité dans le fichier `count.py`.

- Un deuxième groupe s'est occupé de la reconnaissance des câbles à proprement parler. En effet, les résultats du premier groupe permettent d'obtenir la coordonnée, pour chacun des câbles de l'image, d'un pixel de ce câble (une "graine"), c'est comme cela que l'on compte le nombre de câbles. A l'aide de cette graine, on peut déduire la liste des coordonnées de l'ensemble des pixels constituant le câble, et ainsi récupérer toute les informations nécessaires concernant la position de ce dernier. Pour ce faire, on utilise un parcours en largeur, toujours en se basant sur le fait que les pixels des câbles sont plus clairs que ceux du reste de l'image. Cet aspect du problème est traité dans le fichier `wire.py`.

- Enfin, un troisième groupe s'est occupé de standardiser les images d'entrées, afin de pouvoir disposer d'un repère absolu pour analyser les images. Il a donc fallu trouver un moyen de recadrer l'image (rotation, translation, dilatation) grâce à des matrices de changement de base. L'utilité du repère absolu réside dans le fait de pouvoir déterminer la position des pads sur lesquels sont soudés les câbles. En combinant cette donnée avec celle de la position des câbles (fournie par le deuxième groupe), il est alors possible de s'assurer que les câbles sont bel et bien branchés au bon emplacement. Cet aspect du problème est traité dans les fichier `absolute_coordinates.py`, `find_absolute.py` et `recherche_pads.py`

Une fois ces fonctionnalitées implémentées, il a fallu combiner les différents programmes pour aboutir à un résultat global. Par manque de temps, nous n'avons réussi qu'à associer les fonctionnalités des deux premiers sous-groupes, il reste donc encore du travail afin d'obtenir la fonction globale que l'on s'était fixé comme objectif.

**Résultats** :

En définitive nous disposons, à la fin de ces cinq jours de travail, d'une fonction `analyseWires` prenant en entrée le nom du fichier d'une image contenant une photographie d'un module après câblage, et renvoyant les informations suivantes :

- Le nombre de câbles attendus, obtenu à l'aide du nom du fichier qui contient le numéro de série du module, permettant de déterminer quel bit est encodé sur ledit module, et donc de retrouver le nombre total de bits théoriquement présents sur l'image.

- Le nombre de câbles détectés, i.e. ceux qui ont étés effectivement repérés. Cela permet très facilement de se rendre compte s'il y a des câbles manquants ou en trop sur le module.

- Une image modifiée du module, où les câbles "problématiques" ont étés mis en surbrillance. Actuellement, le seul critère que nous avons eu le temps d'implémenter est si oui ou non deux câbles sont en contacts (collés ou croisés, car les câbles ne sont pas gainés, ce qui peut donc causer des courts-circuits).

**Performances** :

- Concernant le fichier qui détermine le repère absolu, on a une variabilité au niveau de la position de l'origine allant jusqu'à 10 pixels dans les pires cas, mais moins en moyenne (environ 2px à 5px), ce qui est acceptable pour la précision que l'on veut sur la position des autres éléments de la carte.
  Pour déterminer la matrice de passage ainsi que l'origine de ce repère, le programme prend quelques secondes à s'exécuter, ce qui est tout à fait raisonnable.

- Concernant le fichier `check_wiring.py`, celui-ci prend quelques minutes à s'exécuter (environ 4 minutes), et marque souvent des fils qui se ne se touchent pas vraiment comme étant en contact. Le contraire en revanche (manquer des fils qui se touchent) n'est pas arrivé à ce stade. Ceci n'est pas problématique donc, car nous visons à assister le travail de l'opérateur qui regarde les cartes à la main à ce stade, pour mettre en surbrillance les zones pententiellement mal câblées. 

**Pistes d'amélioration :**

Avec plus de temps à notre disposition, il aurait été possible de renvoyer plus d'information. Par exemple, deux fils en contact ne posent pas de problème s'ils sont reliés au même pad, et donc au même potentiel. Cette information nécessite de combiner les fonctionnalités du troisième groupe avec celles des deux premiers. Idem, on pourrait vérifier que les extrémités des câbles sont bien localisées sur les emplacements des pads, et mettre en surbrillance les câbles repérés comme défectueux.

Cependant, on dispose tout de même d'une fonction `repere_absolu` prenant en entrée le nom d'un fichier image et renvoyant la matrice de passage permetant de revenir à un repère absolu, ainsi que l'origine de ce repère. En plus de cette fonction, les positions des pads dans le repère absolu ont étés relevées, et sont référencées dans le fichier `data.py`.

Plus précisément, dans le fichier `repere_absolu.py`, il serait possible d'améliorer la performance de l'algorithme (déjà assez peu long) en modifiant la manière dont les contours supérieurs et inférieurs du PCB sont déterminés, par un algorithme de parcours de proche en proche par exemple, ou en réduisant le nombre de points et en les faisants plus adaptés à la forme de l'image (le slicing actuel étant purement arbitraire et choisi pour fonctionner sur cartes câblées et non câblées).
