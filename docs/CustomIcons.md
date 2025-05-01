
# ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_AppIcon.png) LiveboxMonitor - personnaliser les icônes d'appareil

## Sections de cette documentation
1. [Répertoire de configuration](#configuration)
2. [Personnalisation des icônes d'appareil existant](#perso)
3. [Créer un nouveau type d'appareil avec son icônes](#create)


## Répertoire de configuration <a id="configuration"></a>
- Si le programme est lancé par son code source le répertoire de configuration est le même que celui contenant le fichier source de lancement `LiveboxMonitor.py`.

- Si les programmes construits avec [PyInstaller](https://pyinstaller.org) sont utilisés, le répertoire de configuration se trouve dans les répertoires standards du système :
	- Windows : `%APPDATA%\LiveboxMonitor`
	- MacOS : `~/Library/Application Support/LiveboxMonitor`

## Personnalisation des icônes d'appareil existant <a id="perso"></a>
Les nouvelles icônes doivent :
- Se trouver dans un répertoire `custom_icons` à placer dans le répertoire de configuration décrit ci-dessus.
- Être au format PNG.

Les types d'appareils existants supportés par la Livebox sont caractérisés par :
- Une clef, qui est assignée à l'appareil dans la Livebox.
- Un nom qui est affiché par l'interface en fonction de la clef. Ce nom peut être différent de la clef, par exemple en fonction de la langue d'affichage choisie dans l'interface web de la Livebox.
- Une icône à afficher, sachant que la même icône est parfois assignée à plusieurs clefs.

Il est possible de personnaliser une icône de deux façons différentes :
1. En mettant dans le répertoire `custom_icons` un fichier PNG ayant exactement le même nom qu'une icône utilisée par la Livebox. Par exemple un fichier `e_ordibureau_windows.png` remplacera les icônes utilisées pour les clefs `Desktop Windows` et `Computer`, car toutes les deux référencent cette icône.
2. En mettant dans le répertoire `custom_icons` un fichier PNG ayant le même nom que la clef dont on veut modifier l'icône. Par exemple un fichier `Desktop Windows.png` remplacera l'icône uniquement pour la clef `Desktop Windows`.

La table ci-dessous donne l'ensemble des clefs disponibles, les noms affichés dans la version anglaise de l'interface ainsi que les noms d'icône associés. On peut aussi retrouver cette table au format JSON dans le fichier `LmConfig.py` (voir la variable `DEVICE_TYPES`).

| Clef Livebox                  | Nom affiché                  | Icône                        |
| :---------------------------- |:-----------------------------| :----------------------------|
| Unknown                       | Unknown                      | e_default_device.png         |
| AC Outlet                     | AC Outlet                    | e_smart_plug.png             |
| Acces Point                   | Acces Point                  | e_pointacceswifi.png         |
| Airbox                        | Airbox                       | e_airbox_gen.png             |
| Apple AirPort                 | Apple AirPort                | e_apple_express.png          |
| Apple AirPort Time Capsule    | Apple AirPort Time Capsule   | e_apple_extreme_capsule.png  |
| Apple Time Capsule            | Apple Time Capsule           | e_apple_extreme_capsule.png  |
| Apple TV                      | Apple TV                     | e_apple_tv.png               |
| Chromecast                    | Chromecast                   | e_chromecast.png             |
| Desktop                       | Computer                     | e_ordibureau.png             |
| Desktop Linux                 | Computer (Linux)             | e_ordibureau_Linux.png       |
| Desktop iOS                   | Computer (MacOS)             | e_ordibureau_ios.png         |
| Desktop Windows               | Computer (Windows)           | e_ordibureau_windows.png     |
| Game Console                  | Console                      | e_consolejeux.png            |
| Dimmable Color Bulb           | Dimmer Light                 | e_smart_bulb.png             |
| Djingo Speaker                | Djingo Speaker               | e_djingospeaker.png          |
| Domestic Robot                | Domestic Robot               | e_Homelive.png               |
| Domino                        | Domino                       | e_domino.png                 |
| Door Sensor                   | Door Sensor                  | e_door_sensor.png            |
| ExtenderTV                    | Extender TV                  | e_liveplugsolo.png           |
| ExtenderWiFiPlus              | Extender Wi-Fi Plus          | e_pointacceswifi.png         |
| Femtocell                     | Femtocell                    | e_femtocell.png              |
| Google OnHub                  | Google OnHub                 | e_google_onhub.png           |
| HiFi                          | HiFi                         | e_enceinte_hifi.png          |
| HomeLibrary                   | Home Library                 | e_homelibrary.png            |
| HomeLive                      | Home Live                    | e_Homelive.png               |
| Homepoint                     | Home Point                   | e_homepoint.png              |
| IP Camera                     | IP Camera                    | e_camera_ip.png              |
| Laptop                        | Laptop                       | e_ordiportable.png           |
| Laptop iOS                    | Laptop (iOS)                 | e_ordiportable_ios.png       |
| Laptop Linux                  | Laptop (Linux)               | e_ordiportable_Linux.png     |
| Laptop Windows                | Laptop (Windows)             | e_ordiportable_windows.png   |
| leBloc                        | Le Bloc d'Orange             | e_leblocdorange.png          |
| HomePlug                      | Liveplug                     | e_liveplug_cpl.png           |
| LivePlugWifi                  | Liveplug solo Wi-Fi          | e_liveplugsolo.png           |
| WiFiExtender                  | Liveplug Wi-Fi Extender      | e_liveplug_extender.png      |
| Liveradio                     | LiveRadio                    | e_liveradio.png              |
| Motion Sensor                 | Motion Sensor                | e_motion_sensor.png          |
| Nas                           | NAS                          | e_nas.png                    |
| Notebook                      | Notebook                     | e_notebook.png               |
| Notebook Linux                | Notebook (Linux)             | e_notebook_Linux.png         |
| Notebook Windows              | Notebook (Windows)           | e_notebook_windows.png       |
| Old Phone                     | Old Handset Phone            | e_telephoneold.png           |
| Phone                         | Phone                        | e_telephonenew.png           |
| Power Meter                   | Power Meter                  | e_smart_plug.png             |
| Printer                       | Printer                      | e_imprimante.png             |
| Set-top Box                   | Set-top Box                  | e_decodeurTV.png             |
| Set-top Box TV 4              | Set-top Box 4                | e_decodeur_tv_4.png          |
| Set-top Box TV Play           | Set-top Box Play             | e_decodeur_tv_play.png       |
| Set-top Box TV UHD            | Set-top Box UHD              | e_decodeur_tv_uhd.png        |
| Set-top Box TV Universal      | Set-top Box Universal        | e_decodeur_tv_universel.png  |
| Simple Button                 | Simple Button                | e_simple_button.png          |
| Color Bulb                    | Smart Bulb                   | e_smart_bulb.png             |
| Smart Plug                    | Smart Plug                   | e_smart_plug.png             |
| Mobile                        | Smartphone                   | e_mobile.png                 |
| Mobile Android                | Smartphone (Android)         | e_mobile_android.png         |
| Mobile iOS                    | Smartphone (iOS)             | e_mobile_ios.png             |
| Mobile Windows                | Smartphone (Windows)         | e_mobile_windows.png         |
| Smoke Detector                | Smoke Detector               | e_sensorhome.png             |
| Disk                          | Storage Device               | e_periphstockage.png         |
| Switch4                       | Switch (4 ports)             | e_switch4.png                |
| Switch8                       | Switch (8 ports)             | e_switch8.png                |
| Tablet                        | Tablet                       | e_tablette.png               |
| Tablet Android                | Tablet (Android)             | e_tablette_android.png       |
| Tablet iOS                    | Tablet (iOS)                 | e_tablette_ios.png           |
| Tablet Windows                | Tablet (Windows)             | e_tablette_windows.png       |
| TV                            | TV                           | e_TV.png                     |
| TVKey                         | TV Stick                     | e_cletv.png                  |
| TVKey v2                      | TV Stick v2                  | e_cletv_v2.png               |
| USBKey                        | USB Key                      | e_cleusb.png                 |
| WiFi_Access_Point             | Wi-Fi Access Point           | e_pointacceswifi.png         |
| Window Sensor                 | Window Sensor                | e_door_sensor.png            |
| Computer                      | Windows Computer             | e_ordibureau_windows.png     |
| SAH AP                        | Wi-Fi Repeater               | e_pointacceswifi.png         |
| repeteurwifi6                 | Wi-Fi Repeater 6             | e_pointacceswifi.png         |


## Créer un nouveau type d'appareil avec son icône <a id="create"></a>
Il est possible de créer un nouveau type d'appareil en simplement plaçant dans le répertoire `custom_icons` un fichier PNG ayant pour nom la clef du type que l'on veut ajouter (et qui n'est donc pas référencée dans la table ci-dessus).
Par exemple un fichier `Balance.png` aura pour effet de créer une nouvelle clef `Balance` avec exactement le même nom pour l'affichage et utilisant l'icône `Balance.png`.  
Bien évidemment, le type ajouté restera inconnu de l'interface web de la Livebox.
