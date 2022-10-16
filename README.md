# LiveboxMonitor

`LiveboxMonitor` est une application qui permet de disposer d'une interface graphique dynamique pour :
- Controler les appareils qui se connectent à la Livebox,
- Obtenir des statistiques détaillées de traffic,
- Obtenir beaucoup de détails sur la Livebox elle-même et controler la qualité de sa ligne fibre,
- Avoir des détails sur les appareils qui se connectent (actifs ou non),
- Lire le journal des événements d'un appareil donné,
- Controler l'état du Wifi,
- Controler un ou plusieurs répéteur Wifi Orange connecté.

**AVERTISSEMENT** : le programme est actuellement dans une phase béta et nécessite des retours utilisateurs pour certifier qu'il fonctionne dans des contextes différents. Il a été **conçu pour controler une Livebox 5 avec une connection Fibre / ONT**, des tests avec une Livebox 5 ADSL voire des Livebox 6 seraient bienvenus.

Le programme est dynamique car il réagit aux événements envoyés par la Livebox et les interprètes.

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

Le programme supporte ces clefs de configuration.
`Livebox URL` : adresse de la Livebox. La valeur par défaut est `http://livebox.home/`.
`Livebox User` : login pour l'ouverture de session. Par défaut `admin`.
`Livebox Password` : le mot de passe crypté pour l'ouverture de session. Ce le mot de passe est demandé automatiquement au lancement du programme si le mot de passe n'est pas renseigné ou s'il est erroné. La clef de cryptage du mot de passe est située dans le module `LmConfig.py`, variable `SECRET`.
`MacAddr Table File` : nom du fichier de stockage des noms d'appareils. Par défaut `MacAddrTable.txt`.
`MacAddr API Key` : le programme utilise l'API du site [macaddress.io](https://macaddress.io/) pour déterminer le fabriquant d'un appareil à partir de son adresse MAC. C'est un service gratuit, mais il faut créer un compte et indiquer ici l'API Key correspondante pour bénéficier de cette fonctionalité.


### Le fichier MacAddrTable.txt

Ce fichier est géré automatiquement par l'application et il ne devrait pas être nécessaire de l'éditer.
Les clefs correspondent aux adresses MAC des appareils et les valeurs au nom attribué.
Tout appareil détecté dont l'adresse MAC n'est pas répertoriée sera affiché comme 'UNKNOWN' (inconnu) en rouge. Cette fonctionalité est surtout utile pour détecter les nouveaux appareils ou des tentatives d'intrusions.

Pourquoi utiliser une base de noms locale alors que la Livebox stocke aussi des noms?
- Parce que la Livebox "oublie" tout appareil qui ne s'est pas connecté depuis plus d'un mois.
- Parce que parfois la Livebox perd des noms de façon impromptue pour certains appareils. C'est le cas par exemple pour le nom des répéteurs Wifi.
Un fichier de noms local offre la garanti de savoir si un appareil est vraiment inconnu.




