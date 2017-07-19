from factory_connector import FactoryConnector


def main():

    # ########### parameters ###############################################
    # parameters chua cac thong tin nhu
    # device_type: loai thiet bi e.x: ios, junos
    # host: ip
    # protocol: ssh or telnet
    # username: account dang nhap
    # password: mat khau dang nhap


    #27.78.16.56:32771
    parameters = {
        'device_type': 'ios-xr', #or junos, ios, ios-xr 5395
        'host': '27.78.16.56',
        #'host':'27.78.16.56',
        'protocol': 'telnet',
        'username': 'longdn',
        #'password': '123456a@',
        'password': '123456',
        #'port': 32771, #ios
        'port': 32769, #xr
        #'port': 32776, #junos

    }

    ########################################################################

    # ########## commands ##################################################
    # chua mot array lenh
    # luu y: command phai phu hop voi moi loai thiet bi
    '''commands = [
        'config t',
        'hostname longhk',
        'commit'
    ]'''

    commands = [
        #'config terminal'
        'show process cpu'
        #'show configuration'
        #'set system host-name longhk123',
        #'commit'
    ]
    ########################################################################

    ############## lop adaptor ############################################
    # khoi tao truyen params voi **parameters(khai bao cac thong tin ket noi toi thiet bi),
    # tai sao phair **parameters ** de khong phai truyen tung thong tin trong param vao adapter
    fac = FactoryConnector(**parameters)

    # co 2 kieu dung excecute
    # #1 truyen 2 tham so
    #    - tham so mot la mang commands(lenh), tham so 2 la ghi ten filelog output tu thiet bi tra ra
    #fac.execute(commands, 'filelog.log')
    # #2 truyen 1 tham so
    # chi truyen param command, va output cua thiet bi se print len console
    fac.execute(commands)
    ########################################################################################


if __name__ == '__main__':
    print('running')
    main()
