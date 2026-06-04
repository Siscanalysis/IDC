''' 
Artificial Intelligence Techniques SL
artelnics@artelnics.com

Model exported to Python. Use NeuralNetwork().calculate_outputs([...]).

Input Names: 
	0) cement
	1) slag
	2) fly_ash
	3) water
	4) sp
	5) coarse_agg
	6) fine_agg
	7) age

For batch prediction (input must be np.ndarray):
	nn.calculate_batch_output(np.array([[1, 2], [4, 5]]))
''' 
import numpy as np
import pandas as pd

class NeuralNetwork:

	def __init__(self):
		self.inputs_number = 8
		self.input_names = ['cement', 'slag', 'fly_ash', 'water', 'sp', 'coarse_agg', 'fine_agg', 'age']

	@staticmethod
	def Identity(x):
		return x

	@staticmethod
	def Tanh(x):
		return np.tanh(x)

	def calculate_outputs(self, inputs):
		cement = inputs[0]
		slag = inputs[1]
		fly_ash = inputs[2]
		water = inputs[3]
		sp = inputs[4]
		coarse_agg = inputs[5]
		fine_agg = inputs[6]
		age = inputs[7]

		scaled_cement = (cement-281.1656189)/104.5071411
		scaled_slag = (slag-73.89548492)/86.27910614
		scaled_fly_ash = (fly_ash-54.18713379)/63.99646759
		scaled_water = (water-181.5663605)/21.35556793
		scaled_sp = (sp-6.203111649)/5.973491669
		scaled_coarse_agg = (coarse_agg-972.9185791)/77.75382233
		scaled_fine_agg = (fine_agg-773.5788574)/80.1754303
		scaled_age = (age-45.66213608)/63.16991043
		dense2d_layer_1_output_0 = self.Tanh( 0.0178182 + (-0.0341001*scaled_cement) + (-0.0204746*scaled_slag) + (-0.00594196*scaled_fly_ash) + (0.0153683*scaled_water) + (-0.0219673*scaled_sp) + (-0.000234446*scaled_coarse_agg) + (-0.000546323*scaled_fine_agg) + (0.00397293*scaled_age) )
		dense2d_layer_1_output_1 = self.Tanh( -0.727179 + (-0.250932*scaled_cement) + (-0.0348329*scaled_slag) + (-0.0423414*scaled_fly_ash) + (-0.129878*scaled_water) + (0.0772891*scaled_sp) + (-0.0679041*scaled_coarse_agg) + (-0.191801*scaled_fine_agg) + (-1.46058*scaled_age) )
		dense2d_layer_1_output_2 = self.Tanh( -0.00711379 + (0.0137131*scaled_cement) + (0.010227*scaled_slag) + (0.000578585*scaled_fly_ash) + (-0.0049121*scaled_water) + (0.0102136*scaled_sp) + (-0.000468937*scaled_coarse_agg) + (-0.000528436*scaled_fine_agg) + (-0.00103583*scaled_age) )
		dense2d_layer_1_output_3 = self.Tanh( 0.0247351 + (-0.0492974*scaled_cement) + (-0.0310472*scaled_slag) + (-0.00455179*scaled_fly_ash) + (0.0198349*scaled_water) + (-0.0330462*scaled_sp) + (0.00108162*scaled_coarse_agg) + (-0.00111747*scaled_fine_agg) + (0.00533982*scaled_age) )
		dense2d_layer_1_output_4 = self.Tanh( 0.024489 + (-0.0488826*scaled_cement) + (-0.0316227*scaled_slag) + (-0.00400448*scaled_fly_ash) + (0.0201321*scaled_water) + (-0.0326074*scaled_sp) + (0.000386207*scaled_coarse_agg) + (-0.000710097*scaled_fine_agg) + (0.00348214*scaled_age) )
		dense2d_layer_1_output_5 = self.Tanh( 0.0301566 + (-0.0574594*scaled_cement) + (-0.0359448*scaled_slag) + (-0.00927938*scaled_fly_ash) + (0.0235078*scaled_water) + (-0.0350894*scaled_sp) + (-0.000171028*scaled_coarse_agg) + (0.00053169*scaled_fine_agg) + (0.00346438*scaled_age) )
		dense2d_layer_1_output_6 = self.Tanh( -0.0218502 + (0.0724679*scaled_cement) + (0.0446141*scaled_slag) + (0.0137371*scaled_fly_ash) + (-0.0289169*scaled_water) + (0.0409743*scaled_sp) + (0.00303758*scaled_coarse_agg) + (0.0115083*scaled_fine_agg) + (0.013435*scaled_age) )
		dense2d_layer_1_output_7 = self.Tanh( 0.0152883 + (-0.0300587*scaled_cement) + (-0.0185143*scaled_slag) + (-0.00502751*scaled_fly_ash) + (0.0139014*scaled_water) + (-0.0196943*scaled_sp) + (-0.000375591*scaled_coarse_agg) + (-0.00047218*scaled_fine_agg) + (0.00352696*scaled_age) )
		dense2d_layer_1_output_8 = self.Tanh( 0.0537215 + (-0.106243*scaled_cement) + (-0.0589373*scaled_slag) + (-0.0186333*scaled_fly_ash) + (0.0591813*scaled_water) + (-0.0634028*scaled_sp) + (-0.00784001*scaled_coarse_agg) + (-0.0171379*scaled_fine_agg) + (0.00763514*scaled_age) )
		dense2d_layer_1_output_9 = self.Tanh( 0.0186289 + (-0.0368929*scaled_cement) + (-0.0246014*scaled_slag) + (-0.00362841*scaled_fly_ash) + (0.0151074*scaled_water) + (-0.0252816*scaled_sp) + (0.000610172*scaled_coarse_agg) + (-0.000121703*scaled_fine_agg) + (0.00397272*scaled_age) )
		dense2d_layer_1_output_10 = self.Tanh( 0.000311641 + (-0.00379756*scaled_cement) + (-0.00296904*scaled_slag) + (0.00252395*scaled_fly_ash) + (-0.000290218*scaled_water) + (-0.00337513*scaled_sp) + (0.000932171*scaled_coarse_agg) + (0.00138552*scaled_fine_agg) + (0.0011997*scaled_age) )
		dense2d_layer_1_output_11 = self.Tanh( -0.00310449 + (0.00555614*scaled_cement) + (0.00427397*scaled_slag) + (0.000772145*scaled_fly_ash) + (-0.00223182*scaled_water) + (0.00382807*scaled_sp) + (2.70473e-05*scaled_coarse_agg) + (-0.000305885*scaled_fine_agg) + (-0.00021662*scaled_age) )
		dense2d_layer_1_output_12 = self.Tanh( -0.0230749 + (0.0428542*scaled_cement) + (0.0257026*scaled_slag) + (0.0083179*scaled_fly_ash) + (-0.0205977*scaled_water) + (0.027897*scaled_sp) + (0.000845876*scaled_coarse_agg) + (0.00172682*scaled_fine_agg) + (-0.00480221*scaled_age) )
		dense2d_layer_1_output_13 = self.Tanh( 0.0200092 + (-0.0375935*scaled_cement) + (-0.024788*scaled_slag) + (-0.00304215*scaled_fly_ash) + (0.0141377*scaled_water) + (-0.0248906*scaled_sp) + (0.00108295*scaled_coarse_agg) + (0.000202187*scaled_fine_agg) + (0.00450268*scaled_age) )
		dense2d_layer_1_output_14 = self.Tanh( -0.0265183 + (0.0517683*scaled_cement) + (0.0295907*scaled_slag) + (0.0066775*scaled_fly_ash) + (-0.0216962*scaled_water) + (0.0347145*scaled_sp) + (-0.000389169*scaled_coarse_agg) + (0.00125173*scaled_fine_agg) + (-0.00765403*scaled_age) )
		dense2d_layer_1_output_15 = self.Tanh( -0.0109971 + (0.0191711*scaled_cement) + (0.0126204*scaled_slag) + (0.00378403*scaled_fly_ash) + (-0.00910328*scaled_water) + (0.0128734*scaled_sp) + (0.000352639*scaled_coarse_agg) + (0.000422275*scaled_fine_agg) + (-0.00195273*scaled_age) )
		dense2d_layer_1_output_16 = self.Tanh( -0.0134185 + (0.0278755*scaled_cement) + (0.0170328*scaled_slag) + (7.0348e-06*scaled_fly_ash) + (-0.0100612*scaled_water) + (0.018378*scaled_sp) + (-0.00134066*scaled_coarse_agg) + (-0.00103672*scaled_fine_agg) + (-0.00377658*scaled_age) )
		dense2d_layer_1_output_17 = self.Tanh( 0.00509203 + (-0.00818265*scaled_cement) + (-0.00536439*scaled_slag) + (-0.00281936*scaled_fly_ash) + (0.00510822*scaled_water) + (-0.00489697*scaled_sp) + (-0.000530231*scaled_coarse_agg) + (-0.00100425*scaled_fine_agg) + (0.00065122*scaled_age) )
		dense2d_layer_1_output_18 = self.Tanh( -0.00406661 + (0.00844103*scaled_cement) + (0.00436791*scaled_slag) + (0.00163515*scaled_fly_ash) + (-0.00430522*scaled_water) + (0.0054719*scaled_sp) + (0.000254135*scaled_coarse_agg) + (0.000200474*scaled_fine_agg) + (-0.00169081*scaled_age) )
		dense2d_layer_1_output_19 = self.Tanh( -0.0307314 + (0.0584354*scaled_cement) + (0.0351248*scaled_slag) + (0.00774945*scaled_fly_ash) + (-0.0242954*scaled_water) + (0.0389528*scaled_sp) + (-0.00034491*scaled_coarse_agg) + (0.00236488*scaled_fine_agg) + (-0.00627788*scaled_age) )
		dense2d_layer_1_output_20 = self.Tanh( -0.0329129 + (0.0612622*scaled_cement) + (0.0370086*scaled_slag) + (0.01088*scaled_fly_ash) + (-0.0265993*scaled_water) + (0.0404913*scaled_sp) + (0.000762018*scaled_coarse_agg) + (0.00567094*scaled_fine_agg) + (-0.00427455*scaled_age) )
		dense2d_layer_1_output_21 = self.Tanh( -0.000837606 + (-0.000245347*scaled_cement) + (-0.000757604*scaled_slag) + (0.00214052*scaled_fly_ash) + (-0.00125104*scaled_water) + (-0.000541053*scaled_sp) + (0.000559012*scaled_coarse_agg) + (0.00084994*scaled_fine_agg) + (0.000830062*scaled_age) )
		dense2d_layer_1_output_22 = self.Tanh( -0.000376394 + (0.001427*scaled_cement) + (0.00130365*scaled_slag) + (-0.000706972*scaled_fly_ash) + (5.65532e-05*scaled_water) + (0.000952124*scaled_sp) + (-0.000364702*scaled_coarse_agg) + (-0.000160859*scaled_fine_agg) + (-0.000207712*scaled_age) )
		dense2d_layer_1_output_23 = self.Tanh( -0.0107626 + (0.0206244*scaled_cement) + (0.0144163*scaled_slag) + (0.00227963*scaled_fly_ash) + (-0.00860224*scaled_water) + (0.0143764*scaled_sp) + (-0.000119881*scaled_coarse_agg) + (-0.000103327*scaled_fine_agg) + (-0.00150716*scaled_age) )
		dense2d_layer_1_output_24 = self.Tanh( -0.0211159 + (0.0399962*scaled_cement) + (0.0248471*scaled_slag) + (0.00596414*scaled_fly_ash) + (-0.0176356*scaled_water) + (0.0267136*scaled_sp) + (6.48194e-05*scaled_coarse_agg) + (0.0010083*scaled_fine_agg) + (-0.00380491*scaled_age) )
		dense2d_layer_1_output_25 = self.Tanh( 0.00801277 + (-0.0140944*scaled_cement) + (-0.00968713*scaled_slag) + (-0.00211511*scaled_fly_ash) + (0.00646775*scaled_water) + (-0.00940028*scaled_sp) + (0.000201475*scaled_coarse_agg) + (-0.000826324*scaled_fine_agg) + (0.00125265*scaled_age) )
		dense2d_layer_1_output_26 = self.Tanh( 0.00242715 + (-0.00397478*scaled_cement) + (-0.00247978*scaled_slag) + (-0.000982605*scaled_fly_ash) + (0.00226435*scaled_water) + (-0.00233203*scaled_sp) + (0.000166526*scaled_coarse_agg) + (-0.000953819*scaled_fine_agg) + (0.000642412*scaled_age) )
		dense2d_layer_1_output_27 = self.Tanh( -0.00221522 + (0.0061662*scaled_cement) + (0.00463253*scaled_slag) + (-0.00158649*scaled_fly_ash) + (-0.000933257*scaled_water) + (0.0048256*scaled_sp) + (-0.000620413*scaled_coarse_agg) + (-0.000974001*scaled_fine_agg) + (0.000576059*scaled_age) )
		dense2d_layer_1_output_28 = self.Tanh( 0.0264851 + (-0.0517598*scaled_cement) + (-0.0321835*scaled_slag) + (-0.00583643*scaled_fly_ash) + (0.0216861*scaled_water) + (-0.0344632*scaled_sp) + (0.000671787*scaled_coarse_agg) + (-0.00192327*scaled_fine_agg) + (0.00485286*scaled_age) )
		dense2d_layer_1_output_29 = self.Tanh( 0.144709 + (0.144619*scaled_cement) + (0.432861*scaled_slag) + (0.0711714*scaled_fly_ash) + (0.0652776*scaled_water) + (-0.0408224*scaled_sp) + (0.00962846*scaled_coarse_agg) + (-0.406498*scaled_fine_agg) + (0.0409582*scaled_age) )
		dense2d_layer_1_output_30 = self.Tanh( -0.0291962 + (0.0605499*scaled_cement) + (0.0376223*scaled_slag) + (0.00552642*scaled_fly_ash) + (-0.0258868*scaled_water) + (0.0399222*scaled_sp) + (-2.90654e-05*scaled_coarse_agg) + (8.6818e-05*scaled_fine_agg) + (-0.00323826*scaled_age) )
		dense2d_layer_1_output_31 = self.Tanh( 0.00178827 + (-0.00345965*scaled_cement) + (-0.00113744*scaled_slag) + (-0.00226053*scaled_fly_ash) + (0.00332422*scaled_water) + (-0.00222029*scaled_sp) + (-0.000279643*scaled_coarse_agg) + (-0.0013774*scaled_fine_agg) + (0.00112347*scaled_age) )
		dense2d_layer_1_output_32 = self.Tanh( 0.0267369 + (-0.0583642*scaled_cement) + (-0.0270897*scaled_slag) + (-0.0123692*scaled_fly_ash) + (0.0267467*scaled_water) + (-0.0371654*scaled_sp) + (-0.00243094*scaled_coarse_agg) + (-0.00757065*scaled_fine_agg) + (0.00442084*scaled_age) )
		dense2d_layer_1_output_33 = self.Tanh( 0.0181554 + (-0.0348759*scaled_cement) + (-0.0223983*scaled_slag) + (-0.00429077*scaled_fly_ash) + (0.0148963*scaled_water) + (-0.0234035*scaled_sp) + (0.000426609*scaled_coarse_agg) + (-0.000798872*scaled_fine_agg) + (0.00363525*scaled_age) )
		dense2d_layer_1_output_34 = self.Tanh( 0.0094775 + (-0.0187095*scaled_cement) + (-0.0135388*scaled_slag) + (-0.000696087*scaled_fly_ash) + (0.00679968*scaled_water) + (-0.0132898*scaled_sp) + (0.000498977*scaled_coarse_agg) + (0.000726408*scaled_fine_agg) + (0.00166652*scaled_age) )
		dense2d_layer_1_output_35 = self.Tanh( 0.00943723 + (-0.0189164*scaled_cement) + (-0.0133582*scaled_slag) + (-0.00126322*scaled_fly_ash) + (0.00745686*scaled_water) + (-0.0133217*scaled_sp) + (0.000614395*scaled_coarse_agg) + (-0.000239635*scaled_fine_agg) + (0.000814071*scaled_age) )
		dense2d_layer_1_output_36 = self.Tanh( -0.0122012 + (0.0242848*scaled_cement) + (0.0153615*scaled_slag) + (0.00286151*scaled_fly_ash) + (-0.0104647*scaled_water) + (0.0165137*scaled_sp) + (-7.62185e-05*scaled_coarse_agg) + (0.000144142*scaled_fine_agg) + (-0.00215737*scaled_age) )
		dense2d_layer_1_output_37 = self.Tanh( 0.0319108 + (-0.0652606*scaled_cement) + (-0.0401648*scaled_slag) + (-0.00941222*scaled_fly_ash) + (0.0251114*scaled_water) + (-0.0439869*scaled_sp) + (0.00154911*scaled_coarse_agg) + (-0.00239656*scaled_fine_agg) + (0.00389091*scaled_age) )
		dense2d_layer_1_output_38 = self.Tanh( -0.0188379 + (0.0360436*scaled_cement) + (0.0230434*scaled_slag) + (0.00366684*scaled_fly_ash) + (-0.014064*scaled_water) + (0.0243746*scaled_sp) + (-0.000643547*scaled_coarse_agg) + (-0.000852216*scaled_fine_agg) + (-0.0048146*scaled_age) )
		dense2d_layer_1_output_39 = self.Tanh( 0.0252349 + (-0.0487642*scaled_cement) + (-0.0307363*scaled_slag) + (-0.00592*scaled_fly_ash) + (0.0203189*scaled_water) + (-0.0314788*scaled_sp) + (0.000627683*scaled_coarse_agg) + (-0.00156606*scaled_fine_agg) + (0.00459139*scaled_age) )
		dense2d_layer_1_output_40 = self.Tanh( 0.0364542 + (-0.415033*scaled_cement) + (-0.206789*scaled_slag) + (-0.141275*scaled_fly_ash) + (0.574557*scaled_water) + (-0.274616*scaled_sp) + (0.0634366*scaled_coarse_agg) + (-0.0801914*scaled_fine_agg) + (0.0139168*scaled_age) )
		dense2d_layer_1_output_41 = self.Tanh( -0.0175164 + (0.0356076*scaled_cement) + (0.0239215*scaled_slag) + (0.00300964*scaled_fly_ash) + (-0.0145067*scaled_water) + (0.0240805*scaled_sp) + (-0.00111909*scaled_coarse_agg) + (0.0010663*scaled_fine_agg) + (-0.00244157*scaled_age) )
		dense2d_layer_1_output_42 = self.Tanh( -0.027604 + (0.05128*scaled_cement) + (0.030983*scaled_slag) + (0.00889708*scaled_fly_ash) + (-0.022718*scaled_water) + (0.0337632*scaled_sp) + (3.95411e-05*scaled_coarse_agg) + (0.0021197*scaled_fine_agg) + (-0.00575239*scaled_age) )
		dense2d_layer_1_output_43 = self.Tanh( -0.0311406 + (0.0611577*scaled_cement) + (0.0375116*scaled_slag) + (0.00824183*scaled_fly_ash) + (-0.0221263*scaled_water) + (0.0369145*scaled_sp) + (-0.00354525*scaled_coarse_agg) + (-0.00121125*scaled_fine_agg) + (-0.00338369*scaled_age) )
		dense2d_layer_1_output_44 = self.Tanh( 0.000764096 + (0.000112564*scaled_cement) + (0.000877624*scaled_slag) + (-0.00216823*scaled_fly_ash) + (0.00165815*scaled_water) + (0.0006355*scaled_sp) + (-0.000729801*scaled_coarse_agg) + (-0.000763944*scaled_fine_agg) + (0.000966218*scaled_age) )
		dense2d_layer_1_output_45 = self.Tanh( 0.031411 + (-0.0683572*scaled_cement) + (-0.0451383*scaled_slag) + (-0.0115236*scaled_fly_ash) + (0.0229888*scaled_water) + (-0.0417188*scaled_sp) + (0.000497376*scaled_coarse_agg) + (0.00136491*scaled_fine_agg) + (-0.00136228*scaled_age) )
		dense2d_layer_1_output_46 = self.Tanh( -0.00917663 + (0.0172933*scaled_cement) + (0.0105662*scaled_slag) + (0.00332154*scaled_fly_ash) + (-0.00856442*scaled_water) + (0.010936*scaled_sp) + (0.000302772*scaled_coarse_agg) + (0.000944725*scaled_fine_agg) + (-0.00146734*scaled_age) )
		dense2d_layer_1_output_47 = self.Tanh( -0.0242555 + (0.0483966*scaled_cement) + (0.0311243*scaled_slag) + (0.0047178*scaled_fly_ash) + (-0.0198416*scaled_water) + (0.0330762*scaled_sp) + (-0.00105409*scaled_coarse_agg) + (0.00128303*scaled_fine_agg) + (-0.00490878*scaled_age) )
		dense2d_layer_1_output_48 = self.Tanh( -0.0124624 + (0.0227567*scaled_cement) + (0.0157927*scaled_slag) + (0.00227003*scaled_fly_ash) + (-0.00906108*scaled_water) + (0.0154148*scaled_sp) + (-0.000396397*scaled_coarse_agg) + (8.36801e-05*scaled_fine_agg) + (-0.00134968*scaled_age) )
		dense2d_layer_1_output_49 = self.Tanh( 0.0130576 + (-0.0251995*scaled_cement) + (-0.0162306*scaled_slag) + (-0.00345199*scaled_fly_ash) + (0.011371*scaled_water) + (-0.0170145*scaled_sp) + (0.000161909*scaled_coarse_agg) + (-0.000659282*scaled_fine_agg) + (0.00267303*scaled_age) )
		dense2d_layer_1_output_50 = self.Tanh( -0.0263337 + (-0.112724*scaled_cement) + (-0.177482*scaled_slag) + (-0.0243676*scaled_fly_ash) + (-0.0604882*scaled_water) + (-0.0231907*scaled_sp) + (0.00757326*scaled_coarse_agg) + (0.202935*scaled_fine_agg) + (-0.0791138*scaled_age) )
		dense2d_layer_1_output_51 = self.Tanh( -0.0231474 + (0.0461854*scaled_cement) + (0.028183*scaled_slag) + (0.00572545*scaled_fly_ash) + (-0.0204688*scaled_water) + (0.0308317*scaled_sp) + (-3.91049e-05*scaled_coarse_agg) + (0.00173745*scaled_fine_agg) + (-0.00485962*scaled_age) )
		approximation_layer_output_0 = self.Identity( -0.327485 + (-0.0553036*dense2d_layer_1_output_0) + (-1.36577*dense2d_layer_1_output_1) + (0.020542*dense2d_layer_1_output_2) + (-0.0767079*dense2d_layer_1_output_3) + (-0.0740823*dense2d_layer_1_output_4) + (-0.0884759*dense2d_layer_1_output_5) + (0.0982754*dense2d_layer_1_output_6) + (-0.0492645*dense2d_layer_1_output_7) + (-0.155587*dense2d_layer_1_output_8) + (-0.0580059*dense2d_layer_1_output_9) + (-0.00396458*dense2d_layer_1_output_10) + (0.00909348*dense2d_layer_1_output_11) + (0.0711865*dense2d_layer_1_output_12) + (-0.0581342*dense2d_layer_1_output_13) + (0.083975*dense2d_layer_1_output_14) + (0.0319953*dense2d_layer_1_output_15) + (0.0437706*dense2d_layer_1_output_16) + (-0.014574*dense2d_layer_1_output_17) + (0.0141471*dense2d_layer_1_output_18) + (0.0920849*dense2d_layer_1_output_19) + (0.0959381*dense2d_layer_1_output_20) + (0.00136156*dense2d_layer_1_output_21) + (0.000941208*dense2d_layer_1_output_22) + (0.0323847*dense2d_layer_1_output_23) + (0.0645403*dense2d_layer_1_output_24) + (-0.021954*dense2d_layer_1_output_25) + (-0.00579554*dense2d_layer_1_output_26) + (0.00789565*dense2d_layer_1_output_27) + (-0.0807403*dense2d_layer_1_output_28) + (0.508071*dense2d_layer_1_output_29) + (0.0924012*dense2d_layer_1_output_30) + (-0.00630672*dense2d_layer_1_output_31) + (-0.0940477*dense2d_layer_1_output_32) + (-0.0548822*dense2d_layer_1_output_33) + (-0.0280842*dense2d_layer_1_output_34) + (-0.02833*dense2d_layer_1_output_35) + (0.0387158*dense2d_layer_1_output_36) + (-0.0991933*dense2d_layer_1_output_37) + (0.0575875*dense2d_layer_1_output_38) + (-0.0755346*dense2d_layer_1_output_39) + (-0.806252*dense2d_layer_1_output_40) + (0.0536239*dense2d_layer_1_output_41) + (0.0831231*dense2d_layer_1_output_42) + (0.0893805*dense2d_layer_1_output_43) + (-0.00191224*dense2d_layer_1_output_44) + (-0.100936*dense2d_layer_1_output_45) + (0.0281253*dense2d_layer_1_output_46) + (0.0756922*dense2d_layer_1_output_47) + (0.0353034*dense2d_layer_1_output_48) + (-0.0402317*dense2d_layer_1_output_49) + (-0.251462*dense2d_layer_1_output_50) + (0.0738571*dense2d_layer_1_output_51) )
		scaled_cement=approximation_layer_output_0*16.70567894+35.81783676
		strength = scaled_cement
		outputs = [strength]
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
	cement = 0  # cement
	slag = 0  # slag
	fly_ash = 0  # fly_ash
	water = 0  # water
	sp = 0  # sp
	coarse_agg = 0  # coarse_agg
	fine_agg = 0  # fine_agg
	age = 0  # age

	# --- Data conversion (DO NOT modify) ---
	inputs = []

	inputs.append(cement)
	inputs.append(slag)
	inputs.append(fly_ash)
	inputs.append(water)
	inputs.append(sp)
	inputs.append(coarse_agg)
	inputs.append(fine_agg)
	inputs.append(age)

	nn = NeuralNetwork()
	outputs = nn.calculate_outputs(inputs)
	print(outputs)

if __name__ == "__main__":
	main()
