'''
    Copyright (c) 2014  OpenISDM

    Project Name:

        OpenISDM MAD-IS

    Version:

        1.0

    File Name:

        fileSystem.py

    Abstract:

        fileSystem.py is a module of Interface Server (IS) of
        Mobile Assistance for Disasters (MAD) in the OpenISDM
        Virtual Repository project.
        It handles the items of search and creating on file system.

    Authors:

        Bai Shan-Wei, k0969032@gmail.com

    License:

        GPL 3.0 This file is subject to the terms and conditions defined
        in file 'COPYING.txt', which is part of this source code package.

    Major Revision History:

        2014/6/10: complete version 1.0
'''


import os
import json
import socket
import urllib
import urllib2


class FileSystem:
    """
        The class "FileSystem" allow you/me to build folder&file        on local computer.
    """

    # get the current directory path.
    mydir = os.path.dirname(os.path.abspath(__file__))
    # get local ip address
    my_web_addr = 'http://'+socket.gethostbyname(socket.gethostname())

    my_topic_dir = mydir + '/static/Topic/'

    def create_folder(self, foldername):

        '''
            Create folder on local computer.

            foldername:
                the folder name that want to name.
        '''

        path = FileSystem.mydir+foldername

        # if file not exist, create new.
        if not os.path.exists(path):
            os.makedirs(path, 0755)

    def create_xml_file(self, city, content):
        '''
            Create xml file that about district information by city.

            city:
                The city user have to serve.
            content:
                The xml content that will be inserted.
        '''

        filedir = FileSystem.mydir+"/District Info/"+city+'.xml'
        f = open(filedir, "w")
        f.write(content)
        f.close()

    def download_file(self, topic_dir, pos_id, format, content, mode):
        '''
            Create topic file that have various formats.

            topic_dir:
                Path that place topic files.
            pos_id:
                The POS server ID.
            format:
                Json, rdf , png or other.
            content:
                The content that will be inserted to make file.
            mode:
                Write or Read.
        '''
        filename = FileSystem.mydir+topic_dir+pos_id+'/'+pos_id+'.'+format
        f = open(filename, mode)
        if format == "png":
            response = urllib2.urlopen(content)
            f.write(response.read())
        else:
            f.write(content)
        f.close()
