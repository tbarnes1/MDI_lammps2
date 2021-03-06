import os
import subprocess
import sys
import yaml

def format_return(input_string):
    my_string = input_string.decode('utf-8')

    # remove any \r special characters, which sometimes are added on Windows
    my_string = my_string.replace('\r','')

    return my_string

def insert_list( original_list, insert_list, pos ):
    for ielement in range(len(insert_list)):
        element = insert_list[ielement]
        original_list.insert( pos + ielement + 1, element )

n_tested_commands = 0
def test_command( command, nrecv, recv_type, nsend, send_type ):
    global n_tested_commands

    port_num = 8050 + n_tested_commands
    mdi_driver_options = "-role DRIVER -name driver -method TCP -port " + str(port_num)
    print("   Driver Options: " + str(command) + " " + str(nrecv) + " " + str(recv_type) + " " + str(nsend) + " " + str(send_type))
    if nrecv is not None and nsend is not None:
       driver_proc = subprocess.Popen([sys.executable, "min_driver.py", "-command", command, 
                                        "-nreceive", str(nrecv), "-rtype", str(recv_type), 
                                        "-nsend", str(nsend), "-stype", str(send_type), 
                                        "-mdi", mdi_driver_options],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./drivers")
    elif nrecv is not None:
        driver_proc = subprocess.Popen([sys.executable, "min_driver.py", "-command", command, 
                                        "-nreceive", str(nrecv), "-rtype", str(recv_type), 
                                        "-mdi", mdi_driver_options],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./drivers")
    elif nsend is not None:
        driver_proc = subprocess.Popen([sys.executable, "min_driver.py", "-command", command, 
                                        "-nsend", str(nsend), "-stype", str(send_type), 
                                        "-mdi", mdi_driver_options],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./drivers")
    else:
        driver_proc = subprocess.Popen([sys.executable, "min_driver.py", "-command", command, 
                                        "-mdi", mdi_driver_options],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="./drivers")
    
    # Run LAMMPS as an engine
    mdi_engine_options = "-role ENGINE -name TESTCODE -method TCP -hostname localhost -port " + str(port_num)
    working_dir = "../../user/mdi_tests/test1"
    os.system("rm -rf ./_work")
    os.system("cp -r " + str(working_dir) + " _work")
    os.chdir("./_work")
    os.system("${USER_PATH}/lammps/src/lmp_mdi -mdi \"" + str(mdi_engine_options) + "\" -in lammps.in > lammps.out")
    os.chdir("../")

    # Convert the driver's output into a string
    driver_tup = driver_proc.communicate()
    driver_out = format_return(driver_tup[0])
    driver_err = format_return(driver_tup[1])
    
    print("   Driver out: " + str(driver_out))
    print("   Driver err: " + str(driver_err))

    if driver_err == "":
        return True
    else:
        return False

def write_supported_commands():
    # List of all commands in the MDI Standard
    command_list = []
    commands = None
    
    with open(r'../mdi_standard.yaml') as standard_file:
        standard = yaml.load(standard_file, Loader=yaml.FullLoader)
        commands = standard['commands']
    
        for command in commands.keys():
            values = commands[command]
            command_list.append( command )

    # Write the README.md section that lists all supported commands
    command_sec = []

    # Write the section header
    command_sec.append( "## Supported Commands\n" )
    command_sec.append( "\n" )
    command_sec.append( "| | @DEFAULT |\n" )
    command_sec.append( "| ------------- | ------------- |\n" )

    # Write the list of supported commands
    for command in command_list:
        nrecv = None
        recv_type = None
        nsend = None
        send_type = None
        print("---------------------------------------")
        print("Testing command: " + str(command))
        if commands[command] is not None and 'recv' in commands[command].keys():
            nrecv = commands[command]['recv']['count']
            recv_type = commands[command]['recv']['datatype']
        if commands[command] is not None and 'send' in commands[command].keys():
            nsend = commands[command]['send']['count']
            send_type = commands[command]['send']['datatype']
        command_works = test_command( command, nrecv, recv_type, nsend, send_type )
        if command_works:
            # Display a bright green box
            command_status = "![command](.travis/badges/box-brightgreen.svg)"
        else:
            # Display a light gray box
            command_status = "![command](.travis/badges/box-lightgray.svg)"
        line = "| " + str(command) + " | " + str(command_status) + "  |\n"
        command_sec.append( line )

    # Replace all ">" or "<" symbols with Markdown escape sequences
    for iline in range(len(command_sec)):
        line = command_sec[iline]
        line = line.replace(">", "&gt;")
        line = line.replace("<", "&lt;")
        command_sec[iline] = line
    
    return command_sec
    
# Read the README.md file
with open(r'../README.base') as file:
    readme = file.readlines()

# Check the README.md file for any comments for travis
for iline in range(len(readme)):
    line = readme[iline]
    sline = line.split()
    if len(sline) > 0 and sline[0] == '[travis]:':
        instruction = sline[3]

        if instruction == "supported_commands":
            # Need to insert a list of supported commands here
            command_sec = write_supported_commands()
            insert_list( readme, command_sec, iline )

# Write the updates to the README file
with open('./README.temp', 'w') as file:
    file.writelines( readme )
