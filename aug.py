from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets as wid
import sys
import matplotlib.pyplot as plt
from PyQt5 import uic
import numpy as np
from keras.preprocessing.image import load_img,img_to_array
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import apply_affine_transform,apply_brightness_shift


class Ui(wid.QMainWindow):    
    
    switch_window = QtCore.pyqtSignal()
    
    def __init__(self):    
        super(Ui, self).__init__()
        uic.loadUi('assets/Interface.ui',self)
        self.currentImage=''
        self.init_ui()
        
    def edit_values(self,name=''):
        zX=1
        zY=1
        self.heightValue.setText(f'{self.heightSlider.value()}')
        self.widthValue.setText(f'{self.widthSlider.value()}') 
        self.rotationValue.setText(f'{self.rotationDial.value()}') 
        self.shearValue.setText(f'{self.shearSlider.value()}') 
        self.zoomXValue.setText(f'{self.zoomXSlider.value()*zX/10}') 
        if self.flipCheckBoxX.isChecked():
            zX=-1
        if self.flipCheckBoxY.isChecked():
            zY=-1
        if self.currentImage!='':
            img=load_img(self.currentImage)
            img=img_to_array(img)
            img=apply_affine_transform(x=img/255,theta=self.rotationDial.value(),tx=self.heightSlider.value(),
                                           ty=self.widthSlider.value(),shear=self.shearSlider.value(),
                                           zx=self.zoomXSlider.value()*zX/10,zy=self.zoomXSlider.value()*zY/10
                                           ,fill_mode=self.fillMode.currentText()) # fill mode can be changed
            img=apply_brightness_shift(img/255,self.brightnessBox.value())
            plt.imsave('assets/temp.png',img/255)
            self.image_display('assets/temp.png')
            
    def reset(self):
        self.heightSlider.setValue(0)
        self.widthSlider.setValue(0)
        self.flipCheckBoxX.setChecked(False)
        self.flipCheckBoxY.setChecked(False)
        self.rotationDial.setValue(0)
        self.shearSlider.setValue(0)
        self.zoomXSlider.setValue(10)
        self.brightnessBox.setValue(1)
        self.fillMode.setCurrentText('constant')
        
    def init_ui(self):
        self.setWindowTitle("VI-Aug : Visualize Image Augmentaion")
        self.setWindowIcon(QtGui.QIcon("assets/logo.png"))
        self.browseButton.clicked.connect(self.browse)
        self.heightSlider.valueChanged.connect(lambda : self.edit_values('heightSlider'))  
        self.widthSlider.valueChanged.connect(lambda : self.edit_values('widthSlider'))  
        self.flipCheckBoxX.stateChanged.connect(lambda : self.edit_values('flipCheckBoxX'))
        self.flipCheckBoxY.stateChanged.connect(lambda : self.edit_values('flipCheckBoxY'))
        self.rotationDial.valueChanged.connect(lambda : self.edit_values('rotationDial'))
        self.shearSlider.valueChanged.connect(lambda : self.edit_values('shearSlider'))
        self.zoomXSlider.valueChanged.connect(lambda : self.edit_values('zoomXSlider'))
        self.brightnessBox.valueChanged.connect(lambda : self.edit_values('brightnessBox'))
        self.fillMode.activated.connect(lambda : self.edit_values('fillMode'))
        self.resetButton.clicked.connect(self.reset)
        
    def image_display(self,img_path=''):
        image_profile = QtGui.QImage(img_path)
        self.imagePreview.setPixmap(QtGui.QPixmap.fromImage(image_profile))   
    
    def apply(self,names,ext): 
        self.switch_window.emit()
        
    def browse(self):
        self.name,ftype=self.file_open()
        x=[i[i.rfind('/')+1:] for i in self.name]
        x=','.join(x)
        self.textEdit.setText(x)
        if len(self.name)!=0:
            fileExt=[i[i.rfind('.')+1:] for i in self.name]
            if len(set(fileExt))!=1:
                self.statusLabel.setText('Files with different extensions are not allowed')
                self.statusLabel.setStyleSheet('background-color:black;color:red;font-size:20px;padding:2px;')
            else:
                if fileExt[0].lower() in set({'jpeg','jpg','gif','png'}):
                    self.statusLabel.setStyleSheet('background-color:none;')
                    self.statusLabel.setText('')
                    self.image_display(self.name[0])
                    self.currentImage=self.name[0]
                    self.applyEffect.clicked.connect(lambda : self.apply(self.name,fileExt[0]))
                else:
                    self.statusLabel.setText('Invalid Files: allowed extentions : jpeg , jpg , gif , png')
                    self.statusLabel.setStyleSheet('background-color:black;color:red;font-size:20px;padding:2px;')
        else:
            self.imagePreview.clear()
    def file_open(self):
        name, _ = wid.QFileDialog.getOpenFileNames(self, 'Open File', options=wid.QFileDialog.DontUseNativeDialog)
        return name,_

class MakeData (wid.QMainWindow):
    def __init__(self,parent):           
        super(MakeData, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.heightSlider=parent.heightSlider.value()
        self.widthSlider=parent.widthSlider.value()
        self.flipCheckBoxX=parent.flipCheckBoxX.isChecked()
        self.flipCheckBoxY=parent.flipCheckBoxY.isChecked()
        self.rotationDial=parent.rotationDial.value()
        self.shearSlider=parent.shearSlider.value()
        self.zoomXSlider=parent.zoomXSlider.value()/10
        self.brightnessBox=parent.brightnessBox.value()
        self.fill_mode=parent.fillMode.currentText()
        self.images_path=parent.name
        self.folder_name=''
        self.batch_size=1
        uic.loadUi('assets/MakeData.ui',self)
        self.initUi()
    def initUi(self):
        self.setWindowTitle("Save - VI-Aug ")
        self.setWindowIcon(QtGui.QIcon("assets/logo.png"))
        self.editinfoLabel.setText(f"""Height Slider : {self.heightSlider}\nWidth Slider:{self.widthSlider}\nFlip X:{self.flipCheckBoxX}\nFlip Y:{self.flipCheckBoxY}\nRotation : {self.rotationDial}\nShear Value:{self.shearSlider}\nZoom :{self.zoomXSlider*10:.3f}\nBrightness : {self.brightnessBox:.3f}""")
        self.batch_size_val.valueChanged.connect(self.valuechange)
        self.browseButton.clicked.connect(self.folder_select)
        self.saveButton.clicked.connect(self.apply_effect)
        
    def valuechange(self):
        self.batch_size=self.batch_size_val.value()
    
    def apply_effect(self):
        if self.folder_name!='':
            for img in self.images_path:
                temp=load_img(img)
                temp=img_to_array(temp)
                temp=np.expand_dims(temp,0)
                zrange=()
                if self.zoomXSlider < 1:
                    zrange=(self.zoomXSlider,1)
                else:
                    zrange=(1,self.zoomXSlider)
                datagen=ImageDataGenerator(horizontal_flip=self.flipCheckBoxY,vertical_flip=self.flipCheckBoxX,
                        height_shift_range=self.heightSlider/100,width_shift_range=self.widthSlider/100,
                        brightness_range=(self.brightnessBox,1.2),shear_range=self.shearSlider/10,
                        zoom_range=zrange,rotation_range=self.rotationDial,fill_mode=self.fill_mode
                        )
                j=1 
                for batch in datagen.flow(temp,save_format=self.saveType.currentText()
                                          ,save_to_dir=self.folder_name+'/',save_prefix=self.prefixText.text()):
                    if j==self.batch_size:
                        break
                    j+=1   
            self.close()
        else:
            self.statusLabel.setStyleSheet('background-color:black;color:red;font-size:20px;padding:2px;')
            self.statusLabel.setText('Destination directory not defined')
        
    def folder_select(self):
        self.folder_name=wid.QFileDialog.getExistingDirectory(self,'Select Directory')
        self.folderLabel.setText(self.folder_name)
        self.statusLabel.setStyleSheet('background-color:none;')
        self.statusLabel.setText('')
class Controller:
    def __init__(self):
        pass
    def show_ui(self):
        self.window = Ui()
        self.window.switch_window.connect(self.make_data)
        self.window.show()
    def make_data(self):
        self.md=MakeData(self.window)
        self.md.show()        

if __name__=='__main__':
    app = wid.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("assets/logo.png"))
    controller = Controller()
    controller.show_ui()
    app.exec_()
