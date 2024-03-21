from src.utils.sites import Sites


class Driver:
    def search(self):
        for site in Sites.read():
            print(site)




