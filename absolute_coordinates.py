from find_absolute import *
import sys

def main(path:str, draw = False):
    return repere_absolu(path, draw)

if __name__ == '__main__' :
    path = sys.argv[1]

    if len(sys.argv) == 2 :
        print(repere_absolu(path))

    else :
        draw=sys.argv[2] 
        print(repere_absolu(path,draw))