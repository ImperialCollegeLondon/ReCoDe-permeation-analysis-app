# Time Lag Analysis: Theoretical Foundation

## TLDR
The time-lag method allows us to calculate both the diffusion coefficient (D) and solubility coefficient (S) from a single gas permeation experiment. By plotting cumulative gas flux versus time, we observe a straight line during steady-state. The x-intercept of this line is the "time lag" $\theta$v, from which we calculate $D = \frac{L^2}{6\theta}$ where $L$ is membrane thickness. The slope gives permeability $P$, allowing us to determine $S = \frac{P}{D}$. This technique, pioneered by Daynes (1920) and Barrer (1939), is fundamental for characterising gas transport through membranes.


## Introduction to Gas Transport Phenomena

Gas transport through membranes is a fundamental process in many areas of chemical engineering, materials science, and environmental applications. Understanding and quantifying this transport is essential for designing materials for gas separation, barrier materials, and controlled release systems.

## The Time-Lag Method

The time-lag method was first developed and applied to gas diffusion studies in the early 20th century by Daynes [1] and further developed by Barrer [2].

These works established the theoretical foundation that remains the basis for contemporary membrane permeation analysis.
The time-lag method is a technique used to determine two key transport parameters simultaneously:
- Diffusion coefficient ($D$)
- Solubility coefficient ($S$)

Together, these parameters determine the material's permeability:

$$P = D \times S$$

## Theoretical Background

### Fick's Laws and Boundary Conditions

The time-lag method is based on Fick's laws of diffusion:

1. **Fick's First Law**: Relates the diffusive flux to the concentration gradient
   
   $$J = -D \frac{\partial C}{\partial x}$$

   Where:
   - $J$ is the diffusion flux [mol/(m²·s)]
   - $D$ is the diffusion coefficient [m²/s]
   - $C$ is the concentration [mol/m³]
   - $x$ is position [m]

2. **Fick's Second Law**: Describes how concentration changes with time due to diffusion

   $$\frac{\partial C}{\partial t} = D \frac{\partial^2 C}{\partial x^2}$$

   For a membrane of thickness $L$ with the following boundary conditions:
   - $C(0,t) = C_1$ (upstream/feed side concentration)
   - $C(L,t) = 0$ (downstream/permeate side concentration, initially evacuated)
   - $C(x,0) = 0$ (initial condition: no gas in membrane)

### The Time-Lag Derivation

<!-- TODO: Add a diagram to show the concentration as a function of x -->

When gas permeation reaches steady state, the cumulative amount of gas that has permeated through the membrane ($Q$) follows:

$$Q(t) = \frac{DC_1}{L}\left(t - \frac{L^2}{6D}\right)$$

The time-lag ($\theta$) is defined as the x-intercept of the extrapolated steady-state line and is related to the diffusion coefficient:

$$\theta = \frac{L^2}{6D}$$

Therefore:

$$D = \frac{L^2}{6\theta}$$

The steady-state flux ($J_{\infty}$) is related to permeability ($P$):

$$J_{\infty} = \frac{P \cdot \Delta p}{L}$$

Where:
- $P$ is permeability
- $\Delta p$ is pressure difference

Since $P = D \times S$, we can calculate solubility:

$$S = \frac{P}{D}$$

## Units and Conventions

While the theoretical equations are typically presented using SI units, in practice, different fields often use specialised unit systems. In this application, we use the following units:

- Length: centimeters [cm]
- Time: seconds [s]
- Pressure: bar [bar]
- Volume: standard cubic centimeters [cm³(STP)]
- Temperature: degrees Celsius [°C]

The key parameters have these units:
- Diffusion coefficient ($D$): [cm²/s]
- Permeability ($P$): [cm³(STP)·cm/(cm²·s·bar)]
- Solubility coefficient ($S$): [cm³(STP)/(cm³·bar)]
- Time lag ($\theta$): [s]

Note that STP refers to "Standard Temperature and Pressure" conditions (typically 0°C and 1 bar), which is important when reporting gas volumes. The units chosen reflect common conventions in membrane science and gas permeation studies, facilitating comparison with literature values.

## Experimental Implementation

In practice:
1. A gas is introduced on one side of a membrane at time $t=0$. The downstream pressure is maintained by using a continuously sweeping flow of nitrogen (N2).
2. The gas flux through the membrane is measured over time on the permeate side
3. Initially, there is a transient state as the concentration profile develops in the membrane
4. Eventually, a steady-state is reached with a constant flux

Each method ensures that the concentration at the downstream face of the membrane remains effectively zero (or negligibly small compared to the upstream concentration), maintaining the boundary condition $C(L,t) = 0$ needed for the time-lag analysis.

By plotting the cumulative amount of permeated gas vs. time, and extrapolating the steady-state line back to the time axis, the time-lag ($\theta$) is determined.

<!-- TODO: Add example -->

## Significance and Applications

The time-lag method provides:
- A straightforward way to determine both diffusion and solubility coefficients
- Insights into the transport mechanisms through polymers and other materials
- Data essential for designing gas separation membranes, food packaging, and barrier materials

In this application, we implement the time-lag method for analysing experimental permeation data and visualising the results, providing a computational tool that researchers can use and adapt to their specific needs.

## Limitations of the Time Lag Method

While the time-lag method is a powerful technique, it has several important limitations that should be considered:

1. **Constant Diffusion Coefficient Assumption**: The classical time-lag method assumes that the diffusion coefficient is concentration-independent. For materials with strong gas-polymer interactions, this assumption may not hold, leading to inaccurate results.

2. **Steady-State Requirement**: Accurate time-lag determination requires reaching true steady-state conditions. Premature termination of experiments can lead to incorrect extrapolation and inaccurate diffusion coefficients.

3. **Downstream Boundary Condition**: The method requires maintaining near-zero concentration at the downstream membrane face. Insufficient sweep gas flow or downstream accumulation can violate this condition, compromising time-lag accuracy.

These limitations highlight the importance of careful experimental design and thoughtful interpretation of results when using the time-lag method for membrane characterisation.

## Bibliography

1. Daynes, H.A. "The process of diffusion through a rubber membrane." *Royal Society Proceedings*, 97 (1920), pp. 286-307.

2. Barrer, R.M. "Permeation, diffusion and solution of gases in organic polymers." *Transactions of the Faraday Society*, 35 (1939), pp. 628-643.
