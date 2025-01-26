# ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_AppIcon.png) LiveboxMonitor - historique des versions


## v1.5 - 26/01/2025

- Ajustement des niveaux de logs pour faciliter la lecture. Toutes les logs de l'application sont au niveau 1 et les logs de trafic au niveau 2.
- Amélioration de la sécurité avec un clef dynamique d'encryption des mots de passe, stockée dans un fichier Key.txt et encryptée avec une clef unique correspondant à l'ordinateur. Cette nouvelle version vous redemandera tous vos mots de passe (quand les cookies expireront).
- Nouveau bouton "Notifications" dans l'onglet "Événements" permettant de recevoir des notifications automatiques par email ou de générer une log dans un fichier CSV local pour des événements concernant des appareils (connexion, déconnexion, changement de point d'accès, appareil connu ou inconnu, etc).
- Possibilité de forcer la réauthentification à un répéteur Wifi si indiqué comme inactif.
- Affichage du nombre total de redémarrages dans les informations Livebox & Répéteurs.
- Affichage du voltage et du BIAS à la bonne unité pour les Livebox 6 et 7.
- Possibilité de configurer le caractère séparateur à utiliser lors de la génération de fichiers CSV.
- Nouveaux boutons dans l'onglet "Actions" pour configurer le DynDNS, la DMZ et gérer les sauvegardes/restaurations.
- Nouvelle option pour empêcher l'ordinateur de partir en veille lorsque le logiciel est lancé.
- Nouvelle option pour spécifier une marge de timeout pour les requêtes à la Livebox. Utile en cas d'accès sur un réseau lent ou à distance.
- Adaptations au nouveau firmeware, notamment pour contrôler le planificateur Wifi.
- Affichage du mode d'opération, du mode WPS et du type de lien dans les informations Wifi des répéteurs.
- Nouvelle fonction (et bouton) pour assigner tous les noms locaux de façon identique aux noms assignés à la Livebox, pour tous les appareils inconnus. Lors de son premier lancement le programme propose d'utiliser ces noms.
- Tous les messages sont maintenant traduits en français.
- Nouveau bouton "WakeOnLAN" dans l'onglet "Infos Appareil", pour déclencher l'allumage de l'appareil s'il supporte cette fonction.
- Lorsqu'on édite un contact depuis la liste d'appels, celui-ci est maintenant cherché par numéro et plus par nom.
- Nouvelle méthode d'identification des répéteurs Wifi plus robuste.
- Nouveau bouton "Spam" dans l'onglet "Téléphone" pour vérifier l'origine d'un appel sur le site numeroinconnu.fr.
- Nouvelle option pour choisir d'enregistrer les mots de passe ou pas.
- Ajustement de l'affichage des couleurs pour les puissances d'émission/réception des lignes XGS-PON.
- Diverses améliorations et corrections de bugs mineures.


## v1.4 - 24/04/2024

- Support des icônes personnalisées pour les appareils / possibilité de créer de nouveaux types d'appareils avec leurs icônes.
- Les icônes d'appareils sont maintenant stockées en cache local pour améliorer les performances.
- Les valeurs de bande passante dans "Internet Infos" ont été corrigées pour être exprimées en GB au lieu de MB.
- Les LB4 connectées en Fibre via un module SFP externe sont maintenant reconnues comme telle.
- Le bouton "ONT infos" est disponible pour les LB4 connectées en Fibre.
- ONT Max Bit Rate Suppported: valeur corrigée pour être exprimée en Gbps au lieu de mW.
- Correction du calcul de la couleur du champ SignalTxPower dans "ONT infos".
- Amélioration de la gestion du défilement automatique des valeurs des graphes de trafic, corrigeant quelques cas qui ne fonctionnaient pas correctement.
- Correction mineure dans la gestion de l'événement notifiant du changement de type d'un appareil.
- Suppression de la possibilité d'indiquer un port externe pour les règles NAT IPv6 car non supporté par la Livebox.
- Rajout de l'unité dBm dans les valeurs de force de signal Wifi.


## v1.3 - 01/11/2023

- Support des plages de port dans les règles NAT/PAT pour IPv4 et IPv6.
- Nouveau bouton "Générer documentation APIs..." dans l'onglet "Actions" permettant de générer dans des fichiers texte l'ensemble de la documentation accessible sur les APIs de la Livebox, par module. Par défaut le programme génère l'ensemble des instances trouvées par type de ressources (ou "object") ainsi que toutes les valeurs trouvées par paramètres, mais ces valeurs sont filtrées si on maintient la touche `Ctrl` en cliquant sur le bouton. Cela permet de partager librement ces fichiers sans divulguer d'informations spécifiques à sa configuration.
- Les documentations (filtrées) générées pour les Livebox 5, 6, 6 Pro et 7 sont disponibles dans le repo.
- Correction du séparateur des en-têtes dans les exports CVS des graphes.
- Redirection d'URL par ligne de commande (par @jfgiorgi).
- En cas de connexion wifi, la colonne "Accès" dans la liste des appareils affiche s'il s'agit du réseau wifi invité.
- Le dernier niveau de signal wifi connu est maintenant masqué pour les appareils non actifs, pour plus de clarté.
- Correction d'un problème mineur lors de l'assignation d'un nom à un appareil.
- Nouvelle méthode plus robuste pour désactiver/activer le planificateur wifi. Il s'agit de la même méthode que celle utilisée par l'app "MaLivebox".
- Amélioration de la gestion des erreurs de chargement des icônes.
- Support de la Livebox 7.


## v1.2 - 25/06/2023

- Nouvel onglet NAT/PAT permettant de régler finement les règles de redirection de port et de protocole, d'exporter et d'importer les règles, etc.
- Plus d'informations sur le modèle de Livebox sont disponibles via le bouton "Infos Livebox".
- Nouveau bouton "Niveaux de pare-feu..." dans l'onglet "Actions" permettant de régler le niveau de protection des pare-feux IPv4 et IPv6.
- Nouveau bouton "Réponses aux pings..." dans l'onglet "Actions" permettant de régler les réponses aux pings en IPv4 et en IPv6.
- Nouveau bouton "DNS..." dans l'onglet "Appareils" permettant d'obtenir la liste intégrale des noms DNS assignés aux appareils.
- Il est maintenant possible d'assigner, de modifier ou de supprimer le nom DNS d'un appareil via le bouton "Assigner Nom..." de l'onglet "Infos Appareil".
- Quand la Livebox retourne des erreurs plus d'informations sont disponibles dans le dialogue.
- Corrections de bugs mineurs.


## v1.1.1 - 15/05/2023

- Le chargement des icônes en accès distant fonctionne.
- Les graphes de statistiques affichent maintenant une grille en fond qui aide à mieux visualiser les volumes.
- Utilisation du séparateur d'Excel ( ; ) pour l'export CSV des statistiques de trafic et plus la virgule ( , )
- Le programme maintenant vérifie au lancement si une nouvelle version a été publiée et averti l'utilisateur. Possibilité d'inhiber les avertissements.
- Correction concernant les onglets Événements et DHCP qui empêchait l'affichage des tooltips.
- S'il y a des appareils dans la liste de l'onglet Graphe, leur nom est maintenant automatiquement mis à jour s'il est changé.
- Correction d'un bug dans le décodage des informations de topologie qui pouvait amener à afficher des noms de point d'accès erronés dans certains cas (colonne "Accès").


## v1.1 - 01/05/2023

- Correction d'un problème de crash en mode no-console si les logs étaient activées.
- Correction d'un problème d'export des infos Livebox pour les LB4.
- Support de l'HTTPS pour l'accès à distance.
- Les exceptions et erreurs fatales s'affichent maintenant dans un dialogue au lieu de la console, ce qui est plus pratique pour les visualiser.
- L'ONT n'étant pas détectable sur les LB4 le bouton permettant de voir ses informations n'apparaît plus pour ces modèles.
- Support des répéteurs Wifi 5, ancienne génération.
- Détection automatique du profil à utiliser au démarrage en fonction de la Livebox détectée.
- Certaines statistiques d'interface ne recyclent plus à 4 Go grâce à l'utilisation d'une autre API pour choper des compteurs avec une plus haute résolution.
- Nouvelle préférence pour désactiver les statistiques Wifi temps réel des appareils (qui apparaissent en bleu). Cette option est désactivée par défaut, car cela parasite  un peu les statistiques qui affichent les taux toutes les 30 secondes, on n'a pas vraiment le temps de les lire...
- Comme l'interface "Windows" de base est finalement assez moche rajout d'une option pour basculer sur le style "Fusion" qui est plus sympa. C'est ce style qui est maintenant utilisé par défaut, sur Mac comme sur Windows, mais si vous préférez l'interface native de votre OS vous avez cette option.
- Les adresses IP sont maintenant triées de façon numérique, ce qui est plus logique.
- Nouvel onglet pour visualiser graphiquement les statistiques des interfaces et des appareils sur plusieurs jours.
- La fenêtre principale dispose maintenant d'une barre de statut. Elle affiche les tâches en cours (qui apparaissaient dans le titre de la fenêtre dans les versions précédentes), et le nom du profil en cours. Un clic sur le nom du profil affiche le dialogue pour changer de profil.
- Les onglets peuvent maintenant être déplacés à la souris y compris les onglets des répéteurs pour être mis dans n'importe quel ordre. Cet ordre est sauvé dans la configuration pour être restauré au lancement du programme.


## v1.0 - 26/02/2023

- L'alerte intempestive sur le "Wrong or inexistant MacAddrTable.txt file" a été fixée.
- Toutes les colonnes sont maintenant redimensionnables à la souris à l'exception des colonnes dynamiques qui s'ajustent avec la taille de la fenêtre.
- La détermination de l'adresse IP est beaucoup plus robuste, surtout si plusieurs sont assignées à un appareil (et dans ce cas, l'adresse active s'affiche dans les informations appareils).
- Nouveau tab DHCP qui permet de gérer les baux statiques sur les domaines "Home" et "Guest", voir toutes les informations DHCP y compris les options envoyées et reçues, et gérer les paramètres DHCP. Les informations appareils affichent aussi l'option DHCP 55.
- Les informations appareils affichent maintenant les standards Wifi supportés (2.4G / 5G / 6G).
- Le noms du profil courant, pour l'identifier, s'affiche dans les titres des dialogues de connexion.
- Adaptations pour Livebox 4.
- Barres de défilement natives MacOS, évitant qu'elles mordent sur les colonnes de liste.
- Une traduction française est maintenant disponible. Cette traduction est néanmoins partielle car elle concerne l'ensemble des labels de l'interface et pas les messages d'alerte, mais c'est déjà largement suffisant. Du coup une option est disponible dans les préférences pour choisir la langue entre français et anglais. Si quelqu'un veut faire une autre langue c'est très simple grâce au fichier template LmLanguage_XX.py.
- Des tooltips sont maintenant disponibles à peu près partout dans le but de pouvoir se passer de la documentation. Tous les tooltips français sont là, seuls quelques uns dans la version anglaises. D'ailleurs si une bonne âme se sent de faire la version anglaise complète c'est très simple (fichier LmLanguage_EN.py, en recopiant les textes depuis la version française LmLanguage_FX.py). Les tooltips sont activés par défaut mais une option dans les préférences permet de les désactiver.
- Nouveau paramêtre controlant la fréquence de rafraîchissement des statistiques temps réel, avec 3 secondes par défaut.


### v0.9.7 - 22/01/2023

- Le prefix IPv6 est affiché dans les infos Internets.
- Dans les infos d'appareils, rajout du scope des adresses IPv6, pour différencier les adresses "Globales" des "Links".
- Un dialogue IPv6 a été rajouté montrant le statut IPv6 de la Livebox, son adresse et préfixe et la liste des appareils actifs ou non ayant une ou plusieurs IPv6.
- Si le fichier de configuration est incorrect, le programme ne le réinitialise plus sans demander avant.
- Une section "Debug" a été rajoutée dans l'onglet "Actions" dans lequel on peut retrouver les boutons Raw device list, Raw topology plus un bouton pour contrôler le niveau de log dans la console.
- Le programme supporte maintenant plusieurs Livebox via un système de profils. Au démarrage de l'application s'il n'y a pas de profil par défaut ou si la touche Ctrl est enfoncée, un dialogue permet de choisir lequel utiliser. Un bouton est disponible dans l'onglet "Actions" pour changer de profil. Si plusieurs profils sont configurés, le profil en cours est affiché dans la titre de la fenêtre principale.
- S'il y a un problème pour se connecter à la Livebox le programme affiche maintenant un dialogue au démarrage pour configurer l'URL. Et s'il y a un problème au niveau de l'authentication le programme demande maintenant le nom d'utilisateur en plus du mot de passe.
- Il y a maintenant un bouton dans l'onglet "Actions" pour configurer les profils et toutes les préférences. Il n'est plus utile maintenant d'ouvrir le fichier de configuration, tout peut être géré depuis l'interface graphique.


### v0.9.6 - 07/01/2023

- Un nouvel onglet "Phone" a été rajouté pour supporter les appels téléphoniques et la liste des contacts. Contrairement à l'interface web d'Orange la liste des appels affiche aussi la durée des appels, et la correspondance avec le nom du contact. Si la Livebox n'a pas enregistré de nom pour l'appel (car elle le fait bien), alors le programme essai de trouver lui-même un nom. Un double clic sur un appel permet de créer ou de retrouver le contact correspondant rapidement. La liste des contacts peut être exportée dans un fichier, ou importée depuis un ou plusieurs fichiers en un coup. Le format est le standard VCF, supporté par la plupart des gestionnaires de contacts (Gmail, Thunderbird, Outlook, etc). L'export est particulièrement utile pour la sauvegarde, la migration à une autre Livebox, etc.
- Le paramètre Phone Code a été rajouté pour connaitre le code international par défaut des numéros de téléphone (par défaut 33 pour la France).
- L'interface a été mieux réglée pour les systèmes Linux.
- Le bouton de test de sonnerie de téléphone (maintenant dans l'onglet "Phone") permet de choisir parmi les 7 types de sonneries.
- Un bouton pour quitter l'application a été rajouté dans l'onglet "Actions". Même effet que fermer la fenêtre.
- Une zone "À propos" a été rajoutée dans l'onglet "Actions", avec un lien permettant de retrouver la page de l'application en cliquant dessus.
- Les paramètres List Header Height / List Line Height ont été rajoutés pour régler la hauteur des entêtes et lignes des listes du programme.
- Les paramètres List Header Font Size / List Line Font Size ont été rajoutés pour régler la taille de la police de caractère des entêtes et lignes des listes.
- Le programme supporte maintenant le fait que les répéteurs Wifi aient des mots de passe différents de celui de la Livebox (chose possible avec une Livebox 6).
- Pour pouvoir supporter des polices de caractères plus grandes les tables de statistiques dans les onglets de la Livebox et des répéteurs Wifi ont été élargies.


### v0.9.5 - 25/12/2022

- Les appareils sont détectés de manière bien plus native. Le programme détecte maintenant l'ensemble exhaustif des appareils référencés par la Livebox, y compris parfois des appareils "fantômes" probablement déclarés par les routeurs/switches du réseau. Du coup rajout du paramètre ci-dessous pour gérer cela.
- Paramètre 'Filter Devices' dans le fichier de config, actif par défaut, qui permet de filtrer ces appareils "fantômes". Pour vraiment tout voir, mettre ce paramètre à "false".
- Le programme se comporte maintenant correctement lorsque le PC/Mac sort de veille, il restore automatiquement toutes les sessions et repart normalement. Cependant un "Refresh" est conseillé tout de suite derrière car pendant la période de veille de nombreux événements importants ont probablement été manqués.
- Meilleure couleur de fond pour les listes sur MacOS.
- Ajout du bouton "Forget..." dans l'écran "Device Infos" qui permet de demander à la Livebox (et donc au programme) d'oublier définitivement un appareil. Utile pour "nettoyer" les listes et supprimer des appareils inactifs qui n'ont aucune chance de se reconnecter. Par contre le bouton fonctionne aussi pour les appareils actifs, dans ce cas l'appareil en question n'est absolument pas banni (il y a un bouton "Block" pour cela), sa connexion reste toujours effective, il devient juste invisible jusqu'à sa prochaine tentative de connexion.
- Et une longue liste d'amèliorations mineures...


### v0.9.4 - 03/12/2022

- Adaptations pour Livebox 6.
- Détection plus robuste des répéteurs Wifi.
- Nom des interfaces Ethernet et leur numérotation maintenant alignée sur ce qu'on peut voir physiquement sur la Livebox (tout comme le fait l'interface Web de la Livebox).


### v0.9.3 - 20/11/2022

- Nouvelle colonne montrant l'icône de la Livebox correspondant au type d'appareil.
- La colonne "Active" affiche maintenant des icônes.
- Toutes les colonnes affichant des icônes sont maintenant triables.


### v0.9.2 - 06/11/2022

- Première béta.
