#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>

class mat4x4 {
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
            U[0]=V[1]*N[2] - V[2]-N[1];
            U[1]=V[2]*N[0] - V[0]-N[2];
            U[2]=V[0]*N[1] - V[1]-N[0];


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

        static mat4x4 janela_portavisao(int xmin, int xmax, int ymin, int ymax, int umin, int umax, int vmin, int vmax){
            mat4x4 mjp;

            mjp(0,0) = (umax - umin)/(xmax-xmin);
            mjp(1,1) = (vmin - vmax)/(ymax-ymin);
            mjp(0,3) = -xmin*((umax - umin)/(xmax-xmin))-umin;
            mjp(1,3) = ymin*((vmax - vmin)/(ymax-ymin))+vmax;
            mjp(2,2) = 1.0f; mjp(3,3) = 1.0f;

            return mjp;
        }

        static mat4x4 pipeline(const float* vrp, const float* p, const float* view_up, int xmin, int xmax, int ymin, int ymax, int umin, int umax, int vmin, int vmax){
            mat4x4 sru_src = SRU_SRC(vrp, p, view_up);
            mat4x4 proj = projecao();
            mat4x4 mjp = janela_portavisao(xmin, xmax, ymin, ymax, umin, umax, vmin, vmax);
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