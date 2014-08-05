LOG-735 Éditeur de texte distribué
---------------------------------
Notre application est codé en Python. 
Le client utilise ausis la librairie PyQt4 (http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt)

-------------------
Serveur
-------------------
Pour le lancer il serveur, il suffit d'exécuter le script "server.py"

python server.py

*On peut spécifier le port d'écoute
pytohn server.py -p ####

### étant le port d'écoute voulu

----------------------
Client
----------------------
Le client est une application GUI et elle utilise PyQt4.

Pour lancer le client, si suffit d'exécuter le script "client_form.py"

python client_form.py


*Ensuite, on se connecte à avec le menu de la fenêtre " File -> Connect..."
Et on peut spécifier l'adresse et le port du serveur