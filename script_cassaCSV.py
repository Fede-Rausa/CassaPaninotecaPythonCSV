
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
from PyQt5.QtWidgets import QPushButton, QVBoxLayout #, QDialog, QApplication
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Ui_MainWindow(object):

    def __init__(self):
        #codice os da lasciare in commento in fase di esportazione di eseguibile, utile solo per sperimentare lo script
        # print('vecchia dir: ' + os.getcwd())
        # filepath = os.path.dirname(os.path.realpath(__file__)) ##trova da solo la directory in cui questo file è salvato
        # print('nuova dir: ' + filepath)
        # os.chdir(filepath)

        self.quanti = []
        self.etiche = [] 
        self.path_impostazioni = "impostazioniCassa.csv"
        self.path_dataset = "datiCassa.csv"
        self.basicHeaders = np.array(['cliente', 'scontoSpeciale', 'sconto', 'prezzo', 'giorno', 'ts', 'NOTE'])
        self.importaDati()
        #self.foglio1 = None
        #self.foglio2 = None


    def importaDati(self):
        self.impostazioni = pd.read_csv(self.path_impostazioni, sep=';', decimal=',')
        if (os.path.exists(self.path_dataset)):
            self.dataset = pd.read_csv(self.path_dataset, sep=';', decimal=',')
        else:
            df = pd.DataFrame(columns = np.append(self.basicHeaders, np.array(self.impostazioni['prodotti'])).tolist() )
            df.to_csv(self.path_dataset, sep=';', index=False)
            self.dataset = pd.read_csv(self.path_dataset, sep=';', decimal=',')

        #self.foglio1 = pd.read_excel(self.xlsxname, sheet_name="cassa")
        #self.foglio2 = pd.read_excel(self.xlsxname, sheet_name="tecnico")


    def aggiornaDati(self, newrow):
        df = self.dataset
        df.loc[len(df)] = newrow.tolist()

        for i in self.dataset.columns:
            if (i not in ['cliente','giorno', 'ts', 'NOTE']):
                self.dataset[i] = pd.to_numeric(self.dataset[i])
        #print(self.dataset.dtypes)
        df.to_csv(self.path_dataset, sep=';', index=False, decimal=',', encoding='utf-8')
        #writer = pd.ExcelWriter("newexcel.xlsx", engine='xlsxwriter')
        #df.to_excel(writer, sheet_name = 'cassa')

    def attivaCassa(self):
        self.canvas.hide()
        self.button.hide()
        self.toolbar.hide()
        for w in range(len(self.formWidgets)):
            self.formWidgets[w].show()
        
    def attivaPlot(self):
        self.canvas.show()
        self.button.show()
        self.toolbar.show()
        for w in range(len(self.formWidgets)):
            self.formWidgets[w].hide()

    def fattura(self):
        _translate = QtCore.QCoreApplication.translate
        Qvet = np.array([q.value() for q in self.quanti])
        Pvet = np.array(self.impostazioni['prezzi'])
        contaPanini = np.array(self.impostazioni['panino_menu'])
        contaContorni = np.array(self.impostazioni['contorno_menu'])
        sconto = min(np.sum(Qvet[contaPanini]), np.sum(Qvet[contaContorni])) + self.scontoTot0.value()
        prezzoBase = np.dot(Qvet, Pvet)
        prezzo = prezzoBase - sconto
        self.scontoTot.setText(_translate("MainWindow", str(round(sconto, 2)) + " €"))
        self.prezzoTot0.setText(_translate("MainWindow", str(round(prezzoBase, 2)) + " €"))
        self.prezzoTot.setText(_translate("MainWindow", str(round(prezzo, 2)) + " €"))

    def conferma(self):
        Qvet = np.array([q.value() for q in self.quanti]).astype(float)
        Pvet = np.array(self.impostazioni['prezzi']).astype(float)
        contaPanini = np.array(self.impostazioni['panino_menu']).astype(bool)
        contaContorni = np.array(self.impostazioni['contorno_menu']).astype(bool)
        sconto0 = self.scontoTot0.value()
        sconto = min(np.sum(Qvet[contaPanini]), np.sum(Qvet[contaContorni])) + sconto0
        prezzoBase = np.dot(Qvet, Pvet)
        prezzo = prezzoBase - sconto
        clientID = self.NOME.text()
        orario = datetime.datetime.now() 
        giorno = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom'][orario.weekday()]
        note = self.NOTE.toPlainText()
        riga = np.append(np.array([clientID, sconto0, sconto, prezzo, giorno, str(orario), note]), Qvet)
        self.pulisci()
        if (prezzoBase > 0):
            print('registrato: '+str(riga))
            self.aggiornaDati(riga)
        else:
            print('ordine nullo')

    def pulisci(self):
        for j in range(len(self.quanti)):
            self.quanti[j].setValue(0)
        self.NOTE.setPlainText('')
        self.NOME.setText('cli:'+str(len(self.dataset)))
        self.scontoTot0.setValue(0)
        self.fattura()


    def setupPlot(self):        
        layout = QVBoxLayout()
        self.figure, self.axs = plt.subplots(1, 2)
        # Create a canvas to display the figure
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.centralwidget)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        # Create a button to refresh the plot
        self.button = QPushButton("Refresh Plot")
        self.button.clicked.connect(self.plotta)
        # Add the button to the layout
        layout.addWidget(self.button)
        # Set the layout for the main window
        self.centralwidget.setLayout(layout)
        #initialize the plots
        self.plotta()
        # enable cassa (hidden by the plots)
        self.attivaCassa()

    def plotta(self):
        # Clear the figure to avoid overlapping plots
        # self.figure.clear()

        # data for plotting
        colonne = list(self.impostazioni['prodotti']) + ['sconto', 'prezzo']
        for c in colonne:
            self.dataset[c] = pd.to_numeric(self.dataset[c])

        # Pie
        self.axs[0].clear()
        if (len(self.dataset) > 0):
            df1 = self.dataset[self.impostazioni['prodotti']]
            totali = [df1[prod].sum() for prod in self.impostazioni['prodotti']]
            def absolute_value(val):
                a  = str(round(val, 2)) + '%  : ' + str(round(val/100*np.array(totali).sum()))
                return a

            self.axs[0].pie(totali, labels = self.impostazioni['prodotti'], autopct=absolute_value, startangle=45)
            self.axs[0].set_title('ventite totali')

        # Pivot
        self.axs[1].clear()
        if (len(self.dataset) > 0):
            print(self.dataset)
            pivoTab = self.dataset.pivot_table(index = 'giorno', 
                                               values = colonne,
                                               aggfunc='sum',
                                               sort=False).T
            #totcol = pd.DataFrame({'TOT' : pivoTab.sum(axis=1)})
            #print(totcol)
            pivoTab = pivoTab.assign(TOT=pivoTab.sum(axis=1))
            #pivoTab = pivoTab.round(2)
            for c in pivoTab.columns:
                    pivoTab[c] = pivoTab[c].astype(int)
            print(pivoTab)
            self.axs[1].axis('off')
            self.axs[1].table(cellText = pivoTab.values, rowLabels = pivoTab.index, colLabels=pivoTab.columns, loc ='center')
            self.axs[1].set_title('totali per giorno')

        # Draw the canvas to update the plot
        self.canvas.draw()



    def setupForm(self):
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(200, 50, 500, 500))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")

        # self.noteLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        # self.noteLayoutWidget.setGeometry(QtCore.QRect(100, 400, 200, 200))
        # self.noteLayout = QtWidgets.QVBoxLayout(self.noteLayoutWidget)
        # self.noteLayout.setContentsMargins(0, 0, 0, 0)

        #CHIAMA FUN
        self.importaDati
        nomi = self.impostazioni["prodotti"]
        prezzi = self.impostazioni["prezzi"]
        font = QtGui.QFont("MS Shell Dlg 2", 10)
        _translate = QtCore.QCoreApplication.translate
        for n in range(len(nomi)):
            self.nome = QtWidgets.QLabel(self.formLayoutWidget)
            self.nome.setFont(font)
            self.quanto = QtWidgets.QSpinBox(self.formLayoutWidget) 
            self.quanto.setFont(font)
            self.formLayout.setWidget(n+1, QtWidgets.QFormLayout.LabelRole, self.nome)
            self.formLayout.setWidget(n+1, QtWidgets.QFormLayout.FieldRole, self.quanto)
            self.nome.setText(_translate("MainWindow", nomi[n] + " - " + str(prezzi[n])))
            self.quanto.valueChanged.connect(self.fattura)
            self.quanti.append(self.quanto)
            self.etiche.append(self.nome)

        self.labelSconto0 = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+2, QtWidgets.QFormLayout.LabelRole, self.labelSconto0)
        self.scontoTot0 = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.formLayout.setWidget(n+2, QtWidgets.QFormLayout.FieldRole, self.scontoTot0)
        self.scontoTot0.valueChanged.connect(self.fattura)
        self.labelSconto0.setText(_translate("MainWindow", "SCONTO SPECIAL:"))
        self.labelSconto0.setFont(font)
        self.scontoTot0.setFont(font)

        self.labelSconto = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+3, QtWidgets.QFormLayout.LabelRole, self.labelSconto)
        self.scontoTot = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+3, QtWidgets.QFormLayout.FieldRole, self.scontoTot)
        self.labelSconto.setText(_translate("MainWindow", "SCONTO TOT:"))
        self.scontoTot.setText(_translate("MainWindow", "0"))  
        self.labelSconto.setFont(font)
        self.scontoTot.setFont(font)

        self.labelPrezzo0 = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+4, QtWidgets.QFormLayout.LabelRole, self.labelPrezzo0)
        self.prezzoTot0 = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+4, QtWidgets.QFormLayout.FieldRole, self.prezzoTot0)
        self.labelPrezzo0.setText(_translate("MainWindow", "PREZZO BASE:"))
        self.prezzoTot0.setText(_translate("MainWindow", "0"))  
        self.labelPrezzo0.setFont(font)
        self.prezzoTot0.setFont(font)

        self.labelPrezzo = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+5, QtWidgets.QFormLayout.LabelRole, self.labelPrezzo)
        self.prezzoTot = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+5, QtWidgets.QFormLayout.FieldRole, self.prezzoTot)
        self.labelPrezzo.setText(_translate("MainWindow", "PREZZO TOT:"))
        self.prezzoTot.setText(_translate("MainWindow", "0"))
        self.labelPrezzo.setFont(font)
        self.prezzoTot.setFont(font)

        self.labelNome = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+6, QtWidgets.QFormLayout.LabelRole, self.labelNome)
        self.NOME = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.formLayout.setWidget(n+6, QtWidgets.QFormLayout.FieldRole, self.NOME)
        self.labelNome.setText(_translate("MainWindow", "ID cliente:"))
        self.labelNome.setFont(font)
        self.NOME.setFont(font)

        self.labelNote = QtWidgets.QLabel(self.formLayoutWidget)
        self.formLayout.setWidget(n+7, QtWidgets.QFormLayout.LabelRole, self.labelNote)
        self.NOTE = QtWidgets.QPlainTextEdit(self.formLayoutWidget)
        self.formLayout.setWidget(n+7, QtWidgets.QFormLayout.FieldRole, self.NOTE)
        self.labelNote.setText(_translate("MainWindow", "NOTE:"))
        self.labelNote.setFont(font)
        #self.noteLayout.addWidget(self.labelNote)
        #self.noteLayout.addWidget(self.NjOTE)

        self.confButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.formLayout.setWidget(n+8, QtWidgets.QFormLayout.LabelRole, self.confButton)
        self.confButton.clicked.connect(self.conferma)
        self.confButton.setText(_translate("MainWindow", "CONFERMA"))
        self.confButton.setFont(font)
        self.clearButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.formLayout.setWidget(n+8, QtWidgets.QFormLayout.FieldRole, self.clearButton)
        self.clearButton.clicked.connect(self.pulisci)
        self.clearButton.setText(_translate("MainWindow", "CLEAR"))
        self.clearButton.setFont(font)


        self.formWidgets = [self.labelSconto0, self.scontoTot0, self.labelSconto, self.scontoTot, 
                            self.labelPrezzo0, self.prezzoTot0, self.labelPrezzo, self.prezzoTot,
                            self.confButton, self.clearButton, self.labelNote, self.labelNome, self.labelNote,
                            self.NOME, self.NOTE]


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.setupForm()
        self.setupPlot()

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menuBar.setObjectName("menuBar")

        self.cassaOn = self.menuBar.addAction("CASSA")
        self.plotOn = self.menuBar.addAction("GRAFICI")
        self.cassaOn.triggered.connect(self.attivaCassa)
        self.plotOn.triggered.connect(self.attivaPlot)

        MainWindow.setMenuBar(self.menuBar)

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CASSA PANINOTECA"))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())