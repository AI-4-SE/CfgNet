from cfgnet.linker.substring_linker import SubstringLinker
from cfgnet.config_types.config_types import ConfigType
from cfgnet.network.nodes import OptionNode, ValueNode


def test_check_config_types():
    linker = SubstringLinker()

    option_port = OptionNode("port", "2", config_type=ConfigType.PORT)
    port_value = ValueNode(name="8000")
    option_port.add_child(port_value)

    option_username = OptionNode("username", "3", config_type=ConfigType.USERNAME)
    username_value = ValueNode(name="max")
    option_username.add_child(username_value)

    option_url = OptionNode("url", "3", ConfigType.URL)
    url_value = ValueNode(name="http://127.0.0.1:8000")
    option_url.add_child(url_value)

    option_email = OptionNode("email", "3", config_type=ConfigType.EMAIL)
    email_value = ValueNode(name="max@test.com")
    option_email.add_child(email_value)

    option_command = OptionNode("run", "3", config_type=ConfigType.COMMAND)
    command_value = ValueNode(name="python3 run.py")
    option_command.add_child(command_value)

    option_path = OptionNode("path", "4", config_type=ConfigType.PATH)
    path_value = ValueNode(name="run.py")
    option_path.add_child(path_value)

    assert linker._check_config_types(url_value, port_value)
    assert linker._check_config_types(username_value, email_value)
    assert linker._check_config_types(command_value, path_value)
