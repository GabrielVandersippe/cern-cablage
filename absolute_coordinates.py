from Coordinates.find_absolute import repere_absolu
import sys

if __name__ == '__main__' :
    path = sys.argv[1]

    if len(sys.argv) == 2 :
        print(repere_absolu(path))

    else :
        draw=sys.argv[2] 
        print(repere_absolu(path,draw))