import arcpy


class Toolbox(object):
	def __init__(self):
		self.label = "MyBuffer"
		self.description = ""
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
		
		#Fourth Parameter
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

		params = [in_features, distance, buffer_units, Clip_Feature, out_features]
		return params
    	def isLicensed(self):
        	return True

   	def updateParameters(self, parameters):
        	return
	
	def updateMessages(self, parameters):
		return

   	def execute(self, parameters):
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
