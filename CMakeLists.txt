cmake_minimum_required(VERSION 3.10)
project(Trabalho_2_CG C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define o diretório onde está o ImGui
set(IMGUI_DIR ${CMAKE_CURRENT_SOURCE_DIR}/imgui/imgui)

# Lista os arquivos fonte do ImGui
set(IMGUI_SOURCES
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_demo.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/imconfig.h
    ${IMGUI_DIR}/imgui.h
    ${IMGUI_DIR}/imgui_internal.h
    ${IMGUI_DIR}/imstb_rectpack.h
    ${IMGUI_DIR}/imstb_textedit.h
    ${IMGUI_DIR}/imstb_truetype.h
)

# Adiciona os backends específicos (exemplo para GLFW + OpenGL3)
set(IMGUI_BACKENDS
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.h
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.h
)

# Adiciona os diretórios de include
include_directories(${IMGUI_DIR} ${IMGUI_DIR}/backends)

# Encontra as dependências (exemplo: GLFW e OpenGL)
set(OpenGL_GL_PREFERENCE GLVND)
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)

# Define o executável do seu projeto
add_executable(${PROJECT_NAME} 
    src/teste.cpp
    ${IMGUI_SOURCES}
    ${IMGUI_BACKENDS}
)

# Vincula as bibliotecas necessárias
target_link_libraries(${PROJECT_NAME} OpenGL::GL glfw)