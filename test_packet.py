'''
 Cours : LOG735
 Session : Été 2014
 Groupe : 01
 Projet : Projet: editeur de texte distribue
 Étudiants :
    Jordan Guérin
    Frederic Langlois
 Code(s) perm. :
    GUEJ06118807
    LANF07078402
 Date :
    creation:
    modification:
 ==================================================================
 Description of file

 Pour tester les packets qu'on utilise dans le systeme
 ==================================================================
'''
import packet

def print_packet(p):

    print "Packet Id : %d" % p.packet_id
    print "Packet Type : %d" % p.packet_type
    print "Fields : "

    for k in p.fields:
        print "\t%s : %s" % (k, p.fields[k])

def chars_escape_comma():
    p = packet.packet()

    p.fields['var1'] = "hello"
    p.fields['var2'] = 'josh,allo,yes'

    txt = p.to_string()

    p2 = packet.packet(txt)
    txt2 = p2.to_string()

    print "Packet 1 :"
    print "\t%s" % txt
    print "-----------"
    #print_packet(p)
    print "Packet 2 :"
    print "\t%s" % txt2
    print "-----------"
    #print_packet(p2)

    return txt == txt2

def chars_parentheses():

    p = packet.packet()
    p.fields['var1'] = 'test var1 )'
    p.fields['var2'] = "This data (should,) be included !"

    txt = p.to_string()

    p2 = packet.packet(txt)
    txt2 = p2.to_string()

    print "Packet 1 :"
    print "\t%s" % txt
    print "Packet 2 :"
    print "\t%s" % txt2

    return txt == txt2

def packet_iterator():

    p = packet.packet()

    p2 = packet.packet()

    return p.packet_id == p2.packet_id - 1

if __name__ == '__main__':
    print "Packet Unit Test"

    #character escaping
    #comma
    if chars_escape_comma():
        print "Comma test passed"
    else:
        print "Comma test failed"

    #bracket test
    if chars_parentheses():
        print "Parentheses test passed"
    else:
        print "Parentheses test failed"

    #packet iterator
    if packet_iterator():
        print "Packet iterator test passed"
    else:
        print "Packet iterator test failed"
