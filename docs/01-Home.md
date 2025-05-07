# ReCode: Time Lag Analysis Application

## Purpose of this Exemplar

This exemplar serves as a learning tool for understanding how to design and structure scientific software. It is not intended to teach Python programming from scratch, but rather to demonstrate software design practices in a research context.

The application in this exemplar analyses gas permeation through membrane materials using the time-lag method. While this method is primarily employed within diffusion modelling contexts in chemical engineering and materials science, it illustrates a framework for constructing a comprehensive computational workflow suitable for implementing diverse empirical methodologies in Python.

Through this specific application, you will learn the principles of scientific software design. By the end of this exemplar, you will be able to adapt the code in this exemplar to your own research applications.

## What You'll Learn

- Techniques for processing experimental data.
- Implementation of numerical methods (PDE solving) using `scipy.solve_ivp`.
- Approaches for data visualisation using `matplotlib`.
- Building user interfaces for scientific applications using `CustomTkinter`.
- Create an end-to-end analysis workflow: from data extraction and processing to visualisation and saving results.

## Before You Begin

This exemplar assumes you have:

- Basic Python programming knowledge.
- Familiarity with scientific computing concepts.
- Understanding of numerical methods fundamentals.
- Experience with plotting data.

## How to Use This Documentation

1. Start by understanding the theoretical background (`02-Theoretical-Background`).
2. Learn about data management and processing (`03-Data-Management-and-Processing`).
3. Explore the time lag analysis implementation (`04-TimelagAnalysis-Implementation`).
4. Study the PDE solving approach with Python (`05-Python-PDE-Implementation`).
5. Review scientific visualisation techniques (`06-Scientific-Visualisation`).
6. Examine GUI implementation with `CustomTkinter` (`07-GUI-Implementation`).
7. Understand how components integrate into a workflow (`08-Application-Workflow`).
8. Test your understanding with exercises and learn best practices (`09-Exercises-and-Best-Practices`).

## Major Steps in this Time Lag Analysis App

The implementation follows these key steps:

1. Data Loading and Preprocessing - Loading experimental data files and preparing data for analysis.
2. Stabilisation Time Detection - Identifying when the system reaches steady-state permeation.
3. Linear Regression of Steady-State Data - Fitting the steady-state portion of the flux curve.
4. Time Lag Calculation - Determining the time lag from the linear regression.
5. Diffusion Coefficient Determination - Calculating diffusion coefficient from time lag.
6. Permeability and Solubility Calculation - Computing additional transport parameters.
7. PDE-Based Validation - Numerically solving the diffusion equation to validate results.
8. Visualisation - Creating plots and visual representations of the analysis.
9. Workflow Integration - Combining all steps into a cohesive analysis pipeline.
10. GUI Implementation - Building a user-friendly interface to the analysis tools.

## Navigation Guide

### Getting Started

- [`01-Home`](01-Home.md) - Introduction to the project and navigation guide.
- [`02-Theoretical-Background`](02-Theoretical-Background.md) - Scientific foundations and principles.

### Core Implementation

- [`03-Data-Management-and-Processing`](03-Data-Management-and-Processing.md) - Data handling and processing (Step 1).
- [`04-TimelagAnalysis-Implementation`](04-TimelagAnalysis-Implementation.md) - Core analysis algorithms (Steps 2-6).
- [`05-Python-PDE-Implementation`](05-Python-PDE-Implementation.md) - PDE-based validation (Step 7).

### User Interface and Visualisation

- [`06-Visualisation`](06-Visualisation.md) - Creating effective visualisations (Step 8).
- [`07-GUI-Implementation`](07-GUI-Implementation.md) - Building interfaces with CustomTkinter (Step 10).

### Integration and Practice

- [`08-Application-Workflow`](08-Application-Workflow.md) - Combining components cohesively (Step 9).
- [`09-Exercises-and-Best-Practices`](09-Exercises-and-Best-Practices.md) - Hands-on activities and best practices.