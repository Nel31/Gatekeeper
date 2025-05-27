from colorama import Fore, Style, init
init(autoreset=True)

print(Fore.RED + Style.BRIGHT + "Ceci est un test en rouge et gras !" + Style.RESET_ALL)
print(Fore.GREEN + "Ceci est en vert.")
print("Ceci est normal.")
