"""Shared, read-only Locust scenario for an INVISAP module."""

import os

from locust import HttpUser, between, task


class ModuleLoadUser(HttpUser):
    abstract = True
    wait_time = between(1, 2)
    endpoint = '/'
    module_name = 'INVISAP'
    request_description = 'consulta GET de solo lectura'

    def on_start(self):
        session_cookie = os.environ.get('INVISAP_PERF_SESSION_COOKIE')
        if session_cookie:
            self.client.headers['Cookie'] = session_cookie

    @task
    def read_module_endpoint(self):
        with self.client.get(
            self.endpoint,
            name=f'{self.module_name} - {self.request_description}',
            catch_response=True,
            allow_redirects=False,
            timeout=15,
        ) as response:
            if response.status_code != 200:
                response.failure(f'HTTP {response.status_code}')
