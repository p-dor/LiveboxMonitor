# ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_AppIcon.png) LiveboxMonitor

L'application [LiveboxMonitor](https://github.com/p-dor/LiveboxMonitor) est une interface graphique dynamique pour :
- Contrôler les appareils qui se connectent à la Livebox et détecter rapidement les intrusions,
- Obtenir des statistiques détaillées de trafic, par appareil, global,
- Obtenir beaucoup de détails sur la Livebox elle-même et contrôler la qualité de sa ligne fibre,
- Avoir beaucoup de détails sur les appareils qui se connectent (actifs ou non),
- Lire le journal des événements d'un appareil donné,
- Contrôler de manière fine les réglages du serveur DHCP,
- Contrôler l'état du Wifi,
- Contrôler les appels téléphoniques ainsi que la liste des contacts,
- Contrôler un ou plusieurs répéteurs Wifi Orange connectés.

**AVERTISSEMENT** : le programme est actuellement dans une phase bêta et nécessite des retours utilisateurs pour certifier qu'il fonctionne dans des contextes différents. Il a été **conçu pour contrôler une Livebox 5 et a été adapté avec quelques tests pour les Livebox 4 et 6**, des tests supplémentaires avec une Livebox 4 ou 6 seraient bienvenus. 

L'application est dynamique car elle réagit aux événements envoyés par la Livebox et les interprète.

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceList.png)


## Installation

L'application est écrite en [Python 3.9](https://www.python.org/downloads/) et est basée sur [PyQT 6](https://pypi.org/project/PyQt6/) pour l'interface graphique.

Les autres dépendances sont `requests`, `cryptography` et `python-dateutil`.

**Note** : Le module `LmSession` est une adaptation du package [sysbus](https://github.com/rene-d/sysbus) pour les Livebox 5 & 6. Le support des événements a aussi été rajouté.

### Téléchargement

Des programmes autonomes construits avec [PyInstaller](https://pyinstaller.org) sont disponibles pour les plateformes Windows & MacOS :
- Windows : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor.exe)
- Windows avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor_Console.exe)
- MacOS (Intel) : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor.dmg)
- MacOS (Intel) avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor_Console.dmg)
- MacOS (Silicon) : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor_Silicon.dmg)
- MacOS (Silicon) avec console : [Télécharger](https://github.com/p-dor/LiveboxMonitor/releases/download/0.9.7/LiveboxMonitor_Silicon_Console.dmg)


### Utilisation directe via les sources

Installation :  
```
    git clone https://github.com/p-dor/LiveboxMonitor.git  
    cd LiveboxMonitor  
    pip install -r requirements.txt
```

Lancement : 
``` 
    python3 LiveboxMonitor.py
```


## Prise en main

L'interface se veut intuitive mais il vaut mieux se reporter à la documentation pour comprendre certains comportements ou représentations.
Les points importants à comprendre avant de commencer :
- La connexion s'établit avec exactement les mêmes informations que pour accéder à l'interface Web de configuration de la Livebox. Pour l'URL il faut essayer http://livebox.home/, http://livebox/ ou http://192.168.1.1/. Pour l'utilisateur il faut laisser à la valeur par défaut `admin`. Et pour le mot de passe c'est soit ce que vous avez indiqué vous-même soit le mot de passe d'origine. Plus d'informations [ici](https://assistance.orange.fr/livebox-modem/toutes-les-livebox-et-modems/installer-et-utiliser/piloter-et-parametrer-votre-materiel/l-interface-de-configuration/livebox-5-acceder-a-l-interface-de-configuration_292471-827404) pour la Livebox 5, ou [ici](https://assistance.orange.fr/livebox-modem/toutes-les-livebox-et-modems/installer-et-utiliser/piloter-et-parametrer-votre-materiel/l-interface-de-configuration/livebox-6-acceder-a-l-interface-de-configuration_363963-897414) pour la Livebox 6.
- Il est normal que lors du premier lancement de l'application tous les appareils soient marqués comme inconnus (**UNKNOWN** en rouge). En effet un des buts de ce programme est d'identifier rapidement des appareils inconnus connectés sur le réseau grâce à une base de noms locale (le fichier `MacAddrTable.txt`). Il faut donc commencer par nommer chaque appareil que vous jugez légitime grâce au bouton `Assign Name...` de l'onglet `Device Infos`. Cette base locale constituera la référence de confiance de tous les appareils légitimes sur votre réseau. Le bouton `Assign name...` vous permettra aussi de facilement assigner le même nom que celui qui a été donné à la Livebox.
- Il est normal que les statistiques réseau apparaissent et disparaissent. En effet le programme rafraîchit ces statistiques toutes les secondes (ou toutes les 30 secondes dans certains cas), et si d'un rafraîchissement à l'autre il n'y a pas eu de transfert la case devient vide. Ce choix a été fait pour permettre de mieux visualiser les cases non-vides, là où il se passe quelque chose.
- Toutes les colonnes dans le programme sont redimensionnables à la souris sauf certaines qui s'élargissent dynamiquement en fonction de la taille de la fenêtre. Donc, en fonction de la situation, vous pouvez soit redimensionner la colonne soit la fenêtre avec la souris pour ajuster la largeur d'une colonne.
- On peut copier la valeur de n'importe quelle cellule de liste dans le presse-papiers. Pour cela il suffit de cliquer sur la cellule et de taper Ctrl-C.


## Discussion

Un [fil de discussion](https://lafibre.info/orange-les-news/controler-son-reseau-livebox-5-ou-6/) est actif sur le forum [lafibre.info](https://lafibre.info). Il est possible d'y poster vos commentaires, résultats de tests ou de faire des demandes de fonctionnalités.


## Configuration

Le programme créé automatiquement dans son répertoire deux fichiers de configuration au format JSON :
- `Config.txt` : contient tous les paramètres de l'application.
- `MacAddrTable.txt` : contient la correspondance entre les adresses MAC et les noms d'appareil.

**Note** : lorsque les programmes construits avec [PyInstaller](https://pyinstaller.org) sont utilisés, les fichiers de configurations se trouvent dans les répertoires standards du système :
- Windows : `%APPDATA%\LiveboxMonitor`
- MacOS : `~/Library/Application Support/LiveboxMonitor`

### Le fichier Config.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer. Les réglages principaux se font via le bouton `Preferences...` de l'onglet `Actions`.  
À savoir :  
- Les mots de passe y sont stockés cryptés. La clef de cryptage du mot de passe peut être modifiée, elle est située dans le module `LmConfig.py`, variable `SECRET`.
- La clef `Repeaters` est générée automatiquement par le programme si des mots de passe différents sont utilisés pour le ou les répéteurs Wifi Orange connectés. La structure de ce paramètre est aussi au format JSON, utilise pour clef les adresses MAC des répéteurs, et référence pour chaque répéteur les valeurs 'User' & 'Password'.

### Le fichier MacAddrTable.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer.
Les clefs correspondent aux adresses MAC des appareils et les valeurs au nom attribué.
Tout appareil détecté dont l'adresse MAC n'est pas répertoriée sera affiché comme 'UNKNOWN' (inconnu) en rouge. Cette fonctionnalité est surtout utile pour détecter les nouveaux appareils ou des tentatives d'intrusions.

Pourquoi utiliser une base de noms locale alors que la Livebox stocke aussi des noms ?
- Parce que la Livebox "oublie" tout appareil qui ne s'est pas connecté depuis plus d'un mois.
- Parce que parfois la Livebox perd des noms de façon impromptue pour certains appareils. C'est le cas par exemple pour le nom des répéteurs Wifi.  
Un fichier de noms local offre la garantie de savoir si un appareil est vraiment inconnu.


## Device List - Liste des appareils connectés

### Liste
La liste des appareils affiche les colonnes suivantes :
- **T** : icône correspondant au type de l'appareil. Ce type peut être attribué ou changé via le bouton `Assign Type...` de l'onglet `Device Infos`.
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign Name...` de l'onglet `Device Infos`.
- **Livebox Name** : nom de l'appareil tel que paramétré dans la Livebox et visible dans l'interface Web de la Livebox. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign Name...` de l'onglet `Device Infos`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP v4 de l'appareil sur le LAN. Cette adresse s'affiche en caractères gras si cette adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox. Et elle s'affiche en rouge si l'adresse n'est pas atteignable sur le réseau (unreacheable), typiquement lorsque l'appareil n'est pas actif.
- **Link** : point de liaison de l'appareil avec le réseau. D'abord le nom de l'appareil, c'est-à-dire la Livebox elle-même ou le nom d'un des répéteurs Wifi Orange connectés, et ensuite l'interface sur cet appareil. `eth` signifie une des prises Ethernet suivi du numéro de prise. `Wifi` signifie une connexion Wifi suivi par la bande de connexion, soit 2.4GHz soit 5GHz.
- **A** : indique par une icône si l'appareil est actif ou non. Par défaut la liste est triée pour montrer d'abord les appareils actifs.
- **Wifi** : qualité de la connexion Wifi.
- **E** : indique par une icône avec un point d'exclamation ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Exclamation.png) lorsqu'un événement est reçu pour cet appareil. La liste détaillée des événements, ainsi que le contenu des événements eux-mêmes, peuvent être consultés via l'onglet `Events`.
- **Down** : nombre d'octets reçus par l'appareil depuis le dernier démarrage de la Livebox.
- **Up** : nombre d'octets envoyés par l'appareil depuis le dernier démarrage de la Livebox.
- **DRate** : taux d'octets reçus par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.
- **URate** : taux d'octets envoyés par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.

Les statistiques d'octets envoyés ou reçus par seconde sont calculées grâce aux statistiques envoyées par la Livebox sous forme d'événement toutes les 30 secondes par appareil. Cette résolution étant peu significative le programme utilise une autre interface disponible pour les appareils Wifi uniquement pour obtenir des statistiques toutes les secondes. Ces dernières sont affichées en bleu.
Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par la Livebox.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).

### Boutons
L'onglet `Device List` propose les boutons suivants :
- **`Refresh`** : permet de forcer le rafraîchissement de la liste des appareils, non seulement dans cet onglet mais aussi dans les onglets `Device Infos` et `Events`. Utile par exemple si le programme est actif alors que l'ordinateur sort de veille : des événements ayant probablement été raté par le programme, un rafraîchissement permettra de retrouver une vue à jour.
- **`Device Infos`** : permet de basculer dans l'onglet `Device Infos` pour l'appareil sélectionné et de voir directement ses informations.
- **`Device Events`** : permet de basculer dans l'onglet `Events` pour l'appareil sélectionné et de voir directement les événements reçus le concernant.
- **`IPv6...`** : permet d'avoir le statut d'activation de l'IPv6, l'adresse IPv6 de la Livebox ainsi que son préfixe, et la liste des appareils connectés ou non ayant une ou plusieurs IPv6 assignées.


## Livebox Stats/Infos - Statistiques de trafic et infos avancées de la Livebox

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_LiveboxInfos.png)

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations sont accessibles par les boutons, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier.

### Statistiques

Liste permettant de surveiller l'état du trafic :
- **Name** : nom de l'interface réseau. `Fiber` concerne tout le trafic WAN, c'est-à-dire externe entre la Livebox et internet. `LAN` tout le trafic interne transitant à travers la Livebox. Ensuite on dispose des statistiques par interface précise. Les interfaces `Guest` concernent le trafic du réseau Wifi invité, s'il est activé.
- **Down** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **Up** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **DRate** : taux d'octets reçus par seconde par l'interface dans la dernière seconde.
- **URate** : taux d'octets envoyés par seconde par l'interface dans la dernière seconde.

Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par la Livebox.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).

### Boutons
L'onglet `Livebox Stats/Infos` propose les boutons suivants :
- **`Livebox Infos`** : affiche les informations principales concernant la Livebox, telles que les versions de logiciels, l'adresse IP WAN, les services actifs, l'état de la mémoire, etc.
- **`Internet Infos`** : affiche le type d'accès internet, les identifiants de connexion, les adresses IPs v4 & v6, la date et heure de la dernière connexion, la bande passante de la connexion, la MTU, etc
- **`Wifi Infos`** : affiche les informations générales sur la connectivité Wifi, et l'état de chaque accès y compris pour les accès invités. Pour chaque accès on dispose d'informations détaillées telles que le canal, le standard, la bande passante, la qualité, la bande, le nombre d'appareils connectés, etc.
- **`LAN Infos`** : affiche les informations générales sur la connectivité LAN. Il s'agit des informations DHCP de base et pour chaque interface Ethernet on peut identifier si elle est active ou non, la bande passante, etc.
- **`ONT Infos`** : affiche les informations importantes concernant la connexion et le module Fibre (ONT), telles que la bande passante, la qualité du signal, le numéro de série et les versions logicielles, etc. Les champs `Signal RxPower`, `Signal TxPower`, `Temperature`, `Voltage` et `BIAS` affichent des valeurs vertes si elles correspondent aux normes de qualité acceptables pour la connexion, en rouge si elles représentent un problème.
![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_LiveboxInfos_ONT.png)
- **`VoIP Infos`** : affiche les informations générales concernant la téléphonie, telles que le protocole, le numéro de téléphone, la version logicielle de l'interface DECT, etc.
- **`IPTV Infos`** : affiche les informations générales relatives aux services de télévision.
- **`USB Infos`** : affiche les informations concernant le ou les ports USBs. Si une clef USB est insérée, ou a été insérée depuis le dernier démarrage de la Livebox, ses informations sont affichées.
- **`Export...`** : permet d'exporter l'ensemble des informations affichées par chacun des boutons dans un fichier texte. Utile pour communiquer ces informations ou faire un suivi pour détecter les changements.


## Device Infos - Informations détaillées pour chaque appareil connu

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign Name...`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.

Lorsqu'un appareil est sélectionné dans cette liste ses informations détaillées s'affichent dans la liste de droite. Attributs notables :
- **Active** : indique si l'appareil est actif (True) ou non (False).
- **Authenticated** : indique si la connexion Wifi de l'appareil a bien été authentifiée.
- **Blocked** : indique si vous avez bloqué la connexion de l'appareil à la Livebox (True) ou non (False). Le blocage peut être contrôlé avec les boutons `Block` et `Unblock`. Il peut être utile de bloquer un appareil inconnu si vous avez des suspicions.
- **First connection** : date et heure de la première connexion. Attention cette valeur peut aussi correspondre à la date/heure d'un précédent redémarrage de la Livebox.
- **Last connection** : date et heure de la dernière connexion.
- **Last changed** : date et heure du dernier changement détecté pour cet appareil.
- **Name** : nom connu par la Livebox pour cet appareil, avec la source de ce nom entre parenthèses. Ainsi plusieurs noms peuvent s'afficher pour des sources différentes.
- **Type** : type connu par la Livebox pour cet appareil, avec la source de ce type entre parenthèses. Ainsi plusieurs types peuvent s'afficher pour des sources différentes.
- **IPvX Address** : adresse IP (v4 ou v6) de l'appareil. Entre parenthèses s'affiche si l'adresse est atteignable sur le réseau (reacheable) ou non (not reacheable). Si l'adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox une mention s'affiche (Reserved).
- **Manufacturer** : le fabricant de cet appareil, déduit à partir de son adresse MAC. Le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabricant. C'est un service gratuit, mais il faut créer un compte et indiquer l'API Key correspondante dans les préférences pour bénéficier de cette fonctionnalité.
- **Wifi Signal Strength** et **Wifi Signal Noise Ratio** : donne des indications sur la qualité de la connexion pour les appareils Wifi.

### Boutons
L'onglet `Device Infos` propose les boutons suivants :
- **`Refresh`** : rafraîchit les informations affichées pour l'appareil sélectionné.
- **`Assign Name...`** : permet d'attribuer ou d'effacer le nom local (Monitor) et/ou le nom Livebox de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos_AssignName.png)

    Décocher la boite pour effacer le nom. Les deux noms peuvent être différents.
- **`Assign Type...`** : permet d'attribuer ou d'effacer le type de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos_AssignType.png)

    Il est possible de sélectionner un des types standards connus par la Livebox dans le menu, chaque type étant affiché avec son icône Livebox correspondante. Lorsqu'un type standard est sélectionné, son nom connu par la Livebox est automatiquement rempli dans la zone de texte et on peut valider le dialogue. Il reste possible d'assigner manuellement un type non connu par la Livebox en le tapant directement dans la zone de texte. Note : bien que le type "Djingo Speaker" soit référencé comme standard par la Livebox 5, ce type ne semble pas (encore ?) supporté par l'interface graphique de la Livebox.
- **`Forget...`** : permet de demander à la Livebox d'oublier définitivement cet appareil. Il disparaîtra donc immédiatement de toutes les listes. Attention si l'appareil en question est actif, sa connexion ne sera nullement suspendue, cependant toute son activité restera invisible et ce jusqu'à sa prochaine tentative de connexion.
- **`Block`** : permet de bloquer la connexion de l'appareil sélectionné.
- **`Unblock`** : permet de débloquer la connexion de l'appareil sélectionné. L'état bloqué ou non s'affiche dans les informations de l'appareil, champs "Blocked".


## Events - Liste des événements reçus pour chaque appareil connu

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Events.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign Name...` de l'onglet `Device Infos`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.

Lorsqu'un appareil est sélectionné dans cette liste tous les événements reçus depuis le lancement du programme pour cet appareil s'affichent dans la liste de droite. La plupart de ces événements ont été interprétés par le programme pour mettre à jour l'interface dynamiquement, et cette liste permet d'avoir un historique. La taille de cet historique par appareil est limitée aux 100 dernières entrées (cette limite peut être ajustée facilement en modifiant la variable `MAX_EVENT_BUFFER_PER_DEVICE` du module `LmEventsTab.py`).

La liste des événements est composée des colonnes :
- **Time** : heure de réception de l'événement.
- **Reason** : le type d'événement généré par la Livebox.
- **Attributes** : aperçu des données brutes de l'événement lui-même, au format.

Un double clic sur un événement ou un clic sur le bouton **`Display Event`** permet d'afficher un dialogue contenant les informations complètes :
- **Raised** : date et heure précise de réception de l'événement.
- **Handler** : gestionnaire de l'événement, contenant la plupart du temps la clef de l'appareil qui n'est autre que son adresse MAC.
- **Reason** : le type d'événement.
- **Attributes** : données brutes complètes de l'événement lui-même, au format JSON tel que généré par la Livebox.


## DHCP - Contrôle fin du serveur DHCP

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DHCP.png)

### Baux statiques
La liste des baux statiques configurés est affichée sur la gauche. Les deux domaines de réseau sont gérés :
- `Home` : votre réseau privé, dont vous pouvez configurer sa plage d'IPs.
- `Guest` : le réseau Wifi invité, qui a sa propre plage d'IPs (non-modifiable).
La liste affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign Name...` de l'onglet `Device Infos`.
- **Domain** : domaine d'assignation, `Home` ou `Guest`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP assignée statiquement à l'appareil.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des baux :
- **`Refresh`** : rafraîchit la liste des baux statiques.
- **`Add...`** : permet d'ajouter un bail.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DHCP_AddBinding.png)
    La liste des appareils proposés est triée et est composée d'un mélange des appareils connectés et ceux référencés dans le fichier local des adresses MAC. L'adresse MAC est directement déduite de l'appareil sélectionné mais on peut en taper une totalement à la main. Choisir le domaine réseau entre `Home` ou `Guest`, et une adresse IP libre sera automatiquement proposée mais elle ci reste bien sûr configurable. Attention un même appareil ne peut être configuré que sur un seul domaine, et s'il se connecte sur un domaine alors qu'un bail statique est configuré sur l'autre ce bail sera automatiquement supprimé.
- **`Delete`** : supprime le bail sélectionné.

### Informations DHCP détaillées
La liste sur la droite affiche de nombreux détails sur le serveur DHCP:
- La configuration détaillée des deux domaines `Home` et `Guest`.
- Des détails sur le DHCPv4 ainsi que toutes les options DHCP envoyées et reçues.
- Des détails sur le DHCPv6 ainsi que toutes les options DHCP envoyées et reçues.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des baux :
- **`Refresh`** : rafraîchit la liste des informations DHCP.
- **`DHCP Setup...`** : permet de configurer le serveur DHCP.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DHCP_Setup.png)
    Permet d'activer ou de désactiver le serveur, de changer l'adresse IP de la Livebox, de changer le masque de sous-réseau du serveur DHCP ainsi que la plage d'adresse IP pour le domaine `Home`.


## Phone - Liste des appels téléphoniques / liste des contacts

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Phone.png)

### Appels téléphoniques
La liste des appels téléphoniques, sur la gauche, affiche les colonnes suivantes :
- **T** : icône correspondant au type de l'appel.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Call_In.png) : appel reçu.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Call_In_Missed.png) : appel manqué. Dans ce cas toute la ligne est indiquée en couleur rouge.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Call_Out.png) : appel émis.
    - ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Call_Out_Failed.png) : appel émis mais non abouti.
- **Time** : date et heure de l'appel.
- **Number** : numéro de téléphone concerné.
- **Contact** : le nom du contact déterminé par la Livebox en fonction de la liste des contacts au moment de l'appel. Si la Livebox n'a mémorisé aucun nom, alors le programme essai d'en trouver un dynamiquement à partir de la liste des contacts enregistrés par correspondance avec le numéro de téléphone.
- **Duration** : durée de l'appel.

Un **double clic** sur un appel permet de facilement créer ou éditer le contact correspondant.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des appels :
- **`Refresh`** : rafraîchit la liste des appels.
- **`Delete`** : supprime l'appel sélectionné.
- **`Delete all...`** : supprime tous les appels.

### Contacts
La liste des contacts, sur la droite, affiche les colonnes suivantes :
- **Name** : nom du contact, au format nom + prénom.
- **Mobile** : numéro de téléphone portable.
- **Home** : numéro de téléphone fixe.
- **Work** : numéro de téléphone professionnel.
- **Ring** : type de sonnerie sélectionné parmi les 7 supportés par la Livebox.

Un **double clic** sur un contact permet de facilement l'éditer.  
**Attention** : la Livebox supporte un maximum de 255 contacts.

### Boutons
Les boutons suivants sont proposés pour gérer la liste des contacts :
- **`Refresh`** : rafraîchit la liste des contacts.
- **`Add..`** : permet de rajouter un contact. Attention aucun test de doublon n'est effectué.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Phone_Contact.png)

- **`Edit...`** : pour éditer le contact sélectionné.
- **`Delete`** : supprime le contact sélectionné.
- **`Delete all...`** : supprime tous les contacts.
- **`Phone Ring`** : permet de tester le téléphone. Sur la gauche du bouton on peut sélectionner un des 7 types de sonnerie proposés par la Livebox, sinon le type par défaut est utilisé.
- **`Export...`** : permet d'exporter l'ensemble des contacts dans un fichier au [format VCF](https://en.wikipedia.org/wiki/VCard). Très utile pour les sauvegarder.
- **`Import...`** : permet d'importer un ou plusieurs fichiers au [format VCF](https://en.wikipedia.org/wiki/VCard). Attention aucun test de doublon n'est effectué. Si la limite du nombre de contacts maximum supporté (255) est atteint l'import est interrompu.


## Actions - Boutons d'actions et de contrôle

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Actions.png)

Cet onglet permet une liste d'actions par catégorie.

Les actions concernant le **Wifi** :
- **`Wifi ON`** : permet d'activer l'interface Wifi de la Livebox.
- **`Wifi OFF`** : permet de désactiver l'interface Wifi de la Livebox.
- **`Guest Wifi ON`** : permet d'activer l'interface Wifi invité de la Livebox.
- **`Guest Wifi OFF`** : permet de désactiver l'interface Wifi invité de la Livebox.
- **`Wifi Scheduler ON`** : permet d'activer le planificateur Wifi de la Livebox. Ce planificateur doit être configuré depuis l'interface Web de la Livebox.
- **`Wifi Scheduler OFF`** : permet de désactiver le planificateur Wifi de la Livebox.
- **`Show Global Status...`** : permet d'afficher l'état global du Wifi, en incluant l'état Wifi de tous les répéteurs Wifi Orange potentiellement connectés.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Actions_WifiGlobalStatus.png)

Les actions concernant les **Reboots** (redémarrages de la Livebox) :
- **`Reboot Livebox...`** : permet de forcer un redémarrage de la Livebox.
- **`Reboot History...`** : permet d'afficher l'historique des derniers redémarrages.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Actions_RebootHistory.png)

    Cet historique est particulièrement utile pour détecter les redémarrages forcés par Orange pour mettre à jour le logiciel de la Livebox.
    La liste affiche les colonnes suivantes :
    - **Boot Date** : date et heure du démarrage.
    - **Boot Reason** : la raison de ce démarrage. Typiquement "NMC" indique un démarrage forcé par logiciel et "Unsupported chipset" un redémarrage causé par une coupure de courant ou l'interrupteur de la Livebox.
    - **Shutdown Date** : la date et heure de l'extinction.
    - **Shutdown Reason** : la raison de cette extinction. Typiquement vide pour une coupure de courant, "Upgrade" pour une mise à jour logiciel et "GUI_Reboot" pour un redémarrage demandé depuis l'interface Web ou LiveboxMonitor.

Les actions concernant le **Setup** (réglages) :
- **`Preferences...`** : permet d'afficher l'écran des préférences du programme.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Actions_Preferences.png)

    Le programme supporte de pouvoir gérer plusieurs Livebox à l'aide de profils différents. Chaque profil doit avoir un nom unique. Par défaut un profil principal (main) est créé automatiquement. Si plusieurs profils sont configurés le nom du profil en cours est affiché dans le titre de la fenêtre principale entre crochets.
    Au lancement du programme, le profil par défaut est utilisé, mais si aucun profil par défaut n'est configuré ou si la touche `Ctrl` est enfoncée le programme affiche un dialogue pour sélectionner le profil à utiliser.  
 
    Pour chaque **profil** il est possible de configurer :
    - `Name` : nom du profil.
    - `Livebox URL` : adresse de la Livebox. La valeur par défaut est `http://livebox.home/`.
    - `Livebox User` : login pour l'ouverture de session. Par défaut `admin`. Le mot de passe est demandé automatiquement lors de l'utilisation du profil s'il n'est pas renseigné ou s'il est erroné.
    - `Filter Devices` : active le filtrage des appareils afin de ne pas montrer certains appareils "fantômes" détectés par la Livebox. Quand ce paramètre est activé le programme affiche les mêmes appareils que l'interface Web de la Livebox. Ce paramètre est activé par défaut.
    - `MacAddr Table File` : nom du fichier de stockage des noms d'appareils. Par défaut `MacAddrTable.txt`. Voire `Le fichier MacAddrTable.txt` de la section `Configuration` pour plus d'explications.
    - `Default` : indique qu'il s'agit du profil par défaut à utiliser au lancement du programme. Il ne peut y avoir qu'un seul profil par défaut.  

    Les **préférences** générales permettent de régler :
    - `macaddress.io API Key` : le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabriquant d'un appareil à partir de son adresse MAC (champ **Manufacturer** dans les informations détaillées par appareil). C'est un service gratuit, mais il faut créer un compte et indiquer ici l'API Key correspondante pour bénéficier de cette fonctionnalité.
    - `Intl Phone Code` : indicatif téléphonique local, utile pour faire correspondre les appels téléphoniques avec les numéros de contacts. Par défaut le code de la France est utilisé, c'est-à-dire 33.
    - `List Header Height` : hauteur en pixels des entêtes de liste, par défaut 25.
    - `List Header Font Size` : taille de la police de caractères des entêtes de liste. Une valeur à zéro signifie d'utiliser la taille système. Par défaut ce paramètre est à zéro.
    - `List Line Height` : hauteur en pixels des lignes de liste, par défaut 30.
    - `List Line Font Size` : taille de la police de caractères des lignes de liste. Une valeur à zéro signifie d'utiliser la taille système. Par défaut ce paramètre est à zéro.
- **`Change Profile...`** : affiche un dialogue permettant de changer le profil en cours et de relancer le programme.

Les actions techniques de **Debug** (débogage) :
- **`Raw Device List...`** : permet d'afficher la réponse brute JSON de la Livebox concernant la liste des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`Raw Topology...`** : permet d'afficher la réponse brute JSON de la Livebox concernant la topologie de connexion des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`Set Log Level...`** : permet de changer le niveau de logs dans la console. Ce niveau est stocké dans la configuration du programme et sera donc conservé au prochain lancement du programme.


Autres actions :
- **Quit Application** : pour quitter l'application. Strictement équivalent à fermer la fenêtre de l'application.
- Un clic sur le lien GitHub de l'application ouvrira la page correspondante sur votre navigateur.


## Onglets répéteurs Wifi

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Repeater.png)

Le programme créé dynamiquement un onglet par répéteur connecté. Si le répéteur a un nom local, celui-ci est utilisé dans l'onglet, sinon le nom par défaut est de type "RW #" suivit du numéro de répéteur dans l'ordre de détection.
Les répéteurs font aussi parti des appareils connus, ils sont donc visibles dans l'onglet `Device List` et leur nom peut être changé via le bouton `Assign Name...` de l'onglet `Device Infos`.

Une icône dans le nom de l'onglet permet de connaître l'état de la connexion avec le répéteur :
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Cross.png) : le répéteur est inactif ou n'a pas d'adresse IP attribuée.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Prohibition.png) : le répéteur est actif mais aucune session n'est ouverte. Si cet état subsiste vous pouvez essayer de forcer la création d'une session en cliquant sur le bouton `Resign...`.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Tick.png) : le répéteur est actif et une session a été créée pour communiquer avec lui.

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations détaillées sont accessibles via la barre de boutons en bas, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier. Enfin, une série d'actions est possible via les boutons sur la gauche.

### Statistiques

Liste permettant de surveiller l'état du trafic géré par le répéteur :
- **Name** : nom de l'interface réseau. `LAN` concerne tout le trafic entre le répéteur et la Livebox. Ensuite on dispose des statistiques par interface précise (les deux prises Ethernet ainsi que les deux bandes Wifi).
- **Down** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **Up** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue. Attention ce compteur est circulaire et ne dépasse pas les 4 Go.
- **DRate** : taux d'octets reçus par seconde par l'interface dans la dernière seconde.
- **URate** : taux d'octets envoyés par seconde par l'interface dans la dernière seconde.

Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par le répéteur.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie le répéteur (il ne s'agit pas d'un défaut du programme).

### Actions - Boutons d'actions et de contrôle

Les actions concernant le **Wifi** :
- **`Wifi ON`** : permet d'activer l'interface Wifi du répéteur.
- **`Wifi OFF`** : permet de désactiver l'interface Wifi du répéteur.
- **`Wifi Scheduler ON`** : permet d'activer le planificateur Wifi du répéteur. Ce planificateur doit être configuré depuis l'interface Web du répéteur.
- **`Wifi Scheduler OFF`** : permet de désactiver le planificateur Wifi du répéteur.

L'état global du Wifi peut être consulté via le bouton `Show Global Status...` de l'onglet `Actions`.

Les actions concernant les **Reboots** (redémarrages du répéteur) :
- **`Reboot Repeater...`** : permet de forcer un redémarrage du répéteur.
- **`Reboot History...`** : permet d'afficher l'historique des derniers redémarrages.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Repeater_RebootHistory.png)

    Cet historique est particulièrement utile pour détecter les redémarrages forcés par Orange pour mettre à jour le logiciel du répéteur.
    La liste affiche les colonnes suivantes :
    - **Boot Date** : date et heure du démarrage.
    - **Boot Reason** : la raison de ce démarrage. Typiquement "NMC" ou "POR" indique un démarrage forcé par logiciel et "Unsupported chipset" un redémarrage causé par une coupure de courant ou l'interrupteur du répéteur.
    - **Shutdown Date** : la date et heure de l'extinction.
    - **Shutdown Reason** : la raison de cette extinction. Typiquement vide pour une coupure de courant, "Upgrade" pour une mise à jour logiciel et "WebUI reboot" pour un redémarrage demandé depuis l'interface Web ou LiveboxMonitor.

Les actions diverses :
- **Resign...** : pour forcer la création d'une nouvelle session avec le répéteur. Si vous laissez trop longtemps le programme tourner sans visualiser les statistiques du répéteur ni effectuer la moindre action, la session sera automatiquement libérée par le répéteur. Dans ce cas des erreurs vont se produire en effectuant des actions : ce bouton permettra de recréer la session, permettant de reprendre les actions sans erreur.

### Boutons
Les onglets de répéteur Wifi proposent les boutons suivants :
- **`Repeater Infos`** : affiche les informations principales concernant le répéteur, telles que les versions de logiciels, le nom du modèle, l'heure de l'horloge internet, etc.
- **`Wifi Infos`** : affiche les informations générales sur la connectivité Wifi, et l'état de chaque accès. Pour chaque accès on dispose d'informations détaillées telles que le canal, le standard, la bande passante, la qualité, la bande, le nombre d'appareils connectés, etc.
- **`LAN Infos`** : affiche les informations générales sur la connectivité LAN. Pour chaque interface Ethernet on peut identifier si elle est active ou non, la bande passante, etc.
- **`Export...`** : permet d'exporter l'ensemble des informations affichées par chacun des boutons dans un fichier texte. Utile pour communiquer ces informations ou faire un suivi pour détecter les changements.
