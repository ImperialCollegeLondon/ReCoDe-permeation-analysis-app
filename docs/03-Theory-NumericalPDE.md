# Numerical Solution of Partial Differential Equations

## TLDR
We solve Fick's Second Law ($\frac{\partial C}{\partial t} = D\frac{\partial ^2 C}{\partial x^2}) using an explicit finite difference method to simulate gas diffusion through a membrane. The membrane initially contains no gas; one side maintains constant concentration while the other side stays at zero concentration. We discretise space and time, replacing continuous derivatives with discrete approximations. The method is conditionally stable, requiring $\Delta_t \le \frac{\Delta_t^2}{2D}. Our implementation ensures stability, properly handles boundary conditions, and calculates flux at the permeate side using Fick's First Law, allowing us to visualise the concentration profile and flux evolution.


## Mathematical Background

### Diffusion Equation

The core of our application deals with solving Fick's Second Law of diffusion:

$$\frac{\partial C}{\partial t} = D \frac{\partial^2 C}{\partial x^2}$$

where:
- $C$ is the concentration of gas in the membrane
- $t$ is time
- $D$ is the diffusion coefficient
- $x$ is the position within the membrane

This is a parabolic PDE that describes how the concentration of gas changes over time due to diffusion.

## Boundary and Initial Conditions

For the time-lag analysis problem, we define the following conditions:

### Initial Condition
At time $t = 0$, the membrane contains no gas:
$$C(x, 0) = 0 \quad \text{for} \quad 0 < x < L$$

### Boundary Conditions
1. **Feed Side** (upstream boundary at $x = 0$):  
   A constant concentration is maintained:
   $$C(0, t) = C_0$$

2. **Permeate Side** (downstream boundary at $x = L$):  
   Zero concentration is maintained:
   $$C(L, t) = 0$$

These conditions represent a physical scenario where gas is introduced to one side of a membrane that initially contains no gas, while the other side is kept at zero concentration.

## Numerical Discretisation

To solve Fick's Second Law numerically, we follow a three-step process:

1. **Discretise the domain**: Convert continuous space and time into finite points
2. **Approximate the derivatives**: Replace continuous derivatives with discrete approximations
3. **Implement a solution scheme**: Choose between explicit and implicit approaches

### Discretising the Domain

We transform the continuous problem into a discrete one by:

- Dividing the spatial domain $[0, L]$ into $N$ equally spaced points with spacing $\Delta x = L/(N-1)$
- Dividing the time domain $[0, T]$ into $M$ time steps with step size $\Delta t$

This creates a grid of points $(x_i, t_n)$ where:
- $x_i = i \cdot \Delta x$ for $i = 0, 1, 2, ..., N-1$
- $t_n = n \cdot \Delta t$ for $n = 0, 1, 2, ..., M-1$

### Approximating the Derivatives

At each grid point, we replace the continuous derivatives with finite differences:

1. **Second spatial derivative** using central differences:

   $$\frac{\partial^2 C}{\partial x^2} \approx \frac{C(x+\Delta x, t) - 2C(x, t) + C(x-\Delta x, t)}{(\Delta x)^2}$$

2. **Time derivative** using forward differences:

   $$\frac{\partial C}{\partial t} \approx \frac{C(x, t+\Delta t) - C(x, t)}{\Delta t}$$

### Selecting a Solution Scheme

#### Explicit vs Implicit Approaches

We have two main options for advancing the solution in time:

**Explicit Scheme (Our Choice)**

$$C[i, n+1] = C[i, n] + r \cdot (C[i+1, n] - 2C[i, n] + C[i-1, n])$$

where $r = D\frac{\Delta t}{(\Delta x)^2}$ is a dimensionless parameter that represents the ratio of the time step to the spatial step squared, scaled by the diffusion coefficient. This parameter controls both the accuracy and stability of the solution:

- When $r$ is small: The solution changes slowly and remains stable
- When $r$ is large: The solution can become unstable with oscillations that grow exponentially

The explicit scheme has these characteristics:
- Direct calculation from current time step values
- Simple implementation and transparency
- Limited by stability condition: $r \leq \frac{1}{2}$

**Implicit Scheme**

$$-r \cdot C[i-1, n+1] + (1 + 2r) \cdot C[i, n+1] - r \cdot C[i+1, n+1] = C[i, n]$$

Using the same parameter $r$, the implicit scheme has the characteristics:
- Unconditionally stable regardless of the value of $r$
- Requires solving a system of linear equations at each time step
- Permits larger time steps without becoming unstable
- More complex to implement

We selected the explicit scheme for educational clarity and implementation simplicity. For our diffusion problem, the stability constraints are reasonable, making the explicit approach an efficient choice.

### Mathematical Formulation

Substituting our discrete approximations into Fick's Second Law yields the explicit finite difference scheme:

$$C(x_i, t_{n+1}) = C(x_i, t_n) + D\frac{\Delta t}{(\Delta x)^2} \cdot [C(x_{i+1}, t_n) - 2C(x_i, t_n) + C(x_{i-1}, t_n)]$$

Using array notation, this simplifies to:

$$C[i, n+1] = C[i, n] + r \cdot (C[i+1, n] - 2C[i, n] + C[i-1, n])$$

where $r = D\frac{\Delta t}{(\Delta x)^2}$ is the key dimensionless parameter governing stability.

## Stability Considerations

### The Stability Criterion

For the explicit scheme, stability requires:

$$r = D\frac{\Delta t}{(\Delta x)^2} \leq \frac{1}{2}$$

If this condition is not met, numerical errors can grow exponentially and the solution becomes meaningless.

### Ensuring Stability in Our Implementation

In our code, we check this condition before running the simulation:

```python
assert dt <= dx**2 / (2 * D), "Stability condition not met, reduce dt or increase dx"
```

## Implementation Approach

Our numerical solution follows these steps:

1. Initialise the concentration array with zeros
2. Apply the boundary conditions ($C[0, n] = C_0$ and $C[N-1, n] = 0$)
3. For each time step:
   - Update interior points using the explicit scheme
   - Re-apply boundary conditions
   - Calculate the flux at the permeate side

## Calculating Flux

The flux at the permeate side ($x = L$) is calculated using Fick's First Law:

$$J = -D \cdot \frac{\partial C}{\partial x}$$

Using a backward difference approximation at $x = L$:

$$J \approx -D \cdot \frac{C[N-1, n] - C[N-2, n]}{\Delta x}$$

## Verification and Validation

The numerical solution is verified by comparing with the analytical solution for simple cases where it exists. For the time-lag problem, the analytical solution for the cumulative flux shows that the steady-state behaviour is linear with an intercept that gives the time-lag.