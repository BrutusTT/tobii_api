import os.path as op

from tobii_api.manager import Manager
    

    
    
def main():    
    m = Manager(op.expanduser('~/software/datasets/tobii'))
    for name in m.getProjectNames():
        print (name)
    
        p = m.getProject( name)
        for rec_name in p.getRecordingNames():

            print ('\t' + rec_name)
            r = p.getRecording(rec_name)
            
            if r:
                print ('\t\t' + r.uid + '\t' + str(r.segments))
                for x in r.segments_data:
                    print (x)
                    
            
#     s = m.getProject('ijkrmxv').getRecording('gkngat5').segments_data[0]
#     s.loadData()
#     s.show()


if __name__ == '__main__':
    main()