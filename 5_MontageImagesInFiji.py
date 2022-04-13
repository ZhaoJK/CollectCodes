#Author: Jiakuan
#Date: 20220413
#Description: open images in a folder, align according to Row identifer "A-H" and Column identifer "1-12".
#input: folder name; file name pattern ".*_([A-Ha-h])_(\d*)_.*", e.g. mSCA_B_9_201905.tif
#output: save tiff to destination folder

#@ File (label="Input Folder", style="directory") srcFile
#@ File (label = "Output directory", style = "directory") dstFile
#@ String (label="FileName structure") fNmStr

from ij import IJ, WindowManager, ImagePlus
from ij.plugin import ImagesToStack, MontageMaker
import os, re

def fileNmToArray(fileNms, fNmStr):
	shortFileNmDic = {}
	for fNm in fileNms:
		print(fNm)
		m = re.search(fNmStr, fNm)
		if m:
			shortFileNmDic[str(m.group(1)) + str(m.group(2)).zfill(2)] = fNm
	return shortFileNmDic

def calRowCol(namedic):
	arrList = sorted(namedic.keys())
	
	rowLetter = set()
	for arrLetter in arrList:
		rowLetter.add(arrLetter[0])
	rowLen = len(rowLetter)
	
	colLen = 0
	for rowId in rowLetter:
		currentRowDig = []
		for arrLetter in arrList:
			if rowId in arrLetter:
				currentRowDig.append(arrLetter[1:3])
		colLen = max(len(currentRowDig), colLen)
	return [rowLen, colLen]

def createImgStack(fNms, fNmDic, currentDir):
	arrayofImps = []
	orderImgNm = sorted(fNmDic.keys())
	
	for fNmId in orderImgNm:
		fNm = fNmDic.get(fNmId)
		imp = IJ.openImage(os.path.join(currentDir, fNm))
		arrayofImps.append(imp)
	return arrayofImps

def saveTif(dstFile, imp, fileNm):
	saveDir = os.path.join(dstDir, fileNm)
	if not os.path.exists(saveDir):
		os.makedirs(saveDir)
	print "Saving to", saveDir
	IJ.saveAs(imp, "Tiff", os.path.join(saveDir, fileNm));

def run():
	srcDir = srcFile.getAbsolutePath()
	dstDir = dstFile.getAbsolutePath()
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort()
		
	fNmDic = fileNmToArray(filenames, fNmStr)
	rcLen =calRowCol(fNmDic)

	arrImps = createImgStack(filenames, fNmDic, root)
	imp = ImagesToStack.run(arrImps)
	imp = MontageMaker.makeMontage2(imp, rcLen[1], rcLen[0], 1, 1, imp.getNSlices(), 1, 5, False)
	IJ.run(imp, "Make Montage...", "columns=" + str(rcLen[1]) + " rows=" + str(rcLen[0]) + " scale=1 border=5")

	fileNm = "stack.tiff"
	saveTif(dstFile, imp, fileNm)
 
if __name__ == "__main__":
	run()


