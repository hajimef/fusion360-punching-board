#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

defaultWidth = 3.0
defaultDepth = 3.0
defaultHeight = 0.3
defaultRadius = 0.3
defaultPitch = 0.5

handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface
    product = app.activeProduct
design = adsk.fusion.Design.cast(product)
rootComp = design.rootComponent

class PunchingBoard:
    def __init__(self):
        self._name = 'board'
        self._width = adsk.core.ValueInput.createByReal(defaultWidth)
        self._height = adsk.core.ValueInput.createByReal(defaultHeight)
        self._depth = adsk.core.ValueInput.createByReal(defaultDepth)
        self._radius = adsk.core.ValueInput.createByReal(defaultRadius)
        self._pitch = adsk.core.ValueInput.createByReal(defaultPitch)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, value):
        self._width = value
    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value):
        self._height = value
    @property
    def depth(self):
        return self._depth
    @depth.setter
    def depth(self, value):
        self._depth = value
    @property
    def radius(self):
        return self._radius
    @radius.setter
    def radius(self, value):
        self._radius = value
    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, value):
        self._pitch = value

    def build(self):
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        is_ok = True
        try:
            tl = adsk.core.Point3D.create(-self.width / 2, -self.depth / 2, 0)
            tr = adsk.core.Point3D.create(self.width / 2, -self.depth / 2, 0)
            bl = adsk.core.Point3D.create(-self.width / 2, self.depth / 2, 0)
            br = adsk.core.Point3D.create(self.width / 2, self.depth / 2, 0)
            cw = math.floor(self.width / 2 / self.pitch)
            if self.pitch * cw + self.radius > self.width / 2:
                cw -= 1
            cd = math.floor(self.depth / 2 / self.pitch)
            if self.pitch * cd + self.radius > self.depth / 2:
                cd -= 1
        except:
            is_ok = False

        if is_ok:
            pc = (cw * 2 + 1) * (cd * 2 + 1)
            if pc > 400:
                r = ui.messageBox("点の数が多く、ハングアップする可能性があります。続行しますか？", "確認", 3)
                if r == 3:
                    is_ok = False

        if is_ok:
            try:
                lines = sketch.sketchCurves.sketchLines
                lines.addByTwoPoints(tl, tr)
                lines.addByTwoPoints(tr, br)
                lines.addByTwoPoints(br, bl)
                lines.addByTwoPoints(bl, tl)
                prof = sketch.profiles.item(0)
                extrudes = rootComp.features.extrudeFeatures
                extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                distance = adsk.core.ValueInput.createByReal(self.height)
                extInput.setDistanceExtent(False, distance)
                ext = extrudes.add(extInput)
                ext.bodies[0].name = self.name
                endFaces = ext.endFaces
                endFace = endFaces.item(0)
    
    
    
    
                pointSketch = sketches.add(endFace)
                points = pointSketch.sketchPoints
                ptColl = adsk.core.ObjectCollection.create()
                for x in range(-cw, cw + 1):
                    for y in range(-cd, cd + 1):
                        c = adsk.core.Point3D.create(x * self.pitch, y * self.pitch, 0)
                        pt = points.add(c)
                        ptColl.add(pt)
    
                holes = rootComp.features.holeFeatures
                dist = adsk.core.ValueInput.createByReal(self.radius * 2)
                holeInput = holes.createSimpleInput(dist)
                holeInput.setPositionBySketchPoints(ptColl)
                holeInput.setDistanceExtent(dist)
                hole = holes.add(holeInput)
            except:
                print("Modeling error")
#                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
#        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), self.radius)

#        ui.messageBox(cw)
#        for x in range(-cw, cw + 1):
#            for y in range(-cd, cd + 1):
#                circles.addByCenterRadius(adsk.core.Point3D.create(x * self.pitch, y * self.pitch, 0), self.radius)

class PunchingBoardCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            pb = PunchingBoard()
            for input in inputs:
                if input.id == 'boardName':
                    pb.name = input.value
                elif input.id == 'boardWidth':
                    pb.width = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'boardDepth':
                    pb.depth = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'boardHeight':
                    pb.height = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'boardRadius':
                    pb.radius = unitsMgr.evaluateExpression(input.expression, "mm") / 2
                elif input.id == 'boardPitch':
                    pb.pitch = unitsMgr.evaluateExpression(input.expression, "mm")
#                    ui.messageBox(input.value.format(traceback.format_exc()))
            pb.build()
            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class PunchingBoardCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
class PunchingBoardCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = PunchingBoardCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = PunchingBoardCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = PunchingBoardCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs
            inputs.addStringValueInput('boardName', '名前', 'ボード')
            initWidth = adsk.core.ValueInput.createByReal(defaultWidth)
            inputs.addValueInput('boardWidth', '幅','cm',initWidth)
            initDepth = adsk.core.ValueInput.createByReal(defaultDepth)
            inputs.addValueInput('boardDepth', '奥行','cm',initDepth)
            initHeight = adsk.core.ValueInput.createByReal(defaultHeight)
            inputs.addValueInput('boardHeight', '厚み','mm',initHeight)

            initRadius = adsk.core.ValueInput.createByReal(defaultRadius)
            inputs.addValueInput('boardRadius', '穴の直径','mm',initRadius)

            initPitch = adsk.core.ValueInput.createByReal(defaultPitch)
            inputs.addValueInput('boardPitch', '穴の間隔','mm',initPitch)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
#        ui.messageBox('Hello script')

        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('Punching board')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Punching board',
                    'パンチングボード',
                    'パンチングボードの作成.',
                    './resources') # relative resource file path is specified

        onCommandCreated = PunchingBoardCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
