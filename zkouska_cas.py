class Adresa():
    def __init__(self):
        self.BASE_URL = "www.seznam.cz"
        self.base_url = self.BASE_URL

    def set_url(self,myurl = None):
        if myurl == None:
            self.base_url = self.BASE_URL
        else:
            self.base_url = myurl
        return self.base_url

    def get_url(self):
        return self.base_url

if __name__ == "__main__":
    mojeurl = Adresa()
    print("1: "+str(mojeurl.get_url()))
    mojeurl.set_url("www.travelasap.cz")
    print("2: "+str(mojeurl.get_url()))
    mojeurl.set_url("www.salongaladriel.cz")
    print("3: "+str(mojeurl.get_url()))
    mojeurl.set_url()
    print("4: "+str(mojeurl.get_url()))
