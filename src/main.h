#ifndef MAIN_H
#define MAIN_H

class Camera{
public:
    float vrp[3] = {5, 5, 5};
    float p[3] = {0, 0, 0};
    float view_up[3] = {0, 1, 0};
};

class fonte_luz{
   int pos[3]={300, 300, 1200};
   int ila[3]={60, 40, 50};
   int il[3]={200, 200, 210};
   float ka[3]={0.3f, 0.6f, 0.4f};
   float kd[3]={0.3f, 0.6f, 0.8f};
   float ks[3]={0.3f, 0.6f, 0.8f};
   int n = 3;
};

// Estrutura para pontos 3D
class XYZ {
public:
    float x, y, z;
        
    XYZ() : x(0), y(0), z(0) {}
    XYZ(float x, float y, float z) : x(x), y(y), z(z) {}
};

#endif // MAIN_H