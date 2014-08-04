'''
 Cours : LOG735
 Session : Ete 2014
 Groupe : 01
 Projet : Projet: editeur de texte distribue
 Etudiants :
    Jordan Guerin
    Frederic Langlois
 Code(s) perm. :
    GUEJ06118807
    LANF07078402
 ==================================================================
 Description of file

Horloge logique de lamport
 ==================================================================
'''

class lamport_clock:

    def __init__(self):
        self.tick = 1

    def increment(self):
        stamp = self.tick
        self.tick += 1
        return stamp

    def set_stamp(self, server_tick):
        self.tick = server_tick + 1
