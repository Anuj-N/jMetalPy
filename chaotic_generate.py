import cpso
import benchmark as bench


def generateChaos():
	objective = bench.Rastrigin(None, dims=1)
	llim = objective.llim
	rlim = objective.rlim
	func = objective.obj
	der = objective.objder
	swarm = cpso.EMPSO.get_chaotic_swarm(
		{	
		'init_cmap'    : {
		'name'      : 'logistic',        # Initialisation map --> Logistic map
		'args'      : ()                 # Default logistic parameter --> 4
		},

		'dyn_cmap'     : {
			'name'      : 'tent',            # Chaotic map for r1, r2 --> Tent map
			'args'      : ()                 # Default tent paraneter --> 0.49999
		}
		}
	)
	mizer = swarm(func, llim, rlim, 25)
	retpack = mizer.optimize()
	opt, approxGrad = retpack['rets']
	return opt.reshape(1,-1)[0]