#include <GLFW/glfw3.h>
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <stdio.h>
#include <iostream>
#include <float.h>

#include "main.h"

#include "pipeline_transf.cpp"
#include "pipeline_tela.cpp"
#include "spline_Surface.cpp"

// Função para tratamento de erros do GLFW
void error_callback(int error, const char* description) {
    fprintf(stderr, "Erro GLFW %d: %s\n", error, description);
}

// Função para renderizar a superfície
void renderSurface(const SplineSurface& surface) {
    glBegin(GL_POINTS);
    for (const auto& row : surface.outp) {
        for (const auto& point : row) {
            glVertex3f(point.x, point.y, point.z);
        }
    }
    glEnd();
}

// Função para renderização
void render(
    const std::vector<std::vector<XYZ>>& new_inp,  // Pontos de controle transformados
    const std::vector<std::vector<XYZ>>& new_outp, // Pontos da malha transformados
    const ImVec4& clear_color                      // Cor de fundo
) {
    // Limpa o buffer de cor e profundidade
    glClearColor(clear_color.x, clear_color.y, clear_color.z, clear_color.w);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // Configura a matriz de projeção e modelo
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    // Calcula o intervalo dos pontos para ajustar a projeção
    float minX = std::numeric_limits<float>::max();
    float maxX = std::numeric_limits<float>::min();
    float minY = std::numeric_limits<float>::max();
    float maxY = std::numeric_limits<float>::min();

    for (const auto& row : new_outp) {
        for (const auto& point : row) {
            if (point.x < minX) minX = point.x;
            if (point.x > maxX) maxX = point.x;
            if (point.y < minY) minY = point.y;
            if (point.y > maxY) maxY = point.y;
        }
    }

    glOrtho(minX, maxX, minY, maxY, -1.0, 1.0); // Projeção ortográfica ajustada

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // Desenha os pontos de controle (new_inp)
    glPointSize(5.0f); // Tamanho dos pontos
    glColor3f(1.0f, 0.0f, 0.0f); // Cor dos pontos (vermelho)
    glBegin(GL_POINTS);
    for (const auto& row : new_inp) {
        for (const auto& point : row) {
            glVertex3f(point.x, point.y, point.z);
        }
    }
    glEnd();

    // Desenha os pontos da malha (new_outp)
    glPointSize(3.0f); // Tamanho dos pontos
    glColor3f(0.0f, 0.0f, 1.0f); // Cor dos pontos (azul)
    glBegin(GL_POINTS);
    for (const auto& row : new_outp) {
        for (const auto& point : row) {
            glVertex3f(point.x, point.y, point.z);
        }
    }
    glEnd();

    // Desenha as arestas da malha (new_outp)
    glColor3f(0.0f, 1.0f, 0.0f); // Cor das arestas (verde)
    glBegin(GL_LINES);
    for (int i = 0; i < new_outp.size(); i++) {
        for (int j = 0; j < new_outp[i].size(); j++) {
            // Arestas horizontais (conecta pontos na mesma linha)
            if (j < new_outp[i].size() - 1) {
                glVertex3f(new_outp[i][j].x, new_outp[i][j].y, new_outp[i][j].z);
                glVertex3f(new_outp[i][j + 1].x, new_outp[i][j + 1].y, new_outp[i][j + 1].z);
            }

            // Arestas verticais (conecta pontos na mesma coluna)
            if (i < new_outp.size() - 1 && j < new_outp[i + 1].size()) {
                glVertex3f(new_outp[i][j].x, new_outp[i][j].y, new_outp[i][j].z);
                glVertex3f(new_outp[i + 1][j].x, new_outp[i + 1][j].y, new_outp[i + 1][j].z);
            }
        }
    }
    glEnd();
}

void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    glViewport(0, 0, width, height);
    // Atualize a matriz de projeção ou outros parâmetros de renderização aqui, se necessário
}

int main() {
    // Variáveis gerais
    int width = 800, height = 600;
    Camera camera;
    SplineSurface surface;

    // Inicializa GLFW
    if (!glfwInit()) {
        std::cerr << "Falha ao inicializar GLFW" << std::endl;
        return -1;
    }
    glfwSetErrorCallback(error_callback);

    // Configura versão OpenGL e perfil
    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

    // Cria janela
    GLFWwindow* window = glfwCreateWindow(width, height, "Interface GLFW + ImGui", NULL, NULL);
    if (!window) {
        std::cerr << "Falha ao criar janela GLFW" << std::endl;
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1); // Habilita VSync

    // Inicializa ImGui
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard; // Habilita navegação por teclado

    // Configura estilo
    ImGui::StyleColorsDark();

    // Configura platform/renderer backends
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init(glsl_version);

    // Cores para limpar a tela
    ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);
    bool show_demo_window = false;
    bool show_another_window = false;

    // Configura o callback para redimensionamento da janela
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // Loop principal
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        // Inicia o frame do ImGui
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // Barra de menu principal
        if (ImGui::BeginMainMenuBar()) {
            if (ImGui::BeginMenu("Arquivo")) {
                if (ImGui::MenuItem("Novo", "Ctrl+N")) {}
                if (ImGui::MenuItem("Abrir", "Ctrl+O")) {}
                if (ImGui::MenuItem("Salvar", "Ctrl+S")) {}
                ImGui::Separator();
                if (ImGui::MenuItem("Sair", "Alt+F4")) {
                    glfwSetWindowShouldClose(window, true);
                }
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Editar")) {
                if (ImGui::MenuItem("Desfazer", "Ctrl+Z")) {}
                if (ImGui::MenuItem("Refazer", "Ctrl+Y")) {}
                ImGui::Separator();
                if (ImGui::MenuItem("Recortar", "Ctrl+X")) {}
                if (ImGui::MenuItem("Copiar", "Ctrl+C")) {}
                if (ImGui::MenuItem("Colar", "Ctrl+V")) {}
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Visualizar")) {
                ImGui::MenuItem("Demo ImGui", NULL, &show_demo_window);
                ImGui::MenuItem("Janela Exemplo", NULL, &show_another_window);
                ImGui::EndMenu();
            }

            if (ImGui::BeginMenu("Ajuda")) {
                if (ImGui::MenuItem("Sobre")) {}
                ImGui::EndMenu();
            }

            ImGui::EndMainMenuBar();
        }

        // Janela principal
        {
            ImGui::Begin("Configuração da Malha"); 
            if (ImGui::CollapsingHeader("Elementos da Malha")) {
                static int ni = 4;
                static int nj = 4;
                static int ti = 1;
                static int tj = 1;
                static int resI = 10;
                static int resJ = 10;
                ImGui::InputInt("Pontos de controle I", &ni, 4, 100);
                ImGui::InputInt("Pontos de controle J", &nj, 4, 100);
                ImGui::InputInt("grau em I", &ti, 0, 10);
                ImGui::InputInt("grau em J", &tj, 0, 10);
                ImGui::InputInt("Linhas da malha", &resI, 2, 100);
                ImGui::InputInt("Colunas da malha", &resJ, 2, 100);

                ImGui::Separator();

                if (ImGui::Button("Aplicar")) {
                    surface.NI = ni;
                    surface.NJ = nj;
                    surface.TI = ti;
                    surface.TJ = tj;
                    surface.RESOLUTIONI = resI;
                    surface.RESOLUTIONJ = resJ;

                    //surface.generateSurface(); // Regenera a superfície
                    ImGui::Text("Valores aplicados com sucesso!");
                    ni = nj = ti = tj = resI = resJ = 0;
                }
            }
            ImGui::End();
        }

        std::vector<std::vector<XYZ>> new_inp = mat4x4::pipeline(surface.inp, camera.vrp, camera.p, camera.view_up, -width, width, -height, height, 0, width-1, 0, height-1);
        std::vector<std::vector<XYZ>> new_outp = mat4x4::pipeline(surface.outp, camera.vrp, camera.p, camera.view_up, -width, width, -height, height, 0, width-1, 0, height-1);
        
         // Limpa o buffer de cor e profundidade
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // Renderização
        ImGui::Render();
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        render(new_inp, new_outp, clear_color); // Renderiza a superfície
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
    }

    // Limpeza
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}