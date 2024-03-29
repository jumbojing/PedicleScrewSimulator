# encoding=utf-8
from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorWizard import *
#from .PedicleScrewSimulatorStep import *
#from .Helper import *

import PythonQt
import os
import string
import numpy as np


class PlanningLandmarksStep(PedicleScrewSimulatorStep):

  def __init__(self, stepid):
    self.initialize(stepid)
    self.setName('3. Place the Landmarks')
    self.setDescription("Place **the Vertebral Anterior Point (VAP)** and **the Pedkcle Isthmus Point(PIP)** for each level")

    self.__parent = super(PlanningLandmarksStep, self)
    qt.QTimer.singleShot(0, self.killButton)
    self.levels = (
      "C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11",
      "T12",
      "L1", "L2", "L3", "L4", "L5", "S1") #, "place")
    self.startCount = 0
    self.addCount = 0
    self.adjustCount = 0
    self.adjustCount2 = 0
    self.fiducialNodeObservations = []
    self.fiduciallist = []

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='Final')
    if len(bl):
      bl[0].hide()

  def begin(self):
    # TODO: we could prepare placement mode here
    pass

  def stop(self):
    self.startMeasurements.placeModeEnabled = False

  def onTableCellClicked(self):
    if self.table2.currentColumn() == 0:
      logging.debug(self.table2.currentRow())
      self.currentFid = self.table2.currentRow()
    position = [0, 0, 0]
    self.fidNode.GetNthFiducialPosition(self.currentFid, position)
    logging.debug(position)
    # self.cameraFocus(position)

    self.zoomIn()
    self.sliceChange()
    self.fidNode.AddObserver('ModifiedEvent', self.fidMove)

  def fidMove(self, observer, event):
    # coords = [0,0,0]
    # observer.GetFiducialCoordinates(coords)
    self.sliceChange()

  def updateTable(self):
    # logging.debug(pNode.GetParameter('vertebrae'))
    self.fiducial = self.fiducialNode()
    self.fidNumber = self.fiducial.GetNumberOfFiducials()
    logging.debug(self.fidNumber)
    self.fidLabels = []
    self.items = []
    self.Label = qt.QTableWidgetItem()

    self.table2.setRowCount(self.fidNumber)
    logging.debug(self.fiduciallist)
    for i in range(0, self.fidNumber):
      self.Label = qt.QTableWidgetItem(self.fiducial.GetNthFiducialLabel(i))
      self.items.append(self.Label)
      self.table2.setItem(i, 0, self.Label)
      self.combofidlist = qt.QComboBox()
      self.combofidlist.addItems(self.fiduciallist)
      self.table2.setCellWidget(i, 1, self.combofidlist)
    logging.debug(self.fiduciallist)

  def deleteFiducial(self):
    if self.table2.currentColumn() == 0:
      item = self.table2.currentItem()
      self.fidNumber = self.fidNode.GetNumberOfFiducials()
      self.fiducial = self.fiducialNode()
      for i in range(0, self.fidNumber):
        if item.text() == self.fiducial.GetNthFiducialLabel(i):
          deleteIndex = i
      self.fiducial.RemoveMarkup(deleteIndex)
      deleteIndex = -1

      logging.debug(self.table2.currentRow())
      row = self.table2.currentRow()
      self.table2.removeRow(row)

  def lockFiducials(self):
    fidNode = self.fidNode
    slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode, True)

  def addFiducials(self):

    pass

  def addFiducialToTable(self, observer, event):
    logging.debug("Modified - {0}".format(event))

    self.fidNumber = self.fidNode.GetNumberOfFiducials()
    slicer.modules.markups.logic().SetAllMarkupsVisibility(self.fidNode, 1)
    logging.debug(self.fidNumber)
    self.fidLabels = []
    self.items = []
    self.Label = qt.QTableWidgetItem()

    self.table2.setRowCount(self.fidNumber)

    for i in range(0, self.fidNumber):
      self.Label = qt.QTableWidgetItem(
        self.fidNode.GetNthFiducialLabel(i))
      self.items.append(self.Label)
      self.table2.setItem(i, 0, self.Label)
      self.combofidlist = qt.QComboBox()
      self.combofidlist.addItems(self.fiduciallist)
      self.table2.setCellWidget(i, 1, self.combofidlist)
      # if i == 0 or i == 1:
      #   self.table2.cellWidget(i, 1).setCurrentIndex(0)
      #   if i == 1:
      #     self.table2.cellWidget(i, 2).setCurrentIndex(1)
      # elif i == 2 or i == 3:
      #   self.table2.cellWidget(i, 1).setCurrentIndex(1)
      #   if i == 3:
      #     self.table2.cellWidget(i, 2).setCurrentIndex(1)
      # elif i == 4 or i == 5:
      #   self.table2.cellWidget(i, 1).setCurrentIndex(2)
      #   if i == 5:
      #     self.table2.cellWidget(i, 2).setCurrentIndex(1)

  def sliceChange(self):
    logging.debug("changing")
    coords = [0, 0, 0]
    if self.fidNode is not None:
      self.fidNode.GetNthFiducialPosition(self.currentFid, coords)

      lm = slicer.app.layoutManager()
      redWidget = lm.sliceWidget('Red')
      redController = redWidget.sliceController()

      yellowWidget = lm.sliceWidget('Yellow')
      yellowController = yellowWidget.sliceController()

      greenWidget = lm.sliceWidget('Green')
      greenController = greenWidget.sliceController()

      yellowController.setSliceOffsetValue(coords[0])
      greenController.setSliceOffsetValue(coords[1])
      redController.setSliceOffsetValue(coords[2])
    else:
      return

  def zoomIn(self):
    logging.debug("zoom")
    slicer.app.applicationLogic().PropagateVolumeSelection(2)

  def makeFidAdjustments(self):
    if self.adjustCount == 0:
      fidNode = self.fiducialNode()
      slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode,False)
      self.adjustCount = 1
      self.adjustFiducials.setText("Lock Points")
      if self.measureCount == 1:
        self.startMeasure()
    elif self.adjustCount == 1:
      fidNode = self.fiducialNode()
      slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode,True)
      self.adjustCount = 0
      self.adjustFiducials.setText("Adjust Points")

  def crosshairVisible(self):
    if self.adjustCount2 == 0:
      # Disable Slice Intersections
      viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
      for viewNode in viewNodes:
        viewNode.SetSliceIntersectionVisibility(0)

      self.adjustCount2 = 1
      self.crosshair.setText("Show Crosshair")

    elif self.adjustCount2 == 1:
      # Enable Slice Intersections
      viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
      for viewNode in viewNodes:
        viewNode.SetSliceIntersectionVisibility(1)

      self.adjustCount2 = 0
      self.crosshair.setText("Hide Crosshair")
  def createUserInterface(self):
    markup = slicer.modules.markups.logic()
    markup.AddNewFiducialNode()

    self.__layout = self.__parent.createUserInterface()
    self.startMeasurements = slicer.qSlicerMarkupsPlaceWidget()
    self.startMeasurements.setButtonsVisible(False)
    self.startMeasurements.placeButton().show()
    self.startMeasurements.setMRMLScene(slicer.mrmlScene)
    self.startMeasurements.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    self.startMeasurements.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)

    # 加个调节和cross显示选择
    self.adjustFiducials = qt.QPushButton("Adjust Landmarks")
    self.adjustFiducials.connect('clicked(bool)', self.makeFidAdjustments)

    self.crosshair = qt.QPushButton("Hide Crosshair")
    self.crosshair.connect('clicked(bool)', self.crosshairVisible)

    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addWidget(self.startMeasurements)
    self.__layout.addRow(buttonLayout)
    buttonLayout2 = qt.QHBoxLayout()
    buttonLayout2.addWidget(self.adjustFiducials)
    buttonLayout2.addWidget(self.crosshair)
    self.__layout.addRow(buttonLayout2)

    self.table2 = qt.QTableWidget()
    self.table2.setRowCount(1)
    self.table2.setColumnCount(2)
    self.table2.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
    self.table2.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Preferred)
    self.table2.setMinimumWidth(400)
    self.table2.setMinimumHeight(215)
    self.table2.setMaximumHeight(215)
    horizontalHeaders = ["Fiducial", "Level\Side\Landmarks"]
    self.table2.setHorizontalHeaderLabels(horizontalHeaders)
    self.table2.itemSelectionChanged.connect(self.onTableCellClicked)
    self.__layout.addWidget(self.table2)

    self.deleteFid = qt.QPushButton("Remove Selected Fiducial")
    self.deleteFid.connect('clicked(bool)', self.deleteFiducial)
    self.__layout.addWidget(self.deleteFid)
    self.oldPosition = 0

    # 就是在这里加个位置选择选择
    aText = qt.QLabel("Camera:")
    self.aSelector = qt.QComboBox()
    # self.aSelector.setMaximumWidth(120)
    self.aSelector.addItems(["Posterior", "Anterior", "Right", "Left"])
    self.__layout.addRow(aText)
    self.__layout.addRow(self.aSelector)

    reconCollapsibleButton = ctk.ctkCollapsibleButton()
    reconCollapsibleButton.text = "Change Slice Reconstruction"
    self.__layout.addWidget(reconCollapsibleButton)
    reconCollapsibleButton.collapsed = True
    # Layout
    reconLayout = qt.QFormLayout(reconCollapsibleButton)

    # label for ROI selector
    reconLabel = qt.QLabel('Recon Slice:')
    rotationLabel = qt.QLabel('Rotation Angle:')

    # creates combobox and populates it with all vtkMRMLAnnotationROINodes
    # in the scene
    self.selector = slicer.qMRMLNodeComboBox()
    self.selector.nodeTypes = ['vtkMRMLSliceNode']
    self.selector.toolTip = "Change Slice Reconstruction"
    self.selector.setMRMLScene(slicer.mrmlScene)
    self.selector.addEnabled = 1

    # add label + combobox
    reconLayout.addRow(reconLabel, self.selector)

    self.slider = ctk.ctkSliderWidget()
    self.slider.connect('valueChanged(double)', self.sliderValueChanged)
    self.slider.minimum = -100
    self.slider.maximum = 100
    reconLayout.addRow(rotationLabel, self.slider)

    qt.QTimer.singleShot(0, self.killButton)
    # slicer.app.connect（“startupCompleted（）”，self.killButton）
    # self.updateTable()

  def sliderValueChanged(self, value):
    logging.debug(value)
    logging.debug(self.oldPosition)

    transform = vtk.vtkTransform()

    if self.selector.currentNodeID == 'vtkMRMLSliceNodeRed':
      logging.debug("red")
      redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
      transform.SetMatrix(redSlice.GetSliceToRAS())
      transform.RotateX(value - self.oldPosition)
      redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
      redSlice.UpdateMatrices()

    elif self.selector.currentNodeID == 'vtkMRMLSliceNodeYellow':
      logging.debug("yellow")
      redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
      transform.SetMatrix(redSlice.GetSliceToRAS())
      transform.RotateY(value - self.oldPosition)
      redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
      redSlice.UpdateMatrices()

    elif self.selector.currentNodeID == 'vtkMRMLSliceNodeGreen':
      logging.debug("green")
      redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
      transform.SetMatrix(redSlice.GetSliceToRAS())
      transform.RotateZ(value - self.oldPosition)
      redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
      redSlice.UpdateMatrices()
    self.oldPosition = value

  def onEntry(self, comingFrom, transitionType):

    super(PlanningLandmarksStep, self).onEntry(comingFrom, transitionType)

    qt.QTimer.singleShot(0, self.killButton)
    viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
    for viewNode in viewNodes:
      viewNode.SetSliceIntersectionVisibility(1)
    pNode = self.parameterNode()
    # baselineVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))
    # self.__baselineVolume = baselineVolume
    logging.debug(pNode)
    self.vol = slicer.util.getNode("baselineROI")
    self.vol.CreateDefaultDisplayNodes()
    slicer.util.setSliceViewerLayers(self.vol, fit=True)
    # self.outputVolume.CreateDefaultDisplayNodes()
    lm = slicer.app.layoutManager()
    if lm == None:
      return
      lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
      # logging.debug("开始选点")
      self.zoomIn()

    self.vertebra = str(pNode.GetParameter('vertebra'))
    # logging.debug("椎体")
    logging.debug(self.vertebra)
    self.inst_length = str(pNode.GetParameter('inst_length'))
    self.sides = str(pNode.GetParameter('sides'))
    # logging.debug("这里")
    logging.debug(self.sides)
    # self.approach = str(pNode.GetParameter('approach'))
    self.croppedBaselineVolumeID = str(pNode.GetParameter('croppedBaselineVolumeID'))
    # self.screwAng = []
    for i in range(self.levels.index(self.vertebra), self.levels.index(self.vertebra) + int(self.inst_length)):
      # logging.debug(self.levels[i])
      # self.levelselection.append(self.levels[i])
      # if self.vertebra == "部位":
      #   self.fiduciallist.append(self.vertebra + "_" + str(i) + "/--/入皮点")
      #   self.fiduciallist.append(self.vertebra + "_" + str(i) + "/--/靶点")
      # else:
      if self.sides == "L&R":
        self.fiduciallist.append(self.levels[i] + "/-" + "/VAP")
        self.fiduciallist.append(self.levels[i] + "/Left" + "/PIP")
        self.fiduciallist.append(self.levels[i] + "/Right" + "/PIP")

      else:
        self.fiduciallist.append(self.levels[i] + "/" + self.sides + "/Entry")
        self.fiduciallist.append(self.levels[i] + "/" + self.sides + "/target")
    # logging.debug("Fiducial list: {0}".format(self.fiduciallist))

    # logging.debug(self.screwAng)
    self.fidNode = slicer.mrmlScene.GetFirstNodeByName("T")
    if self.fidNode == None:
      self.fidNode = self.fiducialNode()
    self.startMeasurements.setCurrentNode(self.fidNode)
    if slicer.app.majorVersion > 4 or (slicer.app.majorVersion == 4 and slicer.app.minorVersion > 10):
      self.fiducialNodeObservations.append(
        self.fidNode.AddObserver(
          slicer.vtkMRMLMarkupsNode.PointModifiedEvent,
          self.addFiducialToTable))
    else:
      # backward compatibility for Slicer-4.10 and earlier
      self.fidObserve = fiducialNode.AddObserver('ModifiedEvent', self.addFiducialToTable)
    if comingFrom.id() == 'DefineROI':
      self.updateTable()

  def getLandmarksNode(self):
    return self.startMeasurements.currentNode()

  def onExit(self, goingTo, transitionType):

    self.progress = qt.QProgressDialog(slicer.util.mainWindow())
    self.progress.minimumDuration = 0
    self.progress.show()
    self.progress.setValue(0)
    self.progress.setMaximum(0)
    self.progress.setCancelButton(0)
    self.progress.setMinimumWidth(500)
    self.progress.setWindowModality(2)

    self.progress.setLabelText('Calculation...')
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.repaint()

    self.doStepProcessing()

    # close progress bar
    self.progress.setValue(2)
    self.progress.repaint()
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.close()
    self.progress = None

    if goingTo.id() == 'Measurements' or goingTo.id() == 'DefineROI':
      self.stop()
      fiducialNode = self.fidNode
    for observation in self.fiducialNodeObservations:
      fiducialNode.RemoveObserver(observation)
    self.fiducialNodeObservations = []
    self.doStepProcessing()
    if goingTo.id() != 'DefineROI' and goingTo.id() != 'Measurements':
      return

    super(PlanningLandmarksStep, self).onExit(goingTo, transitionType)

  def validate(self, desiredBranchId):

    self.__parent.validate(desiredBranchId)
    self.__parent.validationSucceeded(desiredBranchId)

    fidNumber = self.fidNode.GetNumberOfFiducials()

    # pNode = self.parameterNode()
    if fidNumber != 0:
      self.__parent.validationSucceeded(desiredBranchId)
    else:
      self.__parent.validationFailed(desiredBranchId, 'Error',
                                     'Please place at least one fid on the model before proceeding')

  def doStepProcessing(self):

    pNode = self.parameterNode()
    pNode.SetParameter('approach', self.aSelector.currentText)

    logging.debug('Done')
    self.lockFiducials()
