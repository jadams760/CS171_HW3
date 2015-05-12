#! /usr/bin/env python
import network
import CLI

if __name__ == '__main__':
    sites = [(1,'localhost',9991), (2,'localhost',9992), (3,'localhost',9993), (4,'localhost',9994),(5,'localhost',9995)]
    t = CLI.CLI(1,sites,'localhost',9991,'localhost',9999)
    t.start()

