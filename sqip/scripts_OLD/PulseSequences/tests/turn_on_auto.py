

def main():
    import labrad
    cxn = labrad.connect()
    cxn.dac_server.reset_queue()
    cxn.pulser.switch_auto('adv',True)
    cxn.pulser.switch_auto('rst',True)
    
    
    
if __name__ == '__main__':
        main()