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

## Liste
La liste des appareils affiche les colonnes suivantes :
- **Name** : Nom local de l'appareil. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...` de l'onglet `Device Infos`.
- **Livebox Name*** : Nom de l'appareil tel que paramétré dans la Livebox et visible dans l'interface Web de la Livebox. Ce nom peut être attribué, changé ou supprimé via le bouton `Assign name...` de l'onglet `Device Infos`.
- **MAC** : adresse MAC, aussi appelée adresse physique de l'appareil.
- **IP** : adresse IP v4 de l'appareil sur le LAN. Cette adresse s'affiche en caractères gras si cette adresse est réservée pour cet appareil dans la configuration DHCP de la Livebox. Et elle s'affiche en rouge si l'adresse n'est pas atteignable sur le réseau (unreacheable), typiquement lorsque l'appareil n'est pas actif.
- **Link** : point de liaison de l'appareil avec le réseau. D'abord le nom de l'appareil, c'est à dire la Livebox elle-même ou le nom d'un des répéteurs Wifi Orange connectés, et ensuite l'interface sur cet appareil. `eth`  signifie une des prises Ethernet suivi du numéro de prise. `Wifi` signifie une connexion Wifi suivi par le standard de connexion, soit 2.4GHz soit 5GHz.
- **A** : indique si l'appareil est actif ou nom par un A sur fond vert. Par défaut la liste est triée pour montrer d'abord les appareils actifs.
- **Wifi** : qualité de la connexion Wifi.
- **E** : indique par une icône avec un point d'exclamation lorsqu'un événement est reçu pour cet appareil. La liste détaillée des événements, ainsi que le contenu des événements eux-mêmes, peuvent être consulter via l'onglet `Events`.
- **Down** : nombre d'octets reçus par l'appareil depuis le dernier démarrage de la Livebox.
- **Up** : nombre d'octets envoyés par l'appareil depuis le dernier démarrage de la Livebox.
- **DRate** : taux d'octets reçus par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.
- **URate** : taux d'octets envoyés par seconde par l'appareil dans les dernières 30 secondes si affiché en noir, dans la dernière seconde si affiché en bleu.

Les statistiques d'octets envoyés ou reçus par seconde sont calculés grâce aux statistiques envoyées par la Livebox sous forme d'événement toutes les 30 secondes par appareil. Cette résolution étant peu significative le programme utilise une autre interface disponible pour les appareils Wifi uniquement pour obtenir des statistiques toutes les secondes. Ces dernières sont affichées en bleues.
Les statistiques semblent parfois surprenantes, mais il s'agit d'une interprétation sans filtre de ce que renvoie la Livebox (il ne s'agit pas d'un défaut du programme).

## Boutons
L'onglet `Device List` propose les boutons suivants:
- **`Refresh`** : permet de forcer le rafraichissement de la liste des appareils, non seulement dans cet onglet mais aussi dans les onglets `Device Infos` et `Events`.
- **`Device Infos`** : permet de basculer dans l'onglet `Device Infos` pour l'appareil sélectionné et de voir directement ses informations.
- **`Device Events`** : permet de basculer dans l'onglet `Events` pour l'appareil sélectionné et de voir directement les événements reçus le concernant.
- **`Raw Device List`** : permet d'afficher la réponse brute JSON de la Livebox concernant la liste des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.
- **`Raw Topology`** : permet d'afficher la réponse brute JSON de la Livebox concernant la topologie de connexion des appareils connus. Utile pour avoir plus d'informations ou pour le débogage.



## Prochaines fonctionnalités prévues

Prochaines fonctionalités en cours de développement:
- Support de la liste des contacts téléphoniques.
- Support des appels téléphoniques.
- Paramétrage du style graphique de l'application.
