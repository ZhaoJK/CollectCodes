#Date: 20220331
#Author: Jiakuan ZHAO
#Description: generate a binary for extract multichannel TIFF
#input: channel number 3
#output: a list contain rsponse bit, like 001, 010, 100, 011, 101, 110, 111

def toBin(value, bitLen):
    binChar = ""
    temp = value
    for i in range(bitLen):
        binC = bin(temp % 2)[-1]
        temp = temp // 2
        binChar = binC + binChar
    return binChar

def toBinList(chNum):
    outputList = []
    value = 2 ** chNum
    for i in range(1, value):
        outputList.append(toBin(i, chNum))
    return outputList

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chNum = 3
    print(toBinList(chNum))
