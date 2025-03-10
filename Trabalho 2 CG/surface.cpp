#include <iostream>
#include <cstdlib>
#include <cmath>

// Constants
#define NI 3
#define NJ 4
#define TI 3
#define TJ 3
#define RESOLUTIONI 30
#define RESOLUTIONJ 40

// Structure to represent a 3D point
struct XYZ {
    double x, y, z;
};

// Global arrays
XYZ inp[NI + 1][NJ + 1];       // Control points
int knotsI[NI + TI + 1];       // Knot vector for i direction
int knotsJ[NJ + TJ + 1];       // Knot vector for j direction
XYZ outp[RESOLUTIONI][RESOLUTIONJ]; // Output surface points

// Function to generate knot vectors
void SplineKnots(int *knots, int numControlPoints, int splineOrder) {
    int n = numControlPoints + splineOrder;
    for (int i = 0; i <= n; i++) {
        if (i < splineOrder) {
            knots[i] = 0; // Start with repeated knots
        } else if (i <= numControlPoints) {
            knots[i] = i - splineOrder + 1; // Incrementally increase knots
        } else {
            knots[i] = numControlPoints - splineOrder + 2; // End with repeated knots
        }
    }
}

// Function to compute the blending function
double SplineBlend(int controlPointIndex, int splineOrder, int *knots, double parameter) {
    double blendValue = 0.0;
    double temp1, temp2;

    // Base case: order 1
    if (splineOrder == 1) {
        if (knots[controlPointIndex] <= parameter && parameter < knots[controlPointIndex + 1]) {
            blendValue = 1.0;
        } else {
            blendValue = 0.0;
        }
    }
    // Recursive case: higher order
    else {
        // Avoid division by zero
        if (knots[controlPointIndex + splineOrder - 1] - knots[controlPointIndex] != 0) {
            temp1 = (parameter - knots[controlPointIndex]) /
                    (knots[controlPointIndex + splineOrder - 1] - knots[controlPointIndex]);
            temp1 *= SplineBlend(controlPointIndex, splineOrder - 1, knots, parameter);
        } else {
            temp1 = 0.0;
        }

        // Avoid division by zero
        if (knots[controlPointIndex + splineOrder] - knots[controlPointIndex + 1] != 0) {
            temp2 = (knots[controlPointIndex + splineOrder] - parameter) /
                    (knots[controlPointIndex + splineOrder] - knots[controlPointIndex + 1]);
            temp2 *= SplineBlend(controlPointIndex + 1, splineOrder - 1, knots, parameter);
        } else {
            temp2 = 0.0;
        }

        blendValue = temp1 + temp2;
    }

    return blendValue;
}

// Main function
int main() {
    // Create a random surface
    srand(1111);
    for (int i = 0; i <= NI; i++) {
        for (int j = 0; j <= NJ; j++) {
            inp[i][j].x = i;
            inp[i][j].y = j;
            inp[i][j].z = (rand() % 10000) / 5000.0 - 1;
        }
    }

    // Calculate the knots
    SplineKnots(knotsI, NI, TI);
    SplineKnots(knotsJ, NJ, TJ);

    // Step size along the curve
    double incrementI = (NI - TI + 2) / ((double)RESOLUTIONI - 1);
    double incrementJ = (NJ - TJ + 2) / ((double)RESOLUTIONJ - 1);

    // Compute the spline surface
    double intervalI = 0;
    for (int i = 0; i < RESOLUTIONI - 1; i++) {
        double intervalJ = 0;
        for (int j = 0; j < RESOLUTIONJ - 1; j++) {
            outp[i][j].x = 0;
            outp[i][j].y = 0;
            outp[i][j].z = 0;
            for (int ki = 0; ki <= NI; ki++) {
                for (int kj = 0; kj <= NJ; kj++) {
                    double bi = SplineBlend(ki, TI, knotsI, intervalI);
                    double bj = SplineBlend(kj, TJ, knotsJ, intervalJ);
                    outp[i][j].x += (inp[ki][kj].x * bi * bj);
                    outp[i][j].y += (inp[ki][kj].y * bi * bj);
                    outp[i][j].z += (inp[ki][kj].z * bi * bj);
                }
            }
            intervalJ += incrementJ;
        }
        intervalI += incrementI;
    }

    // Display the surface in OOGL format
    std::cout << "LIST\n";
    std::cout << "{ = CQUAD\n";
    for (int i = 0; i < RESOLUTIONI - 1; i++) {
        for (int j = 0; j < RESOLUTIONJ - 1; j++) {
            std::cout << outp[i][j].x << " " << outp[i][j].y << " " << outp[i][j].z << " 1 1 1 1\n";
            std::cout << outp[i][j + 1].x << " " << outp[i][j + 1].y << " " << outp[i][j + 1].z << " 1 1 1 1\n";
            std::cout << outp[i + 1][j + 1].x << " " << outp[i + 1][j + 1].y << " " << outp[i + 1][j + 1].z << " 1 1 1 1\n";
            std::cout << outp[i + 1][j].x << " " << outp[i + 1][j].y << " " << outp[i + 1][j].z << " 1 1 1 1\n";
        }
    }
    std::cout << "}\n";

    return 0;
}