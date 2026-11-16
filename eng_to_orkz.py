import os
import random
import threading
import time

commentString = "#"
prefixString = "~pre "
suffixString = "~suf "

currentWord = ""
translationMap = {}
prefixDefaultMap = {}
suffixDefaultMap = {}


def loadFile(fileName):
    with open(fileName, encoding="utf-8-sig") as file:
        fileText = file.read()

    for line in fileText.splitlines():
        if not line or line.startswith(commentString):
            continue

        if line.startswith(suffixString):
            parts = [
                part.strip(' \t\r\n"')
                for part in line[len(suffixString) :].split('","')
            ]
            suffixDefaultMap[parts[0]] = [parts[1], parts[2]]
            continue

        if line.startswith(prefixString):
            parts = [
                part.strip(' \t\r\n"')
                for part in line[len(prefixString) :].split('","')
            ]
            prefixDefaultMap[parts[0]] = [parts[1], parts[2]]
            continue

        parts = [part.strip(' \t\r\n"') for part in line.split('","')]
        if len(parts) == 2:
            keys = parts[0].split("/")
            values = parts[1].split("/")

            for key in keys:
                newValues = values.copy()
                if key in translationMap:
                    for value in translationMap[key]:
                        if value not in newValues:
                            newValues.append(value)
                translationMap[key] = newValues


def translateWord(word):
    newWord = word
    wordOneLess = word[:-1]

    if word in translationMap:
        newWord = random.choice(translationMap[word])
    elif word.endswith("s") and wordOneLess in translationMap:
        newWord = random.choice(translationMap[wordOneLess]) + "s"
    else:
        for key in suffixDefaultMap:
            nLen = len(newWord)
            kLen = len(key)
            if nLen > kLen and newWord.endswith(key):
                if random.randint(1, 100) <= int(suffixDefaultMap[key][1]):
                    newWord = newWord[: nLen - kLen] + suffixDefaultMap[key][0]

        for key in prefixDefaultMap:
            nLen = len(newWord)
            kLen = len(key)
            if nLen > kLen and newWord.startswith(key):
                if random.randint(1, 100) <= int(prefixDefaultMap[key][1]):
                    newWord = prefixDefaultMap[key][0] + newWord[kLen:]

    return newWord


def main():
    from pynput import keyboard

    global currentWord
    controller = keyboard.Controller()
    sendingText = False

    def handleSpace(word):
        nonlocal sendingText
        try:
            newWord = translateWord(word)
            time.sleep(0.05)
            for _ in range(len(word) + 1):
                controller.press(keyboard.Key.backspace)
                controller.release(keyboard.Key.backspace)
            controller.type(newWord + " ")
            time.sleep(0.05)
        finally:
            sendingText = False

    def onPress(key):
        nonlocal sendingText
        global currentWord

        if sendingText:
            return

        if key == keyboard.Key.backspace:
            currentWord = currentWord[:-1]
        elif key == keyboard.Key.space:
            word = currentWord
            currentWord = ""
            sendingText = True
            threading.Thread(target=handleSpace, args=(word,), daemon=True).start()
        elif (
            hasattr(key, "char")
            and key.char
            and key.char.lower() in "abcdefghijklmnopqrstuvwxyz"
        ):
            currentWord += key.char.lower()

    fileName = os.path.join(os.path.dirname(__file__), "eng_to_orkz.txt")
    loadFile(fileName)

    with keyboard.Listener(on_press=onPress) as listener:
        listener.join()


if __name__ == "__main__":
    main()
