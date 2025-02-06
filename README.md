# GNS
le fichier python génère et remplace automatiquement les fichiers de configs de chaque routeur avant de les restart
les bgp policies sur R2 et R7 ainsi que l'ospf cost value sur R6 ne sont pas générés automatiquement avec l'intent file
les bgp policies permettent de tag les routes de l'as 65003 au niveau de R7 et au niveau de R2 de filtrer les routes de son client (as 65003) et de leur donner une local preference de 200 contre 100 pour les autres.
