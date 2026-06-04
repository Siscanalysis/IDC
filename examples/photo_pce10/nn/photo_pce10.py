''' 
Artificial Intelligence Techniques SL
artelnics@artelnics.com

Your model has been exported to this python file.
You can manage it with the 'NeuralNetwork' class.
Example:
 
	model = NeuralNetwork()
	sample = [input_1, input_2, input_3, input_4, ...]
	outputs = model.calculate_outputs(sample)
 
 
Inputs Names: 
	0) mat_1
	1) mat_2
	2) mat_3
	3) mat_4

You can predict with a batch of samples using calculate_batch_output method	 
IMPORTANT: input batch must be <class 'numpy.ndarray'> type
Example_1:
	model = NeuralNetwork()
	input_batch = np.array([[1, 2], [4, 5]])
	outputs = model.calculate_batch_output(input_batch)
Example_2:
	input_batch = pd.DataFrame( {'col1': [1, 2], 'col2': [3, 4]})
	outputs = model.calculate_batch_output(input_batch.values)
''' 
import numpy as np
import pandas as pd

class NeuralNetwork:

	def __init__(self):
		self.inputs_number = 4
		self.input_names = ['mat_1', 'mat_2', 'mat_3', 'mat_4']

	@staticmethod
	def Linear(x):
		return x

	@staticmethod
	def HyperbolicTangent(x):
		return np.tanh(x)

	def calculate_outputs(self, inputs):
		mat_1 = inputs[0]
		mat_2 = inputs[1]
		mat_3 = inputs[2]
		mat_4 = inputs[3]

		scaled_mat_1 = (mat_1-0.2495769262)/0.197744295
		scaled_mat_2 = (mat_2-0.2457499951)/0.1984143406
		scaled_mat_3 = (mat_3-0.2534807622)/0.2009759694
		scaled_mat_4 = (mat_4-0.2511923015)/0.1976905167
		dense2d_layer_1_output_0 = self.HyperbolicTangent( 0.324053 + (0.134775*scaled_mat_1) + (-0.357958*scaled_mat_2) + (-0.280396*scaled_mat_3) + (0.508766*scaled_mat_4) )
		dense2d_layer_1_output_1 = self.HyperbolicTangent( -0.000169057 + (1.56528*scaled_mat_1) + (0.151212*scaled_mat_2) + (-0.859527*scaled_mat_3) + (-0.842377*scaled_mat_4) )
		dense2d_layer_1_output_2 = self.HyperbolicTangent( 0.653614 + (0.331136*scaled_mat_1) + (0.275208*scaled_mat_2) + (-0.352424*scaled_mat_3) + (-0.248154*scaled_mat_4) )
		dense2d_layer_1_output_3 = self.HyperbolicTangent( -1.79562 + (-0.138745*scaled_mat_1) + (-0.207325*scaled_mat_2) + (-1.04557*scaled_mat_3) + (1.40918*scaled_mat_4) )
		dense2d_layer_1_output_4 = self.HyperbolicTangent( 2.28209 + (1.07756*scaled_mat_1) + (-0.345742*scaled_mat_2) + (0.101955*scaled_mat_3) + (-0.834836*scaled_mat_4) )
		dense2d_layer_1_output_5 = self.HyperbolicTangent( 1.63095 + (-0.956043*scaled_mat_1) + (1.52286*scaled_mat_2) + (0.0677736*scaled_mat_3) + (-0.641562*scaled_mat_4) )
		dense2d_layer_1_output_6 = self.HyperbolicTangent( 1.53039 + (-0.0404439*scaled_mat_1) + (-0.652522*scaled_mat_2) + (1.96467*scaled_mat_3) + (-1.30124*scaled_mat_4) )
		dense2d_layer_1_output_7 = self.HyperbolicTangent( -0.994038 + (-2.29756*scaled_mat_1) + (0.268869*scaled_mat_2) + (1.51496*scaled_mat_3) + (0.487207*scaled_mat_4) )
		dense2d_layer_1_output_8 = self.HyperbolicTangent( 0.189383 + (-0.121722*scaled_mat_1) + (-0.720045*scaled_mat_2) + (0.574491*scaled_mat_3) + (0.260576*scaled_mat_4) )
		dense2d_layer_1_output_9 = self.HyperbolicTangent( -0.563978 + (-1.24488*scaled_mat_1) + (0.197112*scaled_mat_2) + (-1.1062*scaled_mat_3) + (2.17148*scaled_mat_4) )
		dense2d_layer_1_output_10 = self.HyperbolicTangent( -0.642898 + (0.540825*scaled_mat_1) + (0.619632*scaled_mat_2) + (-1.88916*scaled_mat_3) + (0.757576*scaled_mat_4) )
		dense2d_layer_1_output_11 = self.HyperbolicTangent( 1.97962 + (-0.670562*scaled_mat_1) + (-0.489628*scaled_mat_2) + (1.19864*scaled_mat_3) + (-0.0546227*scaled_mat_4) )
		dense2d_layer_1_output_12 = self.HyperbolicTangent( -0.283772 + (-0.0644305*scaled_mat_1) + (-0.209574*scaled_mat_2) + (-0.0595431*scaled_mat_3) + (0.334996*scaled_mat_4) )
		dense2d_layer_1_output_13 = self.HyperbolicTangent( -0.574275 + (1.1367*scaled_mat_1) + (-1.42992*scaled_mat_2) + (0.499495*scaled_mat_3) + (-0.210877*scaled_mat_4) )
		dense2d_layer_1_output_14 = self.HyperbolicTangent( 1.45824 + (-0.332888*scaled_mat_1) + (-0.511716*scaled_mat_2) + (-1.16733*scaled_mat_3) + (2.03211*scaled_mat_4) )
		dense2d_layer_1_output_15 = self.HyperbolicTangent( -0.172206 + (-0.231622*scaled_mat_1) + (0.523816*scaled_mat_2) + (-1.17187*scaled_mat_3) + (0.89584*scaled_mat_4) )
		dense2d_layer_1_output_16 = self.HyperbolicTangent( -1.25695 + (0.47786*scaled_mat_1) + (-0.159213*scaled_mat_2) + (-0.869164*scaled_mat_3) + (0.565011*scaled_mat_4) )
		dense2d_layer_1_output_17 = self.HyperbolicTangent( 2.24218 + (-0.282889*scaled_mat_1) + (1.4847*scaled_mat_2) + (-0.236091*scaled_mat_3) + (-0.966371*scaled_mat_4) )
		dense2d_layer_1_output_18 = self.HyperbolicTangent( -0.540244 + (0.580642*scaled_mat_1) + (1.21242*scaled_mat_2) + (-1.15682*scaled_mat_3) + (-0.62222*scaled_mat_4) )
		dense2d_layer_1_output_19 = self.HyperbolicTangent( 1.71316 + (0.476375*scaled_mat_1) + (-0.342197*scaled_mat_2) + (0.87598*scaled_mat_3) + (-1.02224*scaled_mat_4) )
		dense2d_layer_1_output_20 = self.HyperbolicTangent( 0.0393434 + (0.357924*scaled_mat_1) + (1.18707*scaled_mat_2) + (0.092838*scaled_mat_3) + (-1.64469*scaled_mat_4) )
		dense2d_layer_1_output_21 = self.HyperbolicTangent( 0.0471687 + (-0.536741*scaled_mat_1) + (1.76407*scaled_mat_2) + (0.989567*scaled_mat_3) + (-2.23939*scaled_mat_4) )
		dense2d_layer_1_output_22 = self.HyperbolicTangent( -1.0824 + (-1.13416*scaled_mat_1) + (-0.0375989*scaled_mat_2) + (0.34462*scaled_mat_3) + (0.823667*scaled_mat_4) )
		dense2d_layer_1_output_23 = self.HyperbolicTangent( -1.99305 + (-0.241486*scaled_mat_1) + (-0.924197*scaled_mat_2) + (0.364368*scaled_mat_3) + (0.799581*scaled_mat_4) )
		dense2d_layer_1_output_24 = self.HyperbolicTangent( -0.266905 + (0.236392*scaled_mat_1) + (-1.98397*scaled_mat_2) + (2.32519*scaled_mat_3) + (-0.607844*scaled_mat_4) )
		dense2d_layer_1_output_25 = self.HyperbolicTangent( 0.204012 + (0.513262*scaled_mat_1) + (-0.423726*scaled_mat_2) + (-0.280263*scaled_mat_3) + (0.19827*scaled_mat_4) )
		dense2d_layer_1_output_26 = self.HyperbolicTangent( -0.511599 + (1.12358*scaled_mat_1) + (0.524574*scaled_mat_2) + (0.436612*scaled_mat_3) + (-2.09468*scaled_mat_4) )
		dense2d_layer_1_output_27 = self.HyperbolicTangent( -1.34132 + (-1.26714*scaled_mat_1) + (0.856674*scaled_mat_2) + (0.348812*scaled_mat_3) + (0.0519567*scaled_mat_4) )
		dense2d_layer_1_output_28 = self.HyperbolicTangent( 1.48098 + (0.786821*scaled_mat_1) + (1.45009*scaled_mat_2) + (-1.99177*scaled_mat_3) + (-0.21665*scaled_mat_4) )
		dense2d_layer_1_output_29 = self.HyperbolicTangent( -0.827989 + (-0.417498*scaled_mat_1) + (0.298183*scaled_mat_2) + (0.293512*scaled_mat_3) + (-0.179538*scaled_mat_4) )
		dense2d_layer_2_output_0 = self.HyperbolicTangent( 0.241812 + (-0.256157*dense2d_layer_1_output_0) + (0.448356*dense2d_layer_1_output_1) + (0.0778422*dense2d_layer_1_output_2) + (0.371493*dense2d_layer_1_output_3) + (0.643367*dense2d_layer_1_output_4) + (-0.0617937*dense2d_layer_1_output_5) + (0.765339*dense2d_layer_1_output_6) + (0.169727*dense2d_layer_1_output_7) + (-0.106761*dense2d_layer_1_output_8) + (0.818168*dense2d_layer_1_output_9) + (0.0576277*dense2d_layer_1_output_10) + (-0.368024*dense2d_layer_1_output_11) + (-0.108463*dense2d_layer_1_output_12) + (0.0214203*dense2d_layer_1_output_13) + (-1.07064*dense2d_layer_1_output_14) + (-0.27089*dense2d_layer_1_output_15) + (0.200248*dense2d_layer_1_output_16) + (-2.11479*dense2d_layer_1_output_17) + (0.606008*dense2d_layer_1_output_18) + (0.921666*dense2d_layer_1_output_19) + (0.05953*dense2d_layer_1_output_20) + (0.359143*dense2d_layer_1_output_21) + (-0.835914*dense2d_layer_1_output_22) + (0.952443*dense2d_layer_1_output_23) + (0.550782*dense2d_layer_1_output_24) + (-0.378848*dense2d_layer_1_output_25) + (0.288196*dense2d_layer_1_output_26) + (0.0573845*dense2d_layer_1_output_27) + (-0.415276*dense2d_layer_1_output_28) + (0.166613*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_1 = self.HyperbolicTangent( 0.182567 + (-0.174635*dense2d_layer_1_output_0) + (-4.60859e-05*dense2d_layer_1_output_1) + (0.415673*dense2d_layer_1_output_2) + (0.385412*dense2d_layer_1_output_3) + (0.686339*dense2d_layer_1_output_4) + (0.226315*dense2d_layer_1_output_5) + (-0.429627*dense2d_layer_1_output_6) + (0.653966*dense2d_layer_1_output_7) + (0.100967*dense2d_layer_1_output_8) + (0.578343*dense2d_layer_1_output_9) + (-0.742449*dense2d_layer_1_output_10) + (-1.15323*dense2d_layer_1_output_11) + (-0.219668*dense2d_layer_1_output_12) + (0.191461*dense2d_layer_1_output_13) + (0.686121*dense2d_layer_1_output_14) + (0.060203*dense2d_layer_1_output_15) + (0.068677*dense2d_layer_1_output_16) + (0.439241*dense2d_layer_1_output_17) + (0.157629*dense2d_layer_1_output_18) + (-0.221863*dense2d_layer_1_output_19) + (0.448574*dense2d_layer_1_output_20) + (-0.210604*dense2d_layer_1_output_21) + (0.400922*dense2d_layer_1_output_22) + (-0.651475*dense2d_layer_1_output_23) + (0.450942*dense2d_layer_1_output_24) + (-0.263002*dense2d_layer_1_output_25) + (1.20601*dense2d_layer_1_output_26) + (-0.144439*dense2d_layer_1_output_27) + (-0.514833*dense2d_layer_1_output_28) + (-0.0900445*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_2 = self.HyperbolicTangent( 0.64295 + (-0.141901*dense2d_layer_1_output_0) + (-0.269958*dense2d_layer_1_output_1) + (0.0740212*dense2d_layer_1_output_2) + (0.327135*dense2d_layer_1_output_3) + (0.212567*dense2d_layer_1_output_4) + (0.587581*dense2d_layer_1_output_5) + (0.0865324*dense2d_layer_1_output_6) + (0.171581*dense2d_layer_1_output_7) + (0.19368*dense2d_layer_1_output_8) + (-0.088705*dense2d_layer_1_output_9) + (-0.346656*dense2d_layer_1_output_10) + (0.284116*dense2d_layer_1_output_11) + (-0.232428*dense2d_layer_1_output_12) + (-0.226163*dense2d_layer_1_output_13) + (0.205598*dense2d_layer_1_output_14) + (0.0225079*dense2d_layer_1_output_15) + (-0.19203*dense2d_layer_1_output_16) + (0.418082*dense2d_layer_1_output_17) + (-0.106883*dense2d_layer_1_output_18) + (0.277764*dense2d_layer_1_output_19) + (-0.00548578*dense2d_layer_1_output_20) + (0.1148*dense2d_layer_1_output_21) + (-0.624951*dense2d_layer_1_output_22) + (-0.181475*dense2d_layer_1_output_23) + (-1.20403*dense2d_layer_1_output_24) + (0.125443*dense2d_layer_1_output_25) + (-0.513394*dense2d_layer_1_output_26) + (0.0089468*dense2d_layer_1_output_27) + (0.593677*dense2d_layer_1_output_28) + (-0.0611754*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_3 = self.HyperbolicTangent( 0.592625 + (0.0232103*dense2d_layer_1_output_0) + (-0.383615*dense2d_layer_1_output_1) + (0.116031*dense2d_layer_1_output_2) + (0.253124*dense2d_layer_1_output_3) + (-1.00905*dense2d_layer_1_output_4) + (-0.109007*dense2d_layer_1_output_5) + (-0.853818*dense2d_layer_1_output_6) + (-0.286395*dense2d_layer_1_output_7) + (-0.398794*dense2d_layer_1_output_8) + (-0.76324*dense2d_layer_1_output_9) + (0.855825*dense2d_layer_1_output_10) + (0.407071*dense2d_layer_1_output_11) + (0.15407*dense2d_layer_1_output_12) + (-0.195699*dense2d_layer_1_output_13) + (-1.52045*dense2d_layer_1_output_14) + (-0.586038*dense2d_layer_1_output_15) + (-0.0553276*dense2d_layer_1_output_16) + (-0.8134*dense2d_layer_1_output_17) + (-0.155831*dense2d_layer_1_output_18) + (-0.808787*dense2d_layer_1_output_19) + (-0.157247*dense2d_layer_1_output_20) + (0.361008*dense2d_layer_1_output_21) + (-0.165616*dense2d_layer_1_output_22) + (0.560423*dense2d_layer_1_output_23) + (-0.175375*dense2d_layer_1_output_24) + (0.0136451*dense2d_layer_1_output_25) + (0.336138*dense2d_layer_1_output_26) + (-0.144921*dense2d_layer_1_output_27) + (-0.592625*dense2d_layer_1_output_28) + (-0.733911*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_4 = self.HyperbolicTangent( -0.143372 + (-0.123638*dense2d_layer_1_output_0) + (0.0157385*dense2d_layer_1_output_1) + (-0.569947*dense2d_layer_1_output_2) + (0.484802*dense2d_layer_1_output_3) + (-1.36891*dense2d_layer_1_output_4) + (-0.132559*dense2d_layer_1_output_5) + (-0.750113*dense2d_layer_1_output_6) + (-0.505457*dense2d_layer_1_output_7) + (0.424445*dense2d_layer_1_output_8) + (-0.142669*dense2d_layer_1_output_9) + (-0.0630101*dense2d_layer_1_output_10) + (0.0985908*dense2d_layer_1_output_11) + (0.341026*dense2d_layer_1_output_12) + (-0.356449*dense2d_layer_1_output_13) + (-0.170514*dense2d_layer_1_output_14) + (0.142504*dense2d_layer_1_output_15) + (0.264666*dense2d_layer_1_output_16) + (-0.837638*dense2d_layer_1_output_17) + (0.153348*dense2d_layer_1_output_18) + (-1.0246*dense2d_layer_1_output_19) + (0.0627642*dense2d_layer_1_output_20) + (0.476082*dense2d_layer_1_output_21) + (0.180743*dense2d_layer_1_output_22) + (1.17527*dense2d_layer_1_output_23) + (-1.17538*dense2d_layer_1_output_24) + (-0.0577427*dense2d_layer_1_output_25) + (0.177252*dense2d_layer_1_output_26) + (0.366895*dense2d_layer_1_output_27) + (-0.55483*dense2d_layer_1_output_28) + (0.190697*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_5 = self.HyperbolicTangent( 0.255414 + (-0.239853*dense2d_layer_1_output_0) + (-0.612176*dense2d_layer_1_output_1) + (0.0316952*dense2d_layer_1_output_2) + (-0.029058*dense2d_layer_1_output_3) + (-0.30216*dense2d_layer_1_output_4) + (0.248212*dense2d_layer_1_output_5) + (1.36758*dense2d_layer_1_output_6) + (-0.806514*dense2d_layer_1_output_7) + (0.79383*dense2d_layer_1_output_8) + (-1.60667*dense2d_layer_1_output_9) + (-1.07204*dense2d_layer_1_output_10) + (0.432008*dense2d_layer_1_output_11) + (0.0398233*dense2d_layer_1_output_12) + (-1.19503*dense2d_layer_1_output_13) + (0.0356318*dense2d_layer_1_output_14) + (0.681955*dense2d_layer_1_output_15) + (-0.422553*dense2d_layer_1_output_16) + (0.42577*dense2d_layer_1_output_17) + (-0.579661*dense2d_layer_1_output_18) + (0.401288*dense2d_layer_1_output_19) + (-0.425716*dense2d_layer_1_output_20) + (1.10299*dense2d_layer_1_output_21) + (-0.317408*dense2d_layer_1_output_22) + (-0.594715*dense2d_layer_1_output_23) + (0.518342*dense2d_layer_1_output_24) + (-0.478847*dense2d_layer_1_output_25) + (1.17489*dense2d_layer_1_output_26) + (0.325775*dense2d_layer_1_output_27) + (0.491498*dense2d_layer_1_output_28) + (0.418681*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_6 = self.HyperbolicTangent( -0.525766 + (-0.104317*dense2d_layer_1_output_0) + (-0.143167*dense2d_layer_1_output_1) + (0.271414*dense2d_layer_1_output_2) + (0.778353*dense2d_layer_1_output_3) + (0.121166*dense2d_layer_1_output_4) + (-1.00185*dense2d_layer_1_output_5) + (-0.640774*dense2d_layer_1_output_6) + (-0.0669501*dense2d_layer_1_output_7) + (-0.364171*dense2d_layer_1_output_8) + (0.353116*dense2d_layer_1_output_9) + (-0.251093*dense2d_layer_1_output_10) + (-1.19048*dense2d_layer_1_output_11) + (-0.132331*dense2d_layer_1_output_12) + (-0.328535*dense2d_layer_1_output_13) + (0.750011*dense2d_layer_1_output_14) + (-0.227873*dense2d_layer_1_output_15) + (0.625071*dense2d_layer_1_output_16) + (-0.689035*dense2d_layer_1_output_17) + (0.337708*dense2d_layer_1_output_18) + (-0.348493*dense2d_layer_1_output_19) + (1.38428*dense2d_layer_1_output_20) + (-1.02553*dense2d_layer_1_output_21) + (0.0170137*dense2d_layer_1_output_22) + (-0.318273*dense2d_layer_1_output_23) + (-0.789637*dense2d_layer_1_output_24) + (-0.269257*dense2d_layer_1_output_25) + (0.381339*dense2d_layer_1_output_26) + (0.207177*dense2d_layer_1_output_27) + (0.434868*dense2d_layer_1_output_28) + (0.329596*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_7 = self.HyperbolicTangent( 0.174104 + (-0.09084*dense2d_layer_1_output_0) + (0.154324*dense2d_layer_1_output_1) + (-0.113512*dense2d_layer_1_output_2) + (-0.427412*dense2d_layer_1_output_3) + (-0.894922*dense2d_layer_1_output_4) + (0.717133*dense2d_layer_1_output_5) + (-0.263383*dense2d_layer_1_output_6) + (0.258568*dense2d_layer_1_output_7) + (-0.246122*dense2d_layer_1_output_8) + (0.403866*dense2d_layer_1_output_9) + (-0.50447*dense2d_layer_1_output_10) + (-0.322*dense2d_layer_1_output_11) + (-0.198601*dense2d_layer_1_output_12) + (-0.296484*dense2d_layer_1_output_13) + (-0.108208*dense2d_layer_1_output_14) + (0.0327484*dense2d_layer_1_output_15) + (-0.481472*dense2d_layer_1_output_16) + (0.125077*dense2d_layer_1_output_17) + (0.28735*dense2d_layer_1_output_18) + (-0.578147*dense2d_layer_1_output_19) + (-0.224284*dense2d_layer_1_output_20) + (-0.817605*dense2d_layer_1_output_21) + (-0.00540099*dense2d_layer_1_output_22) + (-0.0556187*dense2d_layer_1_output_23) + (0.730016*dense2d_layer_1_output_24) + (-0.302335*dense2d_layer_1_output_25) + (1.06225*dense2d_layer_1_output_26) + (-0.166223*dense2d_layer_1_output_27) + (-0.119185*dense2d_layer_1_output_28) + (0.181955*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_8 = self.HyperbolicTangent( -0.109784 + (-0.521494*dense2d_layer_1_output_0) + (-0.34454*dense2d_layer_1_output_1) + (-0.128026*dense2d_layer_1_output_2) + (0.378997*dense2d_layer_1_output_3) + (0.162964*dense2d_layer_1_output_4) + (-0.655469*dense2d_layer_1_output_5) + (-0.462244*dense2d_layer_1_output_6) + (0.741768*dense2d_layer_1_output_7) + (0.13289*dense2d_layer_1_output_8) + (0.303898*dense2d_layer_1_output_9) + (0.253513*dense2d_layer_1_output_10) + (-0.313564*dense2d_layer_1_output_11) + (-0.0270007*dense2d_layer_1_output_12) + (0.363171*dense2d_layer_1_output_13) + (-0.128233*dense2d_layer_1_output_14) + (0.0262997*dense2d_layer_1_output_15) + (0.61421*dense2d_layer_1_output_16) + (0.223865*dense2d_layer_1_output_17) + (0.0759539*dense2d_layer_1_output_18) + (0.529148*dense2d_layer_1_output_19) + (-0.115058*dense2d_layer_1_output_20) + (-0.149498*dense2d_layer_1_output_21) + (0.369154*dense2d_layer_1_output_22) + (-0.492202*dense2d_layer_1_output_23) + (-0.147764*dense2d_layer_1_output_24) + (-0.387833*dense2d_layer_1_output_25) + (-0.355991*dense2d_layer_1_output_26) + (0.206152*dense2d_layer_1_output_27) + (-0.0329962*dense2d_layer_1_output_28) + (0.509704*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_9 = self.HyperbolicTangent( 0.199065 + (0.108835*dense2d_layer_1_output_0) + (-0.312319*dense2d_layer_1_output_1) + (0.424022*dense2d_layer_1_output_2) + (-0.508849*dense2d_layer_1_output_3) + (0.349876*dense2d_layer_1_output_4) + (-0.207027*dense2d_layer_1_output_5) + (-0.333827*dense2d_layer_1_output_6) + (0.653943*dense2d_layer_1_output_7) + (-0.220862*dense2d_layer_1_output_8) + (0.30068*dense2d_layer_1_output_9) + (-0.173967*dense2d_layer_1_output_10) + (-0.413521*dense2d_layer_1_output_11) + (-0.196937*dense2d_layer_1_output_12) + (-0.390755*dense2d_layer_1_output_13) + (0.126941*dense2d_layer_1_output_14) + (-0.136165*dense2d_layer_1_output_15) + (-0.473927*dense2d_layer_1_output_16) + (0.0138451*dense2d_layer_1_output_17) + (0.31838*dense2d_layer_1_output_18) + (-0.0467079*dense2d_layer_1_output_19) + (0.306715*dense2d_layer_1_output_20) + (-0.451627*dense2d_layer_1_output_21) + (-0.239286*dense2d_layer_1_output_22) + (-0.289395*dense2d_layer_1_output_23) + (0.136653*dense2d_layer_1_output_24) + (0.113393*dense2d_layer_1_output_25) + (0.0198735*dense2d_layer_1_output_26) + (-0.618777*dense2d_layer_1_output_27) + (-0.95154*dense2d_layer_1_output_28) + (-0.427983*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_10 = self.HyperbolicTangent( -0.190738 + (0.366445*dense2d_layer_1_output_0) + (0.576613*dense2d_layer_1_output_1) + (0.173351*dense2d_layer_1_output_2) + (-0.24345*dense2d_layer_1_output_3) + (0.258826*dense2d_layer_1_output_4) + (0.125422*dense2d_layer_1_output_5) + (-0.466215*dense2d_layer_1_output_6) + (0.520295*dense2d_layer_1_output_7) + (-0.144406*dense2d_layer_1_output_8) + (-0.144382*dense2d_layer_1_output_9) + (-0.15537*dense2d_layer_1_output_10) + (-0.464909*dense2d_layer_1_output_11) + (0.149681*dense2d_layer_1_output_12) + (0.819388*dense2d_layer_1_output_13) + (-0.112638*dense2d_layer_1_output_14) + (-0.144506*dense2d_layer_1_output_15) + (0.775967*dense2d_layer_1_output_16) + (0.238129*dense2d_layer_1_output_17) + (-0.0754595*dense2d_layer_1_output_18) + (0.255099*dense2d_layer_1_output_19) + (-0.199057*dense2d_layer_1_output_20) + (0.820494*dense2d_layer_1_output_21) + (0.212223*dense2d_layer_1_output_22) + (-0.292069*dense2d_layer_1_output_23) + (-0.0333714*dense2d_layer_1_output_24) + (-0.0245476*dense2d_layer_1_output_25) + (-0.470933*dense2d_layer_1_output_26) + (0.290879*dense2d_layer_1_output_27) + (0.188589*dense2d_layer_1_output_28) + (0.201511*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_11 = self.HyperbolicTangent( 0.0509288 + (0.262253*dense2d_layer_1_output_0) + (0.133795*dense2d_layer_1_output_1) + (0.22737*dense2d_layer_1_output_2) + (0.897361*dense2d_layer_1_output_3) + (0.153002*dense2d_layer_1_output_4) + (0.990258*dense2d_layer_1_output_5) + (0.809762*dense2d_layer_1_output_6) + (0.324347*dense2d_layer_1_output_7) + (0.256826*dense2d_layer_1_output_8) + (0.189825*dense2d_layer_1_output_9) + (-0.857827*dense2d_layer_1_output_10) + (0.866185*dense2d_layer_1_output_11) + (-0.0589353*dense2d_layer_1_output_12) + (0.0510947*dense2d_layer_1_output_13) + (-0.0183702*dense2d_layer_1_output_14) + (-0.347121*dense2d_layer_1_output_15) + (-0.624988*dense2d_layer_1_output_16) + (0.381864*dense2d_layer_1_output_17) + (-0.744226*dense2d_layer_1_output_18) + (0.200373*dense2d_layer_1_output_19) + (0.415706*dense2d_layer_1_output_20) + (0.822678*dense2d_layer_1_output_21) + (-0.251162*dense2d_layer_1_output_22) + (-0.736717*dense2d_layer_1_output_23) + (0.663521*dense2d_layer_1_output_24) + (0.289543*dense2d_layer_1_output_25) + (0.0472187*dense2d_layer_1_output_26) + (-0.81412*dense2d_layer_1_output_27) + (-0.120824*dense2d_layer_1_output_28) + (-0.193138*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_12 = self.HyperbolicTangent( 0.0687467 + (-0.173021*dense2d_layer_1_output_0) + (0.117783*dense2d_layer_1_output_1) + (0.115582*dense2d_layer_1_output_2) + (0.0408891*dense2d_layer_1_output_3) + (-0.172934*dense2d_layer_1_output_4) + (0.0387215*dense2d_layer_1_output_5) + (-0.0190729*dense2d_layer_1_output_6) + (-0.730813*dense2d_layer_1_output_7) + (-0.044397*dense2d_layer_1_output_8) + (-0.261332*dense2d_layer_1_output_9) + (0.0948356*dense2d_layer_1_output_10) + (-0.145572*dense2d_layer_1_output_11) + (-0.175493*dense2d_layer_1_output_12) + (-0.52429*dense2d_layer_1_output_13) + (-0.357806*dense2d_layer_1_output_14) + (-0.147364*dense2d_layer_1_output_15) + (0.0922557*dense2d_layer_1_output_16) + (0.753088*dense2d_layer_1_output_17) + (0.114208*dense2d_layer_1_output_18) + (0.333739*dense2d_layer_1_output_19) + (-0.0558799*dense2d_layer_1_output_20) + (-0.509774*dense2d_layer_1_output_21) + (-0.365878*dense2d_layer_1_output_22) + (-0.180287*dense2d_layer_1_output_23) + (0.110657*dense2d_layer_1_output_24) + (-0.00657572*dense2d_layer_1_output_25) + (0.614973*dense2d_layer_1_output_26) + (-0.0462467*dense2d_layer_1_output_27) + (0.243938*dense2d_layer_1_output_28) + (0.199343*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_13 = self.HyperbolicTangent( -0.489983 + (-0.165114*dense2d_layer_1_output_0) + (1.08989*dense2d_layer_1_output_1) + (0.198361*dense2d_layer_1_output_2) + (-1.10274*dense2d_layer_1_output_3) + (0.707744*dense2d_layer_1_output_4) + (0.638956*dense2d_layer_1_output_5) + (1.34944*dense2d_layer_1_output_6) + (0.957642*dense2d_layer_1_output_7) + (0.285565*dense2d_layer_1_output_8) + (0.389122*dense2d_layer_1_output_9) + (-0.754311*dense2d_layer_1_output_10) + (0.548065*dense2d_layer_1_output_11) + (-0.158742*dense2d_layer_1_output_12) + (-0.186804*dense2d_layer_1_output_13) + (0.410771*dense2d_layer_1_output_14) + (-1.03457*dense2d_layer_1_output_15) + (-0.0912639*dense2d_layer_1_output_16) + (0.504669*dense2d_layer_1_output_17) + (-1.15851*dense2d_layer_1_output_18) + (0.458504*dense2d_layer_1_output_19) + (-0.464464*dense2d_layer_1_output_20) + (1.36971*dense2d_layer_1_output_21) + (-0.0832896*dense2d_layer_1_output_22) + (-0.663445*dense2d_layer_1_output_23) + (-0.251788*dense2d_layer_1_output_24) + (-0.520291*dense2d_layer_1_output_25) + (0.8938*dense2d_layer_1_output_26) + (-0.251298*dense2d_layer_1_output_27) + (-1.28092*dense2d_layer_1_output_28) + (0.25723*dense2d_layer_1_output_29) )
		dense2d_layer_2_output_14 = self.HyperbolicTangent( -0.101208 + (0.455155*dense2d_layer_1_output_0) + (-0.439484*dense2d_layer_1_output_1) + (0.356974*dense2d_layer_1_output_2) + (0.283785*dense2d_layer_1_output_3) + (-0.0508744*dense2d_layer_1_output_4) + (-0.0727184*dense2d_layer_1_output_5) + (-0.0907005*dense2d_layer_1_output_6) + (-0.32838*dense2d_layer_1_output_7) + (0.272213*dense2d_layer_1_output_8) + (-0.506689*dense2d_layer_1_output_9) + (-0.493729*dense2d_layer_1_output_10) + (0.802703*dense2d_layer_1_output_11) + (0.24214*dense2d_layer_1_output_12) + (-0.0484053*dense2d_layer_1_output_13) + (0.973226*dense2d_layer_1_output_14) + (0.393567*dense2d_layer_1_output_15) + (0.233752*dense2d_layer_1_output_16) + (0.116991*dense2d_layer_1_output_17) + (-0.395878*dense2d_layer_1_output_18) + (0.458776*dense2d_layer_1_output_19) + (-0.0948034*dense2d_layer_1_output_20) + (-0.534308*dense2d_layer_1_output_21) + (-0.0973046*dense2d_layer_1_output_22) + (-0.426509*dense2d_layer_1_output_23) + (0.493195*dense2d_layer_1_output_24) + (-0.0141733*dense2d_layer_1_output_25) + (0.999164*dense2d_layer_1_output_26) + (1.19461*dense2d_layer_1_output_27) + (1.06906*dense2d_layer_1_output_28) + (-0.0906833*dense2d_layer_1_output_29) )
		approximation_layer_output_0 = self.Linear( -0.547441 + (-1.77545*dense2d_layer_2_output_0) + (-1.90718*dense2d_layer_2_output_1) + (-1.65761*dense2d_layer_2_output_2) + (2.53496*dense2d_layer_2_output_3) + (-2.14757*dense2d_layer_2_output_4) + (-2.72941*dense2d_layer_2_output_5) + (2.00292*dense2d_layer_2_output_6) + (1.99816*dense2d_layer_2_output_7) + (-1.52001*dense2d_layer_2_output_8) + (1.40197*dense2d_layer_2_output_9) + (1.70713*dense2d_layer_2_output_10) + (1.95444*dense2d_layer_2_output_11) + (-1.02966*dense2d_layer_2_output_12) + (2.92846*dense2d_layer_2_output_13) + (1.53047*dense2d_layer_2_output_14) )
		unscaling_layer_output_0=approximation_layer_output_0*0.1071702391+0.1770648658
		degradation = unscaling_layer_output_0
		outputs = [degradation]
		return outputs

	def calculate_batch_output(self, input_batch):
		output_batch = np.zeros((len(input_batch), 1))
		for i in range(len(input_batch)):
			inputs = list(input_batch[i])
			output = self.calculate_outputs(inputs)
			output_batch[i] = output
		return output_batch

def main():

	# Introduce your input values here
	mat_1 = 0  # mat_1
	mat_2 = 0  # mat_2
	mat_3 = 0  # mat_3
	mat_4 = 0  # mat_4

	# --- Data conversion (DO NOT modify) ---
	inputs = []

	inputs.append(mat_1)
	inputs.append(mat_2)
	inputs.append(mat_3)
	inputs.append(mat_4)

	nn = NeuralNetwork()
	outputs = nn.calculate_outputs(inputs)
	print(outputs)

if __name__ == "__main__":
	main()
