# SR-Game
Jeu en système distribué dans le cadre du cours de SR (ESIR3)

## Auteurs
* [Benjamin De Zordo](https://github.com/FenrirWolf4566/)
* [Louis Ruellou](https://github.com/Spraduss)
* [Yanis Bouger](https://github.com/12-3-8-s9b9o9j9t)

## Explications du jeu
SR-Game (Super Réunion Game) est un jeu qui voit s'affronter deux joueurs sur un plateau prédéfinis. L'objectif des joueurs est de manger les fruits, le gagnant est décidé à la fin de la partie. La partie est automatiquement terminée lorsque tous les fruits ont été mangés.

Initialement, l'histoire du jeu est la suivante : deux réunionnais sont dans un verger et se battent pour ramasser le plus de fruits. Nous comptions ajouter un système de collision particulier permettant de faire perdre des fruits à l'adversaire afin de faire durer un peu plus les parties et les rendre plus intéressantes. Cependant, ce système, ainsi que des améliorations de l'interface graphique n'ont pas pu être faites par manque de temps (voir la section "Difficultés" pour connaître les raisons).

# Détails techniques

## Choix du langage (Python)
Nous avons donc choisi d'utiliser Python comme langage, cela pour 4 raisons principales :
* C'est un langage avec lequel nous sommes tous les trois familier, ce qui nous permet de développer plus rapidement, car nous connaissons les librairies de base et les fonctions utiles.
* La librairie Pygame est très bien documentée et permet de créer rapidement des interfaces graphiques simples.
* Pour la communication entre le client et le serveur, il existe là aussi des librairies comme socket.
* Enfin, concernant les tests, il est également possible d'en faire avec Pytest ou encore Unitest.

## Architecture Client-serveur
Dans les deux architectures possibles, nous avons choisi d'opter pour une architecture de type Client/Serveur (et non pas Peer to Peer).

Ce choix nous a permis de mieux nous répartir les tâches en isolant les deux comportements (serveur d'un côté, client de l'autre).

Un avantage indirect de cette solution est d'éviter d'avantager le joueur qui "host" la partie.

## Serveur
Dans notre jeu, le serveur est uniquement dédié à la gestion du jeu. Il est chargé d'envoyer l'état du plateau (positions des joueurs et fruits) aux différents clients, de recevoir les déplacements de ces derniers et de les gérer :
* Collision avec les bordures
* Collision avec un autre joueur
* Ramassage d'un fruit

En étant limité à deux joueurs et quinze fruits, on peut vérifier pour chaque déplacement les distances avec chaque élément. Dans le pire cas, cela représente 16 calculs de distance (1 autre joueur et 15 fruits) et quatre vérifications de coordonnées (bordures) à chaque déplacement.

Bien que cette stratégie ne soit absolument pas viable si on commence à vouloir augmenter le nombre de joueurs, dans notre cas, elle n'impacte pas les performances.

Les déplacements des clients sont gérés avec la logique FIFO (First In First Out), ou premier arrivé, premier servi. Comme nous considérons que les deux clients sont distants, nous avons estimé qu'il s'agissait d'un bon équilibre entre la simplicité et l’équité.

## Client
Le client utilise la librairie Pygame pour afficher une interface graphique et "écouter" les inputs de l'utilisateur. Dans notre cas, uniquement les flèches directionnelles où Z/Q/S/D.

Le comportement du client est déterminé à partir des données reçues. On peut distinguer les comportements suivants :
* Si les données contiennent un champ "ID", cela signifie que l'on attend qu'un autre joueur se connecte. Ce champ permettra de s'identifier dans les futures données reçues du serveur.
* Si les données contiennent un champ "score", il s'agit de la liste des joueurs de la forme [id, score, x, y]. Il s'agit du message indiquant la fin de la partie qui déclenche l'affichage de l'écran de fin.
* Sinon, les données contiennent les champs "players", similaire au champ score vus précédemment, et "fruits" qui contient les coordonnées des fruits à afficher.

Les inputs sont simplement envoyés au serveur avec le code suivant :
* UP / Z : 1
* DOWN / S : 2
* RIGHT / D : 3
* LEFT / Q : 4

## Network et communication
Suite à quelques soucis concernant la communication, notamment dus à la taille du buffer de lecture, nous avons opté pour la stratégie suivante : lorsque A envoie un message à B, la fonction qui s'occupe de l'envoi ajoutera un préfixe de quatre caractères au message. Ces derniers représentent la taille du message en bytes. Par exemple, l'envoie de la chaîne "Hello World!", le préfixe sera "0011" (utf-8 donc 1 bytes par caractère).

Ainsi, à la réception, nous commençons par lire les 4 premiers caractères (buffer_size = 4), et nous les convertissons en int. Cela nous donne la taille du message à venir (11 dans notre exemple) ce qui nous permet d'avoir un buffer_size constamment adapté.

Comme dit précédemment, les messages échangés doivent être sous forme binaire. Dans le cas de la communication du client vers le serveur, c'est le cas. Cependant, du serveur vers le client, puisque le message est plus complexe (format JSON), nous avons choisi de convertir ce dernier en base64 en de l'envoyer. Cela nous permet de raccourcir le nombre de bits à envoyer.

Cette stratégie a été adoptée avant de rencontrer certaines difficultés, et nous envisagions encore d’étendre le jeu à plus de joueurs, et donc avoir des messages beaucoup plus volumineux à envoyer. Dans l'état actuel, la conversion en base64 est loin d'être primordiale.

# Difficultés rencontrées
## Implémentation
Durant la première séance, nous avons trouvé un [tutoriel en ligne](https://www.techwithtim.net/tutorials/python-online-game-tutorial) proposant une implémentation initiale d'un client, d'un serveur et de la communication entre les deux. Cependant, durant la seconde, nous avons découvert que la librairie utilisée par ce dernier, "Pickle", permet des RCE (Remote Code Execution). Nous avons donc décidé de refaire la partie communication à partir de 0. Cela a été plus compliqué que prévu et s'est avéré très long.

Finalement, nous avions perdu trop de temps sur ça, et nous avons donc décidé de grandement réduire les features de notre jeu pour nous concentrer sur l'essentiel.

## Organisation
La période durant laquelle s'est déroulé le projet n'a également pas aidé. Nous avions beaucoup de travail dans beaucoup de matières, et donc peu de temps pour avancer sur le projet en dehors des heures dédiées.

Comme nous travaillions rarement tous les trois en même temps, notre organisation était plus complexe, notamment pour gérer le git.
