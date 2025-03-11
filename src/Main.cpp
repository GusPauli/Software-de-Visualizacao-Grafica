//compile command: g++ Main.cpp glad.c -ldl -lglfw

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include <iostream>

#include <pipeline_tela.cpp>
#include <pipeline_transf.cpp>


void framebuffer_size_callback(GLFWwindow* window, int width, int height);
void processInput(GLFWwindow *window);


int main(){

    //inicializa window
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    //glfwWindowHint(GLFW_OPENGL_FOWARD_COMPAT, GL_TRUE);

    //cria window object
    GLFWwindow* window = glfwCreateWindow(800,600, "LearnOpenGL", NULL, NULL);
    if (window==NULL){
        std::cout << "Failed to create GLFW window" << std::endl; 
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    //carrega as funções do OpenGL
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)){
        std::cout << "Failed to initialize GLAD" << std::endl;
        return -1;
    }
    
    glViewport(0,0,800,600);

    while (!glfwWindowShouldClose(window))
    {
        //input
        processInput(window);

        //rendering comands
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        //check and call events and swap buffes
        glfwPollEvents();
        glfwSwapBuffers(window);
    }

    glfwTerminate();
    return 0;
}

void framebuffer_size_callback(GLFWwindow* window, int width, int height){
    glViewport(0,0,width,height);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
}

void processInput(GLFWwindow *window){
    if(glfwGetKey(window, GLFW_KEY_ESCAPE)==GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);
}