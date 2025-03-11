#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>
#include <vector>

#include "main.h"

class mat4x4{
    private:
        std::array<float, 16> data;
    public:
        mat4x4(){
            setIdentity();
        }
        mat4x4(std::initializer_list<float> list){
            if (list.size() == 16){
                std::copy(list.begin(), list.end(), data.begin());
            }
            else{
                setIdentity();
            }
        }

        void setIdentity(){
            data = {
                1.0f, 0.0f, 0.0f, 0.0f,
                0.0f, 1.0f, 0.0f, 0.0f,
                0.0f, 0.0f, 1.0f, 0.0f,
                0.0f, 0.0f, 0.0f, 1.0f
            };
        }

        float& operator()(int row, int col){
            return data[row * 4 + col];
        }
        
        const float& operator()(int row, int col) const{
            return data[row * 4 + col];
        }

        //multiplicação de matriz
        mat4x4 operator*(const mat4x4 other) const{
            mat4x4 result;
            for(int row=0; row < 4; row++){
                for(int col=0; col <4; col++){
                    result(row,col)=
                    (*this)(row,0) * other(0, col)+
                    (*this)(row,1) * other(1, col)+
                    (*this)(row,2) * other(2, col)+
                    (*this)(row,3) * other(3, col);
                }
            }
            return result;
        }

        // Multiplica um ponto (x, y, z, h) pela matriz
        std::array<float, 4> multiplyPoint(const std::array<float, 4>& point) const {
            std::array<float, 4> result = {0.0f, 0.0f, 0.0f, 0.0f};
            for (int row = 0; row < 4; row++) {
                result[row] = (*this)(row, 0) * point[0] +
                              (*this)(row, 1) * point[1] +
                              (*this)(row, 2) * point[2] +
                              (*this)(row, 3) * point[3];
            }
            return result;
        }

//--------------------------------MATRIZES DE VISUALIZACAO--------------------------------------------------

        // Multiplica um array de pontos pela matriz
        std::vector<std::array<float, 4>> multiplyPoints(const std::vector<std::array<float, 4>>& points) const {
            std::vector<std::array<float, 4>> result;
            for (const auto& point : points) {
                result.push_back(multiplyPoint(point)); // Corrigido: chamada correta de multiplyPoint
            }
            return result;
        }
        
        static mat4x4 SRU_SRC(const float* vrp, const float* p, const float* view_up){
            
            //calcula o n = VRP - P 
            float N[3]={
                vrp[0] - p[0],
                vrp[1] - p[1],
                vrp[2] - p[2]
            };
            float modulo = std::sqrt(
                N[0]*N[0] +
                N[1]*N[1] +
                N[2]*N[2]
            );

            N[0] /= modulo;
            N[1] /= modulo;
            N[2] /= modulo;

            //calcula o V = Y - (Y*n)*n
            float aux = view_up[0] * N[0] + 
                        view_up[1] * N[1] + 
                        view_up[2] * N[2]; 
            
            float V[3]= {
                view_up[0] - N[0]*aux,
                view_up[1] - N[1]*aux,
                view_up[2] - N[2]*aux
            };
            modulo = std::sqrt(
                V[0]*V[0] +
                V[1]*V[1] +
                V[2]*V[2]
            );

            V[0] /= modulo;
            V[1] /= modulo;
            V[2] /= modulo;

            //calcula vetor U = VxN
            float U[3];
            U[0]=V[1]*N[2] - V[2]*N[1];
            U[1]=V[2]*N[0] - V[0]*N[2];
            U[2]=V[0]*N[1] - V[1]*N[0];


            mat4x4 mat;
            //preenche a matriz com os vetores
            mat(0,0) = U[0];
            mat(0,1) = U[1];
            mat(0,2) = U[2];
            mat(0,3) = -(vrp[0]*U[0] + vrp[1]*U[1] + vrp[2]*U[2]);

            mat(1,0) = V[0];
            mat(1,1) = V[1];
            mat(1,2) = V[2];
            mat(1,3) = -(vrp[0]*V[0] + vrp[1]*V[1] + vrp[2]*V[2]);

            mat(2,0) = N[0];
            mat(2,1) = N[1];
            mat(2,2) = N[2];
            mat(2,3) = -(vrp[0]*N[0] + vrp[1]*N[1] + vrp[2]*N[2]);

            return mat;
        }

        //projeção axonométrica isometrica
        static mat4x4 projecao(){
            mat4x4 isometrica;

            return isometrica;
        }

        static mat4x4 janela_portavisao(float xmin, float xmax, float ymin, float ymax, float umin, float umax, float vmin, float vmax){
            mat4x4 mjp;

            mjp(0,0) = (umax - umin)/(xmax-xmin);
            mjp(1,1) = (vmin - vmax)/(ymax-ymin);
            mjp(0,3) = -xmin*((umax - umin)/(xmax-xmin))-umin;
            mjp(1,3) = ymin*((vmax - vmin)/(ymax-ymin))+vmax;
            mjp(2,2) = 1.0f; mjp(3,3) = 1.0f;

            return mjp;
        }

        //função que faz a tranformação SRU->SRT
        static std::vector<std::vector<XYZ>> pipeline(const std::vector<std::vector<XYZ>>& points, const float* vrp, const float* p, const float* view_up, int xmin, int xmax, int ymin, int ymax, int umin, int umax, int vmin, int vmax){
            //calcula matrizes para o pipeline
            mat4x4 sru_src = SRU_SRC(vrp, p, view_up);
            mat4x4 proj = projecao();
            mat4x4 mjp = janela_portavisao(xmin, xmax, ymin, ymax, umin, umax, vmin, vmax);

            mat4x4 mcomp = mjp * proj * sru_src;
            
            //aplica a matriz composta aos pontos
            std::vector<std::vector<XYZ>> transformedpoints = points;
            for(auto& row : transformedpoints){
                for(auto& point: row){
                    std::array<float, 4> homogpoint = {point.x, point.y, point.z, 1.0f};
                    std::array<float, 4> transformedpoint = mcomp.multiplyPoint(homogpoint);
                    point = {transformedpoint[0], transformedpoint[1], transformedpoint[2]};
                    // Imprime o ponto transformado
                    std::cout << "Ponto transformado: (" 
                            << std::fixed << std::setprecision(3) 
                            << point.x << ", " << point.y << ", " << point.z << ")\n";
                }
            }
            return transformedpoints;
        }

        //printa matriz, para teste
        void print() const{
            for(int row=0; row <4; row++){
                for(int col=0; col<4;col++){
                    std::cout << std::fixed << std::setprecision(3)
                              << (*this)(row,col) <<"\t"; 
                }
                std::cout << std::endl;
            }
        }
};

/*int main() {
    // Exemplo de uso
    float vrp[3] = {25.0f, 15.0f, 80.0f};
    float p[3] = {20.0f, 10.0f, 25.0f};
    float view_up[3] = {0.0f, 1.0f, 0.0f};

    //mat4x4 result = mat4x4::pipeline(vrp, p, view_up, -8, 8, -6, 6, 0, 319, 0, 239);
    mat4x4 iso = mat4x4::projecao();
    mat4x4 sru = mat4x4::SRU_SRC(vrp, p, view_up);
    mat4x4 jp = mat4x4::janela_portavisao(-8, 8, -6, 6, 0, 319, 0, 239);
    //result.print();

    return 0;
}*/