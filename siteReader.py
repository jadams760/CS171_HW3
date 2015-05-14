import CLI
import network
import resource

if __name__ == '__main__':
    inputFile = "config.txt"
    with open(inputFile, 'r') as f:
        siteID = int(f.readline().strip())
        site1 = f.readline().strip().split()
        site2 = f.readline().strip().split()
        site3 = f.readline().strip().split()
        site4 = f.readline().strip().split()
        site5 = f.readline().strip().split()
        log   = f.readline().strip().split()
        local = f.readline().strip().split()
    sites = [(1, site1[0], int(site1[1])), (2, site2[0], int(site2[1])), (3, site3[0], int(site3[1])), (4, site4[0], int(site4[1])), (5, site5[0], int(site5[1]))]
    if (siteID == 6):
        t = resource.Resource(int(local[1]), local[0])
        t.run()
    else:
        t = CLI.CLI(siteID,local[0],int(local[1]), sites, log[0], int(log[1]))
        t.start()

