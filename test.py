from distutils.ccompiler import new_compiler

if __name__ == '__main__':
    compiler = new_compiler()

    print(compiler.compile(['main.cpp']))
    compiler.link_executable(['main.obj'], 'main')
