import arcpy, os
from arcpy.sa import *


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "My Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CalculateGeometry, MyBuffer, NewTool]

class MyBuffer(object):
	def __init__(self):
		self.label = "MyBuffer"
		self.description = "Buffers a distance around points then clips areas of overlap between each buffer"
		self.canRunInBackground = True
	
	def getParameterInfo(self):
        	#First Parameter
		in_features = arcpy.Parameter(
			displayName="Input Features",
			name="in_features",				
			datatype="Feature Layer",
			parameterType="Required",
			direction="Input")
		in_features.filter.list = ["Point","Polyline"]

		#Second Parameter
		distance = arcpy.Parameter(
			displayName="Distance",
			name="Distance",
	    		datatype="String",
	    		parameterType="Required",
	    		direction="Input")

		#Third Parameter
		buffer_units = arcpy.Parameter(
	    		displayName="Buffer Units",
	    		name="buffer_units",
	    		datatype="String",
	    		parameterType="Required",
	    		direction="Input")
		
		#Fourth parameter
		dissolve = arcpy.Parameter(
			displayName="Dissolve",
			name="dissolve",
			datatype="String",
			parameterType="Required",
			direction="Input")
		#Fifth Parameter
		Clip_Feature = arcpy.Parameter(
	    		displayName="Clip Feature",
	    		name="Clip Feature",
	    		datatype="Feature Layer",
	    		parameterType="Required",
	    		direction="Input")
		Clip_Feature.filter.list = ["Polygon"]

		#Output Parameter
		out_features = arcpy.Parameter(
			displayName="Output Features",
			name="out_features",
			datatype="Feature Layer",
			parameterType="Derived",
			direction="Output")
		
		out_features.parameterDependencies = [in_features.name]
		out_features.schema.clone = True

		params = [in_features, distance, buffer_units, dissolve, Clip_Feature, out_features]
		return params
				
    	def isLicensed(self):
        	return True
	
	def updateParameters(self, parameters):
		in_features = parameters[0]
		buffer_units = parameters[2]
		dissolve = parameters[3]
		
		dissolveList = ['All', 'NONE', 'LIST']

		dissolve.filter.list = dissolveList

		bufferUnitList = ['Centimeters', 'Feet', 'Inches',
				  'Kilometers', 'Meters', 'Miles',
				  'Millimeters', 'Nautical Miles',
				  'Yards', 'Decimal Degrees']

		#Get Shape type of input to display list for buffer_units parameter 		
		if in_features.value:
			desc = arcpy.Describe(in_features.valueAsText)
			if desc.shapeType == 'Point':
				buffer_units.filter.list = bufferUnitList
			elif desc.shapeType == 'Polyline':
				buffer_units.filter.list = bufferUnitList
			elif desc.shapeType == 'Polygon':
				print "File type not supported"

		return
		
	def updateMessages(self, parameters):
		
		return

   	def execute(self, parameters, Buffer_analysis):
		in_features = parameters[0].valueAsText
		buffer_units = parameters[1].valueAsText + " " + parameters[2].valueAsText
		Clip_Feature = parameters[4].valueAsText
		out_features = "C:/Users/mlemmon/Documents/ArcGIS/Default1.gdb/Buffer"
		output = "C:/Users/mlemmon/Documents/ArcGIS/Default1.gdb/Clip"
		dissolve = parameters[3].valueAsText
		
		arcpy.Buffer_analysis(in_features, out_features, buffer_units, "", "", dissolve)
		arcpy.Clip_analysis(Clip_Feature, out_features, output)
		
        	return


class CalculateGeometry(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Geometry"
        self.description = ""
        self.canRunInBackground = True
	self.category = "ESRI Tools"

    def getParameterInfo(self):
        #First Parameter
	in_features = arcpy.Parameter(
		displayName="Input Features",
	        name="in_features",
	        datatype="Feature Layer",
	        parameterType="Required",
	        direction="Input")
	in_features.filter.list = ["Point", "Polyline", "Polygon"]

	#Second Parameter
	field = arcpy.Parameter(
	    displayName="Field Name",
	    name="field_name",
	    datatype="Field",
	    parameterType="Required",
	    direction="Input")

	field.parameterDependencies = [in_features.name]
	field.filter.list = ["Short","Long","Double","Float","Text"]

	#Third Parameter
	geomProperty = arcpy.Parameter(
		displayName="Property",
		name="geomProperty",
		datatype="String",
		parameterType="Required",
		direction="Input")

	#Fourth Parameter
	units = arcpy.Parameter(
		displayName="Units",
		name="units",
		datatype="String",
		parameterType="Optional",
		direction="Input",
		enabled=False)

	#Fifth Parameter
	out_features = arcpy.Parameter(
		displayName="Output Features",
		name="out_features",
		datatype="Feature Layer",
		parameterType="Derived",
		direction="Output")
	
	out_features.parameterDependencies = [in_features.name]
	out_features.schema.clone = True

	params = [in_features, field, geomProperty, units, out_features]
	return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        #Get Inputs
	in_features = parameters[0]
	geomProperty = parameters[2]
	units = parameters[3]

	#Geometry Property Filter Lists
	pointPropertyList   =  ['X Coordinate of Point',
			        'Y Coordinate of Point']
	linePropertyList    =  ['Length', 'X Coordinate of Line Start',
			        'Y Coordinate of Line Start',
			        'X Coordinate of Line End',
			        'Y Coordinate of Line End']
	polygonPropertyList =  ['Area', 'Perimeter',
			        'X Coordinate of Centroid',
			        'Y Coordiante of Centroid']

	#Get shape type of input to determine
	#filter list for geometry property parameter
	if in_features.value:
		desc = arcpy.Describe(in_features.valueAsText)
		if desc.shapeType == 'Point':
			geomProperty.filter.list = pointPropertyList
		elif desc.shapeType == 'Polyline':
			geomProperty.filter.list = linePropertyList
		elif desc.shapeType == 'Polygon':
			geomProperty.filter.list = polygonPropertyList

	#Unit Filter Lists
	areaUnitList	     = ['Acres', 'Ares', 'Hectares',
			 	'Square Centimeters','Square Inches',
				'Square Feet', 'Square Kilometers',
				'Square Meters', 'Square Miles',
				'Square Millimeters', 'Square Yards',
				'Square Decimeters']
	lengthUnitList	     = ['Centimeters', 'Feet', 'Inches',
				'Kilometers', 'Meters', 'Miles',
				'Millimeters', 'Nautical Miles',
				'Yards', 'Decimal Degrees']
	
	#Get geometry property input to determine filter list for unit parameters
	if geomProperty.value:
		if geomProperty.valueAsText == 'Area':
			units.enabled = True
			units.filter.list = areaUnitList
		elif geomProperty.valueAsText in ['Length', 'Perimeter']:
			units.enabled = True
			units.filter.list = lengthUnitList
		else:
			units.value = ""
			units.filter.list = []
			units.enabled = False
	return

    def updateMessages(self, parameters):
        in_features = parameters[0]
	geomProperty = parameters[2]
	units = parameters[3]

	#Check is input is Multipoint or Multipatch and if so set an error
	if in_features.value:
		desc = arcpy.Describe(in_features.valueAsText)
		if desc.shapeType in ['Multipoint', 'Multipatch']:
			in_features.setErrorMessage(
				"{0} features are not supported.".format(desc.shapeType))

	#Check if certain geometry property value is set with no units and add 
	if geomProperty.valueAsText in ['Length', 'Perimeter', 'Area']:
		if not units.value:
			units.setErrorMessage(
				"Units required for {0} property".format(geomProperty.valueAsText))
	return

    def execute(self, parameters, messages):
        #Get Inputs
	in_features = parameters[0].valueAsText
	field = parameters[1].valueAsText
	geomProperty = parameters[2].valueAsText
	units = parameters[3].valueAsText

	shapeFieldName = arcpy.Describe(in_features).shapeFieldName

	#Create the expression
	exp = "!" + shapeFieldName
	if geomProperty == "Area":
		exp += ".area@" + units.replace(' ', '')
	elif geomProperty in ['Length', 'Perimeter']:
		exp += ".length@" + units.replace(' ', '')
	else:
		propertyList = geomProperty.split(' ')
		coord = propertyList[0]
		if propertyList[-1] in ['Point','Start']:
			exp += ".firstPoint." + coord
		elif propertyList[-1] == 'End':
			exp += ".lastPoint." + coord
		elif propetyList[-1] == 'Centroid':
			exp += '.centroid.' + coord
	exp += "!"

	messages.addMessage(
		"\nExpression used for field calculation: {0}\n".format(exp))

	#Calculate Field
	arcpy.CalculateField_management(in_features, field,
					exp, "PYTHON_9.3")
	return
        
class NewTool(object):
	def __init__(self):
		self.label = "aNewTool"
		self.description = "I'm not sure what this is going to be yet..."
		self.canRunInBackground = True
	
	def getParameterInfo(self):
		in_features = arcpy.Parameter(
			displayName="First Parameter",
			name="aFeature",
			datatype=["Feature Layer","Raster Dataset","Layer File"],
			parameterType="Required",
			direction="Input")
		name = arcpy.Parameter(
			displayName="Name",
			name="Name",
			datatype="String",
			parameterType="Required",
			direction="input")
		location = arcpy.Parameter(
			displayName="location",
			name="location",
			datatype="Workspace",
			parameterType="Required",
			direction="input")

		params = [in_features,name,location]
		return params

	def isLicensed(self):
		return True

	def updateParameters(self,parameters):
		in_features = parameters[0]  
		name = parameters[1]  
		location = parameters[2]        
		return
	
	def updateMessage(self, parameters):
		return True

	def execute(self, parameters, Hillshade):
		#arcpy.CheckOutExtension("Spatial")
		in_features = parameters[0].valueAsText
		name = parameters[1].valueAsText
		location = parameters[2].valueAsText
		
		finalPath = os.path.join(location , name)

		hs = arcpy.sa.Hillshade(in_features,finalPath)
		
		hs.save(finalPath)
		
		return 


		#Spatial Analyst Tools require a save
		#Spatial Analyst syntax arcpy.sa.Tool(in_raster, {output_measurement}, {z_factor})
		#3D Analyst syntax -- arcpy.Tool(in_raster=None, out_raster=None, output_measurement=None, z_factor=None)
		
		
	
	
