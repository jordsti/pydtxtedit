LOG-735 �diteur de texte distribu�
---------------------------------
Notre application est cod� en Python. 
Le client utilise ausis la librairie PyQt4 (http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt)

-------------------
Serveur
-------------------
Pour le lancer il serveur, il suffit d'ex�cuter le script "server.py"

python server.py

*On peut sp�cifier le port d'�coute
pytohn server.py -p ####

### �tant le port d'�coute voulu

----------------------
Client
----------------------
Le client est une application GUI et elle utilise PyQt4.

Pour lancer le client, si suffit d'ex�cuter le script "client_form.py"

python client_form.py


*Ensuite, on se connecte � avec le menu de la fen�tre " File -> Connect..."
Et on peut sp�cifier l'adresse et le port du serveur