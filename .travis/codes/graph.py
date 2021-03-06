import os
import sys
import subprocess
import mdi
from graphviz import Digraph

def format_return(input_string):
    my_string = input_string.decode('utf-8')

    # remove any \r special characters, which sometimes are added on Windows
    my_string = my_string.replace('\r','')

    return my_string

def test_nodes():
    port_num = 9001
    mdi_driver_options = "-role DRIVER -name driver -method TCP -port " + str(port_num)

    # Get the number of nodes
    #driver_proc = subprocess.Popen([sys.executable, "min_driver.py", "-command", "<NNODES", 
    #                                "-nreceive", "1", "-rtype", "MDI_INT", 
    #                                "-mdi", mdi_driver_options],
    #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./drivers")

    # Run LAMMPS as an engine
    mdi_engine_options = "-role ENGINE -name TESTCODE -method TCP -hostname localhost -port " + str(port_num)
    working_dir = "../../user/mdi_tests/test1"
    user_path = os.environ['USER_PATH']
    os.system("rm -rf ./_work")
    os.system("cp -r " + str(working_dir) + " _work")
    engine_path = str(user_path) + "/lammps/src/lmp_mdi"
    engine_proc = subprocess.Popen([engine_path, 
                                    "-mdi", mdi_engine_options, 
                                    "-in", "lammps.in"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    cwd="./_work")

    # Convert the driver's output into a string
    #driver_tup = driver_proc.communicate()
    #driver_out = format_return(driver_tup[0])
    #driver_err = format_return(driver_tup[1])

    #print("CHECK_MDI_NODES.PY")
    #print("   Driver out: " + str(driver_out))
    #print("   Driver err: " + str(driver_err))
    
    mdi.MDI_Init(mdi_driver_options, None)
    comm = mdi.MDI_Accept_Communicator()
    nnodes = mdi.MDI_Get_NNodes(comm)
    print("NNodes: " + str(nnodes))
    nodes = [ mdi.MDI_Get_Node(inode, comm) for inode in range(nnodes) ]
    print("Nodes: " + str(nodes))
    for node in nodes:
        ncommands = mdi.MDI_Get_NCommands(node, comm)
        commands = [ mdi.MDI_Get_Command(node, icommand, comm) for icommand in range(ncommands) ]
        print("Commands: " + str(commands))
    mdi.MDI_Send_Command("EXIT", comm)

    engine_tup = engine_proc.communicate()
    engine_out = format_return(engine_tup[0])
    engine_err = format_return(engine_tup[1])
    #print("   Engine out: " + str(engine_out))
    #print("   Engine err: " + str(engine_err))



test_nodes()

dot = Digraph(comment='Node Report', format='svg')

dot.node('@DEFAULT', '@DEFAULT')
dot.node('@INIT_MD', '@INIT_MD')
dot.node('@INIT_OPTG', '@INIT_OPTG')
dot.node('@INIT_MC', '@INIT_MC')
dot.node('@INIT_MD_', '@PRE-FORCES\n@FORCES\n@COORDS')
dot.node('@INIT_OPTG_', '@PRE-FORCES\n@FORCES\n@COORDS')

dot.edge('@DEFAULT', '@INIT_MD')
dot.edge('@DEFAULT', '@INIT_OPTG')
dot.edge('@DEFAULT', '@INIT_MC')
dot.edge('@INIT_MD', '@INIT_MD_')
dot.edge('@INIT_OPTG', '@INIT_OPTG_')

dot.render('../graphs/node-report.gv')
