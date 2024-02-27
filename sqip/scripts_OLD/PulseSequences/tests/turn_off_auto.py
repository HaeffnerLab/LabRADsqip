

def main():
    import labrad
    cxn = labrad.connect()
    cxn.pulser.switch_auto('adv',False)
    cxn.pulser.switch_auto('rst',False)
    cxn.pulser.switch_manual('adv',True)
    cxn.pulser.switch_manual('adv',False)
    
    
if __name__ == '__main__':
        main()