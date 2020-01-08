from .config import Config
from datetime import datetime
import subprocess, os, sys, shutil


def executelig(LogFileName, CommandsFileName, username, filename, itpname, groname, mol):
    LogFile = create_log(LogFileName, username) #cria o arquivo log

    #transferir os arquivos mdp necessarios para a execução
    RunFolder = Config.UPLOAD_FOLDER + username + '/' + filename + '/run/' #pasta q vai rodar
    SecureMdpFolder = os.path.join(os.path.expanduser('~'),Config.MDP_LOCATION_FOLDER)
    MDPList = os.listdir(SecureMdpFolder)

    for mdpfile in MDPList:
        #armazenar o nome completo do arquivo, seu caminho dentro sistema operacional
        fullmdpname = os.path.join(SecureMdpFolder, mdpfile)
        if (os.path.isfile(fullmdpname)):
            shutil.copy(fullmdpname, RunFolder)
    
    #abrir arquivo
    with open(CommandsFileName) as f: #CODIGO PARA A PRODUÇÃO
        content = f.readlines()
    lines = [line.rstrip('\n') for line in content if line is not '\n'] #cancela as linhas em branco do arquivo

    for l in lines:
        if l[0] == '#':
            WriteUserDynamics(l)

        else:
            #estabelecer o diretorio de trabalho
            os.chdir(RunFolder)

            process = subprocess.run(l, shell=True, stdin=LogFile, stdout=LogFile, stderr=LogFile)

            try:
                process.check_returncode()
            except subprocess.CalledProcessError as e:
                    LogFile.close()
                    os.remove(Config.UPLOAD_FOLDER+'executing')
                    os.remove(Config.UPLOAD_FOLDER+username+'/DirectoryLog')
                    return (e.args)
        
        #breakpoint adicionado para possibilitar a interação com os arquivos em tempo de execução
        if l == '#break': 
            #cria o novo arquivo com a molecula complexada
            #pronto 
            diretorio_ltop = RunFolder + mol +'_livre.top'
            diretorio_complx_top = RunFolder + mol +'_complx.top'
            file_ltop =  open(diretorio_ltop,'r')
            file_ltop = file_ltop.read()
            file_complx_top = open(diretorio_complx_top,'w')
            file_complx_top.writelines(file_ltop)

            #cria o novo arquivo com a molecula complexada
            #pronto
            file_complx_top = open(diretorio_complx_top,'r')
            file_complx_top = file_complx_top.readlines()
            for i, text in enumerate(file_complx_top):
                if text.find('system') > -1:
                    file = open(diretorio_complx_top,'w')
                    file_complx_top[i-5] = '\n; Include ligand topology\n'+'#include'+' '+'"'+itpname+'"'+"\n"
                    file.writelines(file_complx_top)
                    file.close()
            
            #acessando arquivo .itp para pegar o moleculetype
            #pronto
            diretorio_itp = RunFolder + itpname
            file = open(diretorio_itp,'r')
            file_itp = file.readlines()         
            for i, text in enumerate(file_itp):
                if text.find('moleculetype') > -1:
                    valor = file_itp[i+2]
                    #acessando o arquivo _complx.top para incluir os dados
                    file_complx_top = open(diretorio_complx_top,'r')
                    file_complx_top = file_complx_top.readlines()
                    file_complx_top.append(valor)
                    #acessa para salvar a alteração
                    file = open(diretorio_complx_top,'w')
                    file.writelines(file_complx_top)
                    file.close()
             
            #modificando o arquivo .gro
            #pronto
            diretorio_gro = RunFolder + groname
            file = open(diretorio_gro,'r')
            file_gro = file.readlines()
            valor_gro = file_gro[1]
            valor_gro = int(valor_gro)
            file_gro.pop()
            file_gro.pop(0)

            #copiando as coordenadas dos atomos
            diretorio_lgro = RunFolder + mol +'_livre.gro'
            diretorio_complx_gro =  RunFolder + mol +'_complx.gro'
            file_complx_gro = open(diretorio_complx_gro,'w')
            file_lgro = open(diretorio_lgro,'r')
            file_lgro = file_lgro.readlines()
            i = len(file_lgro)-1
            last_line = file_lgro[i]
            file_lgro.pop()
            file_complx_gro.writelines(file_lgro)
            file_gro.pop(0)
            file_gro.append(last_line)
            file_complx_gro.writelines(file_gro)
            file_complx_gro.close()            
            
            #somando a quantidade de atomos da enzima
            #pronto
            file_complx_gro = open(diretorio_complx_gro,'r')
            file_complx_gro = file_complx_gro.readlines()
            valor_complx_gro = file_complx_gro[1]
            valor_complx_gro = int(valor_complx_gro)
            total = valor_gro + valor_complx_gro
            total = str(total)
            file_complx_gro[1] = ' '+total+'\n'
            file = open(diretorio_complx_gro,'w')
            file.writelines(file_complx_gro)
            file.close()

    LogFile.close()
    os.remove(Config.UPLOAD_FOLDER+'executing')
    os.remove(Config.UPLOAD_FOLDER+username+'/DirectoryLog')


def create_log(LogFileName, username):
    #formatando nome do arquivo log
    LogFileName = LogFileName+"-{}-{}-{}[{}:{}:{}]{}".format(datetime.now().year,
                                                            datetime.now().month,
                                                            datetime.now().day,
                                                            datetime.now().hour,
                                                            datetime.now().minute,
                                                            datetime.now().second,
                                                            '.log.txt')
        
    LogFile = open(LogFileName, "w+")
    f = open(Config.UPLOAD_FOLDER+username+'/DirectoryLog', 'w')
    f.write(LogFileName)
    return LogFile


def WriteUserDynamics(line):
    filename = Config.UPLOAD_FOLDER + 'executing'
    try:
        f = open(filename,'a')
        f.write(line + '\n')
        f.close()
    except OSError:
        print('erro ao adicionar linha no arquivo de dinamica-usuario')
        raise