import socket
import sys
import ssl

def retrieve_url(url):
    """
    return bytes of the body of the document at url
    """
    host = ""
    path = "/"
    port = 80
    check = None
    if url.find("http://") != -1:
        check = 0
        url = url.replace("http://", "")
        host = url

        if url.find("/") != -1:
            url = url.split("/", 1)
            path = "/"+url[1]
            host = url[0]

        if url[0].find(":") != -1:
            url = url[0].split(":")
            host = url[0]
            port = int(url[1])

    elif url.find("https://") != -1:
        check = 1
        url = url.replace("https://", "")
        host = url
        
        if url.find("/") != -1:
            url = url.split("/", 1)
            path = "/"+url[1]
            host = url[0]

        if url[0].find(":") != -1:
            url = url[0].split(":")
            host = url[0]
            port = int(url[1])

    
    # print(host, path, port, check)
    if check == 1:
        cont = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        sslSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sslSock.connect((host, 443))
            sock = cont.wrap_socket(sslSock)
            msg = ("GET {} HTTP/1.1\r\nHost: {}:{}\r\nUser-Agent: python-requests/2.28.2\r\nConnection: close\r\n\r\n".format(path, host, port))
            sock.send(msg.encode())
            # print(msg)
        except socket.error:
            return None
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            msg = ("GET {} HTTP/1.1\r\nHost: {}:{}\r\nUser-Agent: python-requests/2.28.2\r\nConnection: close\r\n\r\n".format(path, host, port))
            sock.send(msg.encode())
            # print(msg)
        except socket.error:
            return None
    # print(msg)

    ans = b''

    while True:
        try:
            data = sock.recv(4096)
            # print(data.decode())
            if not data or b"":
                break
            ans += data
            # print(ans)
        except socket.error:
            # print("L")
            return None
    # print(ans.find(b'200 OK'))
    # print(ans.decode())
    if ans.find(b'200 OK') != -1:
        ans = ans.split(b'\r\n\r\n', 1)
        # print(ans[1].decode())
        res = ans[1]
        # print(res)
        if ans[0].find(b'Transfer-Encoding: chunked') != -1:
            varData = b''
            while True:
                chunk = res.split(b'\r\n', 1)
                if chunk[0] == b'0':
                    break
                val = int(chunk[0], 16)
                var = chunk[1]
                varData += var[:val]
                res = var[val+2:]
            res = varData
        return res
    elif ans.find(b'Location') != -1:
        pos = ans.find(b'Location')
        pos2 = ans.find(b'\r\n', pos)
        newUrl = ans[pos+10:pos2].decode('utf-8')
        return retrieve_url(newUrl)

    return None

if __name__ == "__main__":
    sys.stdout.buffer.write(retrieve_url(sys.argv[1])) # pylint: disable=no-member
    # retrieve_url('http://www.fieggen.com/shoelace')
