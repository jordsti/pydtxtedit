pydtxtedit
==========
Python Distributed Text Editor

How to make it work
=====
We are using PyQt4 for the Gui Client Side Application.

To Launch the client

Just run 'python client_form.py'

To start a server : 'python server.py'

To put the application in debug mode (server or client)

Just add '-d' or '--debug'

TO DO
===
-A Better script to run the client side application, like a main_client.py

-many other things...

Requirements
===
WORKSPACE-01 : L'espace de travail doit permettre à un utilisateur de se connecter au système à l'aide 
d'une adresse IP et d'un numéro de port.  #completed

WORKSPACE-02 : L'espace de travail doit permettre l'insertion, la modification et la suppression de 
texte. 

WORKSPACE-03 : L'espace de travail doit offrir un bouton qui permet de lancer une demande de droits 
d'écriture au système. Le bouton doit être désactivé pendant l'attente de l'obtention des droits et 
pendant que les droits sont possédés. #completed

WORKSPACE-04 : L'espace de travail doit offrir un bouton qui permet de délaisser les droits d'écriture au 
système. Ce bouton doit être désactivé pendant que les droits ne sont pas possédés. #completed

WORKSPACE-05 : L'espace de travail doit afficher clairement à l'utilisateur les messages reliés aux droits 
d'accès (demande reçue par le système, demande accordée, droits d'accès délaissés, etc.). #WIP miss some msg

WORKSPACE-06 : L'espace de travail doit mettre à jour l'affichage du texte édité par les autres 
utilisateurs du système sans intervention de l'utilisateur. 

GESTION-01 : Le système doit garantir que les droits d'écriture ne sont accordés qu'à un seul utilisateur 
du système. #completed

GESTION-02 : Le système doit gérer les demandes de droits d'écriture concurrentes à l'aide d'une file 
FIFO (« First In, First Out ») et attribuer les droits d'écriture aux utilisateurs selon l'ordre de la file.

GESTION-03 : Le système doit transmettre le texte édité de l'utilisateur qui délaisse ses droits d'écriture 
à tous les autres espaces de travail qui y sont connectés. 

GESTION-04 : Le système doit informer clairement les utilisateurs de l'utilisateur qui possède les droits 
d'écriture à travers le système lorsqu'une acquisition ou un délaissement surviennent.