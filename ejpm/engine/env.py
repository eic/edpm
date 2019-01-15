


class EnvManipulation(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def gen_bash(self, existing_list):
        raise NotImplementedError()

    def gen_csh(self, existing_list):
        raise NotImplementedError()

    @staticmethod
    def mentioned_before(existing_list, env_manip):
        for existing in existing_list:
            if env_manip.name == existing.name:
                return True
        return False


class EnvSource(EnvManipulation):
    def __init__(self, name):
        super(EnvSource, self).__init__(name, None)

    def gen_bash(self, existing_list):
        return "source {name}".format(name=self.name)

    def gen_csh(self, existing_list):
        return self.gen_bash()


class EnvAppend(EnvManipulation):

    def __init__(self, name, value):
        super(EnvAppend, self).__init__(name, value)

    def gen_bash(self, existing_list):
        ret_str = '\n# === {name} ===\n\n'

        if not self.mentioned_before(existing_list, self):
            ret_str += (
                '# Make sure {name} is set\n'
                'if [ -z "${name}" ]; then\n' 
                '    export {name}="{value}"\n'
                'else\n'
                '    export {name}=${name}:"{value}"'
                'fi')
        else:
            ret_str += 'export {name}=${name}:"{value}"'

        return ret_str.format(name=self.name, value=self.value)

    def gen_csh(self, existing_list):

        ret_str = '\n# === {name} ===\n\n'

        if not self.mentioned_before(existing_list, self):
            ret_str += (
                '# Make sure {name} is set\n'
                'if ( ! $?{name} ) then\n'
                '    setenv {name} "{value}"\n'
                'else\n'
                '    setenv {name} ${name}:"{value}"'
                'fi')
        else:
            ret_str += 'setenv {name} ${name}:"{value}"'

        return ret_str.format(name=self.name, value=self.value)


class EnvPrepend(EnvManipulation):
    def __init__(self, name, value):
        super(EnvPrepend, self).__init__(name, value)

    def gen_bash(self, existing_list):
        ret_str = '\n# === {name} ===\n\n'

        if not self.mentioned_before(existing_list, self):
            ret_str += (
                '# Make sure {name} is set\n'
                'if [ -z "${name}" ]; then\n' 
                '    export {name}="{value}"\n'
                'else\n'
                '    export {name}="{value}":${name}'
                'fi')
        else:
            ret_str += 'export {name}="{value}":${name}'

        return ret_str.format(name=self.name, value=self.value)

    def gen_csh(self, existing_list):

        ret_str = '\n# === {name} ===\n\n'

        if not self.mentioned_before(existing_list, self):
            ret_str += (
                '# Make sure {name} is set\n'
                'if ( ! $?{name} ) then\n'
                '    setenv {name} "{value}"\n'
                'else\n'
                '    setenv {name} "{value}":${name}'
                'fi')
        else:
            ret_str += 'setenv {name} "{value}":${name}'

        return ret_str.format(name=self.name, value=self.value)


class EnvSet(EnvManipulation):
    def __init__(self, name, value):
        super(EnvSet, self).__init__(name, value)

    def gen_bash(self, existing_list):
        return 'export {name}="{value}"'.format(name=self.name, value=self.value)

    def gen_csh(self, existing_list):
        return 'setenv {name} "{value}"'.format(name=self.name, value=self.value)

