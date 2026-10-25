import prompt


def welcome() -> None:
    """Запускает основной цикл программы."""
    print("Первая попытка запустить проект!")
    print("\n***\n")
    
    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        
        # prompt.string сам напишет "Введите команду: " и будет ждать ввода
        command = prompt.string("Введите команду: ")
        
        if command == "exit":
            break
        elif command == "help":
            print("Это справочная информация.")
