#! /usr/bin/env python
#! coding: utf-8
# Copyright (C) 2017-2018 cmj<cmj@cmj.tw>. All right reserved.

import pytest
import tempfile
from sisyphus import cli

@pytest.fixture
def client(mocker):
    with mocker.patch.object(cli, 'server'):
        yield cli

def test_args(client):
    client.run('-s')
    client.server.assert_called_once()

def test_single_task(mocker, client):
    with tempfile.NamedTemporaryFile('w', suffix='.py') as fd:
        fd.write('def foo():\n\tprint("Run ...")\n')
        fd.seek(0)

        client.run(f'run --count 1 -F foo {fd.name}')
        client.run(f'run --count 2 -F foo {fd.name}')
