import pickle

def load_cookies():
    """ 读取保存的cookies """
    try:
        with open('cookies.pkl', 'rb') as fr:
            cookies = pickle.load(fr)
        return cookies
    except Exception as e:
        print('-' * 10, '加载cookies失败', '-' * 10)
        print(e)


def save_cookies(login_cookies):
    """ 保存cookies """
    with open('cookies.pkl', 'wb') as fw:
        pickle.dump(login_cookies, fw)