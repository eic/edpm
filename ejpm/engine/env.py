
class BaseEnvAction(object):

    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    def gen_bash(self):
        raise NotImplementedError

    def gen_csh(self):
        raise NotImplementedError

    def update_python_env(self):
        raise NotImplementedError


class EnvSet(BaseEnvAction):

    def __init__(self, name, value, description):
        super(EnvSet, self).__init__(name, value, description)

    def gen_bash(self):
        raise NotImplementedError

    def gen_csh(self):
        raise NotImplementedError

    def update_python_env(self):
        raise NotImplementedError


class EnvAppend(BaseEnvAction):

    def __init__(self, name, value, description):
        super(EnvAppend, self).__init__(name, value, description)

    def gen_bash(self):
        raise NotImplementedError

    def gen_csh(self):
        raise NotImplementedError

    def update_python_env(self):
        raise NotImplementedError


class EnvPrepend(BaseEnvAction):

    def __init__(self, name, value, description):
        super(EnvPrepend, self).__init__(name, value, description)

    def gen_bash(self):
        raise NotImplementedError

    def gen_csh(self):
        raise NotImplementedError

    def update_python_env(self):
        raise NotImplementedError
