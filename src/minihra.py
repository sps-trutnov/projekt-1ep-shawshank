import random
import tkinter as tk
okno=tk.Tk()
okno.geometry("736x448")
okno.title("kámen nůžky papír")

#hráč, počítač
hrac_score=0
pocitac_score=0
hrac_volba=""
pocitac_volba=""

#cisla, volby
def volba_to_cislo(volba):
    rps={"kámen":0,"papír":1,"nůžky":2}
    return rps[volba]

def cislo_to_volba(cislo):
    rps={0:"kámen",1:"nůžky",2:"papír"}
    return rps[cislo]

#random volba počítače
def random_pocitac_choice():
    return random.choice(["kámen", "nůžky", "papír"])

#pocitadlo
def result(clovek_volba,comp_volba):
    global hrac_score
    global pocitac_score
    hrac=volba_to_cislo(clovek_volba)
    pocitac=volba_to_cislo(comp_volba)
    if (hrac==pocitac):
        print("remíza")
    elif((hrac-pocitac)%3==1):
        print("vyhráváš")
        hrac_score +=1
    else:
        print("prohráváš")
        pocitac_score +=1
    rozliseni_tabulky=tk.Text(master=okno,width=30,height=12,bg="#FFFF99")
    rozliseni_tabulky.grid(row=6,column=2)
    answer="tva volba:{uc} \n pocitac volba:{cc} \n tve score:{u}" \
           "\n pocitac score:{c}".format(uc=hrac_volba,cc=pocitac_volba
                                      ,u=hrac_score,c=pocitac_score)
    text_area.insert(tk.END,answer)

#funkčnost tlačítek
def kámen():
    global hrac_volba
    global pocitac_volba
    hrac_volba="kámen"
    pocitac_volba=random_pocitac_volba()                                                   ###tady dodelat

#výroba tlačítek
tlacitko1=tk.Button(text=" kámen ", width=8,height=2,bg="gray")
tlacitko1.grid(row=1,column=0,padx=3,pady=3)

tlacitko2=tk.Button(text=" nůžky ", width=8,height=2,bg="skyblue")
tlacitko2.grid(row=2,column=0,padx=3,pady=3)

tlacitko3=tk.Button(text=" papír ", width=8,height=2,bg="white")
tlacitko3.grid(row=3,column=0,padx=3,pady=3)

okno.mainloop()

        

        