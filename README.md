# LiveboxMonitor

L'application `LiveboxMonitor` est une interface graphique dynamique pour :
- Contrôler les appareils qui se connectent à la Livebox,
- Obtenir des statistiques détaillées de trafic,
- Obtenir beaucoup de détails sur la Livebox elle-même et contrôler la qualité de sa ligne fibre,
- Avoir des détails sur les appareils qui se connectent (actifs ou non),
- Lire le journal des événements d'un appareil donné,
- Contrôler l'état du Wifi,
- Contrôler un ou plusieurs répéteur Wifi Orange connecté.

**AVERTISSEMENT** : le programme est actuellement dans une phase béta et nécessite des retours utilisateurs pour certifier qu'il fonctionne dans des contextes différents. Il a été **conçu pour contrôler une Livebox 5 avec une connexion Fibre / ONT**, des tests avec une Livebox 5 ADSL voire des Livebox 6 seraient bienvenus.

L'application est dynamique car elle réagit aux événements envoyés par la Livebox et les interprète.

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceList.png)


## Installation

L'application est écrite en [Python 3.9](https://www.python.org/downloads/) et est basée sur [PyQT 6](https://pypi.org/project/PyQt6/) pour l'interface graphique.

Les autres dépendances sont `requests` et `cryptography`.

Le module `LmSession` est une adaptation du package [sysbus](https://github.com/rene-d/sysbus) pour la Livebox 5. Le support des événements a aussi été rajouté.


## Configuration

Le programme créé automatiquement dans son répertoire deux fichiers de configuration au format JSON :
- `Config.txt` : contient tous les paramètres de l'application.
- `MacAddrTable.txt` : contient la correspondance entre les adresses MAC et les noms d'appareil.


### Le fichier Config.txt

Le programme supporte ces clefs de configuration :  
`Livebox URL` : adresse de la Livebox. La valeur par défaut est `http://livebox.home/`.  
`Livebox User` : login pour l'ouverture de session. Par défaut `admin`.  
`Livebox Password` : le mot de passe crypté pour l'ouverture de session. Ce le mot de passe est demandé automatiquement au lancement du programme si le mot de passe n'est pas renseigné ou s'il est erroné. La clef de cryptage du mot de passe peut être modifiée, elle est située dans le module `LmConfig.py`, variable `SECRET`.  
`MacAddr Table File` : nom du fichier de stockage des noms d'appareils. Par défaut `MacAddrTable.txt`.  
`MacAddr API Key` : le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabriquant d'un appareil à partir de son adresse MAC. C'est un service gratuit, mais il faut créer un compte et indiquer ici l'API Key correspondante pour bénéficier de cette fonctionnalité.


### Le fichier MacAddrTable.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer.
Les clefs correspondent aux adresses MAC des appareils et les valeurs au nom attribué.
Tout appareil détecté dont l'adresse MAC n'est pas répertoriée sera affiché comme 'UNKNOWN' (inconnu) en rouge.  Cette fonctionnalité est surtout utile pour détecter les nouveaux appareils ou des tentatives d'intrusions.

Pourquoi utiliser une base de noms locale alors que la Livebox stocke aussi des noms ?
- Parce que la Livebox "oublie" tout appareil qui ne s'est pas connecté depuis plus d'un mois.
- Parce que parfois la Livebox perd des noms de façon impromptue pour certains appareils. C'est le cas par exemple pour le nom des répéteurs Wifi.  
Un fichier de noms local offre la garanti de savoir si un appareil est vraiment inconnu.


## Device List - Liste des appareils connectés

### Liste
La liste des appareils affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...` de l'onglet `Device Infos`.
- **Livebox Name** : nom de l'appareil tel que paramétré dans la Livebox et visible dans l'interface Web de la Livebox. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...` de l'onglet `Device Infos`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP v4 de l'appareil sur le LAN. Cette adresse s'affiche en caractères gras si cette adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox. Et elle s'affiche en rouge si l'adresse n'est pas atteignable sur le réseau (unreacheable), typiquement lorsque l'appareil n'est pas actif.
- **Link** : point de liaison de l'appareil avec le réseau. D'abord le nom de l'appareil, c'est à dire la Livebox elle-même ou le nom d'un des répéteurs Wifi Orange connectés, et ensuite l'interface sur cet appareil. `eth`  signifie une des prises Ethernet suivi du numéro de prise. `Wifi` signifie une connexion Wifi suivi par la bande de connexion, soit 2.4GHz soit 5GHz.
- **A** : indique si l'appareil est actif ou nom par un A sur fond vert. Par défaut la liste est triée pour montrer d'abord les appareils actifs.
- **Wifi** : qualité de la connexion Wifi.
- **E** : indique par une icône avec un point d'exclamation ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Exclamation.png) lorsqu'un événement est reçu pour cet appareil. La liste détaillée des événements, ainsi que le contenu des événements eux-mêmes, peuvent être consulter via l'onglet `Events`.
- **Down** : nombre d'octets reçus par l'appareil depuis le dernier démarrage de la Livebox.
- **Up** : nombre d'octets envoyés par l'appareil depuis le dernier démarrage de la Livebox.
- **DRate** : taux d'octets reçus par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.
- **URate** : taux d'octets envoyés par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.

Les statistiques d'octets envoyés ou reçus par seconde sont calculés grâce aux statistiques envoyées par la Livebox sous forme d'événement toutes les 30 secondes par appareil. Cette résolution étant peu significative le programme utilise une autre interface disponible pour les appareils Wifi uniquement pour obtenir des statistiques toutes les secondes. Ces dernières sont affichées en bleues.
Si une statistique s'affiche en rouge cela signifie que des erreurs de transfert ont été détectées par la Livebox.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).

### Boutons
L'onglet `Device List` propose les boutons suivants :
- **`Refresh`** : permet de forcer le rafraichissement de la liste des appareils, non seulement dans cet onglet mais aussi dans les onglets `Device Infos` et `Events`.
- **`Device Infos`** : permet de basculer dans l'onglet `Device Infos` pour l'appareil sélectionné et de voir directement ses informations.
- **`Device Events`** : permet de basculer dans l'onglet `Events` pour l'appareil sélectionné et de voir directement les événements reçus le concernant.
- **`Raw Device List`** : permet d'afficher la réponse brute JSON de la Livebox concernant la liste des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`Raw Topology`** : permet d'afficher la réponse brute JSON de la Livebox concernant la topologie de connexion des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.


## Livebox Stats/Infos - Statistiques de trafic et infos avancées de la Livebox

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_LiveboxInfos.png)

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations sont accessibles par les boutons, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier.

### Statistiques

Liste permettant de surveiller l'état du trafic :
- **Name** : nom de l'interface réseau. `Fiber` concerne tout le trafic WAN, c'est à dire externe entre la Livebox et internet. `LAN` tout le trafic interne transitant à travers la Livebox. Ensuite on dispose des statistiques par interface précise. Les interfaces `Guest` concernent le trafic du réseau Wifi invité, s'il est activé.
- **Down** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue.
- **Up** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue.
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
- **`ONT Infos`** : affiche les informations importantes concernant la connexion et le module Fibre (ONT), telles que la bande passante, la qualité du signal, le numéro de série et les versions logicielles, etc. Les champs `Signal RxPower`, `Signal TxPower`, `Temperature`, `Voltage` et `BIAS` affichent des valeurs vertes si elles correspondent aux normes de qualités acceptables pour la connexion, en rouge si elles représentent un problème.
![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_LiveboxInfos_ONT.png)
- **`VoIP Infos`** : affiche les informations générales concernant la téléphonie, telles que le protocole, le numéro de téléphone, la version logicielle de l'interface DECT, etc.
- **`IPTV Infos`** : affiche les informations générales relative aux services de télévision.
- **`USB Infos`** : affiche les informations concernant le ou les ports USBs. Si une clef USB est insérée, ou a été insérée depuis le dernier démarrage de la Livebox, ses informations sont affichées.
- **`Export...`** : permet d'exporter l'ensemble des informations affichées par chacun des boutons dans un fichier texte. Utile pour communiquer ces informations ou faire un suivi pour détecter les changements.


## Device Infos - Informations détaillées pour chaque appareil connu

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.

Lorsqu'un appareil est sélectionné dans cette liste ses informations détaillées s'affichent dans la liste de droite. Attributs notables :
- **Active** : indique si l'appareil est actif (True) ou non (False).
- **Authenticated** : indique si la connexion Wifi de l'appareil a bien été authentifiée.
- **Blocked** : indique si vous avez bloqué la connexion de l'appareil à la Livebox (True) ou non (False). Le blocage peut être contrôlé avec les boutons `Block` et `Unblock`. Il peut être utile de bloquer un appareil inconnu si vous avez des suspicions.
- **First connection** : date et heure de la première connexion. Attention cette valeur peut aussi correspondre à la date/heure d'un précédant redémarrage de la Livebox.
- **Last connection** : date et heure de la dernière connexion.
- **Last changed** : date et heure du dernier changement détecté pour cet appareil.
- **Name** : nom connu par la Livebox pour cet appareil, avec la source de ce nom entre parenthèses. Ainsi plusieurs noms peuvent s'afficher pour des sources différentes.
- **Type** : type connu par la Livebox pour cet appareil, avec la source de ce type entre parenthèses. Ainsi plusieurs types peuvent s'afficher pour des sources différentes.
- **IPvX Address** : adresse IP (v4 ou v6) de l'appareil. Entre parenthèses s'affiche si l'adresse est atteignable sur le réseau (reacheable) ou non (not reacheable). Si l'adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox une mention s'affiche (Reserved).
- **Manufacturer** : le fabriquant de cet appareil, déduit à partir de son adresse MAC. Le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabriquant. C'est un service gratuit, mais il faut créer un compte et indiquer l'API Key correspondante dans le fichier de configuration (entrée `MacAddr API Key`) pour bénéficier de cette fonctionnalité.
- **Wifi Signal Strength** et **Wifi Signal Noise Ratio** : donne des indications sur la qualité de la connexion pour les appareils Wifi.

### Boutons
L'onglet `Device Infos` propose les boutons suivants :
- **`Refresh`** : rafraichi les informations affichées pour l'appareil sélectionné.
- **`Assign Name...`** : permet d'attribuer ou d'effacer le nom local (Monitor) et/ou le nom Livebox de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos_AssignName.png)

    Décocher la boite pour effacer le nom. Les deux noms peuvent être différents.
- **`Assign Type...`** : permet d'attribuer ou d'effacer le type de l'appareil sélectionné.

    ![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_DeviceInfos_AssignType.png)

    Il est possible de sélectionner un des types standards connus par la Livebox dans le menu, chaque type étant affiché avec son icone Livebox correspondante. Lorsqu'un type standard est sélectionné, son nom connu par la Livebox est automatiquement rempli dans la zone de texte et on peut valider le dialogue. Il reste possible d'assigner manuellement un type non connu par la Livebox en le tapant directement dans la zone de texte. Note : bien que le type "Djingo Speaker" soit référencé comme standard par la Livebox 5, ce type ne semble pas (encore ?) supporté par l'interface graphique de la Livebox.
- **`Block`** : permet de bloquer la connexion de l'appareil sélectionné.
- **`Unblock`** : permet de débloquer la connexion de l'appareil sélectionné. L'état bloqué ou non s'affiche dans les informations de l'appareil, champs "Blocked".


## Events - Liste des événements reçus pour chaque appareil connu

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Events.png)

La liste des appareils connus, sur la gauche, affiche les colonnes suivantes :
- **Name** : nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...` de l'onglet `Device Infos`.
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
- **`Show global status...`** : permet d'afficher l'état global du Wifi, en incluant l'état Wifi de tous les répéteurs Wifi Orange potentiellement connectés.

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

Les actions diverses, **Misc** :
- **Phone Ring** : pour forcer la sonnerie du téléphone afin de la tester.
- **Show LED Status...** : écran expérimental supposé afficher l'état des LEDs de la Livebox, mais les APIs correspondantes ne semblent plus supportées par la Livebox 5 et les valeurs retournées ne sont pas correctes.


## Onglets répéteurs Wifi

![Interface](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Repeater.png)

Le programme créé dynamiquement un onglet par répéteur connecté. Si le répéteur a un nom local, celui-ci est utilisé dans l'onglet, sinon le nom par défaut est de type "RW #" suivit du numéro de répéteur dans l'ordre de détection.
Les répéteurs font aussi parti des appareils connus, ils sont donc visibles dans l'onglet `Device List` et leur nom peut être changé via le bouton `Assign name...` de l'onglet `Device Infos`.

Une icône dans le nom de l'onglet permet de connaitre l'état de la connexion avec le répéteur :
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Cross.png) : le répéteur est inactif ou n'a pas d'adresse IP attribuée.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Prohibition.png) : le répéteur est actif mais aucune session n'est ouverte. Si cet état subsiste vous pouvez essayer de forcer la création d'une session en cliquant sur le bouton `Resign...`.
- ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/Doc_Icon_Tick.png) : le répéteur est actif et une session a été créée pour communiquer avec lui.

Les statistiques de trafic par interface sont affichées sous forme de liste en haut à gauche.
Et toutes les informations détaillées sont accessibles via la barre de boutons en bas, chaque bouton remplissant la liste d'attributs sur la droite. Il est aussi possible d'exporter l'ensemble des informations dans un fichier. Enfin, une série d'actions est possible via les boutons sur la gauche.

### Statistiques

Liste permettant de surveiller l'état du trafic géré par le répéteur :
- **Name** : nom de l'interface réseau. `LAN` concerne tout le trafic entre le répéteur et la Livebox. Ensuite on dispose des statistiques par interface précise (les deux prises Ethernet ainsi que les deux bandes Wifi).
- **Down** : nombre d'octets reçus par l'interface. La fenêtre de temps de ce total n'est pas connue.
- **Up** : nombre d'octets envoyés par l'interface. La fenêtre de temps de ce total n'est pas connue.
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
L'état global du Wifi peut être consulté via le bouton `Show global status...` de l'onglet `Actions`.

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


## Prochaines fonctionnalités prévues

Prochaines fonctionnalités en cours de développement :
- Support de la liste des contacts téléphoniques.
- Support des appels téléphoniques.
