from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import random
app = Flask(__name__)

const_values_list = [0, 0, 0, 0, 0, 25000, 15000, 7500, 3000, 1250, 700, 350, 250, 175, 125, 100, 90, 80, 70, 60, 50, 35, 25, 20, 15, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1]
# Učitavanje modela
def convert_int64_to_int(data):
    if isinstance(data, pd.DataFrame):
        return data.astype(int)
    elif isinstance(data, np.int64):
        return int(data)
    elif isinstance(data, list):
        return [convert_int64_to_int(item) for item in data]
    else:
        return data

@app.route('/predictSec', methods=['GET'])
def predictSec():
    # Provera da li je window_length prosleđen kao query parameter
    file = 'D:\Djordje.stankovic\BingoTest\outputNovi.txt'
    # Generisanje 500 random kombinacija
    dfMain = load_and_prepare_data(file)


    kombinacije = []
    for _ in range(500):
        kombinacija = random.sample(range(1, 35), 6)
        kombinacije.append(kombinacija)

        informacije_o_kombinacijama = []

        # Provera svake kombinacije
        for kombinacija in kombinacije:
            procent_izvucenih, lastTimeDrawn,moneyEarn = procentOfDrawn(dfMain, kombinacija)
            informacije_o_kombinacijama.append({'kombinacija': kombinacija, 'procenat': procent_izvucenih, 'poslednji_put_izvucena': lastTimeDrawn,'zarada' : moneyEarn})

        # Sortiranje po broju izvučenja, a zatim po procentu izvučenih u opadajućem redosledu
        informacije_o_kombinacijama.sort(key=lambda x: (x['poslednji_put_izvucena'], x['procenat']), reverse=True)

        # Dobijanje prvih 15 kombinacija
        top_15_kombinacija = informacije_o_kombinacijama[:15]
        # print(top_15_kombinacija)
        top_15_kombinacija.sort(key=lambda x: (x['procenat'], -x['poslednji_put_izvucena']), reverse=True)

        prve_dve_kombinacije = [elem['kombinacija'] for elem in top_15_kombinacija[:1]]
        informacije_o_kombinacijama.sort(key=lambda x: x['zarada'], reverse=True)

# Uzimanje prve dve kombinacije
        prve_dve_kombinacije_sortirane_po_zaradi = informacije_o_kombinacijama[:1]
        combinationForReturn = [prve_dve_kombinacije,prve_dve_kombinacije_sortirane_po_zaradi]
        

    return prve_dve_kombinacije

def load_and_prepare_data(txt_file_path):
    with open(txt_file_path, 'r') as txt_file:
        txt_lines = txt_file.readlines()


    data = []


    # Parsiranje podataka i dodavanje u listu
    for line in txt_lines:
        timestamp, values = map(str.strip, line.split(' :,'))
        date, time = map(str.strip, timestamp.split(' -'))
        values_array = list(map(int, values.split(',')))


        row_data = {}
        for i in range(1, 36):
            row_data[f'Drawn{i}'] = values_array[i - 1]
        data.append(row_data)


    # Kreiranje DataFrame-a
    df = pd.DataFrame(data)




    return df.tail(20)


def procentOfDrawn(df, top_indexes):
    # Inicijalizujemo brojač, status izvlačenja i promenljivu za najveći indeks
    counter = 0
    status = []
    max_index = -1
    lastTimeDrawn = 0
    last_index = -1
    valueOfPartija = 0

    # Prolazimo kroz redove počevši od drugog reda
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        next_row = df.iloc[i + 1] if i + 1 < len(df) else None


        if next_row is not None:
            # Uzimamo brojeve sa mesta koje su dati indeksi
            numbers_from_indexes = [current_row[index] for index in top_indexes]


            # Inicijalizujemo listu za izvučene brojeve u trenutnom redu i promenljivu za maksimalni indeks
            izvuceni_brojevi = []
            max_index_in_row = -1


            # Proveravamo da li se svi brojevi nalaze u sledećem redu
            if all(number in next_row.values for number in numbers_from_indexes):
                counter += 1
                lastTimeDrawn += 1
                for number in numbers_from_indexes:
    # Pronalazimo indeks trenutnog broja u next_row.values
                    index_in_next_row = next_row.values.tolist().index(number)
                    if(max_index < index_in_next_row):
                        max_index = index_in_next_row
                
                
                valueOfPartija += const_values_list[max_index]
            else :
                lastTimeDrawn = 0
                
               
    return counter / len(dfMain), lastTimeDrawn,valueOfPartija


def nadji_poslednji_red(df, lista):
    # Iteracija kroz sve redove unazad, počevši od poslednjeg
    for i in range(len(df) - 1, -1, -1):
        red = df.iloc[i]
        # Provera da li su svi brojevi iz liste prisutni u redu
        if all(broj in red.values for broj in lista):
            # Ako jesu, vratiti broj reda (računajući unazad od poslednjeg)
            return len(df) - i


    # Ako kombinacija nije pronađena, vratiti None
    return None
def prebroj_brojeve(df):
    # Inicijalizacija praznih rečnika za brojanje
    brojanje_brojeva = {}
    brojevi = {}


    # Iteriranje kroz Drawn pozicije (od Drawn1 do Drawn35)
    for i in range(1, 36):
        # Izdvajanje kolone koja sadrži Drawn pozicije
        kolona_drawn = f'Drawn{i}'


        # Brojanje pojavljivanja svakog broja u toj koloni i ažuriranje brojanja
        brojanje = df[kolona_drawn].value_counts().to_dict()
        brojanje_brojeva[i] = brojanje
        # Sumiranje broja pojavljivanja za svaki broj
        for broj, brojac in brojanje.items():
            brojevi[broj] = brojevi.get(broj, 0) + brojac


    # Kreiranje DataFrame-a za brojeve i njihove brojeve pojavljivanja
    df_brojevi = pd.DataFrame(list(brojevi.items()), columns=['Broj', 'BrojPojavljivanja'])


    # Vraćanje samo 10 brojeva koji se najviše puta javljaju
    top_10 = df_brojevi.nlargest(20, 'BrojPojavljivanja')
    return  top_10['Broj'].tolist()


# def generisi_kombinacije(brojevi, duzina_kombinacije):
#     # Generisanje svih mogućih kombinacija određene dužine
#     sve_kombinacije = list(combinations(brojevi, duzina_kombinacije))
#     return sve_kombinacije


def generisi_kombinacije(broj_kombinacija):
    kombinacije = []
    for _ in range(broj_kombinacija):
        kombinacija = random.sample(range(1, 49), 6)  # Generisanje jedne kombinacije od 6 brojeva
        kombinacije.append(kombinacija)
    return kombinacije




def nadji_najduze_neizasle_kombinacije(df, kombinacije):
   
    rezultati = []
    for kombinacija in kombinacije:
        broj_reda = nadji_poslednji_red(df, kombinacija)
        if broj_reda is not None:
            rezultati.append((kombinacija, broj_reda))
    # Sortiranje rezultata prema broju reda, isključujući None vrednosti
           
    rezultati.sort(key=lambda x: x[1] if x[1] is not None else float('inf'), reverse=True)
    # Vraćanje dve kombinacije sa najvećim brojem reda
    return rezultati[:5]




def get_top_indexes(df):
    # Inicijalizujemo brojač
    counter = {}


    # Prolazimo kroz redove počevši od drugog reda
    for i in range(1, len(df)):
        prev_row = df.iloc[i - 1]
        current_row = df.iloc[i]


        # Uzimamo prvih 10 brojeva iz trenutnog reda
        numbers_to_check = current_row.iloc[:10]


        # Proveravamo svaki broj
        for j, number in enumerate(numbers_to_check):
            # Pogledamo na kojoj je poziciji u prethodnom redu
            if number in prev_row.values:
                position = list(prev_row.values).index(number) + 1
                # Ako se broj nalazi u prethodnom redu, dodajemo 1 na tu poziciju
                if position in counter:
                    counter[position] += 1
                else:
                    counter[position] = 1
            else:
                # Ako se broj ne nalazi u prethodnom redu, dodajemo 1 na poziciju 0
                if 0 in counter:
                    counter[0] += 1
                else:
                    counter[0] = 1


    sorted_counter = {k: v for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True)}
    non_zero_indexes = [k for k in counter.keys() if k != 0]
    sorted_indexes = sorted(non_zero_indexes, key=lambda x: counter[x], reverse=True)
    top_indexes = sorted_indexes[:6]


    return top_indexes
def check_next_row(df, top_indexes):
    # Inicijalizujemo brojač, status izvlačenja i promenljivu za najveći indeks
    counter = 0
    status = []
    max_index = -1


    # Prolazimo kroz redove počevši od drugog reda
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        next_row = df.iloc[i + 1] if i + 1 < len(df) else None


        if next_row is not None:
            # Uzimamo brojeve sa mesta koje su dati indeksi
            numbers_from_indexes = [current_row[index] for index in top_indexes]


            # Inicijalizujemo listu za izvučene brojeve u trenutnom redu i promenljivu za maksimalni indeks
            izvuceni_brojevi = []
            max_index_in_row = -1


            # Proveravamo da li se svi brojevi nalaze u sledećem redu
            if all(number in next_row.values for number in numbers_from_indexes):
                counter += 1
                # status.append("Izvucen")


                # Dodajemo izvučene brojeve u listu
                izvuceni_brojevi = [number for number in numbers_from_indexes if number in next_row.values]


                # Pronalazimo najveći indeks u redu za brojeve iz numbers_from_indexes
                for number in izvuceni_brojevi:
                    index = next_row.values.tolist().index(number)
                    if index > max_index:
                        max_index = index
                    if index > max_index_in_row:
                        max_index_in_row = index
                status.append(f"Izvučeni brojevi: {', '.join(map(str, izvuceni_brojevi))}, Max index: {max_index_in_row}")
            else:
                status.append("Nije izvucen")


            # Dodajemo izvučene brojeve i maksimalni indeks u status
           


        else:
            status.append("Poslednji red, nema sledeceg")


    # Pisanje statusa u fajl
    with open("izvuceni_status.txt", "w") as file:
        for i, line in enumerate(status, start=2):
            file.write(f"Red {i}: {line}\n")


    return counter
def get_numbers_from_indexes(df, top_indexes):
    # Uzimamo poslednji red DataFrame-a
    last_row = df.iloc[-1]


    # Izdvajamo brojeve sa mesta koja su data indeksima
    numbers_from_indexes = [last_row[i] for i in top_indexes]


    return numbers_from_indexes



if __name__ == '__main__':
    app.run(debug=True)