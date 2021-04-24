# Fairly Constricted PSO

Code for the arXiv paper `2104.10040` at https://arxiv.org/abs/2104.10040

We have built three variants of SMPSO on top of the jmetalpy framework ---

    - EMSMPSO - Exponentially-Averaged Momentum-Boosted SMPSO

    - FCPSO_Beta - Fairly Constricted PSO with momentum parameter drawn from uniform
     distribution

    - FCPSO_Omega - Fairly Constricted PSO with an "inverse" momentum parameter (omega) drawn from a uniform distribution

The newly developed algorithms could be used as follows ---

```python
    from jmetal.algorithm.multiobjective import EMSMPSO, FCPSO_Beta, FCPSO_Omega
    problem = ZDT1()
    algo = EMSMPSO # replace with 'FCPSO_Beta' or 'FCPSO_Omega'
    algorithm = algo(
    problem=problem,
    swarm_size=100,
    mutation=PolynomialMutation(probability=1.0/ problem.number_of_variables, distribution_index=20),
    leaders=CrowdingDistanceArchive(100),
    termination_criterion=StoppingByEvaluations(max_evaluations=max_evaluations)
    )
    algorithm.run()
```

The rest of this repository works in the same way as the origin jmetalpy.
