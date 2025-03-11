#include <iostream>
#include <vector>
#include <random>
#include <cmath>

#include "main.h"


class SplineSurface {
public:
    int NI = 4;
    int NJ = 4;
    int TI = 3;
    int TJ = 3;
    int RESOLUTIONI = 4;
    int RESOLUTIONJ = 4;

    std::vector<std::vector<XYZ>> inp;
    std::vector<int> knotsI;
    std::vector<int> knotsJ;
    std::vector<std::vector<XYZ>> outp;

    // Calcula o vetor de nós uniforme
    void splineKnots(std::vector<int>& knots, int n, int t) {
        // Configura o vetor de nós
        for (int i = 0; i <= n + t; i++) {
            if (i < t)
                knots[i] = 0;
            else if (i <= n)
                knots[i] = i - t + 1;
            else
                knots[i] = n - t + 2;
        }
    }
    
    // Calcula o valor de blending para um ponto na spline
    double splineBlend(int k, int t, const std::vector<int>& knots, double v) {
        double result = 0.0;
        
        // Caso base para a recursão
        if (t == 1) {
            if ((knots[k] <= v) && (v < knots[k+1]))
                result = 1.0;
            else
                result = 0.0;
            return result;
        }
        
        // Trata situações onde divisão por zero pode ocorrer
        double d1 = knots[k+t-1] - knots[k];
        double d2 = knots[k+t] - knots[k+1];
        
        double val1 = 0.0, val2 = 0.0;
        
        if (d1 > 0.000001) // Evita divisão por zero
            val1 = ((v - knots[k]) / d1) * splineBlend(k, t-1, knots, v);
            
        if (d2 > 0.000001) // Evita divisão por zero
            val2 = ((knots[k+t] - v) / d2) * splineBlend(k+1, t-1, knots, v);
            
        result = val1 + val2;
        return result;
    }

    SplineSurface() : NI(4), NJ(4), TI(3), TJ(3), RESOLUTIONI(10), RESOLUTIONJ(10){
        // Inicializa as estruturas de dados
        inp.resize(NI + 1, std::vector<XYZ>(NJ + 1));
        knotsI.resize(NI + TI + 1);
        knotsJ.resize(NJ + TJ + 1);
        outp.resize(RESOLUTIONI, std::vector<XYZ>(RESOLUTIONJ));
    }
    
    void generateSurface() {
        // Cria uma superfície aleatória
        std::mt19937 rng(1111); // Gerador de números aleatórios moderno
        std::uniform_real_distribution<double> dist(-20.0, 20.0);
        
        for (int i = 0; i <= NI; i++) {
            for (int j = 0; j <= NJ; j++) {
                inp[i][j].x = i;
                inp[i][j].y = j;
                inp[i][j].z = (rng() % 10000) / 5000.0 - 1;
            }
        }
        
        // Tamanho do passo ao longo da curva
        double incrementI = (NI - TI + 2) / ((double)RESOLUTIONI - 1);
        double incrementJ = (NJ - TJ + 2) / ((double)RESOLUTIONJ - 1);
        
        // Calcula os nós
        splineKnots(knotsI, NI, TI);
        splineKnots(knotsJ, NJ, TJ);
        
        double intervalI = 0;
        double intervalJ = 0;
        for (int i = 0; i < RESOLUTIONI-1; i++) {
            for (int j = 0; j < RESOLUTIONJ-1; j++) {
                outp[i][j].x = 0;
                outp[i][j].y = 0;
                outp[i][j].z = 0;
                for (int ki = 0; ki <= NI; ki++) {
                    for (int kj = 0; kj <= NJ; kj++) {
                        double bi = splineBlend(ki, TI, knotsI, intervalI);
                        double bj = splineBlend(kj, TJ, knotsJ, intervalJ);
                        outp[i][j].x += (inp[ki][kj].x * bi * bj);
                        outp[i][j].y += (inp[ki][kj].y * bi * bj);
                        outp[i][j].z += (inp[ki][kj].z * bi * bj);
                    }
                }
                intervalJ += incrementJ;
            }
            intervalI += incrementI;
        }
        
        // Trata casos de borda
        intervalI = 0;
        for (int i = 0; i < RESOLUTIONI-1; i++) {
            outp[i][RESOLUTIONJ-1].x = 0;
            outp[i][RESOLUTIONJ-1].y = 0;
            outp[i][RESOLUTIONJ-1].z = 0;
            for (int ki = 0; ki <= NI; ki++) {
                double bi = splineBlend(ki, TI, knotsI, intervalI);
                outp[i][RESOLUTIONJ-1].x += (inp[ki][NJ].x * bi);
                outp[i][RESOLUTIONJ-1].y += (inp[ki][NJ].y * bi);
                outp[i][RESOLUTIONJ-1].z += (inp[ki][NJ].z * bi);
            }
            intervalI += incrementI;
        }
        outp[RESOLUTIONI-1][RESOLUTIONJ-1] = inp[NI][NJ];
        
        intervalJ = 0;
        for (int j = 0; j < RESOLUTIONJ-1; j++) {
            outp[RESOLUTIONI-1][j].x = 0;
            outp[RESOLUTIONI-1][j].y = 0;
            outp[RESOLUTIONI-1][j].z = 0;
            for (int kj = 0; kj <= NJ; kj++) {
                double bj = splineBlend(kj, TJ, knotsJ, intervalJ);
                outp[RESOLUTIONI-1][j].x += (inp[NI][kj].x * bj);
                outp[RESOLUTIONI-1][j].y += (inp[NI][kj].y * bj);
                outp[RESOLUTIONI-1][j].z += (inp[NI][kj].z * bj);
            }
            intervalJ += incrementJ;
        }
    }
    
    void outputSurface() const {
        std::cout << "LIST\n";
        
        // Mostra a superfície, neste caso em formato OOGL para GeomView
        std::cout << "{ = CQUAD\n";
        for (int i = 0; i < RESOLUTIONI-1; i++) {
            for (int j = 0; j < RESOLUTIONJ-1; j++) {
                std::cout << outp[i][j].x << " " << outp[i][j].y << " " << outp[i][j].z << " 1 1 1 1\n";
                std::cout << outp[i][j+1].x << " " << outp[i][j+1].y << " " << outp[i][j+1].z << " 1 1 1 1\n";
                std::cout << outp[i+1][j+1].x << " " << outp[i+1][j+1].y << " " << outp[i+1][j+1].z << " 1 1 1 1\n";
                std::cout << outp[i+1][j].x << " " << outp[i+1][j].y << " " << outp[i+1][j].z << " 1 1 1 1\n";
            }
        }
        std::cout << "}\n";
        
        // Polígono de pontos de controle
        for (int i = 0; i < NI; i++) {
            for (int j = 0; j < NJ; j++) {
                std::cout << "{ = SKEL 4 1  \n";
                std::cout << inp[i][j].x << " " << inp[i][j].y << " " << inp[i][j].z << " \n";
                std::cout << inp[i][j+1].x << " " << inp[i][j+1].y << " " << inp[i][j+1].z << " \n";
                std::cout << inp[i+1][j+1].x << " " << inp[i+1][j+1].y << " " << inp[i+1][j+1].z << " \n";
                std::cout << inp[i+1][j].x << " " << inp[i+1][j].y << " " << inp[i+1][j].z << " \n";
                std::cout << "5 0 1 2 3 0\n";
                std::cout << "}\n";
            }
        }
    }
};

/*int main() {
    SplineSurface surface;
    surface.generateSurface();
    surface.outputSurface();
    
    return 0;
}*/