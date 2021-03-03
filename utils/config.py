'''
# @Author       : Chr_
# @Date         : 2020-07-29 14:21:39
# @LastEditors  : Jireh
# @LastEditTime : 2021-03-03 15:06:39
# @Description  : 读取并验证配置
'''

import os
import toml
import chardet
from utils.log import get_logger, init_logger

logger = get_logger('Setting')

SCRIPT_PATH = f'{os.path.split(os.path.realpath(__file__))[0][:-5]}'

DEFAULT_PATH = f'{SCRIPT_PATH}config.toml'

CFG = {}


def get_script_path() -> str:
    '''
    获取脚本所在路径

    返回:
        str: 脚本所在路径
    '''
    return (SCRIPT_PATH)


def get_config(key: str) -> dict:
    '''
    获取某一项配置

    参数:
        key: 要获取的设置键名
    返回:
        dict: 配置信息字典
    '''
    return (CFG.get(key))


def get_all_config() -> dict:
    '''
    获取全部配置

    返回:
        dict: 配置信息字典
    '''
    return (CFG)


def load_config(path: str = DEFAULT_PATH) -> dict:
    '''
    读取并验证配置

    参数:
        [path]: 配置文件路径,默认为config.toml
    返回:
        dict: 验证过的配置字典
    '''
    global CFG
    try:
        logger.debug('开始读取配置')
        with open(path, 'rb') as f:
            content = f.read()
        detect = chardet.detect(content)
        encode = detect.get('encode', 'utf-8')
        raw_cfg = dict(toml.loads(content.decode(encode)))
        CFG = verify_config(raw_cfg)
        debug = os.environ.get('mode', 'release').lower()
        level = 0 if debug == 'debug' else 20
        init_logger(level)
        logger.debug('配置验证通过')
        return (CFG)

    except FileNotFoundError:
        logger.error(f'[*] 配置文件[{path}]不存在')
        raise FileNotFoundError(f'[*] 配置文件[{path}]不存在')
    except ValueError as e:
        logger.error(f'[*] 配置文件验证失败 [{e}]', exc_info=True)


def verify_config(cfg: dict) -> dict:
    '''
    验证配置

    参数:
        cfg: 配置字典
    返回:
        dict: 验证过的配置字典,剔除错误的和不必要的项目
    '''
    vcfg = {'main': {'check_update': False, 'debug': False},
            'ftqq': {'enable': False, 'skey': '', 'only_on_error': False},
            'email': {'port': 465, 'server': '', 'password': '', 'user': '',
                      'recvaddr': '', 'sendaddr': '', 'only_on_error': False},
            '52pojie': [],
            'houqijun': [],
            }

    wuaipojie = cfg.get('52pojie', {})
    houqijun = cfg.get('houqijun', {})
    vcfg['52pojie'] = wuaipojie
    vcfg['houqijun'] = houqijun

    main = cfg.get('main', {})
    if main and isinstance(main, dict):
        debug = bool(main.get('debug', False))
        check_update = bool(main.get('check_update', True))
        vcfg['main'] = {'check_update': check_update, 'debug': debug}
    else:
        logger.debug('[main]节配置有误或者未配置,将使用默认配置')

    ftqq = cfg.get('ftqq', {})
    if ftqq and isinstance(ftqq, dict):
        enable = bool(ftqq.get('enable', False))
        skey = ftqq.get('skey', "")
        only_on_error = bool(ftqq.get('only_on_error', False))
        if enable and not skey:
            raise ValueError('开启了FTQQ模块,但是未指定SKEY,请检查配置文件')
        vcfg['ftqq'] = {'enable': enable, 'skey': skey,
                        'only_on_error': only_on_error}
    else:
        logger.debug('[ftqq]节配置有误或者未配置,将使用默认配置')

    email = cfg.get('email', {})
    if email and isinstance(email, dict):
        enable = bool(email.get('enable', False))
        try:
            port = int(email.get('port', 0))
        except ValueError:
            port = 465
            logger.warning('[*] [email]节port必须为数字')
        server = email.get('server', '')
        password = email.get('password', '')
        user = email.get('user', '')
        recvaddr = email.get('recvaddr', '')
        sendaddr = email.get('sendaddr', '')
        only_on_error = bool(email.get('only_on_error', False))
        if enable and not (port and server
                           and password and user and recvaddr and sendaddr):
            raise ValueError('开启了email模块,但是配置不完整,请检查配置文件')
        vcfg['email'] = {'enable': enable, 'port': port, 'server': server,
                         'password': password, 'user': user,
                         'recvaddr': recvaddr, 'sendaddr': sendaddr,
                         'only_on_error': only_on_error}
    else:
        logger.debug('[email]节配置有误或者未配置,将使用默认配置')

    return (vcfg)
