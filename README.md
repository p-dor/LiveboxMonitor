# ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_AppIcon.png) LiveboxMonitor

L'application [LiveboxMonitor](https://github.com/p-dor/LiveboxMonitor) est une interface graphique dynamique pour :
- Contrôler les appareils qui se connectent à la Livebox et détecter rapidement les intrusions,
- Enregistrer le journal d'activités et recevoir des notifications par email aux connexions ou déconnexions,
- Obtenir des statistiques détaillées de trafic, par appareil, global,
- Visualiser graphiquement les statistiques de trafic sur plusieurs jours, par appareil ou par interface,
- Obtenir beaucoup de détails sur la Livebox elle-même et contrôler la qualité de sa ligne fibre,
- Avoir beaucoup de détails sur les appareils qui se connectent (actifs ou non),
- Lire le journal des événements d'un appareil donné,
- Contrôler de manière fine les réglages du serveur DHCP, des règles NAT/PAT, du DynDNS et de la DMZ,
- Contrôler l'état du Wifi,
- Contrôler les appels téléphoniques ainsi que la liste des contacts,
- Contrôler un ou plusieurs répéteurs Wifi Orange connectés.

**AVERTISSEMENT** : le programme a été **conçu pour contrôler une Livebox 5 et a été adapté avec quelques tests pour les Livebox 4, 6 et 7**, des tests supplémentaires avec une Livebox 4, 6 ou 7 seraient bienvenus. Les architectures étant totalement différentes, **le logiciel n'est pas compatible avec la "Livebox Pro 4"**.

L'application est dynamique car elle réagit aux événements envoyés par la Livebox et les interprète.

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DeviceList.png)


## Sections de cette documentation
1. [Installation](#install)
2. [Configuration minimale](#minimalconfig)
3. [À propos de l'auteur](#author)
4. [Discussion](#discussion)
5. [Prise en main](#handling)
6. [Profils](#profiles)
7. [Options de ligne de commande](#commandline)
8. [Accès à distance](#remoteaccess)
9. [Configuration](#configuration)
10. [Linux](#linux)
11. [Appareils - Liste des appareils connectés](#devicelist)
12. [Stats/Infos Livebox - Statistiques de trafic et infos avancées de la Livebox](#infos)
13. [Graphes - Courbes de trafic par interface et par appareil](#graphs)
14. [Infos Appareil - Informations détaillées pour chaque appareil connu](#deviceinfos)
15. [Événements - Liste des événements reçus pour chaque appareil connu](#events)
16. [DHCP - Contrôle fin du serveur DHCP](#dhcp)
17. [NAT/PAT - Règles de redirection de port et de protocole](#natpat)
18. [Téléphone - Liste des appels téléphoniques / liste des contacts](#phone)
19. [Actions - Boutons d'actions et de contrôle](#actions)
20. [Onglets répéteurs Wifi](#repeaters)
21. [Gestion et personnalisation des icônes d'appareil](#icons)


## Installation <a id="install"></a>

L'application est écrite en [Python 3.9](https://www.python.org/downloads/) et est basée sur [PyQT 6](https://pypi.org/project/PyQt6/) pour l'interface graphique et sur [PyQtGraph](https://www.pyqtgraph.org/) pour les graphes statistiques.

Les autres dépendances sont `requests`, `cryptography` et `python-dateutil`.

**Note** : Le module `LmSession` est une adaptation du package [sysbus](https://github.com/rene-d/sysbus) pour les Livebox 5,6 & 7. Le support des événements a aussi été rajouté.

### Téléchargement - version 1.5 (26/01/2025)

Des programmes autonomes construits avec [PyInstaller](https://pyinstaller.org) sont disponibles pour les plateformes Windows & MacOS :
- Windows : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor.exe)
- Windows avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor_Console.exe)
- MacOS (Intel) : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor.dmg)
- MacOS (Intel) avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor_Console.dmg)
- MacOS (Silicon) : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor_Silicon.dmg)
- MacOS (Silicon) avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/1.5/LiveboxMonitor_Silicon_Console.dmg)

Nouveautés de la version 1.5 et historique des versions : [ici](https://github.com/p-dor/LiveboxMonitor/blob/main/docs/ReleaseHistory.md) ou [ici](https://github.com/p-dor/LiveboxMonitor/releases).


### PyPI - [ici](https://pypi.org/project/LiveboxMonitor/)

Installation :  
```
    pip install LiveboxMonitor
```

Mise à jour :  
```
    pip install --upgrade LiveboxMonitor
```

Lancement :  
```
    LiveboxMonitor
```


### Utilisation directe via les sources

Installation :  
```
    git clone https://github.com/p-dor/LiveboxMonitor.git  
    cd LiveboxMonitor  
    pip install -r requirements.txt
```

Lancement : 
``` 
    cd src\LiveboxMonitor
    python3 lbm.py
```

Ou via un virtualenv.

Installation :  
```
    git clone https://github.com/p-dor/LiveboxMonitor.git
    cd LiveboxMonitor
    virtualenv -p python3 .venv
    source .venv/bin/activate
    pip install -r requirements.txt
``` 

Lancement : 
``` 
    cd src\LiveboxMonitor
    source .venv/bin/activate
    python3 lbm.py
```


## Configuration minimale <a id="minimalconfig"></a>

Étant donné les dépendances documentées de [Python 3.9](https://www.python.org/downloads/release/python-390/), [PyInstaller](https://pyinstaller.org/en/stable/requirements.html) et de [PyQt6](https://www.qt.io/product/qt6/technical-specifications) la configuration minimale requise pour faire tourner cette application est :
- Windows : **Windows 10** ou plus récent.
- MacOS : **10.15 (Catalina)** ou plus récent.


## À propos de l'auteur <a id="author"></a>

L'auteur de ce logiciel est un professionnel de l'informatique n'ayant aucun lien avec Orange. Ce logiciel n'est donc en rien un produit d'Orange.  
Aucune documentation officielle des APIs de la Livebox n'étant disponible, l'élaboration a été effectuée à partir de techniques classiques de rétro-ingénierie (reverse engineering), et l'ensemble du projet sur le temps libre de l'auteur.


## Discussion <a id="discussion"></a>

Un [fil de discussion](https://lafibre.info/orange-les-news/controler-son-reseau-livebox-5-ou-6/) est actif sur le forum [lafibre.info](https://lafibre.info). Il est possible d'y poster vos commentaires, résultats de tests ou de faire des demandes de fonctionnalités.


## Prise en main <a id="handling"></a>

L'interface se veut intuitive mais il vaut mieux se reporter à la documentation pour comprendre certains comportements ou représentations.
Les points importants à comprendre avant de commencer :
- La connexion s'établit avec exactement les mêmes informations que pour accéder à l'interface Web de configuration de la Livebox. Pour l'URL il faut essayer http://livebox.home/, http://livebox/ ou http://192.168.1.1/. Pour l'utilisateur il faut laisser à la valeur par défaut `admin`. Et pour le mot de passe c'est soit ce que vous avez indiqué vous-même soit le mot de passe d'origine. Plus d'informations [ici pour la Livebox 5](https://assistance.orange.fr/livebox-modem/toutes-les-livebox-et-modems/installer-et-utiliser/piloter-et-parametrer-votre-materiel/l-interface-de-configuration/livebox-5-acceder-a-l-interface-de-configuration_292471-827404), ou [ici pour la Livebox 6](https://assistance.orange.fr/livebox-modem/toutes-les-livebox-et-modems/installer-et-utiliser/piloter-et-parametrer-votre-materiel/l-interface-de-configuration/livebox-6-acceder-a-l-interface-de-configuration_363963-897414).
- Il est normal que lors du premier lancement de l'application tous les appareils soient marqués comme inconnus (**INCONNU** en rouge). En effet un des buts de ce programme est d'identifier rapidement des appareils inconnus connectés sur le réseau grâce à une base de noms locale (le fichier `MacAddrTable.txt`). Il faut donc commencer par nommer chaque appareil que vous jugez légitime grâce au bouton `Assigner Nom...` de l'onglet `Infos Appareil`. Cette base locale constituera la référence de confiance de tous les appareils légitimes sur votre réseau. Le bouton `Assigner Noms...` de l'onglet `Appareils` vous permettra aussi de facilement assigner le même nom que celui qui a été donné à la Livebox automatiquement pour tous vos appareils.
- Il est normal que les statistiques réseau apparaissent et disparaissent. En effet le programme rafraîchit ces statistiques toutes les 3 secondes par défaut (ou toutes les 30 secondes dans certains cas), et si d'un rafraîchissement à l'autre il n'y a pas eu de transfert la case devient vide. Ce choix a été fait pour permettre de mieux visualiser les cases non-vides, là où il se passe quelque chose.
- Tous les onglets peuvent être déplacés à la souris pour être mis dans l'ordre qui vous convient. Cet ordre sera restauré au prochain lancement du programme.
- Toutes les colonnes dans le programme sont redimensionnables à la souris sauf certaines qui s'élargissent dynamiquement en fonction de la taille de la fenêtre. Donc, en fonction de la situation, vous pouvez soit redimensionner la colonne soit la fenêtre avec la souris pour ajuster la largeur d'une colonne.
- On peut copier la valeur de n'importe quelle cellule de liste dans le presse-papiers. Pour cela il suffit de cliquer sur la cellule et de taper Ctrl-C.
- Le programme dispose d'une barre de statut en bas de la fenêtre. Elle affiche sur la gauche des tâches en cours et sur la droite le nom du profil en cours (voir la section **Profils** ci-dessous). Un clic sur le nom de profil affichera la fenêtre pour en changer.
- Des **tooltips** sont disponibles dans l'interface pour vous aider à vous passer de la documentation.


## Profils <a id="profiles"></a>
Le programme supporte de pouvoir gérer plusieurs Livebox à l'aide de profils différents. Chaque profil doit avoir un nom unique. Par défaut un profil principal est créé automatiquement, mais il est possible d'en créer d'autres soit au démarrage du programme dans la fenêtre de sélection de profils soit dans les préférences du programme.  
Si plusieurs profils sont configurés le nom du profil en cours est affiché dans le titre de la fenêtre principale entre crochets.  
Plusieurs informations sont associées à chaque profil, telle que l'URL de la Livebox, son mot de passe, etc. Le programme associe aussi automatiquement l'adresse physique (MAC) de la Livebox sur laquelle la connexion s'est effectuée.

Que se passe-t-il au lancement du programme ?
- Si la touche `Ctrl` est enfoncée le programme affiche un dialogue pour sélectionner le profil à utiliser.
- Sinon, si un profil par défaut est configuré, il sera sélectionné.
- Sinon, le programme parcourt la liste des profils et cherche si une Livebox avec la même adresse physique que celle associée au profil répond à l'URL du profil. Le premier profil qui répond à ces critères est sélectionné.
- Si aucun profil trouvé, le programme affiche un dialogue pour sélectionner le profil à utiliser.

Le dialogue de sélection de profils vous prévient si vous tentez d'utiliser un profil pour une Livebox différente de celle avec lequel il est normalement associé. Si vous validez le dialogue, le profil sera mis à jour pour être associé à cette nouvelle Livebox. Le dialogue de sélection de profils vous permet aussi de créer un nouveau profil si aucun dans la liste ne convient.


## Options de ligne de commande <a id="commandline"></a>

- `--redir` `-r`  
Permet de rediriger une URL configurée / utilisée par le programme pour se connecter à la Livebox ou à un répéteur Wifi.
Le format est `url1=url2`.  
Exemple : `LiveboxMonitor --redir http://livebox/=http://myproxy:2080`  
Avec cette option le programme utilisera plutôt l'URL 'http://myproxy:2080/' pour se connecter à 'http://livebox/'.  
Cette option peut être utilisée plusieurs fois sur la même ligne.


## Accès à distance <a id="remoteaccess"></a>
Il est possible d'utiliser le programme à distance si l'accès à distance de la Livebox est activé.
Dans la configuration de la Livebox, cliquez sur la tuile "Mon accès à distance". Activez l'accès, configurez un nom, un mot de passe, et un numéro de port personnalisé. Vous pouvez aussi en profiter pour activer un DynDNS pour éviter de changer l'URL à chaque fois que votre IP internet change.  

Votre URL de connexion devient alors quelque chose comme ceci : https://monIP:monPort/  
Ou alors si vous avez configuré un DynDNS : https://monNomDeDomaine.com:monPort/  
Évidement configurez aussi le nom et le mot de passe de connexion en fonction.


## Configuration <a id="configuration"></a>

### Répertoire de configuration
- Si le programme est lancé par son code source le répertoire de configuration est le même que celui contenant le fichier source de lancement `lbm.py`.

- Si le package PyPI (installation avec la commande 'pip') ou les programmes construits avec [PyInstaller](https://pyinstaller.org) sont utilisés, le répertoire de configuration se trouve dans les répertoires standards du système :
    - Windows : `%APPDATA%\LiveboxMonitor`
    - MacOS : `~/Library/Application Support/LiveboxMonitor`

Le programme créé automatiquement dans son répertoire de configuration deux fichiers au format JSON :
- `Key.txt` : clef de chiffrement unique générée pour crypter tous les mots de passe. Cette clef est elle-même cryptée avec une clef qui est calculée par le programme à partir des caractéristiques uniques de votre PC (y compris son nom). Si quelque chose de significatif change sur votre PC (le processeur, l'OS, son nom, etc), cette clef sera régénérée automatiquement et tous vos mots de passe devront être ressaisis.
- `Config.txt` : contient tous les paramètres de l'application.
- `MacAddrTable.txt` : contient la correspondance entre les adresses MAC et les noms d'appareil.

### Le fichier Config.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer. Les réglages principaux se font via le bouton `Préférences...` de l'onglet `Actions`.  
À savoir :  
- Les mots de passe y sont stockés cryptés grace à la clef de chiffrement du fichier `Key.txt`.
- La clef `Repeaters` est générée automatiquement par le programme si des mots de passe différents sont utilisés pour le ou les répéteurs Wifi Orange connectés. La structure de ce paramètre est aussi au format JSON, utilise pour clef les adresses MAC des répéteurs, et référence pour chaque répéteur les valeurs 'User' & 'Password'.

### Le fichier MacAddrTable.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer.
Les clefs correspondent aux adresses MAC des appareils et les valeurs au nom attribué.
Tout appareil détecté dont l'adresse MAC n'est pas répertoriée sera affiché comme 'INCONNU' en rouge. Cette fonctionnalité est surtout utile pour détecter les nouveaux appareils ou des tentatives d'intrusions.

Pourquoi utiliser une base de noms locale alors que la Livebox stocke aussi des noms ?
- Parce que la Livebox "oublie" tout appareil qui ne s'est pas connecté depuis plus d'un mois.
- Parce que parfois la Livebox perd des noms de façon impromptue pour certains appareils. C'est le cas par exemple pour le nom des répéteurs Wifi.  
Un fichier de noms local offre la garantie de savoir si un appareil est vraiment inconnu.


## Linux <a id="linux"></a>
En cas d'utilisation d'un virtualenv, si des erreurs de plugin Qt apparaissent, rajoutez ces commandes pour l'installation :

```
    apt install qt6-base-dev
    apt install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
```

En cas d'erreurs avec Wayland, il est possible de changer le moteur de rendu de Qt avec la variable d’environnement `QT_QPA_PLATFORM`.  
Par exemple : `QT_QPA_PLATFORM=xcb python3 lbm.py` permet d'utiliser X Window directement (qui éventuellement sera rendu avec Xwayland mais cela fonctionne).

Une autre méthode consiste à supprimer la variable d’environnement `WAYLAND_DISPLAY` uniquement pour l’exécution du programme et pas de façon globale, pour ce faire : `env -u WAYLAND_DISPLAY python3 lbm.py`.


## Appareils - Liste des appareils connectés <a id="devicelist"></a>

### Liste
La liste des appareils affiche les colonnes suivantes :
- **T** : icône correspondant au type de l'appareil. Ce type peut être attribué ou changé via le bouton `Assigner Type...` de l'onglet `Infos Appareil`.
- **Nom** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.
- **Nom Livebox** : nom de l'appareil tel que paramétré dans la Livebox et visible dans l'interface Web de la Livebox. Ce nom peut être attribué, changé ou supprimé via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP v4 de l'appareil sur le LAN. Cette adresse s'affiche en caractères gras si cette adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox. Et elle s'affiche en rouge si l'adresse n'est pas atteignable sur le réseau (unreacheable), typiquement lorsque l'appareil n'est pas actif.
- **Accès** : point d'accès de l'appareil sur le réseau. D'abord le nom de l'appareil, c'est-à-dire la Livebox elle-même ou le nom d'un des répéteurs Wifi Orange connectés, et ensuite l'interface sur cet appareil. `Eth` signifie une des prises Ethernet suivi du numéro de prise. `Wifi` signifie une connexion Wifi suivi par la bande de connexion.
- **A** : indique par une icône si l'appareil est actif ou non. Par défaut la liste est triée pour montrer d'abord les appareils actifs.
- **Wifi** : qualité de la connexion Wifi.
- **E** : indique par une icône avec un point d'exclamation ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Exclamation.png) lorsqu'un événement est reçu pour cet appareil. La liste détaillée des événements, ainsi que le contenu des événements eux-mêmes, peuvent être consultés via l'onglet `Événements`.
- **Rx** : nombre d'octets reçus par l'appareil depuis le dernier démarrage de la Livebox.
- **Tx** : nombre d'octets envoyés par l'appareil depuis le dernier démarrage de la Livebox.
- **TauxRx** : taux d'octets reçus par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans les trois dernières secondes si affiché en bleu (fréquence réglable dans les préférences).
- **TauxTx** : taux d'octets envoyés par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans les trois dernières secondes si affiché en bleu (fréquence réglable dans les préférences).

Les statistiques d'octets envoyés ou reçus par seconde sont calculées grâce aux statistiques envoyées par la Livebox sous forme d'événement toutes les 30 secondes par appareil. Cette résolution étant peu significative le programme utilise une autre interface disponible pour les appareils Wifi uniquement pour obtenir des statistiques toutes les trois secondes (option pour les activer/désactiver dans les préférences, ainsi que la fréquence). Ces dernières sont affichées en bleu.  
Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par la Livebox.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).  
**Note** : le trafic TV standard de la box TV UHD n'est pas comptabilisé dans les statistiques pour cet appareil. Par contre celui de services VOD tel que Netflix est bien comptabilisé.


### Boutons
L'onglet `Appareils` propose les boutons suivants :
- **`Rafraîchir`** : permet de forcer le rafraîchissement de la liste des appareils, non seulement dans cet onglet mais aussi dans les onglets `Infos Appareil` et `Événements`. Utile par exemple si le programme est actif alors que l'ordinateur sort de veille : des événements ayant probablement été raté par le programme, un rafraîchissement permettra de retrouver une vue à jour.
- **`Assigner Noms...`** : permet d'assigner le même nom que celui qui a été donné à la Livebox automatiquement pour tous les appareils inconnus.
- **`Infos Appareil`** : permet de basculer dans l'onglet `Infos Appareil` pour l'appareil sélectionné et de voir directement ses informations.
- **`Événements Appareil`** : permet de basculer dans l'onglet `Événements` pour l'appareil sélectionné et de voir directement les événements reçus le concernant.
- **`IPv6...`** : permet d'avoir le statut d'activation de l'IPv6, l'adresse IPv6 de la Livebox ainsi que son préfixe, et la liste des appareils connectés ou non ayant une ou plusieurs IPv6 assignées.
- **`DNS...`** : permet d'avoir la liste des noms DNS assignés aux appareils. Ces noms DNS peuvent être attribués, changés ou supprimés via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.


## Stats/Infos Livebox - Statistiques de trafic et infos avancées de la Livebox <a id="infos"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_LiveboxInfos.png)

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations sont accessibles par les boutons, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier.

### Statistiques

Liste permettant de surveiller l'état du trafic :
- **Nom** : nom de l'interface réseau. `Fiber` concerne tout le trafic WAN, c'est-à-dire externe entre la Livebox et internet. `LAN` tout le trafic interne transitant à travers la Livebox. Ensuite on dispose des statistiques par interface précise. Les interfaces `Guest` concernent le trafic du réseau Wifi invité, s'il est activé.
- **Rx** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue. S'affiche en rouge si des erreurs de transmission sont détectées. Attention ce compteur est circulaire et ne dépasse pas les 4 Go pour certaines interfaces. En effet pour d'autres, un compteur de plus haute résolution est interprété toutes les 30 secondes environ et qui vient remplacer au lancement du programme le compteur de base limité à 4 Go.
- **Tx** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue. S'affiche en rouge si des erreurs de transmission sont détectées. Attention ce compteur est circulaire et ne dépasse pas les 4 Go pour certaines interfaces. En effet pour d'autres, un compteur de plus haute résolution est interprété toutes les 30 secondes environ et qui vient remplacer au lancement du programme le compteur de base limité à 4 Go.
- **TauxRx** : taux d'octets reçus par seconde par l'interface dans les trois dernières secondes (fréquence réglable dans les préférences). S'affiche en rouge si des erreurs de transmission sont détectées. 
- **TauxTx** : taux d'octets envoyés par seconde par l'interface dans les trois dernières secondes (fréquence réglable dans les préférences). S'affiche en rouge si des erreurs de transmission sont détectées.

Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par la Livebox.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).
**Note** : le trafic TV standard de la box TV UHD n'est pas comptabilisé dans ces statistiques. Par contre celui de services VOD tel que Netflix est bien comptabilisé.

### Boutons
L'onglet `Stats/Infos Livebox` propose les boutons suivants :
- **`Infos Livebox`** : affiche les informations principales concernant la Livebox, telles que les versions de logiciels, l'adresse IP WAN, les services actifs, l'état de la mémoire, etc.
- **`Infos Internet`** : affiche le type d'accès internet, les identifiants de connexion, les adresses IPs v4 & v6, la date et heure de la dernière connexion, la bande passante de la connexion, la MTU, etc
- **`Infos Wifi`** : affiche les informations générales sur la connectivité Wifi, et l'état de chaque accès y compris pour les accès invités. Pour chaque accès on dispose d'informations détaillées telles que le canal, le standard, la bande passante, la qualité, la bande, le nombre d'appareils connectés, etc.
- **`Infos LAN`** : affiche les informations générales sur la connectivité LAN. Il s'agit des informations DHCP de base et pour chaque interface Ethernet on peut identifier si elle est active ou non, la bande passante, etc.
- **`Infos ONT`** : affiche les informations importantes concernant la connexion et le module Fibre (ONT), telles que la bande passante, la qualité du signal, le numéro de série et les versions logicielles, etc. Les champs `Puissance Signal Réception`, `Puissance Signal Transmission`, `Température`, `Voltage` et `BIAS` affichent des valeurs vertes si elles correspondent aux normes de qualité acceptables pour la connexion, en rouge si elles représentent un problème, en orange si elles sont aux limites acceptables.
![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_LiveboxInfos_ONT.png)
- **`Infos VoIP`** : affiche les informations générales concernant la téléphonie, telles que le protocole, le numéro de téléphone, la version logicielle de l'interface DECT, etc.
- **`Infos IPTV`** : affiche les informations générales relatives aux services de télévision.
- **`Infos USB`** : affiche les informations concernant le ou les ports USBs. Si une clef USB est insérée, ou a été insérée depuis le dernier démarrage de la Livebox, ses informations sont affichées.
- **`Export...`** : permet d'exporter l'ensemble des informations affichées par chacun des boutons dans un fichier texte. Utile pour communiquer ces informations ou faire un suivi pour détecter les changements.


## Graphes - Courbes de trafic par interface et par appareil <a id="graphs"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Graph.png)

Affiche les graphiques des données reçues et transmises pour chaque interface / appareil sélectionné à partir de données stockées par la Livebox elle-même. Les volumes sont en méga-octets entre deux échantillons, en principe toutes les 30 secondes (l'échantillonnage et sa fréquence sont contrôlés par la Livebox). Les graphes se mettent à jour automatiquement à la réception de nouveaux échantillons sous forme d'événements.  
Il est possible de naviguer et de zoomer dans les graphiques à la souris, puis de revenir à la vue normale en cliquant dans le coin en bas à gauche. Un clic droit sur un graphe permet d'accéder à d'autres fonctionnalités telles que l'exportation en différents formats. Toute la documentation est accessible [ici](https://pyqtgraph.readthedocs.io/en/latest/user_guide/index.html).

### Sélection des interfaces et des appareils
Il faut commencer par sélectionner les interfaces et/ou les appareils dont on veut obtenir les graphiques, pour cela deux boutons sont disponibles :
- **`Ajouter...`** : affiche un dialogue permettant de sélectionner une interface ou un appareil.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Graph_Add.png)

    Commencer par sélectionner le type, interface ou appareil. Puis l'interface ou l'appareil en question, ainsi que la couleur à utiliser sur le graphique pour cet objet. La sélection n'affiche que des objets pour lesquels des mesures sont potentiellement disponibles. Pour les appareils les noms locaux sont utilisés, et par défaut l'adresse physique (MAC). Le dialogue affiche en informations complémentaires l'identifiant interne à la Livebox de l'objet sélectionné, le nombre d'échantillons stockés dans la Livebox pour cet objet (le nombre maximum est fixé à 8680 par la Livebox) et une estimation de la fenêtre de temps correspondante. Cependant cette fenêtre de temps peut être erronée, car si l'interface ou l'appareil sont déconnectés pendant une période de temps aucun échantillon n'est émis durant cette période. Ce qui veut dire que la période de temps totale entre le plus ancien échantillon et le plus récent peut être bien plus longue que cette estimation.
- **`Supprimer`** : permet de supprimer l'interface ou l'appareil sélectionné.

### Options des graphiques
Des options sont disponibles pour paramétrer les graphiques :
- **`Fenêtre`** : fenêtre de temps en heure de l'affichage des graphiques, à partir du présent. Une valeur à 0 affichera l'ensemble des statistiques disponibles dans la Livebox pour les objets sélectionnés.
- **`Couleur de fond`** : couleur de fond à utiliser pour les graphiques de réception et d'émission. Un clic droit supprime toute couleur, la couleur par défaut sera donc utilisée.

### Génération des graphiques
Le bouton **`Appliquer`** permet de charger toutes les informations relatives aux interfaces et appareils sélectionnés, de dessiner les graphiques correspondants en tenant compte des options ci-dessus, et de sauvegarder la configuration. Celle-ci sera automatiquement rechargée au prochain lancement du programme.  

Le bouton **`Export...`** permet d'exporter au format CSV (avec le point-virgule comme séparateur) les dernières données chargées par le bouton `Appliquer` ainsi que celles reçues entre temps via des événements.


## Infos Appareil - Informations détaillées pour chaque appareil connu <a id="deviceinfos"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DeviceInfos.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Nom** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assigner Nom...`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.

Lorsqu'un appareil est sélectionné dans cette liste ses informations détaillées s'affichent dans la liste de droite. Attributs notables :
- **Actif** : indique si l'appareil est actif ou non.
- **Authentifié** : indique si la connexion Wifi de l'appareil a bien été authentifiée.
- **Bloqué** : indique si vous avez bloqué la connexion de l'appareil à la Livebox ou non. Le blocage peut être contrôlé avec les boutons `Bloquer` et `Débloquer`. Il peut être utile de bloquer un appareil inconnu si vous avez des suspicions.
- **Première Connexion** : date et heure de la première connexion. Attention cette valeur peut aussi correspondre à la date/heure d'un précédent redémarrage de la Livebox.
- **Dernière Connexion** : date et heure de la dernière connexion.
- **Dernier Changement** : date et heure du dernier changement détecté pour cet appareil.
- **Nom** : nom connu par la Livebox pour cet appareil, avec la source de ce nom entre parenthèses. Ainsi plusieurs noms peuvent s'afficher pour des sources différentes.
- **Type** : type connu par la Livebox pour cet appareil, avec la source de ce type entre parenthèses. Ainsi plusieurs types peuvent s'afficher pour des sources différentes.
- **Adresse IPvX** : adresse IP (v4 ou v6) de l'appareil. Entre parenthèses s'affiche si l'adresse est celle active ou non, et atteignable sur le réseau (reacheable) ou non (not reacheable). Si l'adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox une mention s'affiche (Reserved).
- **Fabricant** : le fabricant de cet appareil, déduit à partir de son adresse MAC. Le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabricant. C'est un service gratuit, mais il faut créer un compte et indiquer l'API Key correspondante dans les préférences pour bénéficier de cette fonctionnalité.
- **Force Signal Wifi** et **Taux Bruit Signal Wifi** : donnent des indications sur la qualité de la connexion pour les appareils Wifi.

### Boutons
L'onglet `Infos Appareil` propose les boutons suivants :
- **`Rafraîchir`** : rafraîchit les informations affichées pour l'appareil sélectionné.
- **`Assigner Nom...`** : permet d'attribuer ou d'effacer le nom local, le nom Livebox et/ou le nom DNS de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DeviceInfos_AssignName.png)

    Décocher la boite pour effacer le nom. Les deux noms peuvent être différents.
- **`Assigner Type...`** : permet d'attribuer ou d'effacer le type de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DeviceInfos_AssignType.png)

    Il est possible de sélectionner un des types standards connus par la Livebox dans le menu, chaque type étant affiché avec son icône Livebox correspondante. Lorsqu'un type standard est sélectionné, son nom connu par la Livebox est automatiquement rempli dans la zone de texte et on peut valider le dialogue. Il reste possible d'assigner manuellement un type non connu par la Livebox en le tapant directement dans la zone de texte. Note : bien que le type "Djingo Speaker" soit référencé comme standard par la Livebox 5, ce type ne semble pas (encore ?) supporté par l'interface graphique de la Livebox.
- **`Oublier...`** : permet de demander à la Livebox d'oublier définitivement cet appareil. Il disparaîtra donc immédiatement de toutes les listes. Attention si l'appareil en question est actif, sa connexion ne sera nullement suspendue, cependant toute son activité restera invisible et ce jusqu'à sa prochaine tentative de connexion.
- **`WakeOnLAN`** : permet d\'envoyer un signal de réveil sur réseau à l'appareil sélectionné. Celui-ci doit être configuré pour s'allumer à la réception de ce signal (option WOL) pour que cela fonctionne.
- **`Bloquer`** : permet de bloquer la connexion de l'appareil sélectionné.
- **`Débloquer`** : permet de débloquer la connexion de l'appareil sélectionné. L'état bloqué ou non s'affiche dans les informations de l'appareil, champs "Bloqué".


## Événements - Liste des événements reçus pour chaque appareil connu <a id="events"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Events.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Nom** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.

Lorsqu'un appareil est sélectionné dans cette liste tous les événements reçus depuis le lancement du programme pour cet appareil s'affichent dans la liste de droite. La plupart de ces événements ont été interprétés par le programme pour mettre à jour l'interface dynamiquement, et cette liste permet d'avoir un historique. La taille de cet historique par appareil est limitée aux 100 dernières entrées (cette limite peut être ajustée facilement en modifiant la variable `MAX_EVENT_BUFFER_PER_DEVICE` du module `LmEventsTab.py`).

La liste des événements est composée des colonnes :
- **Heure** : heure de réception de l'événement.
- **Raison** : le type d'événement généré par la Livebox.
- **Attributs** : aperçu des données brutes de l'événement lui-même, au format JSON.

Un double clic sur un événement ou un clic sur le bouton **`Afficher Événement`** permet d'afficher un dialogue contenant les informations complètes :
- **Raised** : date et heure précise de réception de l'événement.
- **Handler** : gestionnaire de l'événement, contenant la plupart du temps la clef de l'appareil qui n'est autre que son adresse MAC.
- **Reason** : le type d'événement.
- **Attributes** : données brutes complètes de l'événement lui-même, au format JSON tel que généré par la Livebox.  

### Notifications automatiques
- Le bouton **`Notifications...`** permet d'accéder à la configuration des notifications automatiques à générer (par exemple par email) à la détection de certains événements.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Events_Notifications.png)

    Vous pouvez créer autant de règles que nécessaire. Ce n'est pas grave si plusieurs règles concernent le ou les mêmes appareils, le programme ne détecte pas non plus les règles dupliquées. Il suffit qu'au moins une règle soit trouvée qui concerne une notification pour un appareil pour que cette notification soit effectuée.
    La liste affiche la liste des règles configurées, avec le ou les appareils concernés, les pastilles bleues indiquent les événements sélectionnés pour la notification, les pastilles vertes le ou les types de notifications sélectionnés (email et/ou fichiers CSV journaliers). Les boutons **`Ajouter`** et **`Supprimer`** permettent de créer une règle ou de supprimer la règle sélectionnée.  

    Paramètres d'une règle :
    - **`Appareil`** : permet de sélectionner le ou les appareils pour lesquels recevoir une notification. `Tout appareil` appliquera la règle pour l'ensemble des appareils. `Tout appareil inconnu` appliquera la règle à n'importe quel appareil inconnu.
    - **`Adresse MAC`** : adresse physique de l'appareil sélectionné.
    - **`Événements`** : sélection des événements pour lesquels recevoir une notification. Ajout ou suppression d'appareils, connexion, déconnexion, ou changement de points d'accès (utile si vous disposez d'un ou plusieurs répéteurs Wifi Orange).
    - **`Actions`** : sélection des actions à réaliser pour notifier. Il est possible de reporter les événements dans un fichier CSV journalier, ou d'envoyer les informations de chaque événement par email instantané.

    Préférences des notifications:
    - **`Fréquences Résolution des Événements`** : les événements sont détectés instantanément, cependant certains événements peuvent s'annuler lorsque générés dans une courte fenêtre de temps, tels que la déconnexion suivie d'une reconnexion dans les 15 secondes d'un appareil donné (arrive fréquemment). Pour éviter des notifications intempestives un temps d'attente de 30 secondes est fortement recommandé pour laisser le programme identifier ces situations. Un temps inférieur à 5 secondes est fortement déconseillé pour éviter que le programme ne consomme trop de ressources.
    - **`Répertoire des fichiers CSV`** : répertoire dans lequel générer les fichiers CSV journaliers. Cocher l'option `Défaut` pour générer les fichiers dans le [le répertoire de configuration du programme](#configuration). Sinon cliquer sur le bouton `Sélectionner` pour choisir un répertoire spécifique.

## DHCP - Contrôle fin du serveur DHCP <a id="dhcp"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DHCP.png)

### Baux statiques
La liste des baux statiques configurés est affichée sur la gauche. Les deux domaines de réseau sont gérés :
- `Home` : votre réseau privé, dont vous pouvez configurer sa plage d'IPs.
- `Guest` : le réseau Wifi invité, qui a sa propre plage d'IPs (non-modifiable).

La liste affiche les colonnes suivantes :
- **Nom** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.
- **Domaine** : domaine d'assignation, `Home` ou `Guest`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP assignée statiquement à l'appareil.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des baux :
- **`Rafraîchir`** : rafraîchit la liste des baux statiques.
- **`Ajouter...`** : permet d'ajouter un bail.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DHCP_AddBinding.png)

    La liste des appareils proposés est triée et est composée d'un mélange des appareils connectés et ceux référencés dans le fichier local des adresses MAC. L'adresse MAC est directement déduite de l'appareil sélectionné mais on peut en taper une totalement à la main. Choisir le domaine réseau entre `Home` ou `Guest`, et une adresse IP libre sera automatiquement proposée mais celle ci reste bien sûr configurable. Attention un même appareil ne peut être configuré que sur un seul domaine, et s'il se connecte sur un domaine alors qu'un bail statique est configuré sur l'autre ce bail sera automatiquement supprimé.
- **`Supprimer`** : supprime le bail sélectionné.

### Informations DHCP détaillées
La liste sur la droite affiche de nombreux détails sur le serveur DHCP:
- La configuration détaillée des deux domaines `Home` et `Guest`.
- Des détails sur le DHCPv4 ainsi que toutes les options DHCP envoyées et reçues.
- Des détails sur le DHCPv6 ainsi que toutes les options DHCP envoyées et reçues.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des baux :
- **`Rafraîchir`** : rafraîchit la liste des informations DHCP.
- **`Réglages DHCP...`** : permet de configurer le serveur DHCP.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_DHCP_Setup.png)

    Permet d'activer ou de désactiver le serveur, de changer l'adresse IP de la Livebox, de changer le masque de sous-réseau du serveur DHCP ainsi que la plage d'adresse IP pour le domaine `Home`.


## NAT/PAT - Règles de redirection de port et de protocole <a id="natpat"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_NatPat.png)

Cet onglet permet de gérer de façon fine les règles de redirection de port et de protocole IPv4, IPv6 et UPnP de la Livebox. De par cette gestion fine il peut arriver que certaines règles, bien que correctement stockées et interprétées par la Livebox, ne s'affichent pas dans l'interface Web de la Livebox. Ceci est normal et ne représente pas vraiment de problème.

### Redirections de port
La liste des règles de redirection de port, en haut, affiche les colonnes suivantes :
- **A** : icône indiquant si la règle est active ou non.
- **Type** : type de la règle, entre IPv4, IPv6 et UPnP. Les règles UPnP sont gérées automatiquement par la Livebox et vous ne devriez normalement pas avoir à les modifier.
- **Nom** : nom de la règle.
- **Description** : description de la règle.
- **Protocoles** : liste des protocoles concernés par la règle. 
- **Port Interne** : port ou plage de ports interne sur lequel le trafic est redirigé.
- **Port Externe** : port ou plage de ports externe à rediriger.
- **Appareil** : appareil (ou son adresse IP) sur lequel le trafic est redirigé.
- **IP Externes** : liste des adresses IPs externes concernées par la règle.

Un **double clic** sur une règle permet de facilement l'éditer.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des règles :
- **`Rafraîchir`** : rafraîchit la liste des règles de redirection de port.
- **`Activer/Désactiver`** : active/désactive la règle sélectionnée.
- **`Ajouter...`** : permet d'ajouter une règle de redirection de port.
- **`Modifier...`** : permet de modifier la règle de redirection de port sélectionnée.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_NatPat_PortForwarding.png)

- **`Supprimer`** : supprime la règle de redirection de port sélectionnée.
- **`Tout Supprimer...`** : permet de supprimer toutes les règles de redirection de port. Il est possible de supprimer uniquement une sélection de types de règle. Si une ou plusieurs règles posent problème à la Livebox (par exemple lorsque leur nom contient des caractères spéciaux) ce bouton peut permettre de revenir à une situation saine.
- **`Export...`** : permet d'exporter dans un fichier les règles de redirection de port d'un ou plusieurs types choisis.
- **`Import...`** : permet de réimporter des règles de redirection de port précédemment exportées dans un fichier. Si des règles de même nom existent déjà elles seront écrasées par celles importées.

### Redirections de protocole
La liste des règles de redirection de protocole, en bas, affiche les colonnes suivantes :
- **A** : icône indiquant si la règle est active ou non.
- **Type** : type de la règle, entre IPv4 et IPv6.
- **Nom** : nom de la règle.
- **Description** : description de la règle.
- **Protocoles** : liste des protocoles concernés par la règle. 
- **Appareil** : appareil (ou son adresse IP) sur lequel le trafic est redirigé.
- **IP Externes** : liste des adresses IPs externes concernées par la règle.

Un **double clic** sur une règle permet de facilement l'éditer.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des règles :
- **`Rafraîchir`** : rafraîchit la liste des règles de redirection de protocole.
- **`Activer/Désactiver`** : active/désactive la règle sélectionnée.
- **`Ajouter...`** : permet d'ajouter une règle de redirection de protocole.
- **`Modifier...`** : permet de modifier la règle de redirection de protocole sélectionnée.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_NatPat_ProtocolForwarding.png)

- **`Supprimer`** : supprime la règle de redirection de protocole sélectionnée.
- **`Tout Supprimer...`** : permet de supprimer toutes les règles de redirection de protocole. Il est possible de supprimer uniquement une sélection de types de règle. Si une ou plusieurs règles posent problème à la Livebox (par exemple lorsque leur nom contient des caractères spéciaux) ce bouton peut permettre de revenir à une situation saine.
- **`Export...`** : permet d'exporter dans un fichier les règles de redirection de protocole d'un ou plusieurs types choisis.
- **`Import...`** : permet de réimporter des règles de redirection de protocole précédemment exportées dans un fichier. Si des règles de même nom existent déjà elles seront écrasées par celles importées.


## Téléphone - Liste des appels téléphoniques / liste des contacts <a id="phone"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Phone.png)

### Appels téléphoniques
La liste des appels téléphoniques, sur la gauche, affiche les colonnes suivantes :
- **T** : icône correspondant au type de l'appel.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Call_In.png) : appel reçu.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Call_In_Missed.png) : appel manqué. Dans ce cas toute la ligne est indiquée en couleur rouge.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Call_Out.png) : appel émis.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Call_Out_Failed.png) : appel émis mais non abouti.
- **Heure** : date et heure de l'appel.
- **Numéro** : numéro de téléphone concerné.
- **Contact** : le nom du contact déterminé par la Livebox en fonction de la liste des contacts au moment de l'appel. Si la Livebox n'a mémorisé aucun nom, alors le programme essai d'en trouver un dynamiquement à partir de la liste des contacts enregistrés par correspondance avec le numéro de téléphone.
- **Durée** : durée de l'appel.

Un **double clic** sur un appel permet de facilement créer ou éditer le contact correspondant.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des appels :
- **`Rafraîchir`** : rafraîchit la liste des appels.
- **`Spam`** : ouvre un site web ([numeroinconnu.fr](https://www.numeroinconnu.fr/)) sur votre navigateur permettant de vérifier l'origine de l'appel sélectionné.
- **`Supprimer`** : supprime l'appel sélectionné.
- **`Tout Supprimer...`** : supprime tous les appels.

### Contacts
La liste des contacts, sur la droite, affiche les colonnes suivantes :
- **Nom** : nom du contact, au format nom + prénom.
- **Portable** : numéro de téléphone portable.
- **Domicile** : numéro de téléphone fixe.
- **Travail** : numéro de téléphone professionnel.
- **Sonnerie** : type de sonnerie sélectionné parmi les 7 supportés par la Livebox.

Un **double clic** sur un contact permet de facilement l'éditer.  
**Attention** : la Livebox supporte un maximum de 255 contacts.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des contacts :
- **`Rafraîchir`** : rafraîchit la liste des contacts.
- **`Ajouter...`** : permet de rajouter un contact. Attention aucun test de doublon n'est effectué.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Phone_Contact.png)

- **`Modifier...`** : pour éditer le contact sélectionné.
- **`Supprimer`** : supprime le contact sélectionné.
- **`Tout Supprimer...`** : supprime tous les contacts.
- **`Sonnerie`** : permet de tester le téléphone. Sur la gauche du bouton on peut sélectionner un des 7 types de sonnerie proposés par la Livebox, sinon le type par défaut est utilisé.
- **`Export...`** : permet d'exporter l'ensemble des contacts dans un fichier au [format VCF](https://en.wikipedia.org/wiki/VCard). Très utile pour les sauvegarder.
- **`Import...`** : permet d'importer un ou plusieurs fichiers au [format VCF](https://en.wikipedia.org/wiki/VCard). Attention aucun test de doublon n'est effectué. Si la limite du nombre de contacts maximum supporté (255) est atteint l'import est interrompu.


## Actions - Boutons d'actions et de contrôle <a id="actions"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions.png)

Cet onglet permet une liste d'actions par catégorie.

Les actions concernant le **Wifi** :
- **`Wifi ON`** : permet d'activer l'interface Wifi de la Livebox.
- **`Wifi OFF`** : permet de désactiver l'interface Wifi de la Livebox.
- **`Wifi Invité ON`** : permet d'activer l'interface Wifi invité de la Livebox.
- **`Wifi Invité OFF`** : permet de désactiver l'interface Wifi invité de la Livebox.
- **`Planificateur Wifi ON`** : permet d'activer le planificateur Wifi de la Livebox. Ce planificateur doit être configuré depuis l'interface Web de la Livebox.
- **`Planificateur Wifi OFF`** : permet de désactiver le planificateur Wifi de la Livebox.
- **`État Global Wifi...`** : permet d'afficher l'état global du Wifi, en incluant l'état Wifi de tous les répéteurs Wifi Orange potentiellement connectés.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_WifiGlobalStatus.png)

Les actions **Diverses** :
- **`Sauvegarde et Restauration...`** : permet de régler la sauvegarde automatique de la configuration de la Livebox, de déclencher une sauvegarde ou de demander une restauration de la configuration.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_BackupRestore.png)

Les actions concernant les **Redémarrages** :
- **`Redémarrer la Livebox...`** : permet de forcer un redémarrage de la Livebox.
- **`Historique Redémarrages...`** : permet d'afficher l'historique des derniers redémarrages.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_RebootHistory.png)

    Cet historique est particulièrement utile pour détecter les redémarrages forcés par Orange pour mettre à jour le logiciel de la Livebox.
    La liste affiche les colonnes suivantes :
    - **Date Redémarrage** : date et heure du démarrage.
    - **Raison Redémarrage** : la raison de ce démarrage. Typiquement "NMC" indique un démarrage forcé par logiciel et "Unsupported chipset" un redémarrage causé par une coupure de courant ou l'interrupteur de la Livebox.
    - **Date Arrêt** : la date et heure de l'arrêt.
    - **Raison Arrêt** : la raison de cet arrêt. Typiquement vide pour une coupure de courant, "Upgrade" pour une mise à jour logiciel et "GUI_Reboot" pour un redémarrage demandé depuis l'interface Web ou LiveboxMonitor.

Les actions concernant le **Réseau** :
- **`Niveaux de pare-feu...`** : permet de régler les niveaux des pare-feux IPv4 et IPv6.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_FirewallLevels.png)
- **`Réponses aux pings...`** : permet de régler les réponses aux requêtes de ping IPv4 et IPv6.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_PingResponses.png)
- **`DynDNS...`** : permet de régler les domaines DynDNS.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_DynDNS.png)
- **`DMZ...`** : permet de configurer les règles de la DMZ. Contrairement à l'application d'Orange on peut ici ajouter plusieurs appareils dans la DMZ, avec un filtrage des IP externes comme pour les règles NAT/PAT.
La règle de l'application d'Orange apparaît avec l'ID `webui`, donc si on veut pouvoir gérer une règle à la fois avec LiveboxMonitor et l'application d'Orange il faut respecter cet identifiant.
Faute de test il n'est pas garanti que cela fonctionne correctement avec plusieurs règles : **tout retour d'utilisation sera bienvenu**.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_DMZ.png)

Les actions concernant les **Réglages** :
- **`Préférences...`** : permet d'afficher l'écran des préférences du programme.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_Preferences.png)

    Voir la section **Profils*** ci-dessus pour plus de détail sur leur fonctionnement.  
 
    Pour chaque **profil** il est possible de configurer :
    - `Nom` : nom du profil.
    - `URL Livebox` : adresse de la Livebox. La valeur par défaut est `http://livebox.home/`.
    - `Utilisateur` : login pour l'ouverture de session. Par défaut `admin`. Le mot de passe est demandé automatiquement lors de l'utilisation du profil s'il n'est pas renseigné ou s'il est erroné.
    - `Filtrage Appareils` : active le filtrage des appareils afin de ne pas montrer certains appareils "fantômes" détectés par la Livebox. Quand ce paramètre est activé le programme affiche les mêmes appareils que l'interface Web de la Livebox. Ce paramètre est activé par défaut.
    - `Fichier Table MacAddr` : nom du fichier de stockage des noms d'appareils. Par défaut `MacAddrTable.txt`. Voire `Le fichier MacAddrTable.txt` de la section `Configuration` pour plus d'explications.
    - `Défaut` : indique qu'il s'agit du profil par défaut à utiliser au lancement du programme. Il ne peut y avoir qu'un seul profil par défaut.  

    Les **préférences** générales permettent de régler :
    - `Langage` : langue utilisée par l'application, à choisir entre Français (défaut) et Anglais.
    - `Tooltips` : active ou non les tooltips.
    - `Fréquence Stats` : Fréquence de rafraîchissement, en secondes, de toutes les statistiques. Par défaut 3 secondes.
    - `API Key macaddress.io` : le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabricant d'un appareil à partir de son adresse MAC (champ **Fabricant** dans les informations détaillées par appareil). C'est un service gratuit, mais il faut créer un compte et indiquer ici l'API Key correspondante pour bénéficier de cette fonctionnalité.
    - `Indicatif Téléphonique` : indicatif téléphonique local, utile pour faire correspondre les appels téléphoniques avec les numéros de contacts. Par défaut le code de la France est utilisé, c'est-à-dire 33.
    - `Hauteur Entêtes` : hauteur en pixels des entêtes de liste, par défaut 25.
    - `Taille Police Entêtes` : taille de la police de caractères des entêtes de liste. Une valeur à zéro signifie d'utiliser la taille système. Par défaut ce paramètre est à zéro.
    - `Hauteur Lignes` : hauteur en pixels des lignes de liste, par défaut 30.
    - `Taille Police Lignes` : taille de la police de caractères des lignes de liste. Une valeur à zéro signifie d'utiliser la taille système. Par défaut ce paramètre est à zéro.
    - `Marge Timeout` : valeur de timeout additionnelle, à utiliser par exemple si vous accédez à une Livebox à distance avec une grande latence réseau.
    - `Séparateur CSV` : séparateur de liste (délimiteur) à utiliser lors de l'export de données dans des fichiers au format CSV.
    - `Statistiques temps réel des appareils wifi` : active ou non les statistiques en temps réel pour les appareils wifi. Celles ci s'affichent en bleu dans l'onglet `Appareils` et viennent recouvrir les statistiques standards qui s'affichent en noir toutes les 30 secondes.
    - `Empêcher la mise en veille` : permet d'empêcher votre ordinateur de se mettre en veille pendant l'exécution de ce programme. Utile pour laisser tourner l'application en permanence, par exemple pour l'export des statistiques ou pour la génération de notifications en temps réel.
    - `Utiliser le style d'interface graphique natif` : par défaut le style "Fusion" est utilisé sur toutes les plateformes. Cette option permet sur les plateformes Windows et MacOS d'utiliser un style graphique plus natif. Cette option n'a aucun effet sur les plateformes Linux.
    - `Sauver les mots de passe` : permet de sauver les mots de passe dans la configuration (encryptés) pour éviter d'avoir à les retaper à chaque lancement.  

- **`Changer de profil...`** : affiche un dialogue permettant de changer le profil en cours et de relancer le programme.

- **`Réglages Email...`** : permet de configurer l'envoi d'emails automatique, par exemple pour les notifications.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Actions_EmailSetup.png)
 
    Il est possible de configurer :
    - `Adresse Origine` : adresse email d'origine des messages.
    - `Adresse Destination` : adresse email de destination des messages.
    - `Préfixe Sujet` : préfixe rajouté aux sujets des messages envoyés.
    - `Serveur SMTP` : serveur SMTP de votre fournisseur de messagerie.
    - `Port` : port SMTP à utiliser. 465 est recommandé pour SSL, 587 pour tout autre protocole.
    - `Utiliser TLS` : utilisation du protocole d'encryption TLS (recommandé).
    - `Utiliser SSL` : utilisation du protocole d'encryption SSL.
    - `Authentification` : à sélectionner si le serveur nécessite de s'authentifier.
    - `Utilisateur` : votre nom d'utilisateur pour s'authentifier.
    - `Mot de passe` : votre mot de passe pour s'authentifier.  

    Le bouton `Test Envoi` permet d'envoyer un message de test avec les réglages courants sans les sauvegarder.  

    La configuration pour le serveur d'Orange est très simple :
    - Adresse origine / utilisateur -> mettre votre adresse@orange.fr
    - Adresse destination -> la destination souhaitée
    - Serveur SMTP -> smtp.orange.fr
    - Port -> 587
    - Cocher "Utiliser TLS" et "Authentification".
    - Mot de passe -> votre mot de passe Orange.  

    Pour gmail c'est un peu plus compliqué :
    - Il faut d'abord régler son compte gmail pour créer un mot de passe dédié pour le programme.
    - Aller sur son compte, onglet "Sécurité" -> [ici](https://myaccount.google.com/security)
    - Vérifier que la "validation en deux étapes" est activée, si ce n'est pas le cas, il faut le faire.
    - Cliquer "Validation en deux étapes" et aller sur "Mots de passe d'application" en bas.
    - Créer un nouveau mot de passe pour l'application 'LiveboxMonitor' et notez le mot de passe (sans les espaces).
    - Retourner dans LiveboxMonitor, réglage email.
    - Dans les champs Adresse origine / utilisateur -> mettre votre adresse@gmail.com
    - Adresse destination -> la destination souhaitée
    - Serveur SMTP -> smtp.gmail.com
    - Port -> 587
    - Cocher "Utiliser TLS" et "Authentification"
    - Mot de passe -> le mot de passe créé ci dessus.  

Les actions techniques de **Débogage** :
- **`JSON Liste Appareils...`** : permet d'afficher la réponse brute JSON de la Livebox concernant la liste des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`JSON Topologie...`** : permet d'afficher la réponse brute JSON de la Livebox concernant la topologie de connexion des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`Niveau de log...`** : permet de changer le niveau de logs dans la console. Ce niveau est stocké dans la configuration du programme et sera donc conservé au prochain lancement du programme.
- **`Générer documentation APIs...`** : permet de générer dans des fichiers texte l'ensemble de la documentation accessible sur les APIs de la Livebox, par module. Le programme génère un fichier par module connu, un fichier "_ALL_MODULES_" contenant l'ensemble des modules en un seul fichier, et un fichier "_PROCESSES_" qui permet d'avoir la liste des tâches tournant sur la Livebox. Certains fichiers ne contiennent qu'une erreur "Permission denied" : c'est normal, ces modules sont protégés et donc non accessibles (mais qui sait dans une prochaine version du firmeware ?). Les paramètres de fonction indiqués entre parenthèses sont optionnels. Par défaut le programme génère l'ensemble des instances trouvées par type de ressources (ou "object") ainsi que toutes les valeurs trouvées par paramètres, mais ces valeurs sont filtrées si on maintient la touche `Ctrl` en cliquant sur le bouton. Cela permet de partager librement ces fichiers sans divulguer d'informations spécifiques à sa configuration, cependant avoir la liste des instances reste crucial pour une documentation vraiment complète.  

Autres actions :
- **Quitter l'application** : pour quitter l'application. Strictement équivalent à fermer la fenêtre de l'application.
- Un clic sur le lien GitHub de l'application ouvrira la page correspondante sur votre navigateur.


## Onglets répéteurs Wifi <a id="repeaters"></a>

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Repeater.png)

Le programme créé dynamiquement un onglet par répéteur connecté. Si le répéteur a un nom local, celui-ci est utilisé dans l'onglet, sinon le nom par défaut est de type "RW #" suivit du numéro de répéteur dans l'ordre de détection.
Les répéteurs font aussi parti des appareils connus, ils sont donc visibles dans l'onglet `Appareils` et leur nom peut être changé via le bouton `Assigner Nom...` de l'onglet `Infos Appareil`.

Une icône dans le nom de l'onglet permet de connaître l'état de la connexion avec le répéteur :
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Cross.png) : le répéteur est inactif ou n'a pas d'adresse IP attribuée.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Prohibition.png) : le répéteur est actif mais aucune session n'est ouverte. Si cet état subsiste vous pouvez essayer de forcer la création d'une session en cliquant sur le bouton `Réauthentifier...`.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Icon_Tick.png) : le répéteur est actif et une session a été créée pour communiquer avec lui.

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations détaillées sont accessibles via la barre de boutons en bas, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier. Enfin, une série d'actions est possible via les boutons sur la gauche.

### Statistiques

Liste permettant de surveiller l'état du trafic géré par le répéteur :
- **Nom** : nom de l'interface réseau. `LAN` concerne tout le trafic entre le répéteur et la Livebox. Ensuite on dispose des statistiques par interface précise (les deux prises Ethernet ainsi que les deux bandes Wifi).
- **Rx** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue. S'affiche en rouge si des erreurs de transmission sont détectées. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **Tx** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue. S'affiche en rouge si des erreurs de transmission sont détectées. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **TauxRx** : taux d'octets reçus par seconde par l'interface dans les trois dernières secondes (fréquence réglable dans les préférences).
- **TauxTx** : taux d'octets envoyés par seconde par l'interface dans les trois dernières secondes (fréquence réglable dans les préférences).

Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par le répéteur.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie le répéteur (il ne s'agit pas d'un défaut du programme).

### Actions - Boutons d'actions et de contrôle

Les actions concernant le **Wifi** :
- **`Wifi ON`** : permet d'activer l'interface Wifi du répéteur.
- **`Wifi OFF`** : permet de désactiver l'interface Wifi du répéteur.
- **`Planificateur Wifi ON`** : permet d'activer le planificateur Wifi du répéteur. Ce planificateur doit être configuré depuis l'interface Web du répéteur.
- **`Planificateur Wifi OFF`** : permet de désactiver le planificateur Wifi du répéteur.

L'état global du Wifi peut être consulté via le bouton `État Global Wifi...` de l'onglet `Actions`.

Les actions concernant les **Redémarrages** :
- **`Redémarrer le Répéteur...`** : permet de forcer un redémarrage du répéteur.
- **`Historique Redémarrages...`** : permet d'afficher l'historique des derniers redémarrages.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_Repeater_RebootHistory.png)

    Cet historique est particulièrement utile pour détecter les redémarrages forcés par Orange pour mettre à jour le logiciel du répéteur.
    La liste affiche les colonnes suivantes :
    - **Date Redémarrage** : date et heure du démarrage.
    - **Raison Redémarrage** : la raison de ce démarrage. Typiquement "NMC" ou "POR" indique un démarrage forcé par logiciel et "Unsupported chipset" un redémarrage causé par une coupure de courant ou l'interrupteur du répéteur.
    - **Date Arrêt** : la date et heure de l'extinction.
    - **Raison Arrêt** : la raison de cette extinction. Typiquement vide pour une coupure de courant, "Upgrade" pour une mise à jour logiciel et "WebUI reboot" pour un redémarrage demandé depuis l'interface Web ou LiveboxMonitor.

Les actions diverses :
- **Réauthentifier...** : pour forcer la création d'une nouvelle session avec le répéteur. Si vous laissez trop longtemps le programme tourner sans visualiser les statistiques du répéteur ni effectuer la moindre action, la session sera automatiquement libérée par le répéteur. Dans ce cas des erreurs vont se produire en effectuant des actions : ce bouton permettra de recréer la session, permettant de reprendre les actions sans erreur.

### Boutons
Les onglets de répéteur Wifi proposent les boutons suivants :
- **`Informations Répéteur`** : affiche les informations principales concernant le répéteur, telles que les versions de logiciels, le nom du modèle, l'heure de l'horloge interne, etc.
- **`Informations Wifi`** : affiche les informations générales sur la connectivité Wifi, et l'état de chaque accès. Pour chaque accès on dispose d'informations détaillées telles que le canal, le standard, la bande passante, la qualité, la bande, le nombre d'appareils connectés, etc.
- **`Informations LAN`** : affiche les informations générales sur la connectivité LAN. Pour chaque interface Ethernet on peut identifier si elle est active ou non, la bande passante, etc.
- **`Export...`** : permet d'exporter l'ensemble des informations affichées par chacun des boutons dans un fichier texte. Utile pour communiquer ces informations ou faire un suivi pour détecter les changements.


## Gestion et personnalisation des icônes d'appareil <a id="icons"></a>

Toutes les icônes d'appareil sont initialement stockées par la Livebox et le programme va les chercher une à une, ce qui peut provoquer une certaine latence (par exemple lorsque l'on clique une première fois sur le bouton `Assigner Type...` pour changer le type d'un appareil).
Pour éviter cette latence, le programme stocke dans un cache local toutes les icônes téléchargées de la Livebox pour pouvoir les retrouver plus rapidement au prochain lancement. Ce cache est contenu dans un répertoire appelé `lbcache_` suivie de la version du firmware de la Livebox (ce qui fait que plusieurs caches peuvent être maintenu si vous accédez à plusieurs Livebox de versions différentes).
Ce répertoire est créé automatiquement dans [le répertoire de configuration du programme](#configuration).

Il est aussi possible de modifier ces icônes, et aussi de créer de nouveaux types d'appareils avec leur propre icône.
Une page d'explication dédiée à ces possibilités est disponible [ici](https://github.com/p-dor/LiveboxMonitor/blob/main/docs/CustomIcons.md).

