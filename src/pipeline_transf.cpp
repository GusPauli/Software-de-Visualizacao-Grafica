#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>

class matrix {
    private:
        std::array<float, 16> data;
    public:
        matrix(){
            setIdentity();
        }
        matrix(std::initializer_list<float> list){
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
        matrix operator*(const matrix other) const{
            matrix result;
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

        //matriz de translação
        static matrix translation(float x, float y, float z){
            matrix mat;
            mat(0,3) = x;
            mat(1,3) = y;
            mat(2,3) = z;
            return mat;
        }
        
        //matriz de escala
        static matrix scale(float x){
            matrix mat;
            mat(0,0) = x;
            mat(1,1) = x;
            mat(2,2) = x;
            return mat;
        }

        //matriz de rotação em X
        static matrix rotationX(float angle){
            matrix mat;
            float cosA= std::cos(angle);
            float sinA= std::sin(angle);
            mat(1,1) = cosA;
            mat(1,2) = -sinA;
            mat(2,1) = sinA;
            mat(2,2) = cosA;
            return mat;
        }

        //matriz de rotação em y
        static matrix rotationY(float angle){
            matrix mat;
            float cosA= std::cos(angle);
            float sinA= std::sin(angle);
            mat(0,0) = cosA;
            mat(0,2) = sinA;
            mat(2,0) = -sinA;
            mat(2,2) = cosA;
            return mat;
        }

        //matriz de rotação em z
        static matrix rotationZ(float angle){
            matrix mat;
            float cosA= std::cos(angle);
            float sinA= std::sin(angle);
            mat(0,0) = cosA;
            mat(0,1) = -sinA;
            mat(1,0) = sinA;
            mat(1,1) = cosA;
            return mat;
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