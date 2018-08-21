#! /usr/bin/env python
#! coding: utf-8
# Copyright (C) 2017-2018 cmj<cmj@cmj.tw>. All right reserved.

import pytest
from sisyphus import cli

class TestCommandLine(object):

    @pytest.fixture
    def client(self, mocker): # pylint: disable=no-self-use
        with mocker.patch.object(cli, 'server'):
            with mocker.patch.object(cli, 'client'):
                yield cli

    def test_args(self, client): # pylint: disable=no-self-use
        client.run('-s')
        client.server.assert_called_once()

        client.run('test')
        client.client.assert_called_with('test')
