#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__      = "Ankirama"
__version__     = "1.0"
__email__       = "ankirama@gmail.com"
__status__      = "Development"

import os, sys
import requests, transmissionrpc
from workflow import Workflow, ICON_WEB, web, ICON_WARNING, PasswordNotFound
from transmissionrpc.error import TransmissionError
from workflow.notify import notify

class Transmission:
    _wf = None
    _tc = None

    def __init__(self, wf):
        self._wf = wf

    def registerConfig(self, server, port, user=None, password=None):
        '''
        Create our config with workflow.save_password (saved into your keychains)
        server must not include http:// or https:// since transmissionrpc adds it
        a server can be localhost or hellworldz.com for example
        It will overwrite your current config every time you call it
        '''
        try:
            self._wf.save_password('nyaa_server_address', server)
            self._wf.save_password('nyaa_server_port', port)
            if (user and password):
                self._wf.save_password('nyaa_server_user', user)
                self._wf.save_password('nyaa_server_password', password)
        except:
            # Error here
            return False

    def resetConfig(self):
        '''
        Reset keychains
        delete_password can raise error PasswordNotFound but we don't need it
        '''
        try:
            self._wf.delete_password('nyaa_server_address')
            self._wf.delete_password('nyaa_server_port')
            self._wf.delete_password('nyaa_server_user')
            self._wf.delete_password('nyaa_server_password')
        finally:
            notify(title='Configuration removed')

    def connection(self):
        '''
        Log a user into its server with transmissionrpc
        '''
        try:
            server = self._wf.get_password('nyaa_server_address')
            port = self._wf.get_password('nyaa_server_port')
        except PasswordNotFound:
            self._wf.add_item('Your config file is not good.',
                subtitle='You must authenticate you again.',
                icon=ICON_WARNING)
            self._wf.send_feedback()
            return False
        else:
            try:
                user = self._wf.get_password("nyaa_server_user")
            except PasswordNotFound:
                user = None
                password = None
            else:
                try:
                    password = self._wf.get_password("nyaa_server_password")
                except PasswordNotFound:
                    self._wf.add_item('Your config file is not good.',
                        subtitle='You must authenticate you again.',
                        icon=ICON_WARNING)
                    self._wf.send_feedback()
                    return False
                else:
                    try:
                        self._tc = transmissionrpc.Client(address=server, port=port, user=user, password=password)
                        return True
                    except TransmissionError:
                        self._wf.add_item('Unable to signin with transmissionrpc',
                            subtitle='You should re-authenticate your server or check your connection.',
                            icon=ICON_WARNING)
                        self._wf.send_feedback()
                        return False
    def addTorrent(self, url):
        '''
        Add torrent on your server
        '''
        if not self._tc:
            notify(title='Configuration not found',
                text='You must authenticate you first.')
            return False
        else:
            try:
                if self._tc.add_torrent(url):
                    notify(title='Torrent added in your transmission server')
                    return True
                else:
                    notify(title='Unable to add your torrent',
                        text='Please check your torrent and try to resend it.')
                    return False
            except:
                notify(title='Unable to add your torrent',
                    text='Please check your torrent and try to resend it.')
                return False
