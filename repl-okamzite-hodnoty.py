ceny_denni_limity = {
    "Egypt":1000,
    "Maledivy":2000,
    "Tunisko":1000,
    "Turecko":1500,
    "ostatní":2000
  }
import random as rnd
msg_type_str = rnd.choice("sale price time".split(" "))



l = ['a', 'b', 'c', 'd']

k = l.pop(0)


import csv


def mySortFunc(e):
  g = e[-1:]+e[0]
  return g

def select_trip_nos_from_file(filename="./trip_nos.csv",number_of_trips = 6):
  with open(filename) as csvfile:
    #for number in range(number_of_trips):
    readCSV = csv.reader(csvfile, delimiter=',')
    writeCSV = csv.writer(csvfile, delimiter=",")
    trip = 0
    for row in readCSV:
      if len(row)>1:
        print("Zájezd: ",row[0]," poslední typ zprávy: ",row[1])
      else:
        print("Zájezd: ",row[0])

      writeCSV.writerow(row)

      trip +=1
      if trip >= number_of_trips:
        break

      

        

x = select_trip_nos_from_file()


best_msg_type = ['time6','sale6', 'price3']
a = "Egypt" in ceny_denni_limity

b = list([t[-1:]+t[:-1] for t in best_msg_type])
c = b.sort()
print(best_msg_type.sort(key = mySortFunc))


