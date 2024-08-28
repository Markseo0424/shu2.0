import socket
import time


def isInternetConnected():
    """
    checks internet is connected or not.
    function gets host name, if internet is lost returns 127.0.0.1
    :return: whether internet is connected or not
    """
    ip = socket.gethostbyname(socket.gethostname())
    return ip != "127.0.0.1"


if __name__ == "__main__":
    start = time.time()
    # print("hello world!")
    print(isInternetConnected())
    print(time.time() - start)