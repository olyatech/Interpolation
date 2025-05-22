# Interpolation

This repository contains realization of algorithms from paper [1]. Project was created as the part of python course in IITP RAS. I follow python tooling guide [2].

A description of the currently implemented algorithms is contained in the section "Implemented algorithms".

## Implemented algorithms

### Node-wise interpolation

A field on the new mesh $\psi_i^{new}(p_i)$ is calculated as:
$$\psi_i^{new}(p_i) = \sum_{j}N_j^{old}(p_i)\psi_i^{old},$$ 
where $N_j^{old}$ are basis functions (finite element or control-volume depending on the nature of the field $\psi_i^{old}$) defined on the old mesh [1].

## References:

[1] A. Adam, D. Pavlidis, J.R. Percival, P. Salinas, Z. Xie, F. Fang, C.C. Pain, A.H. Muggeridge, M.D. Jackson,
Higher-order conservative interpolation between control-volume meshes: Application to advection and multiphase flow problems with dynamic mesh adaptivity,
Journal of Computational Physics,
Volume 321,
2016.

[2] https://cjolowicz.github.io/posts/